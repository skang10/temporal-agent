# Backlog

Known issues and future improvements that don't belong in a specific session plan.

---

## Inference / Label Quality

### ~~Label imbalance in regime classifier~~ ✅ Fixed (PR #52)
Hand-labeled known historical regime periods added to `scripts/demo.py` as `_KNOWN_REGIMES`. Heuristic thresholds also lowered from ±20% to ±15%. Label distribution improved from 92% `range_bound` to a balanced ~30/22/18/12% split.

### ~~Direction column shows "—" for last N rows in demo~~ ✅ Fixed (PR #52)
`_sample_prediction_dates` now picks only dates present in both regime and direction indices.

---

## Sessions Roadmap

| Session | Focus | Status |
|---|---|---|
| Session 1 | Data connectors + TimeSeriesFeaturizer | ✅ Done (PR #43) |
| Session 2 | TabPFN inference wrappers | ✅ Done (PR #45) |
| Session 3 | `src/db/` — SQLModel run/history models + Alembic migration | ✅ Done (PR #51) |
| Session 4 | `src/agent/` — tool definitions + ReAct loop (Anthropic SDK) | ✅ Done (PR #56) |
| Session 5 | Wire up API routes + deferred tools (drift, SHAP, backtest, GPR) | ✅ Done (PR #56) |
| Session 6 | Frontend core — split-pane layout, AgentStream, RegimeCard, DirectionCard, SummaryPanel | Pending |
| Session 7 | Frontend charts — DriftAlert, FeatureImportance (SHAP), BacktestChart | Pending |
