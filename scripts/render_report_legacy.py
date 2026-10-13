#!/usr/bin/env python3
"""Render reports/YYYY-MM-DD.md from data/relevant.json + a summaries module (id -> (bullets, [(sec,label)])) and THEMES."""
import importlib.util, json, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("s", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
date = sys.argv[2] if len(sys.argv) > 2 else datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
rel = json.load(open(f"{ROOT}/data/relevant.json")); allv = json.load(open(f"{ROOT}/data/videos.json"))
def dur(s):
    if not s: return "unknown"
    h, r = divmod(int(s), 3600); mi, se = divmod(r, 60)
    return f"{h}:{mi:02d}:{se:02d}" if h else f"{mi}:{se:02d}"
def ts(s): h, r = divmod(s, 3600); mi, se = divmod(r, 60); return f"{h}:{mi:02d}:{se:02d}" if h else f"{mi}:{se:02d}"
ok = [v for v in rel if v["transcript_status"] == "ok"]
L = [f"# YouTube AI & DevOps digest — {date}", "",
     f"Window: last {allv['hours']} h · {allv['channels']} channels scanned · {len(allv['videos'])} videos found "
     f"({sum(v['is_short'] for v in allv['videos'])} Shorts skipped) · {len(rel)} relevant · {len(ok)} with transcripts.", "",
     "Dates marked *(approx)* came from the yt-dlp fallback, used when a channel's RSS feed returned 404/500; YouTube only gives day-level dates there.", "",
     "## Top themes", ""] + [f"{i}. {t}" for i, t in enumerate(m.THEMES, 1)] + [""]
pending = []
for cat in ("AI", "DevOps"):
    L += [f"## {cat}", ""]
    for v in sorted([v for v in rel if v["category"] == cat], key=lambda v: v["published_utc"], reverse=True):
        if v["transcript_status"] != "ok": pending.append(v); continue
        L += [f"### [{v['title']}]({v['url']})", f"*{v['channel']}* · {v['published_pt']} · length {dur(v.get('duration_s'))}", ""]
        bullets, marks = m.S.get(v["id"], ([], []))
        if not bullets:
            L += ["- Captions exist but contain only music/no speech, so there's nothing to summarize (no spoken transcript).", ""]; continue
        L += [f"- {b}" for b in bullets] + ["", "Key moments: " + " · ".join(f"[{ts(s)} {lab}]({v['url']}&t={s}s)" for s, lab in marks), ""]
L += ["## Videos without a transcript", "",
      "No summary for these; I won't write one without a transcript. **Rate limited** means YouTube returned HTTP 429 for the caption request. It does not mean the video has no captions, and the next run retries them automatically. **Needs Whisper** means yt-dlp found no English captions.", ""]
for v in pending:
    st = "needs Whisper" if v["transcript_status"] == "needs Whisper" else "rate limited (429), retry pending"
    L.append(f"- [{v['title']}]({v['url']}) — *{v['channel']}* · {v['category']} · {v['published_pt']} · {dur(v.get('duration_s'))} · **{st}**")
os.makedirs(f"{ROOT}/reports", exist_ok=True)
open(f"{ROOT}/reports/{date}.md", "w").write("\n".join(L) + "\n"); print(f"{ROOT}/reports/{date}.md")
