# Backlog

Known issues and future improvements that don't belong in a specific session plan.

---

## Inference / Label Quality

### Label imbalance in regime classifier
**Observed:** Demo output shows 92% of training rows labelled `range_bound`, causing the model to collapse — test set predictions are 98% `range_bound` with 99%+ confidence, and minority classes (`bust`, `bull_supercycle`) are never predicted.

**Root cause:** Heuristic thresholds in `scripts/demo.py` are too strict (60-day return >20% for bull/bust), so almost all dates fall through to the `range_bound` default.

**Options to fix:**
- Lower heuristic thresholds (e.g. 60-day return >10% for bull, <-10% for bust)
- Add class weighting / oversampling (e.g. `sklearn` `class_weight="balanced"`) — check if `tabpfn-client` supports it
- Hand-label a reference set of known regime periods (e.g. 2014-2016 bust, 2021-2022 spike) and use that as ground truth

### Direction column shows "—" for last N rows in demo
**Observed:** `sample_dates = X_test.index[-10:]` falls in the last 20 trading days of the dataset, which have no forward direction labels (need 20 days of future price data). All 10 rows show "—".

**Fix:** Change demo to use `X_test.index[10:20]` (or any slice that falls within the labeled window) so direction predictions are always visible.

---

## Sessions Roadmap

| Session | Focus | Status |
|---|---|---|
| Session 1 | Data connectors + TimeSeriesFeaturizer | ✅ Done (PR #43) |
| Session 2 | TabPFN inference wrappers | ✅ Done (PR #45) |
| Session 3 | `src/db/` — SQLModel run/history models + Alembic migration | Pending |
| Session 4 | `src/agent/` — tool definitions + ReAct loop (Anthropic SDK) | Pending |
| Session 5 | Wire up API routes (replace 501s) + WebSocket Redis pub/sub | Pending |
| Session 6 | Frontend — RegimeDashboard + AgentStream components | Pending |
