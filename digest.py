#!/usr/bin/env python3
"""YouTube digest: yt-dlp channel listing -> relevance prefilter -> exact dates -> captions. See README.md."""
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

YTDLP = f"{ROOT}/.venv/bin/yt-dlp"
LIST_N = 15        # newest uploads listed per channel (flat, /videos tab: no Shorts)
APPROX_SLACK = timedelta(hours=36)  # flat dates are day-level ("2 days ago"); widen before exact check

def kw(v):
    text = f"{v['title']} {(v.get('description') or '')[:400]} {v['channel']}".lower()
    return bool(re.search(AI, text)), bool(re.search(DEVOPS, text))

def fetch_rss(ch):
    """Legacy: YouTube channel RSS (feeds/videos.xml) has 404'd globally since Oct 2026. Only with --rss."""
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['Channel Id']}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 youtube-digest"})
        body = urllib.request.urlopen(req, timeout=20).read()
    except Exception as e:
        return None, str(e)
    out = []
    for e in ET.fromstring(body).findall("a:entry", NS):
        pub = datetime.fromisoformat(e.find("a:published", NS).text)
        vid = e.find("yt:videoId", NS).text
        desc = e.find("media:group/media:description", NS)
        out.append({"id": vid, "title": e.find("a:title", NS).text, "url": f"https://www.youtube.com/watch?v={vid}",
            "channel": ch["Channel Title"], "published_utc": pub.isoformat(), "timestamp": pub.timestamp(),
            "description": (desc.text or "")[:1500] if desc is not None else "", "duration_s": None,
            "is_short": "/shorts/" in e.find("a:link", NS).get("href"), "date_exact": True, "source": "rss"})
    return out, None

def list_channel(ch):
    """Flat-list the channel's newest uploads (/videos tab) with approximate dates. Returns (ch, entries, err)."""
    try:
        r = subprocess.run([YTDLP, "--flat-playlist", "--playlist-end", str(LIST_N), "--extractor-args",
            "youtubetab:approximate_date", "--no-warnings", "-J", f"https://www.youtube.com/channel/{ch['Channel Id']}/videos"],
            capture_output=True, text=True, timeout=90)
        d = json.loads(r.stdout) if r.stdout.strip() else None
        if not d: return ch, None, (r.stderr.strip().splitlines() or ["no output"])[-1][:300]
    except Exception as e:
        return ch, None, f"{type(e).__name__}: {e}"[:300]
    out = []
    for e in d.get("entries") or []:
        if not e.get("id"): continue
        ts = e.get("timestamp") or e.get("release_timestamp")
        out.append({"id": e["id"], "title": e.get("title"), "url": f"https://www.youtube.com/watch?v={e['id']}",
            "channel": ch["Channel Title"], "timestamp": ts, "description": (e.get("description") or "")[:1500],
            "duration_s": e.get("duration"), "is_short": False, "date_exact": False, "source": "yt-dlp-flat"})
    return ch, out, None

def full_lookup(v):
    """Full (non-flat) metadata for one video: exact timestamp, full description, duration."""
    try:
        r = subprocess.run([YTDLP, "-J", "--skip-download", "--no-playlist", "--no-warnings", v["url"]],
            capture_output=True, text=True, timeout=120)
        d = json.loads(r.stdout) if r.stdout.strip() else None
        if not d: v["lookup_error"] = (r.stderr.strip().splitlines() or ["no output"])[-1][:300]; return v
    except Exception as e:
        v["lookup_error"] = f"{type(e).__name__}: {e}"[:300]; return v
    ts = d.get("timestamp") or d.get("release_timestamp")
    if not ts and d.get("upload_date"):
        ts = datetime.strptime(d["upload_date"], "%Y%m%d").replace(tzinfo=timezone.utc).timestamp()
    else:
        v["date_exact"] = bool(ts)
    if ts: v["timestamp"] = ts
    v["upload_date"] = d.get("upload_date")
    v["description"] = (d.get("description") or v["description"] or "")[:1500]
    v["duration_s"] = d.get("duration") or v["duration_s"]
    v["is_short"] = v["is_short"] or "/shorts/" in (d.get("webpage_url") or "") or (d.get("duration") or 999) <= 60 and d.get("aspect_ratio", 1.7) < 1
    v["live_status"] = d.get("live_status")
    return v

