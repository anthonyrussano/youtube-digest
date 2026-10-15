#!/usr/bin/env python3
"""Daily X keyword trends: today's post volume vs the 7-day average for each category in config/x_trends.txt.

X reads happen through the routine's MCP tool, so this script plans and computes; it never calls X itself.
  x_trends.py plan      exit 0 + "CACHED" if data/x_trends.json is from today (PT): spend no reads.
                        Otherwise print one JSON line per category with the get_posts_counts_recent args
                        (granularity=day, start_time = 7 days ago); save each result to data/x_counts/<name>.json.
  x_trends.py compute   read data/x_counts/*.json -> data/x_trends.json (ratio = last full-ish day / mean of prior days)
  x_trends.py show      print the ranking and the top categories
Library use: load_trends() -> dict, categories() -> [(name, query, regex)], tag(text) -> [category names].
"""
import glob, json, os, re, sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, CNT = f"{ROOT}/data/x_trends.json", f"{ROOT}/data/x_counts"
TOP_N = 5

def today_pt(): return datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()

def categories():
    cats = []
    for ln in open(f"{ROOT}/config/x_trends.txt", encoding="utf-8"):
        if not ln.strip() or ln.startswith("#"): continue
        name, q, rx = [x.strip() for x in ln.split("|", 2)]
        cats.append((name, q, re.compile(rx, re.I)))
    return cats

def load_trends():
    try: return json.load(open(OUT))
    except Exception: return {}

def tag(text, cats=None):
    return [n for n, _, rx in (cats or categories()) if rx.search(text or "")]

def plan():
    t = load_trends()
    if t.get("date") == today_pt():
        print(f"CACHED trends for {t['date']} (top: {', '.join(t.get('top', []))}); spend no X reads"); return
    os.makedirs(CNT, exist_ok=True)
    for f in glob.glob(f"{CNT}/*.json"): os.remove(f)
    start = (datetime.now(timezone.utc) - timedelta(days=7) + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"# {len(categories())} reads; pace <= 25/min. Save each result to data/x_counts/<name>.json")
    for n, q, _ in categories():
        print(json.dumps({"name": n, "args": {"query": q, "granularity": "day", "start_time": start}}))

def compute():
    rows = []
    for n, q, _ in categories():
        f = f"{CNT}/{n}.json"
        if not os.path.exists(f): print("missing", f); continue
        t = open(f, encoding="utf-8").read()
        try: d = json.loads(t[t.index("{"):t.rindex("}") + 1])
        except ValueError: print("unparsable", f); continue
        b = sorted(d.get("data", []), key=lambda x: x["start"])
        # the last bucket is a partial day; scale it to 24 h by elapsed fraction
        if len(b) < 3: continue
        last = b[-1]; s = datetime.fromisoformat(last["start"].replace("Z", "+00:00"))
        e = min(datetime.fromisoformat(last["end"].replace("Z", "+00:00")), datetime.now(timezone.utc))
        frac = max((e - s).total_seconds() / 86400, 0.05)
        # "today" = last 24 h: previous full bucket if the partial is tiny, else the scaled partial
        today = last["tweet_count"] / frac if frac >= 0.25 else b[-2]["tweet_count"]
        prior = [x["tweet_count"] for x in (b[1:-1] if frac >= 0.25 else b[1:-2])] or [1]
        avg = sum(prior) / len(prior)
        rows.append({"name": n, "today": round(today), "avg7": round(avg), "ratio": round(today / max(avg, 1), 2)})
    # need real volume to count as a trend (avoid 3 -> 9 posts noise)
    rows.sort(key=lambda r: -r["ratio"])
    top = [r["name"] for r in rows if r["avg7"] >= 200 and r["ratio"] >= 1.1][:TOP_N]
    out = {"date": today_pt(), "computed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "top": top, "categories": rows}
    json.dump(out, open(OUT, "w"), indent=1); show(out)

def show(t=None):
    t = t or load_trends()
    if not t: print("no data/x_trends.json; run ./run.sh trends"); return
    print(f"trends {t['date']}: top = {', '.join(t['top']) or '(none above 1.1x)'}")
    for r in t["categories"]: print(f"  {r['ratio']:>5}x  today~{r['today']:>7}  avg7~{r['avg7']:>7}  {r['name']}")

if __name__ == "__main__":
    {"plan": plan, "compute": compute, "show": show}.get((sys.argv[1:] or ["show"])[0], show)()
