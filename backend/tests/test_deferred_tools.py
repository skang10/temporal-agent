from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from src.agent.tools import AgentContext, fetch_data, run_tabpfn

# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture
def ctx():
    return AgentContext(date_range_start="2022-01-01", date_range_end="2022-12-31")


@pytest.fixture
def ctx_with_features(ctx):
    n = 200
    dates = pd.date_range("2022-03-01", periods=n, freq="B")
    ctx.signals["CL=F"] = pd.Series(np.linspace(70, 90, n), index=dates, name="CL=F")
    ctx.features = pd.DataFrame(
        np.random.randn(n, 5),
        index=dates,
        columns=["f1", "f2", "f3", "f4", "f5"],
    )
    return ctx


# ── AgentContext new fields ────────────────────────────────────────────────────


def test_agent_context_has_new_fields(ctx):
    assert ctx.backtest_result is None
    assert ctx.drift_result is None
    assert ctx.shap_result is None
    assert ctx._regime_clf is None
    assert ctx._regime_X_test is None
    assert ctx._regime_y_test is None
    assert ctx.data_manifest == {}


# ── run_tabpfn stores classifier and test split ────────────────────────────────


def test_run_tabpfn_regime_stores_clf_and_test_split(ctx_with_features):
    test_idx = ctx_with_features.features.index[-40:]

    with patch("src.agent.tools.OilRegimeClassifier") as MockCls:
        inst = MockCls.return_value
        inst.predict.return_value = pd.Series("range_bound", index=test_idx, name="regime")
        inst.predict_proba.return_value = pd.DataFrame({"range_bound": [0.8] * 40}, index=test_idx)
        inst.uncertainty.return_value = pd.Series([0.5] * 40, index=test_idx)

        run_tabpfn(task="regime", context=ctx_with_features)

    assert ctx_with_features._regime_clf is not None
    assert ctx_with_features._regime_X_test is not None
    assert ctx_with_features._regime_y_test is not None


# ── fetch_data writes to data_manifest ────────────────────────────────────────


def test_fetch_data_writes_to_data_manifest(ctx):
    fake_series = pd.Series(
        [70.0] * 5,
        index=pd.date_range("2022-01-01", periods=5, freq="D"),
        name="CL=F",
    )
    with patch("src.agent.tools.fetch_price_series", return_value=fake_series):
        fetch_data(tickers=["CL=F"], fred_series=[], context=ctx)

    assert "data_sources" in ctx.data_manifest
    assert "CL=F" in ctx.data_manifest["data_sources"]
    entry = ctx.data_manifest["data_sources"]["CL=F"]
    assert entry["rows"] == 5
    assert entry["provider"] == "yfinance"


# ── detect_drift ──────────────────────────────────────────────────────────────

from src.agent.tools import detect_drift  # noqa: E402


def test_detect_drift_flags_shifted_distribution(ctx):
    n = 100
    dates = pd.date_range("2022-01-01", periods=n, freq="B")
    np.random.seed(0)
    # f1: last 20% shifted by +10 (big shift), f2: random noise (no shift)
    data_f1 = np.concatenate([np.random.randn(80), np.random.randn(20) + 10])
    data_f2 = np.random.randn(n)
    ctx.features = pd.DataFrame({"f1": data_f1, "f2": data_f2}, index=dates)

    result = detect_drift(context=ctx)

    assert result["drift_detected"] is True
    assert "f1" in result["drifted_features"]
    assert ctx.drift_result is not None


def test_detect_drift_result_has_required_keys(ctx):
    n = 100
    dates = pd.date_range("2022-01-01", periods=n, freq="B")
    np.random.seed(0)
    ctx.features = pd.DataFrame({"f1": np.random.randn(n), "f2": np.random.randn(n)}, index=dates)

    result = detect_drift(context=ctx)

    assert set(result.keys()) == {"drift_detected", "psi_score", "drifted_features", "ks_results"}
    assert isinstance(result["psi_score"], float)
    assert isinstance(result["ks_results"], dict)


def test_detect_drift_raises_without_features(ctx):
    with pytest.raises(ValueError, match="engineer_features"):
        detect_drift(context=ctx)
