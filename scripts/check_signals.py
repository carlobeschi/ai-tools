#!/usr/bin/env python3
"""Independently re-measure the public signals behind a category of the
AI Dev Tools Field Guide, so a snapshot can be checked against the source.

Usage:
    python3 scripts/check_signals.py scripts/checks/evals.json > check.json

What it measures per tool (same sources the guide names, see docs/methodology.md):
  hn_comments_12m   HN Algolia comment hits for each query since `since`
                    (max over queries; quoted phrases).
  hn_setup_hits     comment hits inside the Ask HN setup threads listed in
                    `setup_threads` (a lower bound for "HN devs naming it").
  collision         for ambiguous names: a sample of comments on the bare term,
                    split into kept / rejected by the `reject` keywords, plus
                    the kept share. Read the samples; keywords are a first pass.
  github_stars      GitHub stars (needs `gh` authenticated, or GITHUB_TOKEN).
  pypi_last_month   pypistats.org `last_month`.
  npm_last_month    api.npmjs.org last-month point downloads.

Only the standard library is used. Each source is fetched independently and a
failure is recorded as {"error": ...} instead of aborting the run.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HN = "https://hn.algolia.com/api/v1/search"
UA = {"User-Agent": "ai-tools-snapshot-check/1"}


def get_json(url, tries=int(os.environ.get("CHECK_TRIES", "3"))):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except Exception as e:  # rate limits, network policy, 404
            err = e
            time.sleep(2 ** i)
    raise err


def hn(params):
    return get_json(HN + "?" + urllib.parse.urlencode(params))


def safe(fn):
    try:
        return fn()
    except Exception as e:
        return {"error": str(e)}


def hn_comments(query, since_ts):
    return hn({"query": query, "tags": "comment", "hitsPerPage": 0,
               "numericFilters": f"created_at_i>{since_ts}"})["nbHits"]


def hn_setup_hits(query, threads):
    out = {}
    for t in threads:
        res = hn({"query": query, "tags": f"comment,story_{t}", "hitsPerPage": 50,
                  "typoTolerance": "false"})
        out[str(t)] = res["nbHits"]
    return out


def collision_sample(term, reject, since_ts, n=50):
    res = hn({"query": f'"{term}"', "tags": "comment", "hitsPerPage": n,
              "numericFilters": f"created_at_i>{since_ts}", "typoTolerance": "false"})
    kept, rejected = [], []
    for h in res["hits"]:
        text = (h.get("comment_text") or "").lower()
        i = text.find(term.lower())
        snippet = text[max(0, i - 60): i + 60] if i >= 0 else text[:120]
        (rejected if any(k in text for k in reject) else kept).append(
            {"id": h["objectID"], "story": h.get("story_id"), "snippet": snippet})
    total = len(kept) + len(rejected)
    return {"nbHits": res["nbHits"], "sampled": total,
            "kept_share": round(len(kept) / total, 2) if total else None,
            "kept": kept, "rejected": rejected}


def github_stars(repo):
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req = urllib.request.Request(f"https://api.github.com/repos/{repo}",
                                     headers={**UA, "Authorization": f"Bearer {tok}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["stargazers_count"]
    # `gh` search works even where the repos API is scoped down
    out = subprocess.run(["gh", "api", "-X", "GET", "search/repositories", "-f", f"q=repo:{repo}",
                          "--jq", ".items[0].stargazers_count"], capture_output=True, text=True, check=True)
    return int(out.stdout.strip())


def main(cfg_path):
    cfg = json.load(open(cfg_path))
    since = cfg["since"]
    since_ts = int(dt.datetime.fromisoformat(since).replace(tzinfo=dt.timezone.utc).timestamp())
    threads = cfg.get("setup_threads", [])
    result = {"category": cfg["category"], "measured_at": dt.date.today().isoformat(),
              "since": since, "setup_threads": threads, "tools": {}}
    for name, t in cfg["tools"].items():
        r = {}
        qs = t.get("hn_queries", [])
        r["hn_comments_12m"] = {q: safe(lambda q=q: hn_comments(q, since_ts)) for q in qs}
        r["hn_setup_hits"] = {q: safe(lambda q=q: hn_setup_hits(q.strip('"'), threads)) for q in qs}
        if "collision" in t:
            c = t["collision"]
            r["collision"] = safe(lambda: collision_sample(c["term"], c["reject"], since_ts))
        if "github" in t:
            r["github_stars"] = safe(lambda: github_stars(t["github"]))
        if "pypi" in t:
            r["pypi_last_month"] = safe(lambda: get_json(
                f"https://pypistats.org/api/packages/{t['pypi']}/recent")["data"]["last_month"])
        if "npm" in t:
            r["npm_last_month"] = safe(lambda: get_json(
                f"https://api.npmjs.org/downloads/point/last-month/{t['npm']}")["downloads"])
        result["tools"][name] = r
        print(f"done {name}", file=sys.stderr)
    json.dump(result, sys.stdout, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1])
