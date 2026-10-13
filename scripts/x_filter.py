#!/usr/bin/env python3
"""Filter saved X search results down to posts people bookmark more than they like.

Usage: x_filter.py [--min-bookmarks 10] [--hours 24] [--top 15]
Reads data/x_raw/*.json (raw search_posts_all responses saved by the routine; any wrapper text around
the JSON object is tolerated), keeps posts with bookmark_count > like_count and bookmark_count >= floor,
created within the window, drops crypto/spam, de-duplicates by id and near-identical text, ranks by
bookmarks then bookmark/like ratio, and writes data/x_selected.json.
"""
import argparse, glob, json, os, re
from datetime import datetime, timedelta, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--min-bookmarks", type=int, default=10)
ap.add_argument("--hours", type=float, default=24)
ap.add_argument("--top", type=int, default=15)
ap.add_argument("--since", help="ISO UTC; default: state/current_edition.json start_utc, else now-hours")
a = ap.parse_args()
SPAM = re.compile(r"\$[A-Z]{2,6}\b|\b(crypto|memecoin|airdrop|presale|token launch|web3|defi|nft|solana|bitcoin|btc|eth|"
                  r"giveaway|dm me|link in bio|onlyfans|100x|pump)\b", re.I)
try: _cur = json.load(open(f"{ROOT}/state/current_edition.json")).get("start_utc")
except Exception: _cur = None
since = a.since or _cur
cutoff = datetime.fromisoformat(since.replace("Z", "+00:00")) if since else datetime.now(timezone.utc) - timedelta(hours=a.hours)
try: published_x = set(json.load(open(f"{ROOT}/state/published.json")).get("x", []))
except Exception: published_x = set()
posts, users, scanned = {}, {}, 0
for f in sorted(glob.glob(f"{ROOT}/data/x_raw/*.json")):
    t = open(f, encoding="utf-8").read()
    try: d = json.loads(t[t.index("{"):t.rindex("}") + 1])
    except ValueError: print("skip unparsable", f); continue
    for u in d.get("includes", {}).get("users", []): users[u["id"]] = u
    for p in d.get("data", []) or []:
        scanned += 1; p["_query_file"] = os.path.basename(f); posts.setdefault(p["id"], p)
sel, seen_text = [], set()
for p in posts.values():
    m = p.get("public_metrics", {}); b, l = m.get("bookmark_count", 0), m.get("like_count", 0)
    if b < a.min_bookmarks or b <= l or p["id"] in published_x: continue
    if datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")) < cutoff: continue
    text = p.get("note_tweet", {}).get("text") or p.get("text", "")
    if SPAM.search(text): continue
    key = re.sub(r"https?://\S+|\W", "", text.lower())[:120]
    if key in seen_text: continue
    seen_text.add(key); u = users.get(p.get("author_id"), {})
    sel.append({"id": p["id"], "url": p.get("url") or f"https://x.com/{u.get('username','i')}/status/{p['id']}",
                "author": u.get("name"), "username": u.get("username"), "created_at": p["created_at"],
                "bookmarks": b, "likes": l, "ratio": round(b / max(l, 1), 2), "text": text,
                "article_title": (p.get("article") or {}).get("title"), "query_file": p["_query_file"]})
sel.sort(key=lambda s: (-s["bookmarks"], -s["ratio"]))
sel = sel[:a.top]
json.dump(sel, open(f"{ROOT}/data/x_selected.json", "w"), indent=1, ensure_ascii=False)
print(f"window since {cutoff.isoformat()}; {scanned} posts scanned, {len(posts)} unique, {len(sel)} selected -> data/x_selected.json")
for s in sel: print(f"  {s['bookmarks']:>5}b {s['likes']:>5}l @{s['username']}: {s['text'][:90]!r}")
