# Session 6 — Frontend Core Design

## Goal

Build the core frontend for TemporalAgent: a split-pane dashboard that streams live agent reasoning on the left and renders the analysis results on the right. Scope is the four must-have panels (AgentStream, RegimeCard, DirectionCard, SummaryPanel) plus the top bar and theme toggle. Chart panels (DriftAlert, FeatureImportance, BacktestChart) are deferred to Session 7.

---

## Architecture

### File structure

```
frontend/
├── app/
│   ├── layout.tsx          — wrap in ThemeProvider; add dark: body class
│   └── page.tsx            — top bar + split-pane shell; reads from Zustand store
├── components/
│   ├── TopBar.tsx          — date inputs, Quick/Full toggle, Run button, Cancel, theme icon
│   ├── AgentStream.tsx     — left pane; consumes useRunStream, renders messages
│   ├── ResultsPanel.tsx    — right pane; reads result from store, renders sub-cards
│   ├── RegimeCard.tsx      — regime label + confidence bar
│   ├── DirectionCard.tsx   — up/down arrow + confidence bar
│   └── SummaryPanel.tsx    — agent natural-language summary (prose)
├── lib/
│   ├── store.ts            — Zustand: { runId, status, result, setRun, clearRun }
│   ├── api.ts              — existing (unchanged)
│   └── websocket.ts        — existing (unchanged)
└── package.json            — add: next-themes
```

No new pages or API routes. `page.tsx` remains the only route.

---

## Theme

**Library:** `next-themes` — handles SSR flicker, `localStorage` persistence, and the `class` attribute toggle automatically.

**Setup:**
- `ThemeProvider` wraps the root layout with `attribute="class"`
- Tailwind config: `darkMode: 'class'`
- `TopBar` includes a sun/moon icon button calling `setTheme('light' | 'dark')`

**Dark mode** (default): near-black background (`bg-[#0f0f1a]`), `violet-600` accent, `slate-800` card surfaces.

**Light mode**: white/slate background, `blue-600` accent, white card surfaces with `slate-200` borders.

All components use Tailwind `dark:` variants inline — no separate theme files or CSS variables.

---

## Components

### TopBar

Sticky header bar. Contains:
- App name / wordmark (left)
- Date range: two `<input type="date">` fields for `date_range_start` and `date_range_end`
- Mode toggle: Quick / Full pill selector (maps to `analysis_mode` in `AnalyzeRequest`)
- **Run button**: calls `api.analyze()`, writes `{ runId, status: 'running' }` to store; disabled while `status === 'running'`
- **Cancel button**: appears only while running; calls `DELETE /api/runs/{runId}`
- Theme toggle icon (sun/moon, far right)

### AgentStream

Left pane of the split layout. Subscribes to `useRunStream(runId)`.

Renders each `StreamMessage` with a distinct visual treatment:

| Message type | Display |
|---|---|
| `thought` | Grey prose line with 🧠 prefix |
| `tool_call` | Purple monospace badge + tool name + collapsible JSON input |
| `tool_result` | Dimmed monospace output, indented |
| `prediction` | Green highlighted line: regime + confidence |
| `done` | Bold green "✅ Complete" line |

Shows a pulsing "Connecting…" indicator while `connected === false`. Auto-scrolls to the latest message. Empty state: "Run an analysis to see the agent's reasoning."

### ResultsPanel

Right pane. Reads `result` from Zustand store.

- While `status === 'running'` and `result` is null: renders skeleton placeholder cards (animated pulse)
- Once `result` is populated (fetched via `api.getRun()` on `done` WS message): renders RegimeCard, DirectionCard, SummaryPanel stacked vertically
- On fetch error: inline error banner with retry button

### RegimeCard

Displays `result.regime`:
- Regime label in large bold text (e.g. "Range Bound")
- Confidence percentage badge (e.g. "95.0%")
- Confidence bar (filled proportionally, violet gradient in dark / blue in light)
- Entropy value in small muted text below the bar
- Regime label colour-coded: `range_bound` → violet, `bull_supercycle` → green, `bust` → red, `geopolitical_spike` → amber

### DirectionCard

Displays `result.direction`:
- Large directional arrow: ↑ green for `up`, ↓ red for `down`
- Direction label ("Up" / "Down") + confidence percentage badge
- Confidence bar
- Prediction date in muted text ("as of 2023-06-30")

### SummaryPanel

Displays `result.summary` as styled prose. No markdown parsing — the summary is plain text. Renders inside a card with a subtle left border accent.

---

## Data flow

```
User clicks Run
  → TopBar calls api.analyze({ date_range_start, date_range_end, analysis_mode })
  → receives { run_id }
  → writes { runId: run_id, status: 'running', result: null } to Zustand store

useRunStream(runId) connects to WS /ws/runs/{runId}/stream
  → AgentStream receives and renders each StreamMessage live

On { type: "done" } message:
  → api.getRun(runId) fetched once
  → full result written to store: { status: 'completed', result: { regime, direction, ... } }
  → ResultsPanel re-renders with populated cards

User clicks Cancel:
  → DELETE /api/runs/{runId}
  → store cleared: { runId: null, status: 'idle', result: null }
  → WS connection closes (useRunStream cleans up on runId → null)
```

### Zustand store shape

```ts
type RunStore = {
  runId: string | null
  status: 'idle' | 'running' | 'completed' | 'failed'
  result: RunResult | null
  setRun: (runId: string) => void
  setResult: (result: RunResult) => void
  clearRun: () => void
}
```

`RunResult` reuses the existing type from `lib/api.ts`.

---

## Error handling

| Scenario | Behaviour |
|---|---|
| `api.analyze()` throws | Toast/inline error in TopBar; status stays `idle` |
| WebSocket drops mid-stream | AgentStream shows "Connection lost" banner; does not retry automatically |
| `api.getRun()` fails after `done` | ResultsPanel shows error banner with manual retry button |
| Run cancelled | Store cleared, both panes reset to idle state |

---

## Testing

Two new test files following the existing `lib/__tests__/` pattern:

**`components/__tests__/AgentStream.test.tsx`**
- Renders with an empty message list → shows empty state text
- Renders each message type (`thought`, `tool_call`, `tool_result`, `prediction`, `done`) → correct label/icon present
- Connected vs disconnected state → indicator text changes

**`components/__tests__/ResultsPanel.test.tsx`**
- `status === 'running'`, `result === null` → skeleton cards render
- `result` populated → RegimeCard shows correct regime label and confidence
- DirectionCard shows ↑/↓ arrow with correct colour class
- SummaryPanel renders summary text

Tests use Vitest + `@testing-library/react` (already configured). No mocking of WebSocket — `AgentStream` is tested by passing `messages` as a prop to a presentational sub-component.

---

## Out of scope (Session 7)

- `DriftAlert` — PSI score + drifted features warning
- `FeatureImportance` — SHAP bar chart (Recharts)
- `BacktestChart` — walk-forward performance line chart
- History panel (`GET /api/history`)
- Authentication (planned for Mid tier)
