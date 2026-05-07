# Session 5 — Deferred Tools Design

## Goal

Add the 4 deferred agent tools: `fetch_geopolitical_risk`, `detect_drift`, `evaluate_features`, and `backtest`. Each tool plugs into the existing `ToolRegistry` and `AgentContext` pattern established in Session 4.

## Architecture

New domain modules handle non-trivial logic; `src/agent/tools.py` holds thin wrappers that register each tool and glue results into `AgentContext`. Simple tools (drift, SHAP) stay inline in `tools.py`.

```
src/data/gpr.py          — GPR fetch + in-memory TTL cache
src/eval/backtest.py     — walk-forward engine
src/agent/tools.py       — 4 new @registry.tool wrappers
                           (detect_drift and evaluate_features inline)
```

`tabpfn-extensions` added to `pyproject.toml`. No new API routes or DB schema changes.

---

## Module: `src/data/gpr.py`

Fetches the daily Geopolitical Risk (GPR) index from Matteo Iacoviello's Fed page.

**Cache:** module-level `dict[str, tuple[datetime, pd.Series]]`. TTL defaults to 24h; overridable via `GPR_CACHE_TTL_HOURS` in `.env`. URL hardcoded as a constant; overridable via `GPR_DATA_URL` in `Settings`.

**Interface:**
```python
def fetch_gpr_series(start: str, end: str) -> pd.Series:
    """Fetch daily GPR index, return named Series trimmed to [start, end]."""
```

**Tool wrapper** (`fetch_geopolitical_risk`):
- Calls `fetch_gpr_series(context.date_range_start, context.date_range_end)`
- Stores result in `context.signals["GPR"]`
- Returns `{"fetched": {"GPR": len(series)}}`

**Settings additions:**
```python
gpr_data_url: str = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
gpr_cache_ttl_hours: int = 24
```

---

## Module: `src/eval/backtest.py`

Walk-forward evaluation using an expanding window.

**Interface:**
```python
def walk_forward_backtest(
    features: pd.DataFrame,
    wti: pd.Series,
    spy: pd.Series,
    horizon: int = 20,
    step: int = 20,
    min_train: int = 120,
) -> dict[str, Any]:
```

**Algorithm:**
1. Start at `min_train`. For each step window:
   - Fit `OilRegimeClassifier` on `features[:t]`, predict `features[t:t+horizon]`
   - Fit `DirectionClassifier` on `features[:t]`, predict `features[t:t+horizon]`
   - Compare regime predictions to `_make_regime_labels` ground truth
   - Simulate direction strategy: long WTI on "up", flat on "down"; compute log returns
2. Aggregate across all windows.

**Metrics:**
- `regime_accuracy` — fraction of correct regime predictions across all test slices
- `strategy_sharpe` — annualised Sharpe of direction-based WTI log-return strategy
- `benchmark_sharpe` — annualised Sharpe of SPY buy-and-hold over same period
- `n_windows` — number of walk-forward windows evaluated
- `date_range` — `[start, end]` of the evaluated period

**Output:**
```python
{
  "regime_accuracy": 0.71,
  "strategy_sharpe": 1.43,
  "benchmark_sharpe": 0.89,
  "n_windows": 12,
  "date_range": ["2023-01-01", "2023-06-30"]
}
```

**Tool wrapper** (`backtest`):
- Requires `context.features`, `context.signals["CL=F"]`, `context.signals["SPY"]`
- Calls `walk_forward_backtest(...)`, stores result in `context.backtest_result`
- Parameters: `horizon` (default 20), `step` (default 20)

**`AgentContext` addition:**
```python
backtest_result: dict[str, Any] | None = None
```

---

## Tool: `detect_drift` (inline in `tools.py`)

Splits `context.features` into historical (first 80%) and recent (last 20%). Runs two tests:

**KS test** — `scipy.stats.ks_2samp` per feature column. Flags features where p-value < 0.05.

**PSI** — Population Stability Index across all features. Buckets each feature into 10 bins on the historical distribution; computes PSI from recent bin proportions.
- PSI < 0.1: no drift
- 0.1 ≤ PSI < 0.2: moderate drift
- PSI ≥ 0.2: significant drift

**Output:**
```python
{
  "drift_detected": True,
  "psi_score": 0.24,
  "drifted_features": ["CL=F_ret_20d", "DX-Y.NYB_vol_60d"],
  "ks_results": {
    "CL=F_ret_20d": {"statistic": 0.31, "p_value": 0.003},
    "DX-Y.NYB_vol_60d": {"statistic": 0.28, "p_value": 0.012}
  }
}
```

`scipy` is already a transitive dependency via `scikit-learn` — no new package required.

---

## Tool: `evaluate_features` (inline in `tools.py`)

Uses `tabpfn-extensions` SHAP interface to compute feature importances from the fitted `OilRegimeClassifier`. Requires `run_tabpfn(task='regime')` to have been called first (so `context.regime_result` is populated).

Fits SHAP explainer on the test split of `context.features`. Returns top features by mean absolute SHAP value.

**Output:**
```python
{
  "top_features": [
    {"name": "CL=F_ret_20d", "importance": 0.42},
    {"name": "DX-Y.NYB_ret_20d", "importance": 0.31},
    {"name": "XLE_vol_60d", "importance": 0.18}
  ],
  "n_features_evaluated": 45
}
```

**`AgentContext` addition:**
```python
shap_result: dict[str, Any] | None = None
```

**New dependency:** `tabpfn-extensions>=0.0.14` added to `pyproject.toml`.

---

## Updated System Prompt

The agent system prompt in `loop.py` is extended to include the 4 new tools in the ordered workflow:

```
1. fetch_data
2. fetch_geopolitical_risk  ← new (optional, adds GPR signal)
3. engineer_features
4. detect_drift             ← new (warns if features have shifted)
5. run_tabpfn (regime)
6. run_tabpfn (direction)
7. evaluate_features        ← new (SHAP importances)
8. backtest                 ← new (walk-forward performance)
9. explain_prediction
```

---

## Testing

- `tests/test_gpr_connector.py` — mock HTTP fetch, TTL cache hit/miss, date trimming
- `tests/test_backtest.py` — synthetic features + WTI/SPY series, verify output keys and Sharpe sign
- `tests/test_deferred_tools.py` — `detect_drift` (inject known-drifted features), `evaluate_features` (mock tabpfn-extensions), `backtest` tool wrapper, `fetch_geopolitical_risk` tool wrapper
- All tests run without network access (HTTP mocked)

---

## Files Changed

| File | Action |
|---|---|
| `src/data/gpr.py` | Create |
| `src/eval/backtest.py` | Create |
| `src/agent/tools.py` | Add 4 tool wrappers + `AgentContext` fields |
| `src/agent/loop.py` | Extend system prompt |
| `src/config.py` | Add `gpr_data_url`, `gpr_cache_ttl_hours` |
| `.env.example` | Document new settings |
| `pyproject.toml` | Add `tabpfn-extensions` |
| `tests/test_gpr_connector.py` | Create |
| `tests/test_backtest.py` | Create |
| `tests/test_deferred_tools.py` | Create |
