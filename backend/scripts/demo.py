"""
End-to-end demo: fetch market data → featurize → print feature matrix summary.

Usage:
    cd backend && uv run python scripts/demo.py
    cd backend && uv run python scripts/demo.py --start 2021-01-01 --end 2023-12-31

Requires in .env:
    FRED_API_KEY  (for macro data)
    EIA_API_KEY   (optional, for inventory data)
"""

import argparse

import pandas as pd

from src.config import settings
from src.data.connectors import fetch_eia_inventory, fetch_fred_series, fetch_price_series
from src.featurizer import TimeSeriesFeaturizer


def main() -> None:
    parser = argparse.ArgumentParser(description="TemporalAgent pipeline demo")
    parser.add_argument("--start", default="2022-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="2024-12-31", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    start, end = args.start, args.end
    print(f"\nTemporalAgent demo  |  {start} → {end}\n{'─' * 45}")

    # ── 1. Fetch price data ──────────────────────────────
    signals: dict[str, pd.Series] = {}

    for name, ticker in [("wti", "CL=F"), ("dxy", "DX-Y.NYB"), ("xle", "XLE"), ("spy", "SPY")]:
        print(f"Fetching {name} ({ticker})...")
        signals[name] = fetch_price_series(ticker, start, end)
        print(f"  {len(signals[name])} rows")

    # ── 2. Fetch macro data (requires FRED_API_KEY) ──────
    if settings.fred_api_key:
        print("Fetching Industrial Production Index (FRED: INDPRO)...")
        signals["indpro"] = fetch_fred_series("INDPRO", start, end, api_key=settings.fred_api_key)
        print(f"  {len(signals['indpro'])} rows")
    else:
        print("Skipping FRED data (FRED_API_KEY not set)")

    # ── 3. Fetch EIA inventory (requires EIA_API_KEY) ────
    if settings.eia_api_key:
        print("Fetching EIA crude inventory...")
        signals["eia_inventory"] = fetch_eia_inventory(start, end, api_key=settings.eia_api_key)
        print(f"  {len(signals['eia_inventory'])} rows")
    else:
        print("Skipping EIA data (EIA_API_KEY not set)")

    # ── 4. Featurize ─────────────────────────────────────
    print("\nFeaturizing...")
    featurizer = TimeSeriesFeaturizer(windows=[5, 20, 60], lags=[1, 5, 20])
    features = featurizer.transform(signals)

    print(f"\n{'─' * 45}")
    print(f"Feature matrix:  {features.shape[0]} rows × {features.shape[1]} columns")
    print(f"Date range:      {features.index[0].date()} → {features.index[-1].date()}")
    print(f"Any NaN:         {features.isna().any().any()}")
    print("\nSample columns:")
    for col in list(features.columns)[:8]:
        print(f"  {col}")
    print(f"  ... ({features.shape[1] - 8} more)")
    print(f"\n{'─' * 45}")
    print("Pipeline OK — ready for TabPFN inference.\n")


if __name__ == "__main__":
    main()
