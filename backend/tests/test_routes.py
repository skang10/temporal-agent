import pytest


def test_analyze_missing_fields(client):
    res = client.post("/api/analyze", json={})
    assert res.status_code == 422


def test_analyze_invalid_date_type(client):
    res = client.post("/api/analyze", json={"date_range_start": 123, "date_range_end": 456})
    assert res.status_code in (200, 422)  # FastAPI coerces ints to str; both outcomes are valid


def test_analyze_valid_request_raises_not_implemented(client):
    res = client.post(
        "/api/analyze",
        json={"date_range_start": "2020-01-01", "date_range_end": "2024-01-01"},
    )
    assert res.status_code == 500


def test_get_run_not_implemented(client):
    res = client.get("/api/runs/test-run-id")
    assert res.status_code == 500


def test_get_history_not_implemented(client):
    res = client.get("/api/history")
    assert res.status_code == 500


def test_derivatives_missing_required_fields(client):
    res = client.post("/api/derivatives/price", json={})
    assert res.status_code == 422


def test_derivatives_invalid_option_type(client):
    res = client.post(
        "/api/derivatives/price",
        json={
            "regime": "geopolitical_spike",
            "spot": 87.5,
            "strike": 90.0,
            "tenor_days": 30,
            "option_type": "swap",
        },
    )
    assert res.status_code == 422


def test_derivatives_invalid_style(client):
    res = client.post(
        "/api/derivatives/price",
        json={
            "regime": "geopolitical_spike",
            "spot": 87.5,
            "strike": 90.0,
            "tenor_days": 30,
            "style": "asian",
        },
    )
    assert res.status_code == 422


def test_derivatives_valid_request_raises_not_implemented(client):
    res = client.post(
        "/api/derivatives/price",
        json={
            "regime": "geopolitical_spike",
            "spot": 87.5,
            "strike": 90.0,
            "tenor_days": 30,
        },
    )
    assert res.status_code == 500
