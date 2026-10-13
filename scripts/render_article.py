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
date = sys.argv[2] if len(sys.argv) > 2 else datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
src = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/articles/{date}.md"
text = open(src).read()
m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
if not m: sys.exit("article needs front matter with title: and dek:")
fm = dict(re.findall(r'^(\w+):\s*"?(.*?)"?\s*$', m.group(1), re.M)); body = m.group(2).strip()
for k in ("title", "dek"):
    if not fm.get(k): sys.exit(f"front matter missing {k}")
rel = json.load(open(f"{ROOT}/data/relevant.json"))
cited = set(re.findall(r"youtube\.com/watch\?v=([\w-]{11})", body))
def has_speech(v):
    p = v.get("transcript_file")
    return v["transcript_status"].startswith("ok") and p and os.path.exists(f"{ROOT}/{p}") and \
        len(re.sub(r"\[\d+\]|\[music\]|\[Music\]|\s", "", open(f"{ROOT}/{p}").read())) > 200
missing = [v for v in rel if has_speech(v) and v["id"] not in cited]
if missing:
    sys.exit("Not cited in article (every transcribed video must be cited):\n" + "\n".join(f"  {v['id']} {v['title']}" for v in missing))
radar = [v for v in rel if v["id"] not in cited]
if radar and "Also on the radar" not in body:
    def esc(t): return t.replace("[", "(").replace("]", ")").replace("|", "–")
    links = "; ".join(f"[{esc(v['title'])}]({v['url']}) ({v['channel']})" for v in radar)
    body += ("\n\n*Also on the radar:* these also appeared this cycle, but there was no transcript to report from yet "
             "(captions rate-limited by YouTube, no English captions, or no speech), so they aren't summarized here: " + links + ".")
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
out = f"---\nlayout: report\ntitle: {q(fm['title'])}\ndek: {q(fm['dek'])}\ndate: {date}\n---\n\n{body}\n"
os.makedirs(f"{ROOT}/reports", exist_ok=True)
open(f"{ROOT}/reports/{date}.md", "w").write(out); print(f"{ROOT}/reports/{date}.md  ({len(cited)} videos cited, {len(radar)} on the radar)")
