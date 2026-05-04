from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.agent.registry import registry
from src.config import settings
from src.data.connectors import fetch_fred_series, fetch_price_series
from src.featurizer import TimeSeriesFeaturizer
from src.inference import DirectionClassifier, OilRegimeClassifier

# Hand-labeled historical regime periods (same as demo.py — source of truth).
_KNOWN_REGIMES: list[tuple[str, str, str]] = [
    ("2014-07-01", "2016-12-31", "bust"),
    ("2020-02-01", "2020-10-31", "bust"),
    ("2021-01-01", "2022-06-30", "bull_supercycle"),
    ("2022-02-01", "2022-04-30", "geopolitical_spike"),
    ("2023-10-01", "2023-12-31", "geopolitical_spike"),
]


@dataclass
class AgentContext:
    date_range_start: str
    date_range_end: str
    signals: dict[str, pd.Series] = field(default_factory=dict)
    features: pd.DataFrame | None = None
    regime_result: dict[str, Any] | None = None
    direction_result: dict[str, Any] | None = None


def _make_regime_labels(wti: pd.Series, index: pd.DatetimeIndex) -> pd.Series:
    wti_daily = wti.reindex(index, method="ffill")
    ret5 = wti_daily.pct_change(5)
    ret60 = wti_daily.pct_change(60)
    labels = pd.Series("range_bound", index=index, name="regime")
    labels[ret60 > 0.15] = "bull_supercycle"
    labels[ret60 < -0.15] = "bust"
    labels[ret5 > 0.08] = "geopolitical_spike"
    for start, end, regime in _KNOWN_REGIMES:
        mask = (index >= start) & (index <= end)
        labels[mask] = regime
    return labels


def _make_direction_labels(wti: pd.Series, index: pd.DatetimeIndex, horizon: int = 20) -> pd.Series:
    wti_daily = wti.reindex(index, method="ffill")
    forward_ret = wti_daily.shift(-horizon) / wti_daily - 1
    forward_ret = forward_ret.dropna()
    labels = forward_ret.map(lambda r: "up" if r > 0 else "down")
    labels.name = "direction"
    return labels


@registry.tool(
    parameters={
        "type": "object",
        "properties": {
            "tickers": {
                "type": "array",
                "items": {"type": "string"},
                "description": "yfinance ticker symbols, e.g. ['CL=F', 'DX-Y.NYB', 'XLE', 'SPY']",
            },
            "fred_series": {
                "type": "array",
                "items": {"type": "string"},
                "description": "FRED series IDs, e.g. ['INDPRO']. Skipped if FRED_API_KEY not set.",
            },
        },
        "required": ["tickers", "fred_series"],
    }
)
def fetch_data(tickers: list[str], fred_series: list[str], context: AgentContext) -> dict[str, Any]:
    """Fetch price series from yfinance and macro series from FRED."""
    fetched: dict[str, int] = {}
    skipped: list[str] = []

    for ticker in tickers:
        series = fetch_price_series(ticker, context.date_range_start, context.date_range_end)
        context.signals[ticker] = series
        fetched[ticker] = len(series)

    for series_id in fred_series:
        if not settings.fred_api_key:
            skipped.append(series_id)
            continue
        series = fetch_fred_series(
            series_id,
            context.date_range_start,
            context.date_range_end,
            api_key=settings.fred_api_key,
        )
        context.signals[series_id] = series
        fetched[series_id] = len(series)

    return {"fetched": fetched, "skipped": skipped}


@registry.tool(
    parameters={
        "type": "object",
        "properties": {
            "windows": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Rolling window sizes in days, e.g. [5, 20, 60]",
            },
            "lags": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Lag periods in days, e.g. [1, 5, 20]",
            },
        },
        "required": ["windows", "lags"],
    }
)
def engineer_features(windows: list[int], lags: list[int], context: AgentContext) -> dict[str, Any]:
    """Featurize the fetched signals into a tabular feature matrix."""
    if not context.signals:
        raise ValueError("No signals in context. Call fetch_data first.")
    featurizer = TimeSeriesFeaturizer(windows=windows, lags=lags)
    features = featurizer.transform(context.signals)
    context.features = features
    start = str(features.index[0].date())
    end = str(features.index[-1].date())
    return {"shape": list(features.shape), "date_range": [start, end]}


