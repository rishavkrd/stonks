import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import time

def get_max_stock_history(symbol):
    """
    Get the earliest available date for a stock symbol
    """
    try:
        stock = yf.Ticker(symbol)
        # Get max historical data
        df = stock.history(period="max")
        if not df.empty:
            return df.index[0].strftime('%Y-%m-%d')
        return None
    except Exception as e:
        print(f"Error checking history for {symbol}: {str(e)}")
        return None

def download_stock_data(symbol, start_date=None, end_date=None, output_dir='data'):
    """
    Download stock data for a given symbol and save it to a CSV file.
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL' for Apple)
        start_date (str): Start date in 'YYYY-MM-DD' format (default: 5 years ago)
        end_date (str): End date in 'YYYY-MM-DD' format (default: today)
        output_dir (str): Directory to save the CSV files
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            # Try to get the earliest possible date
            earliest_date = get_max_stock_history(symbol)
            start_date = earliest_date if earliest_date else '1970-01-01'
            
        # Download data
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            print(f"No data available for {symbol}")
            return None
            
        # Save to CSV
        filename = f"{symbol}_stock_data.csv"
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath)
        print(f"Successfully downloaded data for {symbol} from {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
        
        return df
        
    except Exception as e:
        print(f"Error downloading data for {symbol}: {str(e)}")
        return None

def download_multiple_stocks(symbols, start_date=None, end_date=None, output_dir='data'):
    """
    Download data for multiple stock symbols.
    
    Args:
        symbols (list): List of stock symbols
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        output_dir (str): Directory to save the CSV files
    """
    for symbol in symbols:
        download_stock_data(symbol, start_date, end_date, output_dir)
        time.sleep(1)  # Add delay to avoid rate limiting

if __name__ == "__main__":
    # Read symbols from CSV file
    try:
        symbols_df = pd.read_csv('symbols_valid_meta.csv')
        stock_symbols = symbols_df['Symbol'].tolist()  # Assuming 'Symbol' is the column name
    except Exception as e:
        print(f"Error reading symbols file: {str(e)}")
        exit(1)
    
    # Create timestamped folder
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = f'stock_data_{timestamp}'
    
    # Set end date to today
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Starting download of {len(stock_symbols)} stocks to folder: {output_dir}")
    print("Getting maximum available historical data for each stock")
    
    # Download data for all symbols
    download_multiple_stocks(stock_symbols, None, end_date, output_dir)
    
    print(f"Download completed. Data saved in: {output_dir}") 