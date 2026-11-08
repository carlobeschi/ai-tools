# ai-tools
Visuals and trends around AI tools adoption in software development

## Treemap view

`index.html` shows one treemap per category: each tile is a tool, its area is the tool's share within the category.
The default size is the number of Hacker News developers who name the tool in "what's your setup" threads;
a toggle switches to Alexis's composite score. Hover a tile for the details.

Open it with any static server (it loads the JSON with `fetch`), e.g. `python3 -m http.server`, or via GitHub Pages.

## Stack self-assessment

`assess.html` asks which tools you use in each category (top 10 chips, Alexis's other scored tools, or free text), then
shows the same treemaps with a person marker on your picks and a 0-100 mainstream-vs-niche bar.
Each pick scores `sqrt(devs naming it / devs naming the category leader)`; tools outside the top 10 score 0; a category
is the mean of its picks and the headline is the mean of answered categories. Answers stay in the browser
(localStorage) and the result is shareable through the URL hash, e.g. `assess.html#terminal=Claude%20Code&editors=Zed`.

### Tests

`node tests/assess.test.js` plays seven developer scenarios in headless Chromium (category leaders everywhere, strong
runners-up, a mixed stack, only invented tool names, free text matching a known tool, niche-but-scored tools, and
someone who uses nothing). It checks score, label, markers and the shared link against values worked out by hand from
the 2026-11-07 snapshot, so update the expected numbers when the scoring or the latest snapshot changes. Needs
Playwright; set `D3_PATH` to a local `d3.min.js` if the CDN is unreachable.

## Trends

`trends.html` compares snapshots: per category, each tool's sparkline across snapshots, its latest value and the change
since the previous one, for HN comments, HN devs, stars, downloads and score, plus the biggest movers. Signals that our
recurring run measures differently from the source are compared only between our own snapshots.

## Data

- `data/snapshots/<date>.json`: one snapshot per research run (schema_version 1). Each has the source, corpus size,
  field definitions, the HN setup poll, and 12 categories with their top 10 tools and raw metrics.
- `data/snapshots/index.json`: list of snapshots and which one is the latest. New runs add a file here, which is what
  the trend views will build on.
- First snapshot (2026-11-07) comes from [Alexis Santos's AI Dev Tools Field Guide](https://alexissantos.dev/ai-dev-tools/).
  Categories 1-8 and the first four tools of "Model access & routing" match his `tools.json`; the rest was transcribed
  from the rendered page and has rounded numbers (flagged as `verbatim: false`).
- `scripts/seed_snapshot_2026-11-07.py` regenerates that first snapshot.
- Later snapshots are collected every two weeks by a GitHub Action (`.github/workflows/snapshot.yml` runs
  `scripts/collect_snapshot.py` over `scripts/tracked_tools.json`) and arrive as a pull request. They add `kind:
  "collected"`, `method`, `hn_devs_12m` and `others` (tracked tools outside the top 10); raw counts and samples go
  to `data/raw/<date>.json`. See [docs/methodology.md](docs/methodology.md).
- Any page takes `?snapshot=YYYY-MM-DD` to show an older snapshot.