@registry.tool(
    parameters={
        "type": "object",
        "properties": {
            "task": {
                "type": "string",
                "enum": ["regime", "direction"],
                "description": "'regime' for OilRegimeClassifier, 'direction' for DirectionClassifier",  # noqa: E501
            },
            "horizon": {
                "type": "integer",
                "description": "Forward-return horizon in trading days for direction labels (ignored for regime)",  # noqa: E501
                "default": 20,
            },
        },
        "required": ["task"],
    }
)
def run_tabpfn(task: str, horizon: int = 20, context: AgentContext | None = None) -> dict[str, Any]:
    """Run TabPFN classification for regime or price direction."""
    if context is None or context.features is None:
        raise ValueError("No features in context. Call engineer_features first.")
    if "CL=F" not in context.signals:
        raise ValueError(
            "WTI price series ('CL=F') not found in context.signals. "
            "Call fetch_data with tickers=['CL=F', ...]."
        )

    features = context.features.dropna()
    wti = context.signals["CL=F"]

    if task == "regime":
        labels = _make_regime_labels(wti, features.index)
        split = int(len(features) * 0.8)
        X_train, X_test = features.iloc[:split], features.iloc[split:]
        y_train = labels.iloc[:split]
        regime_clf = OilRegimeClassifier(n_estimators=8)
        regime_clf.fit(X_train, y_train)
        pred = regime_clf.predict(X_test)
        proba = regime_clf.predict_proba(X_test)
        uncertainty = regime_clf.uncertainty(X_test)
        mean_conf = float(proba.max(axis=1).mean())
        mean_entropy = float(uncertainty.mean())
        current = str(pred.iloc[-1])
        distribution = pred.value_counts().to_dict()
        context.regime_result = {
            "regime": current,
            "confidence": mean_conf,
            "entropy": mean_entropy,
            "distribution": {str(k): int(v) for k, v in distribution.items()},
        }
        return {
            "task": "regime",
            "current_prediction": current,
            "mean_confidence": mean_conf,
            "mean_entropy": mean_entropy,
            "test_size": len(X_test),
            "label_distribution": {str(k): int(v) for k, v in distribution.items()},
        }

    # direction
    direction_labels = _make_direction_labels(wti, features.index, horizon=horizon)
    common_idx = features.index.intersection(direction_labels.index)
    features_dir = features.loc[common_idx]
    labels_dir = direction_labels.loc[common_idx]
    split = int(len(features_dir) * 0.8)
    X_train, X_test = features_dir.iloc[:split], features_dir.iloc[split:]
    y_train = labels_dir.iloc[:split]
    dir_clf = DirectionClassifier(n_estimators=8)
    dir_clf.fit(X_train, y_train)
    pred = dir_clf.predict(X_test)
    proba = dir_clf.predict_proba(X_test)
    uncertainty = dir_clf.uncertainty(X_test)
    mean_conf = float(proba.max(axis=1).mean())
    mean_entropy = float(uncertainty.mean())
    current = str(pred.iloc[-1])
    distribution = pred.value_counts().to_dict()
    context.direction_result = {
        "direction": current,
        "confidence": mean_conf,
        "entropy": mean_entropy,
        "distribution": {str(k): int(v) for k, v in distribution.items()},
    }
    return {
        "task": "direction",
        "current_prediction": current,
        "mean_confidence": mean_conf,
        "mean_entropy": mean_entropy,
        "test_size": len(X_test),
        "label_distribution": {str(k): int(v) for k, v in distribution.items()},
    }


@registry.tool(
    parameters={
        "type": "object",
        "properties": {
            "regime": {"type": "string", "description": "Predicted regime label"},
            "direction": {
                "type": "string",
                "description": "Predicted price direction ('up' or 'down')",
            },
            "confidence": {"type": "number", "description": "Mean confidence score 0-1"},
            "key_features": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Feature names most relevant to this prediction",
            },
        },
        "required": ["regime", "direction", "confidence", "key_features"],
    }
)
def explain_prediction(
    regime: str,
    direction: str,
    confidence: float,
    key_features: list[str],
    context: AgentContext | None = None,
) -> dict[str, Any]:
    """Assemble prediction inputs for the agent's final narrative explanation."""
    return {
        "regime": regime,
        "direction": direction,
        "confidence": confidence,
        "key_features": key_features,
    }
