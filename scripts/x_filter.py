#!/usr/bin/env python3
"""Filter saved X search results down to posts people save and share.

Usage: x_filter.py [--min-bookmarks 10] [--hours 24] [--top 15] [--raw-dir DIR] [--out FILE]
Reads data/x_raw/*.json (raw search_posts_all responses saved by the routine; any wrapper text around
the JSON object is tolerated), keeps posts with bookmark_count >= floor (10) that pass either route:
  saves route:  bookmark_count > like_count
  shares route: retweet_count >= 30 or quote_count >= 5, and bookmarks >= 0.2 x likes (drops celebrity
                chatter that is liked but not saved)
followed route (authors in config/x_accounts.txt, Anthony's followed sources): bookmark_count >= 5 and
                (saves, or retweets >= 10, or quotes >= 3), and bookmarks >= 0.1 x likes (quality floor)
created within the window, drops crypto/spam, de-duplicates by id and near-identical text, tags each post with
trend categories (scripts/x_trends.py), ranks by bookmarks x1.5 when the post matches a top trending category
(data/x_trends.json), then bookmark/like ratio, and writes data/x_selected.json.
"""
import argparse, glob, json, os, re, sys
from datetime import datetime, timedelta, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--min-bookmarks", type=int, default=10)
ap.add_argument("--hours", type=float, default=24)
ap.add_argument("--top", type=int, default=15)
ap.add_argument("--raw-dir", default=None, help="default data/x_raw")
ap.add_argument("--out", default=None, help="default data/x_selected.json")
ap.add_argument("--min-reposts", type=int, default=30)
ap.add_argument("--min-quotes", type=int, default=5)
ap.add_argument("--shares-min-ratio", type=float, default=0.2, help="shares route also needs bookmarks >= ratio*likes")
ap.add_argument("--followed-min-bookmarks", type=int, default=5)
ap.add_argument("--followed-min-reposts", type=int, default=10)
ap.add_argument("--followed-min-quotes", type=int, default=3)
ap.add_argument("--followed-min-ratio", type=float, default=0.1, help="followed route needs bookmarks >= ratio*likes")
ap.add_argument("--since", help="ISO UTC; default: state/current_edition.json start_utc, else now-hours")
a = ap.parse_args()
SPAM = re.compile(r"\$[A-Z]{2,6}\b|\b(crypto|memecoin|airdrop|presale|token launch|web3|defi|nft|solana|bitcoin|btc|eth|"
                  r"giveaway|dm me|link in bio|onlyfans|100x|pump)\b", re.I)
try: _cur = json.load(open(f"{ROOT}/state/current_edition.json")).get("start_utc")
except Exception: _cur = None
since = a.since or _cur
cutoff = datetime.fromisoformat(since.replace("Z", "+00:00")) if since else datetime.now(timezone.utc) - timedelta(hours=a.hours)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x_trends import categories, load_trends, tag
from x_accounts import load as load_accounts
FOLLOWED = {h.lower() for h in load_accounts()}
CATS, TREND = categories(), load_trends()
TOP_TRENDS = TREND.get("top", [])
try: published_x = set(json.load(open(f"{ROOT}/state/published.json")).get("x", []))
except Exception: published_x = set()
posts, users, scanned = {}, {}, 0
for f in sorted(glob.glob(f"{a.raw_dir or ROOT + '/data/x_raw'}/*.json")):
    t = open(f, encoding="utf-8").read()
    try: d = json.loads(t[t.index("{"):t.rindex("}") + 1])
    except ValueError: print("skip unparsable", f); continue
    for u in d.get("includes", {}).get("users", []): users[u["id"]] = u
    for p in d.get("data", []) or []:
        scanned += 1; p["_query_file"] = os.path.basename(f); posts.setdefault(p["id"], p)
sel, seen_text = [], set()
for p in posts.values():
    m = p.get("public_metrics", {}); b, l = m.get("bookmark_count", 0), m.get("like_count", 0)
    saves = b > l
    shares = (m.get("retweet_count", 0) >= a.min_reposts or m.get("quote_count", 0) >= a.min_quotes) and b >= a.shares_min_ratio * l
    u = users.get(p.get("author_id"), {})
    followed = (u.get("username") or "").lower() in FOLLOWED and b >= a.followed_min_bookmarks and \
        b >= a.followed_min_ratio * l and (saves or m.get("retweet_count", 0) >= a.followed_min_reposts
                                           or m.get("quote_count", 0) >= a.followed_min_quotes)
    strict = b >= a.min_bookmarks and (saves or shares)
    if not (strict or followed) or p["id"] in published_x: continue
    if datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")) < cutoff: continue
    text = p.get("note_tweet", {}).get("text") or p.get("text", "")
    if SPAM.search(text): continue
    key = re.sub(r"https?://\S+|\W", "", text.lower())[:120]
    if key in seen_text: continue
    seen_text.add(key)
    sel.append({"id": p["id"], "url": p.get("url") or f"https://x.com/{u.get('username','i')}/status/{p['id']}",
                "author": u.get("name"), "username": u.get("username"), "created_at": p["created_at"],
                "bookmarks": b, "likes": l, "reposts": m.get("retweet_count", 0), "quotes": m.get("quote_count", 0),
                "route": ("saves" if saves else "shares") if strict else "followed", "ratio": round(b / max(l, 1), 2), "text": text,
                "trends": [c for c in tag(text, CATS) if c in TOP_TRENDS],
                "article_title": (p.get("article") or {}).get("title"), "query_file": p["_query_file"]})
sel.sort(key=lambda s: (-s["bookmarks"] * (1.5 if s["trends"] else 1), -s["ratio"]))
sel = sel[:a.top]
out = a.out or f"{ROOT}/data/x_selected.json"
json.dump(sel, open(out, "w"), indent=1, ensure_ascii=False)
print(f"window since {cutoff.isoformat()}; {scanned} posts scanned, {len(posts)} unique, {len(sel)} selected -> {out}")
print(f"top trends ({TREND.get('date', 'none')}): {', '.join(TOP_TRENDS) or '-'}")
for s in sel: print(f"  {s['bookmarks']:>5}b {s['likes']:>5}l {s['reposts']:>4}rt {s['quotes']:>3}q {s['route']:<8} "
                    f"{'+'.join(s['trends']) or '-':<14} @{s['username']}: {s['text'][:70]!r}")
