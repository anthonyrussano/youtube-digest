#!/usr/bin/env python3
"""Render a longform news article into a Jekyll page.

Usage: render_article.py [articles/YYYY-MM-DD.md] [YYYY-MM-DD]
The input is Markdown with front matter (title, dek) and the article body, written per STYLE.md.
This script:
  * checks that every relevant video with a usable transcript is cited at least once (exit 1 if not),
  * appends an "Also on the radar" paragraph linking every relevant video not cited in the body
    (videos still rate limited, needing Whisper, or with no speech),
  * writes reports/YYYY-MM-DD.md with front matter for the site (layout: report).
"""
import json, os, re, sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PT = ZoneInfo("America/Los_Angeles")
def _cur():
    try: return json.load(open(f"{ROOT}/state/current_edition.json"))
    except Exception: return {}
# edition id: YYYY-MM-DD (first edition of the day) or YYYY-MM-DD-HHMM (later editions)
date = sys.argv[2] if len(sys.argv) > 2 else (_cur().get("id") or datetime.now(PT).strftime("%Y-%m-%d"))
src = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/articles/{date}.md"
em = re.match(r"^(\d{4}-\d{2}-\d{2})(?:-(\d{2})(\d{2}))?$", date)
if not em: sys.exit(f"bad edition id {date}")
MIN_X_ONLY = 5
text = open(src).read()
m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
if not m: sys.exit("article needs front matter with title: and dek:")
fm = dict(re.findall(r'^(\w+):\s*"?(.*?)"?\s*$', m.group(1), re.M)); body = m.group(2).strip()
for k in ("title", "dek"):
    if not fm.get(k): sys.exit(f"front matter missing {k}")
try: rel = json.load(open(f"{ROOT}/data/relevant.json"))
except Exception: rel = []
try: published = json.load(open(f"{ROOT}/state/published.json"))
except Exception: published = {"videos": [], "x": []}
NEW = not os.path.exists(f"{ROOT}/reports/{date}.md")
if NEW: rel = [v for v in rel if v["id"] not in set(published.get("videos", []))]  # new edition: only unpublished videos
cited = set(re.findall(r"youtube\.com/watch\?v=([\w-]{11})", body))
cited_x = set(re.findall(r"x\.com/\w+/status/(\d+)", body))
if NEW:  # re-rendering an already published edition is allowed
    reused = (cited & set(published.get("videos", []))) | (cited_x & set(published.get("x", [])))
    if reused: sys.exit("Article reuses stories from an earlier edition: " + ", ".join(sorted(reused)))
def has_speech(v):
    p = v.get("transcript_file")
    return v["transcript_status"].startswith("ok") and p and os.path.exists(f"{ROOT}/{p}") and \
        len(re.sub(r"\[\d+\]|\[music\]|\[Music\]|\s", "", open(f"{ROOT}/{p}").read())) > 200
missing = [v for v in rel if has_speech(v) and v["id"] not in cited]
if missing:
    sys.exit("Not cited in article (every transcribed video must be cited):\n" + "\n".join(f"  {v['id']} {v['title']}" for v in missing))
if not any(has_speech(v) for v in rel) and len(cited_x) < MIN_X_ONLY:
    sys.exit(f"SKIP: no new transcribed videos and only {len(cited_x)} X items (need {MIN_X_ONLY}); do not publish this edition")
radar = [v for v in rel if v["id"] not in cited]
if radar and "Also on the radar" not in body:
    def esc(t): return t.replace("[", "(").replace("]", ")").replace("|", "–")
    links = "; ".join(f"[{esc(v['title'])}]({v['url']}) ({v['channel']})" for v in radar)
    body += ("\n\n*Also on the radar:* these also appeared this cycle, but there was no transcript to report from yet "
             "(captions rate-limited by YouTube, no English captions, or no speech), so they aren't summarized here: " + links + ".")
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
if em.group(2): stamp = f"{em.group(1)} {em.group(2)}:{em.group(3)}:00"
else:
    c = _cur(); t = (c.get("opened_pt") or "")[11:16] if c.get("id") == date else ""
    if os.path.exists(f"{ROOT}/reports/{date}.md"):
        old = re.search(r"^date: (.+)$", open(f"{ROOT}/reports/{date}.md").read(), re.M); stamp = old.group(1).split(" -")[0].split(" +")[0] if old else f"{date} 06:00:00"
        if len(stamp) == 10: stamp += " 06:00:00"
    else: stamp = f"{date} {t or '06:00'}:00"
_h, _m = int(stamp[11:13]), stamp[14:16]
edition = f"{_h % 12 or 12}:{_m} {'AM' if _h < 12 else 'PM'} PT edition"
off = datetime.fromisoformat(stamp).replace(tzinfo=PT).strftime("%z")
out = f"---\nlayout: report\ntitle: {q(fm['title'])}\ndek: {q(fm['dek'])}\ndate: {stamp} {off}\nedition: {q(edition)}\n---\n\n{body}\n"
os.makedirs(f"{ROOT}/reports", exist_ok=True)
open(f"{ROOT}/reports/{date}.md", "w").write(out); print(f"{ROOT}/reports/{date}.md  ({len(cited)} videos cited, {len(cited_x)} X posts cited, {len(radar)} on the radar)")
