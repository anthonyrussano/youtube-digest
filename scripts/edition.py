#!/usr/bin/env python3
"""Edition bookkeeping for multiple editions per day.

  edition.py start [--hours H]   open an edition: pick its id and time window, write state/current_edition.json
  edition.py show                print the current edition (id, window start)
  edition.py published           after a successful push: record cited video/X ids, mark the edition's fetched
                                 videos (data/videos.json) as seen, and record the publish time

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
    seen = set(load(SEEN, [])); added = len(vids - seen)
    json.dump(sorted(seen | vids | set(pub["videos"])), open(SEEN, "w"))
    save(LAST, {"id": cur["id"], "published_utc": iso(now), "window_start_utc": cur["start_utc"]})
    os.remove(CUR); print(f"recorded edition {cur['id']} published at {iso(now)}; {added} videos marked seen")
