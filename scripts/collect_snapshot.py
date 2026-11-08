#!/usr/bin/env python3
"""Collect a fresh snapshot of every tool in scripts/tracked_tools.json.

This is the recurring (every two weeks) run. It re-measures the public signals
behind the AI Dev Tools Field Guide with our own, documented queries (see
docs/methodology.md, "Recurring snapshots"), and writes:

  data/snapshots/<date>.json   same schema as the first snapshot, plus `others`
                               (tracked tools outside the top 10) and `method`
  data/raw/<date>.json         per-query counts, the setup threads used and
                               samples for names that collide, for review
  data/snapshots/index.json    the new date appended and marked latest

Usage:
    python3 scripts/collect_snapshot.py [--date YYYY-MM-DD] [--min-days 13]
                                        [--only terminal,editors] [--dry-run]

Needs network access to hn.algolia.com, api.github.com, pypistats.org,
api.npmjs.org and dev.to (a GitHub Actions runner has it; the Claude cloud
container does not). Set GITHUB_TOKEN for star counts. Standard library only.
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HN = "https://hn.algolia.com/api/v1/"
UA = {"User-Agent": "ai-tools-snapshot/1 (+https://github.com/carlobeschi/ai-tools)"}

# Composite score weights. Same blend as the source's method section, minus the
# two signals we cannot collect (Lobsters 7, tone 6); the rest is rescaled to 100.
WEIGHTS = {"hn_devs": 40, "hn_comments_12m": 20, "reach": 16, "hn_title_points": 12}

# Ask HN threads where developers describe their AI setup. Discovery queries are
# run against Ask HN stories; a title must match SETUP_TITLE to be used.
DISCOVERY_QUERIES = ["AI setup", "agentic setup", "AI coding setup", "AI workflow", "AI coding workflow",
                     "coding agent", "LLM setup", "AI tools", "AI coding tools", "AI stack", "using AI",
                     "Claude Code", "coding assistant", "vibe coding", "LLM workflow", "AI dev",
                     "your setup", "your workflow", "your stack", "how do you use AI", "how are you using AI",
                     "AI-assisted coding", "agentic coding", "LLM coding", "AI programming", "coding with AI",
                     "Cursor", "Copilot", "Codex", "coding agents", "AI tools for developers"]
SETUP_TITLE = re.compile(
    r"(?i)^ask hn\b.*\b(setup|set-up|workflow|stack|tools?|using|use|uses)\b.*"
    r"\b(ai|llms?|agents?|agentic|claude|copilot|cursor|codex|coding assistants?|vibe)\b"
    r"|^ask hn\b.*\b(ai|llms?|agents?|agentic|claude|copilot|cursor|codex)\b.*\b(setup|set-up|workflow|stack)\b")
MIN_THREAD_COMMENTS = 30

stats = {"requests": 0, "errors": 0}


def get_json(url, headers=None, tries=4):
    err = None
    for i in range(tries):
        try:
            stats["requests"] += 1
            req = urllib.request.Request(url, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            err = e
            if e.code == 404:
                break
            time.sleep(2 ** i * (5 if e.code == 429 else 1))
        except Exception as e:  # network hiccups
            err = e
            time.sleep(2 ** i)
    stats["errors"] += 1
    raise err


def hn(endpoint, **params):
    time.sleep(0.05)
    return get_json(HN + endpoint + "?" + urllib.parse.urlencode(params))


def safe(fn, default=None):
    try:
        return fn()
    except Exception as e:
        print(f"  ! {e}", file=sys.stderr)
        return default


def ts(date):
    return int(dt.datetime.combine(date, dt.time()).replace(tzinfo=dt.timezone.utc).timestamp())


# ---------- Ask HN setup threads ----------

def discover_threads(since_ts, seeds, rejected):
    found = {}
    for q in DISCOVERY_QUERIES:
        for page in range(3):
            res = safe(lambda: hn("search", query=q, tags="story,ask_hn", hitsPerPage=100, page=page,
                                  numericFilters=f"created_at_i>{since_ts},num_comments>={MIN_THREAD_COMMENTS}"))
            if not res:
                break
            for h in res["hits"]:
                if SETUP_TITLE.search(h.get("title") or ""):
                    found[int(h["objectID"])] = h
                else:
                    rejected[int(h["objectID"])] = {"title": h.get("title"), "num_comments": h.get("num_comments")}
            if page + 1 >= res.get("nbPages", 0):
                break
    for s in seeds:
        if s not in found:
            h = safe(lambda: get_json(f"{HN}items/{s}"))
            if h:
                found[s] = {"objectID": str(s), "title": h.get("title"), "created_at_i": h.get("created_at_i"),
                            "num_comments": None, "points": h.get("points")}
    return [{"id": k, "title": v.get("title"), "date": dt.datetime.fromtimestamp(v["created_at_i"], dt.timezone.utc).date().isoformat(),
             "points": v.get("points"), "num_comments": v.get("num_comments")}
            for k, v in sorted(found.items(), key=lambda kv: kv[1]["created_at_i"])]


def thread_comments(story_id):
    """All comments of one story. Algolia pages stop at 1000 hits, so walk back by date."""
    out, upper = {}, None
    while True:
        nf = f"created_at_i<{upper}" if upper else "created_at_i>0"
        res = hn("search_by_date", tags=f"comment,story_{story_id}", hitsPerPage=1000, numericFilters=nf)
        hits = res["hits"]
        for h in hits:
            out[h["objectID"]] = {"author": h.get("author"), "t": h.get("created_at_i"),
                                  "text": html.unescape(re.sub(r"<[^>]+>", " ", h.get("comment_text") or ""))}
        if len(hits) < 1000:
            return list(out.values())
        upper = min(h["created_at_i"] for h in hits) + 1  # +1 keeps same-second comments


# ---------- per tool signals ----------

def hn_comments(q, since_ts):
    return hn("search", query=q, tags="comment", hitsPerPage=0, numericFilters=f"created_at_i>{since_ts}")["nbHits"]


def hn_title_points(q, since_ts):
    res = hn("search", query=q, tags="story", hitsPerPage=1000, restrictSearchableAttributes="title",
             numericFilters=f"created_at_i>{since_ts}")
    return sum(h.get("points") or 0 for h in res["hits"])


def github_stars(repo):
    tok = os.environ.get("GITHUB_TOKEN")
    hdr = {"Accept": "application/vnd.github+json", **({"Authorization": f"Bearer {tok}"} if tok else {})}
    return get_json(f"https://api.github.com/repos/{repo}", hdr)["stargazers_count"]


def pypi_month(pkg):
    return get_json(f"https://pypistats.org/api/packages/{pkg.lower()}/recent")["data"]["last_month"]


def npm_month(pkg):
    return get_json(f"https://api.npmjs.org/downloads/point/last-month/{urllib.parse.quote(pkg, safe='@')}")["downloads"]


def devto_posts(tag, since):
    n = 0
    for page in range(1, 11):
        arts = get_json(f"https://dev.to/api/articles?tag={urllib.parse.quote(tag)}&per_page=1000&page={page}")
        n += sum(1 for a in arts if (a.get("published_at") or "")[:10] >= since)
        if len(arts) < 1000:
            break
        time.sleep(0.5)
    return n


def norm(x, top):
    import math
    if not x or not top:
        return 0.0
    return math.log1p(x) / math.log1p(top)


def score_category(rows):
    tops = {k: max((r.get(k) or 0) for r in rows) for k in ("hn_devs", "hn_comments_12m", "github_stars", "downloads_month", "hn_title_points")}
    total = sum(WEIGHTS.values())
    for r in rows:
        reach = max(norm(r.get("github_stars"), tops["github_stars"]), norm(r.get("downloads_month"), tops["downloads_month"]))
        s = (WEIGHTS["hn_devs"] * norm(r.get("hn_devs"), tops["hn_devs"])
             + WEIGHTS["hn_comments_12m"] * norm(r.get("hn_comments_12m"), tops["hn_comments_12m"])
             + WEIGHTS["reach"] * reach
             + WEIGHTS["hn_title_points"] * norm(r.get("hn_title_points"), tops["hn_title_points"]))
        r["score"] = round(100 * s / total, 1)


def snippet(text, m, width=70):
    a, b = max(0, m.start() - width), min(len(text), m.end() + width)
    return re.sub(r"\s+", " ", text[a:b]).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--min-days", type=int, default=0, help="skip if the latest snapshot is younger than this")
    ap.add_argument("--only", help="comma-separated category ids (for testing)")
    ap.add_argument("--dry-run", action="store_true", help="print the snapshot instead of writing files")
    args = ap.parse_args()

    date = dt.date.fromisoformat(args.date)
    idx_path = os.path.join(ROOT, "data/snapshots/index.json")
    idx = json.load(open(idx_path))
    latest = idx["latest"]
    age = (date - dt.date.fromisoformat(latest)).days
    if args.min_days and age < args.min_days:
        print(f"latest snapshot {latest} is {age} days old (< {args.min_days}); nothing to do")
        return 0

    cfg = json.load(open(os.path.join(ROOT, "scripts/tracked_tools.json")))
    prev = json.load(open(os.path.join(ROOT, f"data/snapshots/{latest}.json")))
    prev_tools = {(c["id"], t["name"]): t for c in prev["categories"] for t in c["tools"] + c.get("others", [])}
    prev_cats = {c["id"]: c for c in prev["categories"]}

    since12 = date - dt.timedelta(days=365)
    since12_ts, devs_since_ts = ts(since12), ts(dt.date.fromisoformat(cfg["hn_devs_since"]))

    print("discovering Ask HN setup threads...", file=sys.stderr)
    rejected = {}
    threads = discover_threads(devs_since_ts, cfg.get("setup_threads_seed", []), rejected)
    comments = []
    for th in threads:
        cs = safe(lambda: thread_comments(th["id"]), [])
        th["comments_fetched"] = len(cs)
        comments += cs
        print(f"  {th['id']} {len(cs):5d}  {th['title']}", file=sys.stderr)
    print(f"{len(threads)} threads, {len(comments)} comments", file=sys.stderr)

    only = set(args.only.split(",")) if args.only else None
    raw = {"date": args.date, "since_12m": since12.isoformat(), "hn_devs_since": cfg["hn_devs_since"],
           "setup_threads": threads,
           "rejected_threads": sorted(({"id": k, **v} for k, v in rejected.items() if k not in {t["id"] for t in threads}),
                                      key=lambda x: -(x["num_comments"] or 0))[:150],
           "tools": {}}
    categories = []
    for cid, tools in cfg["categories"].items():
        if only and cid not in only:
            continue
        rows = []
        for name, t in tools.items():
            print(f"{cid}: {name}", file=sys.stderr)
            rx = re.compile(t["re"], 0 if t.get("cs") else re.I)
            authors, authors12, samples = set(), set(), []
            for c in comments:
                m = rx.search(c["text"])
                if m and c["author"]:
                    authors.add(c["author"])
                    if (c["t"] or 0) > since12_ts:
                        authors12.add(c["author"])
                    if t.get("collide") and len(samples) < 8:
                        samples.append(snippet(c["text"], m))
            per_q = {q: safe(lambda q=q: hn_comments(q, since12_ts)) for q in t["q"]}
            plain = re.sub(r"\s*\(.*?\)", "", name)
            diag = {q: safe(lambda q=q: hn_comments(q, since12_ts)) for q in {plain, f'"{plain}"'} if q not in per_q}
            pts_q = {q: safe(lambda q=q: hn_title_points(q, since12_ts)) for q in t["q"]}
            r = {"name": name,
                 "hn_devs": len(authors), "hn_devs_12m": len(authors12),
                 "hn_comments_12m": max([v for v in per_q.values() if v is not None], default=None),
                 "hn_title_points": max([v for v in pts_q.values() if v is not None], default=None),
                 "lobsters": None, "tone": None,
                 "github_stars": safe(lambda: github_stars(t["gh"])) if "gh" in t else None,
                 "downloads_month": None, "devto": None}
            dl = {}
            if "pypi" in t:
                dl["pypi"] = safe(lambda: pypi_month(t["pypi"]))
            if "npm" in t:
                dl["npm"] = safe(lambda: npm_month(t["npm"]))
            r["downloads_month"] = dl.get("pypi") if dl.get("pypi") is not None else dl.get("npm")
            if "devto" in t:
                r["devto"] = safe(lambda: devto_posts(t["devto"], since12.isoformat()))
            p = prev_tools.get((cid, name), {})
            r["url"] = p.get("url")
            r["tags"] = [g for g in p.get("tags", []) if g == "Open source"]
            r["note"] = p.get("note")
            if t.get("collide"):
                r["collision"] = True
            rows.append(r)
            raw["tools"][f"{cid}/{name}"] = {"hn_comments_12m": per_q, "name_queries": diag, "hn_title_points": pts_q, "downloads": dl,
                                             **({"collision_samples": samples} if t.get("collide") else {})}
        score_category(rows)
        rows.sort(key=lambda r: (-r["score"], -(r["hn_devs"] or 0), r["name"]))
        for i, r in enumerate(rows, 1):
            r["rank"] = i
        order = ["rank", "name", "url", "score", "tags", "hn_devs", "hn_devs_12m", "hn_comments_12m", "hn_title_points",
                 "lobsters", "devto", "github_stars", "downloads_month", "tone", "note", "collision"]
        rows = [{k: r[k] for k in order if k in r} for r in rows]
        pc = prev_cats.get(cid, {})
        categories.append({"id": cid, "name": pc.get("name", cid), "description": pc.get("description"),
                           "verbatim": True, "tools": rows[:10], "also_scored": [r["name"] for r in rows[10:]],
                           "others": rows[10:]})

    snap = {
        "schema_version": 1,
        "snapshot_date": args.date,
        "kind": "collected",
        "edition": date.strftime("%B %Y"),
        "source": {"name": "ai-tools recurring snapshot", "author": "carlobeschi/ai-tools",
                   "url": "https://github.com/carlobeschi/ai-tools/blob/main/docs/methodology.md",
                   "baseline": {"name": prev["source"].get("baseline", {}).get("name") or prev["source"]["name"],
                                "url": prev["source"].get("baseline", {}).get("url") or prev["source"]["url"]},
                   "retrieved_at": args.date},
        "corpus": {"hn_comments": len(comments), "ask_hn_threads": len(threads),
                   "tools_scored": sum(len(c["tools"]) + len(c["others"]) for c in categories)},
        "fields": {**prev["fields"],
                   "score": "Composite 0-100 recomputed by collect_snapshot.py: HN devs 40, HN comments 20, max(stars, downloads) 16, HN title points 12, each log-scaled against the category's best tracked tool, rescaled to 100",
                   "hn_devs": f"HN developers naming the tool in Ask HN AI-setup threads since {cfg['hn_devs_since']}",
                   "hn_devs_12m": "Same, counting only comments from the last 12 months",
                   "hn_title_points": "Sum of points of HN stories with the tool in the title, last 12 months",
                   "devto": "dev.to posts with the tool's tag, last 12 months (only for tools with a tag)",
                   "lobsters": "Not collected (lobste.rs disallows automated access)",
                   "tone": "Not collected yet"},
        "method": {"script": "scripts/collect_snapshot.py", "config": "scripts/tracked_tools.json",
                   "weights": WEIGHTS, "raw": f"data/raw/{args.date}.json",
                   "comparable_to_baseline": ["hn_comments_12m", "github_stars", "downloads_month"],
                   "requests": stats["requests"], "errors": stats["errors"]},
        "notes": "Measured with our own queries, not taken from the source. Top 10 per category is re-ranked by the recomputed score among all tracked tools; `others` holds the rest. Names marked collision=true collide with common words: their counts need reading (samples in the raw file).",
        "polls": [],
        "categories": categories,
        "corrections": [],
    }
    if args.dry_run:
        json.dump(snap, sys.stdout, indent=1, ensure_ascii=False)
        return 0
    os.makedirs(os.path.join(ROOT, "data/raw"), exist_ok=True)
    with open(os.path.join(ROOT, f"data/snapshots/{args.date}.json"), "w") as f:
        json.dump(snap, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(ROOT, f"data/raw/{args.date}.json"), "w") as f:
        json.dump(raw, f, indent=1, ensure_ascii=False)
        f.write("\n")
    if args.date not in idx["snapshots"]:
        idx["snapshots"].append(args.date)
    idx["snapshots"].sort()
    idx["latest"] = idx["snapshots"][-1]
    with open(idx_path, "w") as f:
        json.dump(idx, f, indent=1)
        f.write("\n")
    print(f"wrote snapshot {args.date}: {snap['corpus']}, {stats}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
