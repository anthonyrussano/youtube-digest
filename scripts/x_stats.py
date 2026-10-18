#!/usr/bin/env python3
"""./run.sh x-stats: impressions broken down by X Article format (roundup vs deep-dive).

Joins state/x_posts.json (each post's "format": "roundup" | "deep-dive"; posts without one count as roundup, the
only format before edition 2026-10-17-1644) with state/x_impressions.csv (routine C) on post_id. Read-only;
prints to stdout only, because both files are private (never commit their contents)."""
import csv, json, os, statistics as st
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts = json.load(open(f"{ROOT}/state/x_posts.json")).get("posts", [])
rows = {}
try:
    with open(f"{ROOT}/state/x_impressions.csv", newline="") as f:
        rows = {r["post_id"]: r for r in csv.DictReader(f)}
except FileNotFoundError:
    pass
num = lambda v: float(v) if v not in (None, "") else None
groups = {}
for p in posts:
    r = rows.get(str(p.get("post_id")), {})
    age = num(r.get("age_hours_at_measure"))
    groups.setdefault(p.get("format") or "roundup", []).append({
        "edition": p["edition"], "imp": num(r.get("impressions_24h")), "age": age,
        "near24": age is not None and 18 <= age <= 30,
        **{k: num(r.get(k)) for k in ("likes", "replies", "bookmarks", "reposts")}})

def agg(xs, k):
    v = [x[k] for x in xs if x[k] is not None]
    return f"{st.mean(v):7.1f} {st.median(v):7.1f}" if v else "      -       -"

print(f"{'format':10} {'posts':>5} {'meas':>4} {'~24h':>4} | {'imp mean':>8} {'median':>7} | {'~24h mean':>9} {'median':>7} | likes  replies  bookm. (mean)")
for fmt in sorted(groups):
    xs = groups[fmt]; m = [x for x in xs if x["imp"] is not None]; n24 = [x for x in m if x["near24"]]
    means = "  ".join(f"{st.mean(v):5.1f}" if (v := [x[k] for x in m if x[k] is not None]) else "    -" for k in ("likes", "replies", "bookmarks"))
    print(f"{fmt:10} {len(xs):5} {len(m):4} {len(n24):4} | {agg(m, 'imp'):>16} | {agg(n24, 'imp'):>17} | {means}")
print("\nPer post (edition, format, impressions, age h):")
for fmt in sorted(groups):
    for x in groups[fmt]:
        print(f"  {x['edition']:16} {fmt:10} {('-' if x['imp'] is None else int(x['imp'])):>6} {('' if x['age'] is None else x['age']):>6}")
print("\n'~24h' = measured 18-30 h after posting (the fair comparison). Unmeasured posts show '-'.")
