#!/usr/bin/env python3
"""RSS/Atom feeds stage (./run.sh feeds): config/feeds.txt -> data/feeds.json.

  feeds.py [--since ISO] [--hours H] [--workers 10] [--timeout 15] [--shortlist 40] [--no-text]

* Window: --since, else state/current_edition.json start_utc (same as `fetch`), else --hours (default 24).
* Fetches every feed concurrently with a timeout; ETag/Last-Modified cached in state/feeds_http.json
  (bodies cached in data/feeds_cache/ so a 304 still yields entries).
* Drops entries outside the window, entries failing the feed's filter, and URLs already in state/feeds_seen.json
  or published.json "articles" (canonical URL: utm_* params and fragment stripped). Never writes feeds_seen.json:
  only `edition.py published` does, so a skipped edition leaves its items eligible.
* Scores on title+summary: tier (1:3, 2:2, 3:1) + AI/DevOps keyword hits (regexes from digest.py) + 1.5x boost when
  a data/x_trends.json "top" category regex (config/x_trends.txt) matches. Top --shortlist items with a keyword
  hit (or tier 1) get full text via trafilatura (capped ~6000 chars) in data/feeds_text/<hash>.txt, else summary.
"""
import argparse, concurrent.futures as cf, hashlib, html, json, os, re, sys, time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import urllib.request, urllib.error
import feedparser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from feeds_canon import canon
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
TEXT_CAP = 6000
def load(p, d):
    try: return json.load(open(p))
    except Exception: return d
def save(p, o): os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(o, open(p, "w"), indent=1)
def h(s): return hashlib.sha1(s.encode()).hexdigest()[:16]
def clean(t): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t or ""))).strip()
def read_feeds():
    out = []
    for ln in open(f"{ROOT}/config/feeds.txt"):
        if not ln.strip() or ln.lstrip().startswith("#"): continue
        p = [x.strip() for x in ln.split(" | ", 3)]
        f = {"url": p[0], "name": p[1], "tier": int(p[2]) if len(p) > 2 else 3, "filter": p[3] if len(p) > 3 else ""}
        if f["filter"].startswith("kw:"): f["kw"] = re.compile(f["filter"][3:], re.I)
        out.append(f)
    return out
def kw_regexes():
    src = open(f"{ROOT}/digest.py").read()
    return {k: re.compile(re.search(rf'^{k} = r"(.+)"$', src, re.M).group(1), re.I) for k in ("AI", "DEVOPS")}
def trend_regexes():
    top = set(load(f"{ROOT}/data/x_trends.json", {}).get("top", [])); out = {}
    for ln in open(f"{ROOT}/config/x_trends.txt"):
        if ln.startswith("#") or ln.count(" | ") < 2: continue
        name, _, rx = [x.strip() for x in ln.split(" | ", 2)]
        if name in top: out[name] = re.compile(rx, re.I)
    return out

def fetch(f, cache, timeout):
    r = fetch1(f, cache, timeout)
    if r[1] is None and not r[3].startswith("HTTP 4"): time.sleep(1); r = fetch1(f, cache, timeout * 1.5)  # one retry for timeouts/TLS hiccups
    return r
