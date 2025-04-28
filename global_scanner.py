import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from stock_screener import StockScreener

class GlobalScanner:
    def __init__(self, data_folder):
        self.screener = StockScreener(data_folder)
        self.base_output_dir = "screened/global_screen_" + datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs(self.base_output_dir, exist_ok=True)
        
    def get_all_symbols(self, limit=None):
        """
        Get list of stock symbols from the data folder
        
        Args:
            limit (int): Number of files to process (None for all files)
        """
        files = os.listdir(self.screener.data_folder)
        stock_files = [f for f in files if f.endswith('_stock_data.csv')]
        if limit:
            stock_files = stock_files[:limit]
        return [f.replace('_stock_data.csv', '') for f in stock_files]
    
    def generate_backtest_dates(self, start_year=2000):
        """Generate quarterly backtest dates from start_year till current year"""
        end_date = datetime.now()
        dates = []
        
        current_date = datetime(start_year, 1, 1)
        while current_date <= end_date:
            for month in [1, 4, 7, 10]:  # Quarterly months
                test_date = datetime(current_date.year, month, 1)
                if test_date <= end_date:
                    dates.append(test_date.strftime('%Y-%m-%d'))
            current_date = datetime(current_date.year + 1, 1, 1)
            
        return dates
    
    def run_global_scan(self, lookback_days=20, filters=None, min_price_change_pct=None):
        """
        Run screening for all stocks across all quarterly dates
        
        Args:
            lookback_days (int): Number of days to look back for each screen
            filters (dict): Filtering conditions
            min_price_change_pct (float): Minimum price change percentage required
        """
        symbols = self.get_all_symbols()
        dates = self.generate_backtest_dates()
        results_summary = []
        
        print(f"Starting global scan with {len(symbols)} stocks across {len(dates)} dates")
        print(f"Results will be saved in: {self.base_output_dir}")
        
        # Set the output directory in screener
        self.screener.set_output_dir(self.base_output_dir)
        
        for backtest_date in dates:
            try:
                passing_symbols, count, details = self.screener.screen_stocks(
                    symbols, 
                    backtest_date, 
                    lookback_days, 
                    filters,
                    min_price_change_pct
                )
                
                results_summary.append({
                    'date': backtest_date,
                    'passing_count': count
                })
                
                print(f"Completed screening for {backtest_date}: Found {count} matching stocks")
                
            except Exception as e:
                print(f"Error processing date {backtest_date}: {str(e)}")
        
        # Create summary plot
        self.plot_results_summary(results_summary)
        
        return results_summary
    
    def plot_results_summary(self, results_summary):
        """Create a plot showing number of passing stocks over time"""
        df = pd.DataFrame(results_summary)
        df['date'] = pd.to_datetime(df['date'])
        
        plt.figure(figsize=(15, 8))
        plt.plot(df['date'], df['passing_count'], marker='o')
        plt.title('Number of Stocks Passing Filters Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Passing Stocks')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot
        plot_file = os.path.join(self.base_output_dir, 'results_summary.png')
        plt.savefig(plot_file)
        plt.close()
        
        # Save data
        csv_file = os.path.join(self.base_output_dir, 'results_summary.csv')
        df.to_csv(csv_file, index=False)

if __name__ == "__main__":
    # Initialize global scanner
    scanner = GlobalScanner("stock_data_20250427_191539")
    
    # Define filters
    filters = {
        'volume_price': {'operator': '>', 'value': 50000000}
    }
    
    # Run global scan with all files
    results = scanner.run_global_scan(
        lookback_days=60,
        filters=filters,
        min_price_change_pct=30.0
    ) 