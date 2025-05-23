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
        self.output_dir = 'screened'  # Default output directory
        
    def set_output_dir(self, directory):
        """Set the output directory for results and TV files"""
        self.output_dir = directory
        os.makedirs(self.output_dir, exist_ok=True)
        
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
    
    def price_change_percentage(self, symbol, backtest_date, days):
        """
        Calculate percentage change from lowest price to current price
        
        Args:
            symbol (str): Stock symbol
            backtest_date (str): Date in 'YYYY-MM-DD' format
            days (int): Number of days to look back
        
        Returns:
            float: Percentage change from lowest to current price
        """
        df = self.load_stock_data(symbol)
        period_data = self.get_data_before_date(df, backtest_date, days)
        if period_data.empty:
            return 0
        
        lowest_price = period_data['Close'].min()
        current_price = period_data['Close'].iloc[-1]
        
        percentage_change = ((current_price - lowest_price) / lowest_price) * 100
        return percentage_change
    
    def save_results(self, backtest_date, passing_symbols, count, results, lookback_days, filters, tv_symbols, min_price_change_pct=None):
        """
        Save screening results to text files with price change percentage
        
        Args:
            backtest_date (str): Backtest date used
            passing_symbols (list): List of symbols that passed filters
            count (int): Number of passing symbols
            results (dict): Detailed results for passing symbols
            lookback_days (int): Number of days looked back
            filters (dict): Filters used
            tv_symbols (list): List of symbols to include in TV file
            min_price_change_pct (float): Minimum price change percentage required
        """
        # Generate timestamp
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Format backtest date for filenames (keep YYYY-MM-DD format)
        date_obj = datetime.strptime(backtest_date, '%Y-%m-%d')
        file_date = date_obj.strftime('%Y-%m-%d')  # Changed to YYYY-MM-DD
        
        # Save detailed results
        details_file = os.path.join(self.output_dir, f"results_{file_date}.txt")
        with open(details_file, 'w') as f:
            f.write(f"Stock Screening Results\n")
            f.write(f"=====================\n\n")
            f.write(f"Backtest Date: {file_date}\n")  # Also use YYYY-MM-DD in content
            f.write(f"Lookback Days: {lookback_days}\n")
            f.write(f"Total stocks screened: {len(self.stocks_data)}\n")
            f.write(f"Stocks passing all filters: {count}\n")
            if min_price_change_pct is not None:
                f.write(f"Minimum price change required: {min_price_change_pct}%\n")
            f.write("\n")
            
            f.write("Applied Filters:\n")
            for metric, condition in filters.items():
                f.write(f"- {metric}: {condition['operator']} {condition['value']}\n")
            
            if count > 0:
                f.write("\nPassing Stocks (Sorted by Price Change %):\n")
                f.write("=====================================\n\n")
                
                for symbol in passing_symbols:
                    data = results[symbol]
                    f.write(f"Symbol: {symbol}\n")
                    f.write(f"Price Change: {data['price_change_pct']:.2f}%\n")
                    f.write(f"Lowest price ({lookback_days} days): ${data['lowest_price']:.2f}\n")
                    f.write(f"Highest price ({lookback_days} days): ${data['highest_price']:.2f}\n")
                    f.write(f"Total Volume*Price ({lookback_days} days): ${data['volume_price']:,.2f}\n")
                    f.write("-" * 50 + "\n")
        
        # Save TradingView format only if there are passing stocks
        tv_file = None
        if count > 0 and tv_symbols:
            tv_file = os.path.join(self.output_dir, f"tv_{file_date}_{timestamp}.txt")
            with open(tv_file, 'w') as f:
                tradingview_symbols = ','.join(tv_symbols)
                f.write(tradingview_symbols)
        
        return details_file, tv_file

    def screen_stocks(self, symbols, backtest_date, days, filters=None, min_price_change_pct=None, max_tv_stocks=1000):
        """
        Screen stocks based on filters and price change percentage
        
        Args:
            symbols (list): List of stock symbols to screen
            backtest_date (str): Date in 'YYYY-MM-DD' format
            days (int): Number of days to look back
            filters (dict): Dictionary of filter conditions
            min_price_change_pct (float): Minimum price change percentage required
            max_tv_stocks (int): Maximum number of stocks to include in TV file
        """
        results = {}
        passing_symbols = []
        
        for symbol in symbols:
            try:
                result = {
                    'lowest_price': self.lowest_price_filter(symbol, backtest_date, days),
                    'highest_price': self.highest_price_filter(symbol, backtest_date, days),
                    'volume_price': self.total_volume_price_filter(symbol, backtest_date, days),
                    'price_change_pct': self.price_change_percentage(symbol, backtest_date, days)
                }
                
                # Apply basic filters
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
                
                # Apply price change percentage filter
                if min_price_change_pct is not None:
                    passes_all_filters &= result['price_change_pct'] >= min_price_change_pct
                
                if passes_all_filters:
                    passing_symbols.append(symbol)
                    results[symbol] = result
                    
            except Exception as e:
                print(f"Error processing {symbol}: {str(e)}")
        
        # Sort results by price change percentage
        sorted_results = {}
        sorted_symbols = sorted(
            passing_symbols,
            key=lambda x: results[x]['price_change_pct'],
            reverse=True
        )
        
        # Limit to max_tv_stocks for TV file
        tv_symbols = sorted_symbols[:max_tv_stocks]
        
        for symbol in passing_symbols:
            sorted_results[symbol] = results[symbol]
        
        # Save results to files
        details_file, tv_file = self.save_results(
            backtest_date, 
            passing_symbols, 
            len(passing_symbols), 
            sorted_results, 
            days, 
            filters,
            tv_symbols,  # Pass limited symbols for TV file
            min_price_change_pct
        )
        
        print(f"\nResults saved to:")
        print(f"Detailed results: {details_file}")
        print(f"TradingView format: {tv_file}")
        
        return passing_symbols, len(passing_symbols), sorted_results

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
        # 'lowest_price': {'operator': '>', 'value': 10},
        # 'highest_price': {'operator': '<', 'value': 100},
        'volume_price': {'operator': '>', 'value': 50000000}
    }
    
    # Get results
    passing_symbols, count, results = screener.screen_stocks(symbols, backtest_date, lookback_days, filters, min_price_change_pct=5.0)
    
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