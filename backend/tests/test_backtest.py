from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from src.eval.backtest import _annualised_sharpe, walk_forward_backtest


def _make_data(n: int = 300) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    dates = pd.date_range("2020-01-01", periods=n, freq="B")
    np.random.seed(42)
    features = pd.DataFrame(np.random.randn(n, 5), index=dates, columns=[f"f{i}" for i in range(5)])
    wti = pd.Series(np.linspace(50, 80, n) + np.random.randn(n), index=dates, name="CL=F")
    spy = pd.Series(np.linspace(300, 400, n) + np.random.randn(n), index=dates, name="SPY")
    return features, wti, spy


def _mock_clf(default_label: str) -> MagicMock:
    clf = MagicMock()
    clf.fit.return_value = None
    clf.predict.side_effect = lambda X: pd.Series(default_label, index=X.index)
    return clf


def test_walk_forward_backtest_returns_required_keys():
    features, wti, spy = _make_data()
    with (
        patch("src.eval.backtest.OilRegimeClassifier", return_value=_mock_clf("range_bound")),
        patch("src.eval.backtest.DirectionClassifier", return_value=_mock_clf("up")),
    ):
        result = walk_forward_backtest(features, wti, spy, horizon=20, step=20, min_train=120)

    assert set(result.keys()) == {
        "regime_accuracy",
        "strategy_sharpe",
        "benchmark_sharpe",
        "n_windows",
        "date_range",
    }


def test_walk_forward_backtest_produces_multiple_windows():
    features, wti, spy = _make_data()
    with (
        patch("src.eval.backtest.OilRegimeClassifier", return_value=_mock_clf("range_bound")),
        patch("src.eval.backtest.DirectionClassifier", return_value=_mock_clf("up")),
    ):
        result = walk_forward_backtest(features, wti, spy, horizon=20, step=20, min_train=120)

    assert result["n_windows"] > 0


def test_walk_forward_backtest_sharpes_are_floats():
    features, wti, spy = _make_data()
    with (
        patch("src.eval.backtest.OilRegimeClassifier", return_value=_mock_clf("range_bound")),
        patch("src.eval.backtest.DirectionClassifier", return_value=_mock_clf("up")),
    ):
        result = walk_forward_backtest(features, wti, spy, horizon=20, step=20, min_train=120)

    assert isinstance(result["strategy_sharpe"], float)
    assert isinstance(result["benchmark_sharpe"], float)


def test_annualised_sharpe_zero_for_constant_returns():
    assert _annualised_sharpe([0.01, 0.01, 0.01]) == 0.0


def test_annualised_sharpe_positive_for_mostly_positive_returns():
    returns = [0.01] * 50 + [-0.001] * 5
    assert _annualised_sharpe(returns) > 0.0
