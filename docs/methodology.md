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
