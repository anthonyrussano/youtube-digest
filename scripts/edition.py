#!/usr/bin/env python3
"""Edition bookkeeping for multiple editions per day.

  edition.py start [--hours H]   open an edition: pick its id and time window, write state/current_edition.json
  edition.py show                print the current edition (id, window start)
  edition.py published           after a successful push: record cited video/X ids and feed/AINews source URLs, mark the
                                 edition's fetched videos (data/videos.json), feed items (data/feeds.json) and AINews
                                 issues/sources (data/ainews.json -> state/ainews_seen.json) as seen, and record the publish time.
                                 Selected videos without a usable transcript go to state/retry.json instead of
                                 seen.json (dropped after 3 failed editions or 7 days)

Edition id: the first edition of a PT day is YYYY-MM-DD; later ones are YYYY-MM-DD-HHMM (PT time at start).
Window start: state/last_edition.json "published_utc" (previous edition's publish time), else now-24h
(or now-H with --hours). State files are private (state/ is gitignored).
"""
import json, os, re, sys, argparse
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PT = ZoneInfo("America/Los_Angeles"); ST = f"{ROOT}/state"
CUR, LAST, PUB, SEEN = (f"{ST}/current_edition.json", f"{ST}/last_edition.json", f"{ST}/published.json",
                        f"{ST}/seen.json")
def load(p, d):
    try: return json.load(open(p))
    except Exception: return d
def save(p, o): os.makedirs(ST, exist_ok=True); json.dump(o, open(p, "w"), indent=1)
RETRY, RETRY_MAX, RETRY_DAYS = f"{ST}/retry.json", 3, 7
def update_retry(eid, cited):
    """Update state/retry.json after a published edition. Returns (retry dict, ids dropped from it)."""
    retry = load(RETRY, {}); dropped = set(); now_ = datetime.now(timezone.utc)
    rel = {v["id"]: v for v in load(f"{ROOT}/data/relevant.json", [])}
    for vid, v in rel.items():
        if v.get("transcript_status") == "ok" or vid in cited:
            retry.pop(vid, None); continue
        e = retry.get(vid) or {"attempts": 0, "first_edition": eid}
        if e.get("last_edition") != eid: e["attempts"] += 1
        e.update(last_edition=eid, status=v.get("transcript_status"), video=v)
        retry[vid] = e
    for vid in list(retry):
        e = retry[vid]; pu = e.get("video", {}).get("published_utc")
        try: old = now_ - datetime.fromisoformat(pu.replace("Z", "+00:00")) > timedelta(days=RETRY_DAYS)
        except Exception: old = False
        if vid in cited or e["attempts"] >= RETRY_MAX or old:
            retry.pop(vid); dropped.add(vid)
    save(RETRY, retry); return retry, dropped
def iso(dt): return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["start", "show", "published"])
ap.add_argument("--hours", type=float); a = ap.parse_args()
now = datetime.now(timezone.utc)
if a.cmd == "start":
    last = load(LAST, {}).get("published_utc")
    if a.hours: start = now - timedelta(hours=a.hours)
    elif last: start = datetime.fromisoformat(last.replace("Z", "+00:00"))
    else: start = now - timedelta(hours=24)
    start = max(start, now - timedelta(hours=72))  # never reach back more than 3 days
    pt = now.astimezone(PT); day = pt.strftime("%Y-%m-%d")
    eid = day if not os.path.exists(f"{ROOT}/reports/{day}.md") else f"{day}-{pt.strftime('%H%M')}"
    cur = {"id": eid, "start_utc": iso(start), "opened_utc": iso(now), "opened_pt": pt.strftime("%Y-%m-%d %H:%M:%S %z"),
           "hours": round((now - start).total_seconds() / 3600, 2)}
    save(CUR, cur)
    print(f"EDITION={eid}\nSTART={cur['start_utc']}\nHOURS={cur['hours']}")
elif a.cmd == "show":
    print(json.dumps(load(CUR, {}), indent=1))
else:
    cur = load(CUR, None)
    if not cur: sys.exit("no current edition")
    body = open(f"{ROOT}/articles/{cur['id']}.md").read()
    pub = load(PUB, {"videos": [], "x": []})
    pub["videos"] = sorted(set(pub["videos"]) | set(re.findall(r"youtube\.com/watch\?v=([\w-]{11})", body)))
    pub["x"] = sorted(set(pub["x"]) | set(re.findall(r"x\.com/\w+/status/(\d+)", body)))
    save(PUB, pub)
    # the only writer of seen.json: everything this edition fetched counts as considered once it is published
    vids = {v["id"] for v in load(f"{ROOT}/data/videos.json", {}).get("videos", [])}
    vids |= {v["id"] for v in load(f"{ROOT}/data/relevant.json", []) if v.get("transcript_status") == "ok"}
    # retry list (state/retry.json): selected videos that never got a usable transcript (caption 429, Whisper
    # failed/skipped) are NOT marked seen; they are retried by the next editions' transcripts/whisper runs and
    # dropped (then marked seen) after RETRY_MAX failed editions or once RETRY_DAYS old
    retry, dropped = update_retry(cur["id"], set(pub["videos"]))
    vids = (vids - set(retry)) | dropped
    seen = set(load(SEEN, [])); added = len(vids - seen)
    json.dump(sorted(seen | vids | set(pub["videos"])), open(SEEN, "w"))
    # feeds: the only writer of feeds_seen.json; every item this edition fetched (data/feeds.json) counts as
    # considered, cited article URLs go to published.json "articles" (canonical: utm_* and fragment stripped)
    sys.path.insert(0, f"{ROOT}/scripts"); from feeds_canon import canon
    fitems = load(f"{ROOT}/data/feeds.json", {}).get("items_list", [])
    furls = {canon(i["url"]) for i in fitems}
    cited_urls = {canon(u) for u in re.findall(r"\]\((https?://[^)\s]+)\)", body)}
    # AINews (data/ainews.json): every story's source URL and the issue Message-ID count as considered
    # (state/ainews_seen.json); cited non-X source URLs join published.json "articles" like feed articles
    an = load(f"{ROOT}/data/ainews.json", {}); aitems = an.get("items_list", [])
    aurls = {canon(s["url"]) for i in aitems for s in i.get("sources", [])}
    pub["articles"] = sorted(set(pub.get("articles", [])) | (cited_urls & (furls | aurls))); save(PUB, pub)
    if an.get("ok"):
        aseen = load(f"{ST}/ainews_seen.json", {"issues": [], "urls": []})
        aseen["issues"] = sorted(set(aseen.get("issues", [])) | {r["message_id"] for r in an.get("issues", [])})
        aseen["urls"] = sorted(set(aseen.get("urls", [])) | aurls); save(f"{ST}/ainews_seen.json", aseen)
    fseen = set(load(f"{ST}/feeds_seen.json", [])); fadded = len(furls - fseen)
    json.dump(sorted(fseen | furls), open(f"{ST}/feeds_seen.json", "w"))
    save(LAST, {"id": cur["id"], "published_utc": iso(now), "window_start_utc": cur["start_utc"]})
    os.remove(CUR); print(f"recorded edition {cur['id']} published at {iso(now)}; {added} videos and {fadded} feed items marked seen; "
                          f"{len(retry)} videos queued for retry (state/retry.json), {len(dropped)} dropped")
