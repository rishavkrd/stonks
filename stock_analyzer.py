import os
import pandas as pd

def calculate_basic_metrics(symbol, data_dir='data'):
    """
    Calculate basic metrics from downloaded stock data.
    
    Args:
        symbol (str): Stock symbol
        data_dir (str): Directory containing the CSV files
    """
    filepath = os.path.join(data_dir, f"{symbol}_stock_data.csv")
    df = pd.read_csv(filepath)
    
    metrics = {
        'average_price': df['Close'].mean(),
        'highest_price': df['High'].max(),
        'lowest_price': df['Low'].min(),
        'price_volatility': df['Close'].std(),
        'total_volume': df['Volume'].sum()
    }
    
    return metrics 