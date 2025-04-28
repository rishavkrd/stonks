import pandas as pd
from datetime import datetime, timedelta
import os

class StockScreener:
    def __init__(self, data_folder):
        """
        Initialize screener with the folder containing stock data CSVs
        
        Args:
            data_folder (str): Path to folder containing stock CSV files
        """
        self.data_folder = data_folder
        self.stocks_data = {}  # Cache for loaded stock data
        
    def load_stock_data(self, symbol):
        """Load stock data from CSV if not already in cache"""
        if symbol not in self.stocks_data:
            file_path = os.path.join(self.data_folder, f"{symbol}_stock_data.csv")
            df = pd.read_csv(file_path)
            # Convert to datetime with UTC=True to handle timezone consistently
            df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_convert(None)
            df.set_index('Date', inplace=True)
            self.stocks_data[symbol] = df
        return self.stocks_data[symbol]
    
    def get_data_before_date(self, df, backtest_date, days):
        """Get data for specified number of days before the backtest date"""
        backtest_date = pd.to_datetime(backtest_date, utc=True).tz_convert(None)
        mask = df.index <= backtest_date
        return df[mask].tail(days)
    
    def lowest_price_filter(self, symbol, backtest_date, days):
        """
        Find lowest price in given day length before backtest date
        
        Args:
            symbol (str): Stock symbol
            backtest_date (str): Date in 'YYYY-MM-DD' format
            days (int): Number of days to look back
        
        Returns:
            float: Lowest price in the period
        """
        df = self.load_stock_data(symbol)
        period_data = self.get_data_before_date(df, backtest_date, days)
        return period_data['Close'].min()
    
    def highest_price_filter(self, symbol, backtest_date, days):
        """
        Find highest price in given day length before backtest date
        
        Args:
            symbol (str): Stock symbol
            backtest_date (str): Date in 'YYYY-MM-DD' format
            days (int): Number of days to look back
        
        Returns:
            float: Highest price in the period
        """
        df = self.load_stock_data(symbol)
        period_data = self.get_data_before_date(df, backtest_date, days)
        return period_data['Close'].max()
    
    def total_volume_price_filter(self, symbol, backtest_date, days):
        """
        Calculate total (Volume * Price) in given day length before backtest date
        
        Args:
            symbol (str): Stock symbol
            backtest_date (str): Date in 'YYYY-MM-DD' format
            days (int): Number of days to look back
        
        Returns:
            float: Total volume * price in the period
        """
        df = self.load_stock_data(symbol)
        period_data = self.get_data_before_date(df, backtest_date, days)
        return (period_data['Volume'] * period_data['Close']).sum()
    
    def save_results(self, backtest_date, passing_symbols, count, results, lookback_days, filters):
        """
        Save screening results to text files
        
        Args:
            backtest_date (str): Backtest date used
            passing_symbols (list): List of symbols that passed filters
            count (int): Number of passing symbols
            results (dict): Detailed results for passing symbols
            lookback_days (int): Number of days looked back
            filters (dict): Filters used
        """
        # Create screened directory if it doesn't exist
        if not os.path.exists('screened'):
            os.makedirs('screened')
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Format backtest date for filenames (convert YYYY-MM-DD to MM-DD-YYYY)
        date_obj = datetime.strptime(backtest_date, '%Y-%m-%d')
        file_date = date_obj.strftime('%m-%d-%Y')
        
        # Save detailed results
        details_file = f"screened/results_{file_date}.txt"
        with open(details_file, 'w') as f:
            f.write(f"Stock Screening Results\n")
            f.write(f"=====================\n\n")
            f.write(f"Backtest Date: {file_date}\n")  # Also update display date format
            f.write(f"Lookback Days: {lookback_days}\n")
            f.write(f"Total stocks screened: {len(self.stocks_data)}\n")
            f.write(f"Stocks passing all filters: {count}\n\n")
            
            f.write("Applied Filters:\n")
            for metric, condition in filters.items():
                f.write(f"- {metric}: {condition['operator']} {condition['value']}\n")
            
            f.write("\nPassing Stocks:\n")
            f.write("==============\n\n")
            
            for symbol in passing_symbols:
                data = results[symbol]
                f.write(f"Symbol: {symbol}\n")
                f.write(f"Lowest price ({lookback_days} days): ${data['lowest_price']:.2f}\n")
                f.write(f"Highest price ({lookback_days} days): ${data['highest_price']:.2f}\n")
                f.write(f"Total Volume*Price ({lookback_days} days): ${data['volume_price']:,.2f}\n")
                f.write("-" * 50 + "\n")
        
        # Save TradingView format
        tv_file = f"screened/tv_{file_date}_{timestamp}.txt"
        with open(tv_file, 'w') as f:
            tradingview_symbols = ','.join(passing_symbols)
            f.write(tradingview_symbols)
        
        return details_file, tv_file

    def screen_stocks(self, symbols, backtest_date, days, filters=None):
        """
        Screen stocks based on specified filters and return passing symbols
        
        Args:
            symbols (list): List of stock symbols to screen
            backtest_date (str): Date in 'YYYY-MM-DD' format
            days (int): Number of days to look back
            filters (dict): Dictionary of filter conditions
        
        Returns:
            tuple: (passing_symbols: list, count: int, details: dict)
        """
        results = {}
        passing_symbols = []
        
        for symbol in symbols:
            try:
                result = {
                    'lowest_price': self.lowest_price_filter(symbol, backtest_date, days),
                    'highest_price': self.highest_price_filter(symbol, backtest_date, days),
                    'volume_price': self.total_volume_price_filter(symbol, backtest_date, days)
                }
                
                # Apply filters if provided
                passes_all_filters = True
                if filters:
                    for metric, condition in filters.items():
                        value = result[metric]
                        operator = condition['operator']
                        threshold = condition['value']
                        
                        if operator == '>':
                            passes_all_filters &= value > threshold
                        elif operator == '<':
                            passes_all_filters &= value < threshold
                        elif operator == '>=':
                            passes_all_filters &= value >= threshold
                        elif operator == '<=':
                            passes_all_filters &= value <= threshold
                        elif operator == '==':
                            passes_all_filters &= value == threshold
                        
                        if not passes_all_filters:
                            break
                
                if passes_all_filters:
                    passing_symbols.append(symbol)
                    results[symbol] = result
                    
            except Exception as e:
                print(f"Error processing {symbol}: {str(e)}")
        
        # Save results to files
        details_file, tv_file = self.save_results(
            backtest_date, 
            passing_symbols, 
            len(passing_symbols), 
            results, 
            days, 
            filters
        )
        
        print(f"\nResults saved to:")
        print(f"Detailed results: {details_file}")
        print(f"TradingView format: {tv_file}")
        
        return passing_symbols, len(passing_symbols), results

