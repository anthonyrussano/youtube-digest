#!/usr/bin/env python3
"""YouTube digest: RSS fetch -> relevance prefilter -> captions. See README.md."""
import argparse, csv, json, os, re, subprocess, sys, time, urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
ROOT = os.path.dirname(os.path.abspath(__file__))
PT = ZoneInfo("America/Los_Angeles")
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "media": "http://search.yahoo.com/mrss/"}
AI = r"\b(ai|a\.i\.|llms?|gpt\w*|chatgpt|claude|gemini|grok|llama|ollama|openai|anthropic|agents?|agentic|machine learning|ml|deep learning|neural|transformer|copilot|cursor|mcp|rag|diffusion|stable diffusion|comfyui|whisper|vibe cod\w*|prompt\w*|models?|inference|gpu|nvidia|hugging ?face|lora|fine.?tun\w*|codex|deepseek|qwen|mistral)\b"
DEVOPS = r"\b(devops|kubernetes|k8s|k3s|docker|containers?|podman|proxmox|homelab|home lab|self.?host\w*|linux|ubuntu|debian|arch|nixos|terraform|ansible|ci/?cd|github actions|gitlab|jenkins|argo\w*|helm|networking|network|vlan|router|firewall|pfsense|opnsense|wireguard|tailscale|vpn|nas|truenas|unraid|zfs|server|servers|rack|cloud|aws|azure|gcp|security|cyber\w*|hacking|exploit|vulnerabilit\w*|cve|nginx|traefik|dns|ssh|bash|observability|grafana|prometheus|sre|backup)\b"

def load_json(p, d):
    try: return json.load(open(p))
    except Exception: return d

def fetch(ch):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['Channel Id']}"
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 youtube-digest"})
            return ch, urllib.request.urlopen(req, timeout=20).read(), None
        except Exception as e:
            err = str(e); time.sleep(2 * (attempt + 1))
    return ch, None, err

def fallback(ch, cutoff, seen):
    """RSS endpoint is flaky (404/500); list the channel's /videos tab via yt-dlp instead (no Shorts there)."""
    try:
        r = subprocess.run([f"{ROOT}/.venv/bin/yt-dlp", "--flat-playlist", "--playlist-end", "15", "--extractor-args",
            "youtubetab:approximate_date", "-J", f"https://www.youtube.com/channel/{ch['Channel Id']}/videos"],
            capture_output=True, text=True, timeout=90)
        d = json.loads(r.stdout) or {}
    except Exception:
        return None
    out = []
    for e in d.get("entries") or []:
        if not e.get("timestamp"): continue
        pub = datetime.fromtimestamp(e["timestamp"], timezone.utc)
        if pub < cutoff: continue
        out.append({"id": e["id"], "title": e.get("title"), "url": f"https://www.youtube.com/watch?v={e['id']}",
            "channel": ch["Channel Title"], "published_utc": pub.isoformat(),
            "published_pt": pub.astimezone(PT).strftime("%Y-%m-%d") + " (approx)",
            "description": (e.get("description") or "")[:1500], "duration_s": e.get("duration"),
            "is_short": False, "seen": e["id"] in seen, "source": "yt-dlp-fallback"})
    return out

def stage_rss(hours, workers, since=None):
    chans = list(csv.DictReader(open(f"{ROOT}/subscriptions.csv")))
    seen = set(load_json(f"{ROOT}/state/seen.json", []))
    cutoff = datetime.fromisoformat(since.replace('Z', '+00:00')) if since else datetime.now(timezone.utc) - timedelta(hours=hours)
    seen |= set(load_json(f"{ROOT}/state/published.json", {}).get("videos", []))
    # yt-dlp fallback dates are day-level approximations, so give it at least 24 h; seen.json prevents repeats
    fb_cutoff = min(cutoff, datetime.now(timezone.utc) - timedelta(hours=24))
    vids, errors = [], []
    with ThreadPoolExecutor(workers) as ex:
        for ch, body, err in ex.map(fetch, chans):
            if err:
                fb = fallback(ch, fb_cutoff, seen)
                if fb is None: errors.append({"channel": ch["Channel Title"], "error": err + "; yt-dlp fallback failed"})
                else: errors.append({"channel": ch["Channel Title"], "error": err + "; recovered via yt-dlp fallback (approx dates)", "recovered": True}); vids.extend(fb)
                continue
            root = ET.fromstring(body)
            for e in root.findall("a:entry", NS):
                pub = datetime.fromisoformat(e.find("a:published", NS).text)
                if pub < cutoff: continue
                vid = e.find("yt:videoId", NS).text
                link = e.find("a:link", NS).get("href")
                desc = e.find("media:group/media:description", NS)
                vids.append({"id": vid, "title": e.find("a:title", NS).text, "url": f"https://www.youtube.com/watch?v={vid}",
                    "channel": ch["Channel Title"], "published_utc": pub.isoformat(),
                    "published_pt": pub.astimezone(PT).strftime("%Y-%m-%d %H:%M PT"),
                    "description": (desc.text or "")[:1500] if desc is not None else "",
                    "is_short": "/shorts/" in link, "seen": vid in seen})
    for v in vids:
        text = f"{v['title']} {v['description'][:400]} {v['channel']}".lower()
        v["kw_ai"], v["kw_devops"] = bool(re.search(AI, text)), bool(re.search(DEVOPS, text))
        v["candidate"] = (v["kw_ai"] or v["kw_devops"]) and not v["is_short"] and not v["seen"]
    out = {"run_at": datetime.now(PT).isoformat(), "hours": hours, "since_utc": cutoff.isoformat(), "channels": len(chans),
           "videos": vids, "errors": errors}
    json.dump(out, open(f"{ROOT}/data/videos.json", "w"), indent=1)
    print(f"channels={len(chans)} videos={len(vids)} shorts={sum(v['is_short'] for v in vids)} "
          f"candidates={sum(v['candidate'] for v in vids)} rss_errors={len(errors)}")

