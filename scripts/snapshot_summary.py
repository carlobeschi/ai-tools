#!/usr/bin/env python3
"""Markdown summary of a snapshot against the one before it (used as the PR body).

Usage: python3 scripts/snapshot_summary.py 2026-11-09
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(d):
    return json.load(open(os.path.join(ROOT, f"data/snapshots/{d}.json")))


def tools(c):
    return {t["name"]: t for t in c["tools"] + c.get("others", [])}


def pct(a, b):
    if a is None or b in (None, 0):
        return None
    return (a - b) / b * 100


def main(date):
    idx = json.load(open(os.path.join(ROOT, "data/snapshots/index.json")))
    dates = idx["snapshots"]
    prev = dates[dates.index(date) - 1] if dates.index(date) > 0 else None
    new, old = load(date), (load(prev) if prev else None)
    oc = {c["id"]: c for c in old["categories"]} if old else {}
    out = [f"New snapshot **{date}**: {new['corpus']['ask_hn_threads']} Ask HN setup threads, "
           f"{new['corpus']['hn_comments']:,} comments, {new['corpus']['tools_scored']} tools tracked "
           f"({new['method']['requests']} requests, {new['method']['errors']} failed).", ""]
    if prev:
        kind = "the source's own numbers" if old.get("kind") != "collected" else "our previous run"
        out += [f"Compared with **{prev}** ({kind}). Against the source, only stars, downloads and the HN comments of tools "
                "marked `source_query` are measured the same way; compare HN devs and the score between collected snapshots.", ""]
    out += ["| Category | Top 3 now | Biggest move in HN comments (12 mo) |", "|---|---|---|"]
    for c in new["categories"]:
        top = ", ".join(f"{t['name']} ({t['hn_devs']})" for t in c["tools"][:3])
        moves = []
        if c["id"] in oc:
            ot = tools(oc[c["id"]])
            for n, t in tools(c).items():
                p = pct(t.get("hn_comments_12m"), ot.get(n, {}).get("hn_comments_12m"))
                same = old.get("kind") == "collected" or t.get("source_query")
                if same and p is not None and (ot[n]["hn_comments_12m"] or 0) >= 30:
                    moves.append((abs(p), f"{n} {p:+.0f}%"))
        out.append(f"| {c['name']} | {top} | {max(moves)[1] if moves else '–'} |")
    coll = [f"{c['id']}/{t['name']}" for c in new["categories"] for t in c["tools"] if t.get("collision")]
    out += ["", "Numbers are HN devs naming the tool in setup threads.", "",
            "**To review before merging:** these top-10 names collide with common words; read their samples in "
            f"`data/raw/{date}.json` and correct the snapshot (add to `corrections`) if the counts are not backed: "
            + ", ".join(coll) + "."]
    raw = json.load(open(os.path.join(ROOT, f"data/raw/{date}.json")))
    cands = raw.get("candidate_threads", [])[:8]
    if cands:
        out += ["", "**New Ask HN threads that may belong in the corpus** (add good ones to `setup_threads` in "
                "`scripts/tracked_tools.json`):", ""]
        out += [f"- [{c['title']}](https://news.ycombinator.com/item?id={c['id']}) ({c['num_comments']} comments, {c['date']})" for c in cands]
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
