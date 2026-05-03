from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from sklearn.exceptions import NotFittedError

from src.inference.classifier import OilRegimeClassifier


def _feature_df(n: int = 10) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        rng.standard_normal((n, 5)),
        index=dates,
        columns=["f1", "f2", "f3", "f4", "f5"],
    )


def _regime_labels(n: int = 10) -> pd.Series:
    labels = (
        ["bull_supercycle"] * 3 + ["range_bound"] * 3 + ["bust"] * 2 + ["geopolitical_spike"] * 2
    )[:n]
    return pd.Series(labels, name="regime")


def _mock_clf(classes: list[str], proba: list[list[float]]) -> MagicMock:
    mock = MagicMock()
    mock.classes_ = np.array(classes)
    mock.predict_proba.return_value = np.array(proba)
    mock.predict.return_value = np.array([classes[int(np.argmax(row))] for row in proba])
    return mock


REGIME_CLASSES = ["bull_supercycle", "bust", "geopolitical_spike", "range_bound"]
REGIME_PROBA = [
    [0.6, 0.1, 0.2, 0.1],
    [0.1, 0.7, 0.1, 0.1],
    [0.2, 0.1, 0.5, 0.2],
]


def test_regime_predict_returns_series_with_correct_index():
    X = _feature_df(3)
    with patch("src.inference.classifier.TabPFNClassifier") as MockCLF:
        MockCLF.return_value = _mock_clf(REGIME_CLASSES, REGIME_PROBA)
        clf = OilRegimeClassifier()
        clf.fit(X, _regime_labels(3))
        result = clf.predict(X)

    assert isinstance(result, pd.Series)
    assert result.name == "regime"
    assert list(result.index) == list(X.index)


def test_regime_predict_returns_correct_labels():
    X = _feature_df(3)
    with patch("src.inference.classifier.TabPFNClassifier") as MockCLF:
        MockCLF.return_value = _mock_clf(REGIME_CLASSES, REGIME_PROBA)
        clf = OilRegimeClassifier()
        clf.fit(X, _regime_labels(3))
        result = clf.predict(X)

    assert result.iloc[0] == "bull_supercycle"
    assert result.iloc[1] == "bust"
    assert result.iloc[2] == "geopolitical_spike"


def test_regime_predict_proba_columns_match_classes():
    X = _feature_df(3)
    with patch("src.inference.classifier.TabPFNClassifier") as MockCLF:
        MockCLF.return_value = _mock_clf(REGIME_CLASSES, REGIME_PROBA)
        clf = OilRegimeClassifier()
        clf.fit(X, _regime_labels(3))
        result = clf.predict_proba(X)

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == REGIME_CLASSES
    assert list(result.index) == list(X.index)


def test_regime_predict_proba_values():
    X = _feature_df(3)
    with patch("src.inference.classifier.TabPFNClassifier") as MockCLF:
        MockCLF.return_value = _mock_clf(REGIME_CLASSES, REGIME_PROBA)
        clf = OilRegimeClassifier()
        clf.fit(X, _regime_labels(3))
        result = clf.predict_proba(X)

    assert result.iloc[0]["bull_supercycle"] == pytest.approx(0.6)
    assert result.iloc[1]["bust"] == pytest.approx(0.7)


def test_regime_raises_not_fitted_on_predict():
    with patch("src.inference.classifier.TabPFNClassifier"):
        clf = OilRegimeClassifier()
        with pytest.raises(NotFittedError):
            clf.predict(_feature_df(3))


def test_regime_raises_not_fitted_on_predict_proba():
    with patch("src.inference.classifier.TabPFNClassifier"):
        clf = OilRegimeClassifier()
        with pytest.raises(NotFittedError):
            clf.predict_proba(_feature_df(3))