def vtt_to_segments(path):
    segs, recent = [], []
    for block in open(path, encoding="utf-8").read().split("\n\n"):
        m = re.search(r"(\d+):(\d+):(\d+)\.\d+ -->", block)
        if not m: continue
        t = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
        lines = [re.sub(r"<[^>]+>", "", l).strip() for l in block.split("\n") if "-->" not in l]
        for l in lines:
            if l and l not in recent: segs.append((t, l)); recent = (recent + [l])[-4:]
    return segs

def get_transcript(v):
    d = f"{ROOT}/data/subs"; os.makedirs(d, exist_ok=True)
    cmd = [f"{ROOT}/.venv/bin/yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
           "--sub-langs", "en", "--sub-format", "vtt", "--print-to-file", "%(duration)s", f"{d}/{v['id']}.dur",
           "-o", f"{d}/%(id)s.%(ext)s", "--sleep-requests", "2", "--sleep-subtitles", "15", v["url"]]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    files = sorted(f for f in os.listdir(d) if f.startswith(v["id"]) and f.endswith(".vtt"))
    try: v["duration_s"] = int(open(f"{d}/{v['id']}.dur").read().split()[0])
    except Exception: v["duration_s"] = v.get("duration_s")
    if not files:
        v["transcript_status"] = "rate limited (retry later)" if "429" in r.stderr else "needs Whisper"; v["yt_dlp_error"] = r.stderr[-400:]; return v
    pick = next((f for f in files if ".en." in f and "orig" not in f), files[0])
    segs = vtt_to_segments(f"{d}/{pick}")
    with open(f"{ROOT}/data/transcripts/{v['id']}.txt", "w") as fh:
        for t, l in segs: fh.write(f"[{t}] {l}\n")
    v["transcript_status"] = "ok"; v["transcript_file"] = f"data/transcripts/{v['id']}.txt"
    return v

def stage_transcripts(workers):
    os.makedirs(f"{ROOT}/data/transcripts", exist_ok=True)
    data = load_json(f"{ROOT}/data/videos.json", {})
    sel = load_json(f"{ROOT}/data/selected.json", None)  # optional judged list {id: "AI"|"DevOps"}
    todo = [v for v in data["videos"] if (v["id"] in sel if sel is not None else v["candidate"])]
    for v in todo:
        if sel is not None: v["category"] = sel[v["id"]]
    prev = {v["id"]: v for v in load_json(f"{ROOT}/data/relevant.json", [])}
    ids = {v["id"] for v in todo}
    # carry forward videos whose captions were rate limited on an earlier run
    todo += [v for v in prev.values() if v["id"] not in ids and v.get("transcript_status", "").startswith("rate limited")]
    published = set(load_json(f"{ROOT}/state/published.json", {}).get("videos", []))
    todo = [v for v in todo if v["id"] not in published]
    run = [v for v in todo if prev.get(v["id"], {}).get("transcript_status") != "ok"]
    with ThreadPoolExecutor(workers) as ex: got = {v["id"]: v for v in ex.map(get_transcript, run)}
    done = [got.get(v["id"]) or prev[v["id"]] for v in todo]
    json.dump(done, open(f"{ROOT}/data/relevant.json", "w"), indent=1)
    seen = set(load_json(f"{ROOT}/state/seen.json", [])) | {v["id"] for v in data["videos"]}
    json.dump(sorted(seen), open(f"{ROOT}/state/seen.json", "w"))
    print(f"relevant={len(done)} transcripts={sum(v['transcript_status']=='ok' for v in done)} "
          f"needs_whisper={sum(v['transcript_status']!='ok' for v in done)}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["rss", "transcripts", "all"], nargs="?", default="all")
    ap.add_argument("--hours", type=float, default=24)
    ap.add_argument("--since", help="ISO UTC window start; overrides --hours (default: state/current_edition.json start)")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    since = a.since or (None if "--hours" in sys.argv else load_json(f"{ROOT}/state/current_edition.json", {}).get("start_utc"))
    if a.stage in ("rss", "all"): stage_rss(a.hours, a.workers, since)
    if a.stage in ("transcripts", "all"): stage_transcripts(1)
