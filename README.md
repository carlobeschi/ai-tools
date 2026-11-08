# ai-tools
Visuals and trends around AI tools adoption in software development

## Treemap view

`index.html` shows one treemap per category: each tile is a tool, its area is the tool's share within the category.
The default size is the number of Hacker News developers who name the tool in "what's your setup" threads;
a toggle switches to Alexis's composite score. Hover a tile for the details.

Open it with any static server (it loads the JSON with `fetch`), e.g. `python3 -m http.server`, or via GitHub Pages.

## Data

- `data/snapshots/<date>.json`: one snapshot per research run (schema_version 1). Each has the source, corpus size,
  field definitions, the HN setup poll, and 12 categories with their top 10 tools and raw metrics.
- `data/snapshots/index.json`: list of snapshots and which one is the latest. New runs add a file here, which is what
  the trend views will build on.
- First snapshot (2026-11-07) comes from [Alexis Santos's AI Dev Tools Field Guide](https://alexissantos.dev/ai-dev-tools/).
  Categories 1-8 and the first four tools of "Model access & routing" match his `tools.json`; the rest was transcribed
  from the rendered page and has rounded numbers (flagged as `verbatim: false`).
- `scripts/seed_snapshot_2026-11-07.py` regenerates that first snapshot.