def stage_fetch(hours, workers, since=None, use_rss=False, out_path=None):
    t0 = time.time()
    chans = list(csv.DictReader(open(f"{ROOT}/subscriptions.csv")))
    seen = set(load_json(f"{ROOT}/state/seen.json", []))
    cutoff = datetime.fromisoformat(since.replace('Z', '+00:00')) if since else datetime.now(timezone.utc) - timedelta(hours=hours)
    seen |= set(load_json(f"{ROOT}/state/published.json", {}).get("videos", []))
    errors, listed = [], []
    # 1. list channels (flat yt-dlp; optional legacy RSS first)
    def one(ch):
        if use_rss:
            vids, err = fetch_rss(ch)
            if vids is not None: return ch, vids, None
            c, vids, err2 = list_channel(ch)
            return c, vids, (None if vids is not None else f"rss: {err}; yt-dlp: {err2}")
        return list_channel(ch)
    with ThreadPoolExecutor(workers) as ex:
        for ch, vids, err in ex.map(one, chans):
            if vids is None: errors.append({"channel": ch["Channel Title"], "error": err}); continue
            listed.extend(vids)
    # 2. keep new videos (not in seen.json, which only grows when an edition is published) whose approximate date could fall in the window
    dedup = {}
    for v in listed:
        if v["id"] in seen or v["id"] in dedup: continue
        ts = v.get("timestamp")
        if ts is None or datetime.fromtimestamp(ts, timezone.utc) >= cutoff - (timedelta(0) if v["date_exact"] else APPROX_SLACK):
            dedup[v["id"]] = v
    new = list(dedup.values())
    for v in new: v["kw_ai"], v["kw_devops"] = kw(v)
    # 3. exact dates via full lookup, only for keyword matches (2 at a time to stay polite)
    look = [v for v in new if (v["kw_ai"] or v["kw_devops"]) and not v["date_exact"]]
    with ThreadPoolExecutor(min(2, workers)) as ex: list(ex.map(full_lookup, look))
    vids = []
    for v in new:
        ts = v.get("timestamp")
        if ts is None: continue
        pub = datetime.fromtimestamp(ts, timezone.utc)
        if pub < cutoff: continue  # exact dates: strict; approx (non-keyword or failed lookup): day-level estimate
        v["published_utc"] = pub.isoformat()
        v["published_pt"] = pub.astimezone(PT).strftime("%Y-%m-%d %H:%M PT") if v["date_exact"] else pub.astimezone(PT).strftime("%Y-%m-%d") + " (approx)"
        v["kw_ai"], v["kw_devops"] = kw(v)
        v["seen"] = False
        v["candidate"] = (v["kw_ai"] or v["kw_devops"]) and not v["is_short"] and v.get("live_status") not in ("is_upcoming", "is_live")
        vids.append(v)
    vids.sort(key=lambda v: v["published_utc"], reverse=True)
    out = {"run_at": datetime.now(PT).isoformat(), "hours": hours, "since_utc": cutoff.isoformat(), "channels": len(chans),
           "channels_ok": len(chans) - len(errors), "source": "rss+yt-dlp" if use_rss else "yt-dlp",
           "listed": len(listed), "new_in_approx_window": len(new), "full_lookups": len(look),
           "lookup_errors": [{"id": v["id"], "error": v["lookup_error"]} for v in look if v.get("lookup_error")],
           "runtime_s": round(time.time() - t0, 1), "videos": vids, "errors": errors}
    json.dump(out, open(out_path or f"{ROOT}/data/videos.json", "w"), indent=1)
    print(f"channels={len(chans)} ok={out['channels_ok']} failed={len(errors)} listed={len(listed)} new={len(new)} "
          f"lookups={len(look)} lookup_errors={len(out['lookup_errors'])} videos={len(vids)} "
          f"exact={sum(v['date_exact'] for v in vids)} candidates={sum(v['candidate'] for v in vids)} "
          f"runtime={out['runtime_s']}s -> {out_path or 'data/videos.json'}")

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
    # state/seen.json is only written by `edition.py published`, so a skipped edition leaves its videos eligible
    print(f"relevant={len(done)} transcripts={sum(v['transcript_status']=='ok' for v in done)} "
          f"needs_whisper={sum(v['transcript_status']!='ok' for v in done)}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["fetch", "rss", "transcripts", "all"], nargs="?", default="all")
    ap.add_argument("--hours", type=float, default=24)
    ap.add_argument("--since", help="ISO UTC window start; overrides --hours (default: state/current_edition.json start)")
    ap.add_argument("--workers", type=int, default=4, help="parallel channel listings (full lookups use at most 2)")
    ap.add_argument("--rss", action="store_true", help="try legacy channel RSS first (404s globally since Oct 2026)")
    ap.add_argument("--out", help="write the video list here instead of data/videos.json (dry run; state is never written by fetch)")
    a = ap.parse_args()
    since = a.since or (None if "--hours" in sys.argv else load_json(f"{ROOT}/state/current_edition.json", {}).get("start_utc"))
    if a.stage in ("fetch", "rss", "all"): stage_fetch(a.hours, a.workers, since, a.rss, a.out)
    if a.stage in ("transcripts", "all"): stage_transcripts(1)
