# How the snapshot data is collected and checked

This is how we reconstruct, and independently check, the numbers in Alexis
Santos's [AI Dev Tools Field Guide](https://alexissantos.dev/ai-dev-tools/).
It is the basis for the recurring (every two weeks) snapshot check.

## What the source measures

Per tool, the guide publishes these signals (`signals` in its `tools.json`):

| Field | Source | How to reproduce |
|---|---|---|
| `hn_devs` | Ask HN "what's your setup" threads, May 2025 onward | Count distinct commenters naming the tool inside those threads (Algolia `tags=comment,story_<id>`) |
| `hn_comments_12m` | HN comments, last 12 months | Algolia `tags=comment`, `numericFilters=created_at_i>T`, quoted phrase, read `nbHits` |
| `hn_title_points` | HN front-page stories about the tool | Algolia `tags=story`, sum or max of `points` |
| `lobsters` | Lobsters stories | lobste.rs search (blocks automated fetches, see below) |
| `devto` | dev.to posts | `dev.to/api/articles?tag=<tag>` (tag counts, not full-text) |
| `github_stars` | GitHub | `gh api search/repositories -f q=repo:<owner>/<name>` |
| `downloads_month` | npm / PyPI, last month | `pypistats.org/api/packages/<pkg>/recent`, `api.npmjs.org/downloads/point/last-month/<pkg>` |
| `tone` | HN comment sentiment, -1..1 | Not reproduced yet |

The composite `score` (0-100) is the source's own blend, per its method
section: HN devs 40, HN comments 20, stars or downloads 16, HN front-page
points 12, Lobsters 7, dev.to 5, tone ±6. Each signal is log-scaled and
divided by the category leader. We do not recompute it; we only flag when a
wrong input is likely to have moved it.

In the 2026-11-08 check, our `hn_comments_12m`, stars and downloads matched
the source exactly where it published them, so these are the same queries.
For downloads the source uses the PyPI package where one exists, and npm
otherwise (promptfoo).

## Name collisions (false positives)

The source itself says "Names collide: Pi, Cursor, Muse, Phoenix." Any tool
whose name is a common word, a place, or another product must be checked by
reading a sample of hits, not just counting them. Known cases:

| Name | Collides with | Filter |
|---|---|---|
| Phoenix (Arize) | Elixir Phoenix / LiveView, Phoenix AZ, old Firefox name | Query `"arize phoenix"` and `"arize"`; never bare `phoenix` |
| Braintrust | the word "braintrust", Amazon "S3 braintrust" | About 80% true positives in a sample of 20 |
| Laminar | "laminar flow" | About 30% true positives; prefer `lmnr` |
| garak | the Star Trek DS9 character | Mostly false positives |
| Weave (W&B) | the English verb | Query `"wandb weave"` |
| Pi, Cursor, Muse | common words | Read the thread context |

Other caveats:

- Monthly "Who wants to be hired" threads inflate comment counts for tools
  people list on CVs (Langfuse, MLflow). It is a real signal of use, but not
  of setup choice.
- Algolia is typo-tolerant: `arize` matches "arise". Use quoted phrases and
  `typoTolerance=false` when counting inside one thread.
- Algolia caps `nbHits` at 1000 for broad terms; a 1000 means "unknown".

## The check, step by step

1. Put the category's tools in `scripts/checks/<category>.json`: HN queries,
   GitHub repo, PyPI and npm package, and a `collision` block for ambiguous
   names. Add the largest Ask HN setup threads to `setup_threads`.
2. Run `python3 scripts/check_signals.py scripts/checks/<category>.json > out.json`
   from a machine that can reach hn.algolia.com, pypistats.org and
   api.npmjs.org.
3. Compare with the snapshot. For each difference, decide whether it is
   timing (stars and downloads drift), rounding, or a real error.
4. Read the `collision` samples. If a high count is not backed by true
   positives, correct the value.
5. Fix the snapshot JSON and add an entry to its top-level `corrections`
   list (`date`, `category`, `tool`, `field`, `from`, `to`, `reason`).

## Recurring snapshots (every two weeks)

`scripts/collect_snapshot.py` re-measures every tool in `scripts/tracked_tools.json` (each category's top 10 from
the source plus the other tools the source scored, 184 in all) and writes a new `data/snapshots/<date>.json`,
with the details behind it in `data/raw/<date>.json`.

How it runs: `.github/workflows/snapshot.yml` starts every Monday at 06:17 UTC on a GitHub runner (which, unlike
the Claude cloud container, reaches HN, PyPI, npm and dev.to). It collects only when the latest snapshot is 13
days old or more, so a new one lands every second Monday, and opens a pull request `Snapshot <date>` with a
summary. Merging the PR publishes it on the site. "Run workflow" on the Actions tab with `force` collects at once.

What it measures, per tool:

| Field | How |
|---|---|
| `hn_devs` | Distinct HN authors whose comment in one of the curated Ask HN setup threads (`setup_threads`) matches the tool's `re` |
| `hn_devs_12m` | Same, comments from the last 12 months only |
| `hn_comments_12m` | Algolia comment hits for the first query in `q`, last 12 months (the others go to the raw file) |
| `hn_title_points` | Sum of points of HN stories with a `q` phrase in the title, last 12 months |
| `github_stars` | GitHub API, repo `gh` |
| `downloads_month` | pypistats last month for `pypi`, else npm last month for `npm` |
| `devto` | dev.to posts with tag `devto` in the last 12 months (only a few tools have a tag; not in the score) |
| `score` | HN devs 40, HN comments 20, max(stars, downloads) 16, title points 12; each log-scaled against the category's best tracked tool, total rescaled to 100 |

Lobsters and tone are not collected (null).

Tags (Rising, Fading, New in 2026, Open source) are the source's labels, carried forward from the previous
snapshot for each tool; the treemap colours tiles by them. They are not recomputed yet.

Setup threads are a hand-curated list (19 general threads, none about a single tool, May 2025 onward) so the corpus changes only on purpose. Each
run also searches Ask HN stories from the last 60 days with at least 30 comments whose title talks about an AI
setup, workflow or stack, and lists them as candidates in the raw file and the PR; add the good ones to
`setup_threads`.

Comparability with the source: stars and downloads are the same measurement. For HN comments, 62 tools have a
first query that reproduces the source's count within 10% (checked 2026-11-08 against every tool, quoted and
unquoted names and our aliases); they carry `src: true` in the config and `source_query: true` in the snapshot,
and only those are compared with the first snapshot. `hn_devs`, title points and the score are our own
reconstruction (the source's thread list is not published), so the trends page compares them only between
collected snapshots.

Reviewing a snapshot PR: tools marked `collision: true` (Pi, Cursor, Orca, Goose…) match common words. Read
their `collision_samples` in the raw file, correct the snapshot when the matches are not about the tool, and add
the fix to `corrections`. To track a new tool, add it to `tracked_tools.json` (an `re` is required; check it on
a few comments first).

## Access notes

- The Claude cloud container used so far blocks hn.algolia.com, pypistats,
  api.npmjs.org, dev.to and alexissantos.dev for scripts; they were read
  through the web-fetch tool instead. Lobsters refuses automated fetches
  everywhere (robots), so `lobsters` stays as the source published it.
- `gh` works there, including `search/repositories` for star counts.

## Log

- 2026-11-08, Evals & observability: Arize Phoenix `hn_devs` 30 was not
  reproducible (0 "phoenix" hits in Ask HN 50366117 and three other setup
  threads; 5 "arize phoenix" comments on all of HN in 12 months). Set to 0.
  Stars and downloads replaced with exact values; all matched the rounded
  source values.
