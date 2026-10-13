# FloodPath-Care: project rules for Claude Code

Source of truth: `blueprint.md` (v2.1). This run follows `docs/PLAN_2H.md` (2-hour cut). The blueprint's honesty and data rules still apply in full; only scope and process are cut.

## Stack and limits
- **Stack change (user decision, 2026-10-13):** the interface is a **Next.js** app in `web/` (TypeScript, Tailwind, App Router). Streamlit is being replaced and must not be extended. This overrides the blueprint's Python-only rule; blueprint Sections 4, 6 and 14 describe Streamlit and are to be read with this change (see `docs/PLAN_2H.md`).
- **Python** (blueprint says 3.11; this machine has 3.13) keeps all analysis: osmnx, networkx, geopandas, shapely, numpy, pandas, pytest. The Python code writes precomputed JSON/GeoJSON into `web/public/data/`; the Next.js app only reads those files. No live API server, no FastAPI.
- Charts are hand-built SVG components in the reference dashboard's style (no chart library). The map uses Leaflet.
- No database, Docker, or LLM calls.
- Do not download any file over 100 MB without asking.
- Keep raw third-party data out of git (`data/raw/` is ignored); commit download scripts instead. Never commit any UNOSAT file.
- One small Chennai zone; each step should run in under 30 seconds.
- Ask before installing packages or changing the stack.

## Honesty rules (never break)
- Every data feature carries source, date, licence, and an observed / composite / simulated flag.
- Never present simulated ambulance data as real 108 data. Ambulance starts are labelled `simulated`.
- A facility is `phone_verified` only with a `source` and a `verified_on` date. In this build all facilities are `unverified` or `source_listed`.
- Never create fake data and present it as real. Synthetic data carries `label=simulated`.
- Never drop "simulated", "indicative" or "not a prediction" from any language.
- Thresholds and buffers are assumptions; show them, never call them measured or official.
- Do not cite the Karnataka 108 audit's 72% figure as a Tamil Nadu benchmark.

## Language rules
- Every user-visible string comes from `i18n/{en,ta,hi}.json` through `t()`. Add any new key to all three files in the same commit and mark it draft.
- Escape every data string (facility names, ward names, file contents) before placing it in HTML.
- Tamil and Hindi strings are drafts until a reviewer signs off in `docs/TRANSLATION_REVIEW.md`; never describe them as professionally translated.

## Process rules
- Work one phase at a time. After each phase: run its tests, show the results, list deviations from the blueprint, and wait.
- Commit once per phase, only after its Verification passes and the user agrees, with the message `phase-N: <description>`. Never rewrite earlier commits.
- At every preview checkpoint (blueprint Section 14.12; in this run after minutes 45, 90 and 115): run the app, show a screenshot or live preview, say what is real and what is a placeholder, log it in `docs/PREVIEW_LOG.md`, and stop until the user approves. Never present a mockup as a real screenshot.
- If a source file is missing or differs from the blueprint, report it; do not substitute invented data.
- Write and run tests for each step before the next.