# Example usage
if __name__ == "__main__":
    # Initialize screener with your data folder
    screener = StockScreener("stock_data_20250427_191539")
    
    # Example parameters
    backtest_date = "2020-01-01"
    lookback_days = 20
    symbols = ["AAPL", "MSFT", "GOOGL"]  # Add your symbols here
    
    # Example filters
    filters = {
        'lowest_price': {'operator': '>', 'value': 10},
        'highest_price': {'operator': '<', 'value': 100},
        'volume_price': {'operator': '>', 'value': 1000000}
    }
    
    # Get results
    passing_symbols, count, results = screener.screen_stocks(symbols, backtest_date, lookback_days, filters)
    
    # Print summary
    print(f"\nScreening Results:")
    print(f"Total stocks screened: {len(symbols)}")
    print(f"Stocks passing all filters: {count}")
    print(f"\nPassing Symbols: {', '.join(passing_symbols)}")
    
    # Print detailed results for passing stocks
    for symbol in passing_symbols:
        data = results[symbol]
        print(f"\nResults for {symbol}:")
        print(f"Lowest price (20 days): ${data['lowest_price']:.2f}")
        print(f"Highest price (20 days): ${data['highest_price']:.2f}")
        print(f"Total Volume*Price (20 days): ${data['volume_price']:,.2f}")
    
    # Generate TradingView format - modified to only include symbols
    tradingview_symbols = ','.join(passing_symbols)  # Removed NYSE: prefix
    print(f"\nTradingView Format:")
    print(tradingview_symbols) 