def fetch1(f, cache, timeout):
    c = cache.get(f["url"], {}); body_p = f"{ROOT}/data/feeds_cache/{h(f['url'])}.xml"
    req = urllib.request.Request(f["url"], headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"})
    if os.path.exists(body_p):
        if c.get("etag"): req.add_header("If-None-Match", c["etag"])
        if c.get("modified"): req.add_header("If-Modified-Since", c["modified"])
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(); status = r.status
            c = {"etag": r.headers.get("ETag"), "modified": r.headers.get("Last-Modified")}
        os.makedirs(os.path.dirname(body_p), exist_ok=True); open(body_p, "wb").write(body)
    except urllib.error.HTTPError as e:
        if e.code != 304: return f, None, c, f"HTTP {e.code}"
        body = open(body_p, "rb").read(); status = 304
    except Exception as e:
        return f, None, c, f"{type(e).__name__}: {e}"[:200]
    d = feedparser.parse(body)
    if not d.entries and d.bozo: return f, None, c, f"not a feed: {d.bozo_exception}"[:200]
    return f, d, c, f"{status} {time.time()-t0:.1f}s"

def entry_time(e):
    for k in ("published_parsed", "updated_parsed", "created_parsed"):
        if e.get(k): return datetime(*e[k][:6], tzinfo=timezone.utc)
def extract(item, timeout):
    import trafilatura
    p = f"{ROOT}/data/feeds_text/{h(item['url'])}.txt"
    if os.path.exists(p): return item, open(p).read(), "trafilatura (cached)"
    try:
        req = urllib.request.Request(item["url"], headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r: raw = r.read(3_000_000).decode("utf-8", "replace")
        txt = trafilatura.extract(raw, include_comments=False, include_tables=False, favor_precision=True) or ""
    except Exception as e:
        txt = ""; err = f"{type(e).__name__}"
    else: err = "too short"
    if len(txt) < 300: return item, None, f"summary fallback ({err})"
    if len(txt) > TEXT_CAP: txt = txt[:TEXT_CAP].rsplit(" ", 1)[0] + " …"
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(txt)
    return item, txt, "trafilatura"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since"); ap.add_argument("--hours", type=float, default=24)
    ap.add_argument("--workers", type=int, default=10); ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--shortlist", type=int, default=40); ap.add_argument("--no-text", action="store_true")
    ap.add_argument("--out", default=f"{ROOT}/data/feeds.json")
    a = ap.parse_args(); t0 = time.time()
    since = a.since or (None if "--hours" in sys.argv else load(f"{ROOT}/state/current_edition.json", {}).get("start_utc"))
    cutoff = datetime.fromisoformat(since.replace("Z", "+00:00")) if since else datetime.now(timezone.utc) - timedelta(hours=a.hours)
    feeds = read_feeds(); cache_p = f"{ROOT}/state/feeds_http.json"; cache = load(cache_p, {})
    seen = set(load(f"{ROOT}/state/feeds_seen.json", [])) | {canon(u) for u in load(f"{ROOT}/state/published.json", {}).get("articles", [])}
    KW, TR = kw_regexes(), trend_regexes(); now = datetime.now(timezone.utc)
    items, report, dup = [], [], set(); counts = {"seen": 0, "filtered": 0, "undated": 0, "old": 0}
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for f, d, c, msg in ex.map(lambda f: fetch(f, cache, a.timeout), feeds):
            cache[f["url"]] = c; n = 0
            if d is not None:
                for e in d.entries:
                    link = e.get("link") or ""
                    if not link: continue
                    u = canon(link); ts = entry_time(e)
                    if ts is None: counts["undated"] += 1; continue
                    if ts < cutoff or ts > now + timedelta(days=2): counts["old"] += 1; continue
                    if u in seen: counts["seen"] += 1; continue
                    if u in dup: continue
                    title = clean(e.get("title")); summ = clean(e.get("summary") or e.get("description"))[:1500]
                    if f.get("kw") and not f["kw"].search(f"{title} {summ}"): counts["filtered"] += 1; continue
                    dup.add(u); n += 1
                    blob = f"{title} {summ}"
                    ai = len(set(m.lower() for m in KW["AI"].findall(blob))); dv = len(set(m.lower() for m in KW["DEVOPS"].findall(blob)))
                    trends = [k for k, rx in TR.items() if rx.search(blob)]
                    score = {1: 3, 2: 2}.get(f["tier"], 1) + min(ai, 3) + min(dv, 3)  # keyword hits capped at 3 each
                    score = round(score * (1.5 if trends else 1), 2)
                    items.append({"id": h(u), "url": u, "title": title, "feed": f["name"], "tier": f["tier"],
                                  "published_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "summary": summ,
                                  "category": "AI" if ai >= dv and ai else ("DevOps" if dv else None),
                                  "keyword_hits": {"AI": ai, "DevOps": dv}, "trends": trends, "score": score})
            report.append({"feed": f["name"], "url": f["url"], "tier": f["tier"], "status": msg, "ok": d is not None, "new_items": n})
    save(cache_p, cache)
    items.sort(key=lambda i: (-i["score"], i["published_utc"]))
    short = [i for i in items if i["category"] or i["tier"] == 1][:a.shortlist]
    for i in items: i["shortlisted"] = i in short; i["text_source"] = "summary"; i["text"] = i["summary"]
    if not a.no_text and short:
        with cf.ThreadPoolExecutor(8) as ex:
            for i, txt, src in ex.map(lambda i: extract(i, a.timeout), short):
                i["text_source"] = src
                if txt: i["text"] = txt
    out = {"run_at": now.isoformat(), "since_utc": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"), "feeds": len(feeds),
           "feeds_ok": sum(r["ok"] for r in report), "items": len(items), "shortlisted": len(short),
           "skipped": counts, "trend_top": sorted(TR), "elapsed_s": round(time.time() - t0, 1),
           "feed_report": report, "items_list": items}
    save(a.out, out)
    bad = [r for r in report if not r["ok"]]
    print(f"feeds={len(feeds)} ok={out['feeds_ok']} items={len(items)} shortlisted={len(short)} "
          f"text={sum(i['text_source'].startswith('trafilatura') for i in short)} skipped={counts} "
          f"elapsed={out['elapsed_s']}s -> {os.path.relpath(a.out, ROOT)}")
    for r in bad: print(f"  FAILED {r['feed']}: {r['status']}")
if __name__ == "__main__": main()
