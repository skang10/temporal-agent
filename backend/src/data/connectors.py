import pandas as pd
import yfinance as yf


def fetch_price_series(ticker: str, start: str, end: str) -> pd.Series:
    """Fetch daily adjusted close price for a yfinance ticker symbol."""
    raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if raw.empty:
        raise ValueError(f"No data returned for ticker {ticker!r}")
    series = raw["Close"].squeeze()
    series.name = ticker
    series.index = pd.DatetimeIndex(series.index).rename("date")
    return series
