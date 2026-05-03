import pandas as pd
import yfinance as yf
from fredapi import Fred


def fetch_price_series(ticker: str, start: str, end: str) -> pd.Series:
    """Fetch daily adjusted close price for a yfinance ticker symbol."""
    raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if raw.empty:
        raise ValueError(f"No data returned for ticker {ticker!r}")
    series = raw["Close"].squeeze()
    series.name = ticker
    series.index = pd.DatetimeIndex(series.index).rename("date")
    return series


def fetch_fred_series(series_id: str, start: str, end: str, api_key: str) -> pd.Series:
    """Fetch a FRED time series by ID."""
    fred = Fred(api_key=api_key)
    series = fred.get_series(series_id, observation_start=start, observation_end=end)
    series.name = series_id
    series.index.name = "date"
    return series
