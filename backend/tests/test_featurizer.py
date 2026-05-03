import numpy as np
import pandas as pd

from src.featurizer.featurizer import TimeSeriesFeaturizer


def _daily_series(name: str, n: int = 100, start: str = "2020-01-01") -> pd.Series:
    rng = np.random.default_rng(42)
    dates = pd.date_range(start, periods=n, freq="D")
    return pd.Series(rng.standard_normal(n).cumsum() + 100, index=dates, name=name)


def _weekly_series(name: str, n: int = 50, start: str = "2020-01-01") -> pd.Series:
    rng = np.random.default_rng(0)
    dates = pd.date_range(start, periods=n, freq="W")
    return pd.Series(rng.standard_normal(n).cumsum() + 50, index=dates, name=name)


def test_align_two_daily_series_preserves_length():
    f = TimeSeriesFeaturizer()
    s1 = _daily_series("a")
    s2 = _daily_series("b")
    aligned = f.align({"a": s1, "b": s2})
    assert isinstance(aligned, pd.DataFrame)
    assert list(aligned.columns) == ["a", "b"]
    assert len(aligned) == 100


def test_align_weekly_series_forward_fills_to_daily():
    f = TimeSeriesFeaturizer()
    weekly = _weekly_series("inventory")
    aligned = f.align({"inventory": weekly})
    assert (aligned.index[1] - aligned.index[0]).days == 1
    assert aligned["inventory"].notna().all()


def test_align_no_future_leakage():
    f = TimeSeriesFeaturizer()
    dates_daily = pd.date_range("2020-01-01", periods=10, freq="D")
    daily = pd.Series(range(10), index=dates_daily, name="price")
    dates_weekly = pd.date_range("2020-01-04", periods=5, freq="W")
    weekly = pd.Series(range(5), index=dates_weekly, name="inventory")
    aligned = f.align({"price": daily, "inventory": weekly})
    assert aligned.loc[aligned.index < dates_weekly[0], "inventory"].isna().all()


def test_align_empty_dict_returns_empty_dataframe():
    f = TimeSeriesFeaturizer()
    result = f.align({})
    assert isinstance(result, pd.DataFrame)
    assert result.empty
