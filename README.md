# Stock Market Scanner

A Python-based tool for historical stock market analysis and screening. This tool allows you to download stock data and perform backtesting with custom filters across multiple time periods.

## Features

- Download historical stock data from Yahoo Finance
- Screen stocks based on multiple criteria:
  - Price changes
  - Volume analysis
  - Custom price filters
- Generate TradingView-compatible watchlists
- Create historical analysis with visualization
- Backtest screening strategies across different time periods

## Installation

1. Ensure you have Python 3.11 or later installed
2. Install pipenv if you haven't already:
```bash
brew install pipenv  # For macOS
# or
pip install pipenv   # For other systems
```

3. Clone this repository and navigate to the project directory:
```bash
git clone <repository-url>
cd stonks
```

4. Install dependencies using pipenv:
```bash
pipenv install
```

## Usage

### 1. Downloading Stock Data

Use the stock downloader to fetch historical data:

```python
from stock_downloader import download_multiple_stocks

# Define your stock symbols
symbols = ["AAPL", "MSFT", "GOOGL"]

# Download data
download_multiple_stocks(
    symbols,
    start_date="2000-01-01",  # Optional
    end_date="2024-03-15",    # Optional
    output_dir="stock_data"    # Optional
)
```

### 2. Running Stock Screener

The stock screener can be used individually or as part of the global scanner:

```python
from stock_screener import StockScreener

# Initialize screener
screener = StockScreener("stock_data_folder")

# Define filters
filters = {
    'volume_price': {'operator': '>', 'value': 50000000},
    'lowest_price': {'operator': '>', 'value': 10},
    'highest_price': {'operator': '<', 'value': 100}
}

# Screen stocks
passing_symbols, count, results = screener.screen_stocks(
    symbols=["AAPL", "MSFT", "GOOGL"],
    backtest_date="2024-03-15",
    lookback_days=20,
    filters=filters,
    min_price_change_pct=30.0
)
```

### 3. Running Global Scanner

The global scanner performs historical analysis across multiple time periods:

```python
from global_scanner import GlobalScanner

# Initialize scanner
scanner = GlobalScanner("stock_data_folder")

# Define filters
filters = {
    'volume_price': {'operator': '>', 'value': 50000000}
}

# Run global scan
results = scanner.run_global_scan(
    lookback_days=60,
    filters=filters,
    min_price_change_pct=30.0
)
```

## Filter Configuration

You can configure various filters:

```python
filters = {
    'lowest_price': {'operator': '>', 'value': 10},    # Price > $10
    'highest_price': {'operator': '<', 'value': 100},  # Price < $100
    'volume_price': {'operator': '>', 'value': 1000000}  # Volume*Price > 1M
}
```

Supported operators:
- `>`: Greater than
- `<`: Less than
- `>=`: Greater than or equal
- `<=`: Less than or equal
- `==`: Equal to

## Output Files

The screener generates several types of output files:

1. Results Files (`results_MM-DD-YYYY.txt`):
   - Detailed screening results
   - Applied filters
   - Stock metrics and statistics

2. TradingView Files (`tv_MM-DD-YYYY_HHMMSS.txt`):
   - Comma-separated list of symbols
   - Ready to import into TradingView
   - Only created when stocks pass filters
   - Limited to top 50 stocks by performance

3. Global Scan Summary:
   - Results summary plot (`results_summary.png`)
   - CSV data file (`results_summary.csv`)

All files are organized in: 