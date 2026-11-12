#!/usr/bin/env python3
"""Help fill related X posts for an edition script (box-side, no render).

The X search itself is done with the x-namespace MCP tools (not this script).
This helper prints a search query per segment, or ranks a dumped results file
and writes xposts.json (about 3-6 posts per segment).

    python3 auto_xposts.py queries script.md
    python3 auto_xposts.py pick script.md results.json -o xposts.json

results.json shape:
{
  "09": {
    "posts": [ { "id", "text", "url", "possibly_sensitive",
                 "public_metrics": {"like_count","retweet_count","impression_count","quote_count"},
                 "author_id", "in_reply_to_user_id", "referenced_tweets": [{"type": "replied_to"}] } ],
    "users":  { "AUTHOR_ID": { "username", "name", "verified", "verified_type",
                               "public_metrics": {"followers_count"} } }
  }
}

Ranking prefers high-engagement, verified, on-topic posts from established
accounts, and drops replies, Grok replies, "AI Overview" spam, and anything
marked possibly_sensitive. Review the file before building; never auto-post.
"""
import argparse, json, re, sys

STOP = {"the","a","an","and","or","of","to","in","on","for","with","at","by","from",
        "is","are","was","were","be","this","that","it","as","its","their","our"}

def parse_segments(path):
    txt = open(path).read()
    segs = []
    for block in re.split(r"^## ", txt, flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        num, _, title = head.strip().partition(" ")
        if re.match(r"^(cold open|sign-?off|outro)$", title.strip(), re.I):
            continue
        if re.search(r"^(?:Camera|On camera):\s*(self|yes|on camera|none)\s*$", body, re.I | re.M):
            continue
        nar_m = re.search(r"^Narration:\s*(.+)$", body, re.M)
        nar = nar_m.group(1).strip() if nar_m else ""
        segs.append({"num": num, "title": title, "narration": nar})
    return segs

def keywords(title, narration, n=8):
    words = re.findall(r"[A-Za-z][A-Za-z0-9'+-]{2,}", f"{title} {narration}")
    out, seen = [], set()
    for w in words:
        lw = w.lower()
        if lw in STOP or lw in seen:
            continue
        seen.add(lw); out.append(w)
        if len(out) >= n:
            break
    return out

def query_for(seg):
    kws = keywords(seg["title"], seg["narration"])
    # Prefer a quoted title-ish phrase plus a couple of anchors.
    q = " ".join(kws[:6]) + " -is:retweet lang:en"
    return q

def score(post, users):
    if post.get("possibly_sensitive"):
        return None
    text = post.get("text") or ""
    if re.search(r"\bAI Overview\b", text):
        return None
    author = (users or {}).get(str(post.get("author_id") or ""), {}) or {}
    if (author.get("username") or "").lower() == "grok":
        return None
    refs = post.get("referenced_tweets") or post.get("referenced_posts") or []
    if post.get("in_reply_to_user_id") or any((r.get("type") == "replied_to") for r in refs):
        reply = True
    else:
        reply = False
    m = post.get("public_metrics") or {}
    eng = (m.get("like_count") or 0) + 3 * (m.get("retweet_count") or 0) + 2 * (m.get("quote_count") or 0) \
          + 0.001 * (m.get("impression_count") or 0)
    followers = ((author.get("public_metrics") or {}).get("followers_count") or 0)
    vtype = author.get("verified_type") or ""
    bonus = 500 if vtype == "business" else (200 if author.get("verified") or vtype in {"blue", "government"} else 0)
    if followers < 1000 and vtype != "business":
        eng *= 0.3
    if reply:
        eng *= 0.15
    return eng + bonus + min(followers, 1_000_000) / 5000

def pick(seg, blob, lo=3, hi=6):
    posts = blob.get("posts") or blob.get("data") or []
    users = blob.get("users") or {}
    # includes.users list → id map
    if isinstance(users, list):
        users = {str(u.get("id")): u for u in users}
    else:
        users = {str(k): v for k, v in users.items()}
    ranked = []
    for p in posts:
        s = score(p, users)
        if s is None:
            continue
        ranked.append((s, p, users.get(str(p.get("author_id") or ""), {})))
    ranked.sort(key=lambda x: -x[0])
    picked, seen = [], set()
    for s, p, u in ranked:
        pid = str(p.get("id") or "")
        handle = u.get("username")
        if not pid or pid in seen:
            continue
        seen.add(pid)
        url = p.get("url") or (f"https://x.com/{handle}/status/{pid}" if handle else f"https://x.com/i/status/{pid}")
        picked.append({
            "id": pid,
            "url": url,
            "handle": handle,
            "label": u.get("name") or (f"@{handle}" if handle else "X post"),
            "metrics": p.get("public_metrics") or {},
        })
        if len(picked) >= hi:
            break
    return picked[: max(lo, min(hi, len(picked))) ] if picked else []

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queries", help="Print a suggested X search query per segment")
    q.add_argument("script")
    p = sub.add_parser("pick", help="Rank dumped search results and write xposts.json")
    p.add_argument("script")
    p.add_argument("results")
    p.add_argument("-o", "--output", default="xposts.json")
    p.add_argument("--min", type=int, default=3)
    p.add_argument("--max", type=int, default=6)
    args = ap.parse_args()
    segs = parse_segments(args.script)
    if args.cmd == "queries":
        for s in segs:
            print(f"{s['num']}\t{s['title']}\t{query_for(s)}")
        return
    results = json.load(open(args.results))
    mapping = results.get("segments", results)
    out = {}
    for s in segs:
        blob = mapping.get(s["num"]) or mapping.get(str(int(s["num"])) if s["num"].isdigit() else "") or {}
        posts = pick(s, blob, args.min, args.max)
        if posts:
            out[s["num"]] = posts
    json.dump(out, open(args.output, "w"), indent=1)
    print(f"wrote {args.output} ({sum(len(v) for v in out.values())} posts across {len(out)} segments)")

if __name__ == "__main__":
    main()
