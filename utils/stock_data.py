import yfinance as yf
import pandas as pd

def fetch_stock_prices(stock_symbol, start_date, end_date):
    stock = yf.download(stock_symbol, start=start_date, end=end_date)

    if stock.empty or "Close" not in stock.columns:
        raise ValueError("No stock data found or 'Close' column missing.")

    # Reset multi-index if any
    if isinstance(stock.columns, pd.MultiIndex):
        stock.columns = stock.columns.get_level_values(0)

    stock.reset_index(inplace=True)
    stock["Date"] = pd.to_datetime(stock["Date"]).dt.date
    return stock[["Date", "Close"]]
