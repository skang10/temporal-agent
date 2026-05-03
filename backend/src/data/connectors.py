from typing import Any

import httpx
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


def _eia_get(start: str, end: str, api_key: str) -> list[dict[str, Any]]:
    """Isolated HTTP call — kept separate so tests can mock it cleanly."""
    resp = httpx.get(
        "https://api.eia.gov/v2/petroleum/stoc/wstk/data/",
        params={
            "api_key": api_key,
            "frequency": "weekly",
            "data[0]": "value",
            "facets[product][]": "EPC0",
            "facets[duoarea][]": "NUS",
            "facets[process][]": "SAE",
            "start": start,
            "end": end,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "length": 5000,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["response"]["data"]  # type: ignore[no-any-return]


def fetch_eia_inventory(start: str, end: str, api_key: str) -> pd.Series:
    """Fetch EIA weekly US crude oil inventory change (thousand barrels).

    Returns week-over-week difference: positive = build, negative = draw.
    The first observation is dropped (diff produces NaN there).
    """
    rows = _eia_get(start, end, api_key)
    records = {row["period"]: float(row["value"]) for row in rows}
    level = pd.Series(records, name="eia_inventory_level")
    level.index = pd.DatetimeIndex(level.index).rename("date")
    level = level.sort_index()
    change = level.diff().dropna()
    change.name = "eia_inventory_change"
    return change
