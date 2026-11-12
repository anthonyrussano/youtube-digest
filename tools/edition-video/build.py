#!/usr/bin/env python3
"""Build a silent, voiceover-ready 1080p30 edition video from script.md.

Runs ON the render host (never on the box). Usage:
    python3 build.py WORKDIR          # WORKDIR holds script.md; outputs land there too
Env: YTDLP (default ~/grokbot-whisper/bin/yt-dlp), CHROMIUM (default chromium), JOBS (default 6)

script.md format (see tools/edition-video/README.md):
    Edition: <github pages url>
    ## NN Title
    Narration: one paragraph
    Visuals:
    - yt <url> @<seconds> | <label>
    - page <url> | <label> [| fallback title]
    - edition | <label>
    - card <title> | <subtitle>
Outputs: final.mp4, teleprompter.md, timeline.json, report.json (sources, failures, substitutions).
"""
import hashlib, json, math, os, re, shutil, subprocess, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont, ImageStat

W, H, FPS = 1920, 1080, 30
WPS = 2.5            # narration words per second
PAD = 0.7            # breath after each segment, seconds
SHOT = 3.0           # target shot length (2-4 s cuts)
YT_BEFORE, YT_AFTER = 1, 14
YTDLP = os.path.expanduser(os.environ.get("YTDLP", "~/grokbot-whisper/bin/yt-dlp"))
CHROMIUM = os.environ.get("CHROMIUM", "chromium")
JOBS = int(os.environ.get("JOBS", "6"))
HERE = os.path.dirname(os.path.abspath(__file__))
NODE_MODULES = os.environ.get("EV_NODE_MODULES", os.path.expanduser("~/Projects/edition-video/node_modules"))
FONT_B = "/usr/share/fonts/liberation/LiberationSans-Bold.ttf"
FONT_R = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/142.0.0.0 Safari/537.36")

WD = os.path.abspath(sys.argv[1])
C = lambda *p: os.path.join(WD, *p)
for d in ("cache/yt", "cache/page", "cache/card", "shots", "tmp"):
    os.makedirs(C(d), exist_ok=True)
report = {"sources": {}, "failures": [], "substitutions": []}


def run(cmd, timeout=600, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kw)


def h(s):
    return hashlib.sha1(s.encode()).hexdigest()[:12]


# ---------------------------------------------------------------- parse
def parse(path):
    txt = open(path).read()
    m = re.search(r"^Edition:\s*(\S+)", txt, re.M)
    edition = m.group(1) if m else None
    segs = []
    for block in re.split(r"^## ", txt, flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        num, _, title = head.strip().partition(" ")
        nar = re.search(r"^Narration:\s*(.+)$", body, re.M).group(1).strip()
        vis = []
        vpart = body.split("Visuals:", 1)[1] if "Visuals:" in body else ""
        for line in vpart.splitlines():
            line = line.strip()
            if not line.startswith("- "):
                continue
            line = line[2:].strip()
            kind, _, rest = line.partition(" ")
            parts = [p.strip() for p in rest.split("|")] if kind != "edition" else ["", *[p.strip() for p in line.split("|")[1:]]]
            if kind == "yt":
                um = re.match(r"(\S+)\s+@(\d+)", parts[0])
                vis.append({"kind": "yt", "url": um.group(1), "t": int(um.group(2)), "label": parts[1] if len(parts) > 1 else "YouTube"})
            elif kind == "page":
                vis.append({"kind": "page", "url": parts[0], "label": parts[1] if len(parts) > 1 else "",
                            "fallback": parts[2] if len(parts) > 2 else (parts[1] if len(parts) > 1 else "")})
            elif kind == "edition":
                vis.append({"kind": "page", "url": edition, "label": parts[1] if len(parts) > 1 else "The edition",
                            "fallback": "Today's edition", "edition": True})
            elif kind == "card":
                vis.append({"kind": "card", "title": parts[0], "sub": parts[1] if len(parts) > 1 else "", "label": ""})
        segs.append({"num": num, "title": title, "narration": nar, "visuals": vis})
    return edition, segs


# ---------------------------------------------------------------- sources
def vid_id(url):
    q = urllib.parse.urlparse(url)
    return urllib.parse.parse_qs(q.query).get("v", [q.path.rsplit("/", 1)[-1]])[0]


def fetch_yt(v):
    vid = vid_id(v["url"])
    out = C("cache/yt", f"{vid}_{v['t']}.mp4")
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        report["sources"][f"yt {vid}@{v['t']}"] = "cached"
        return out
    s, e = max(0, v["t"] - YT_BEFORE), v["t"] + YT_AFTER
    tmpd = C("tmp", f"yt_{vid}_{v['t']}")
    shutil.rmtree(tmpd, ignore_errors=True); os.makedirs(tmpd)
    err = ""
    for attempt in range(3):
        r = run([YTDLP, "--no-playlist", "--no-cookies", "-q", "--no-warnings",
                 "-f", "bv*[height<=1080][vcodec!=none]/bv*[height<=1080]/b[height<=1080]",
                 "--download-sections", f"*{s}-{e}", "--force-keyframes-at-cuts",
                 "-o", os.path.join(tmpd, "clip.%(ext)s"), f"https://www.youtube.com/watch?v={vid}"], timeout=900)
        files = [f for f in os.listdir(tmpd) if f.startswith("clip.") and not f.endswith(".part")]
        if r.returncode == 0 and files:
            src = os.path.join(tmpd, files[0])
            # normalize: mute, cover-crop to 1920x1080, 30 fps, all-intra-ish for exact seeking
            n = run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", src, "-an",
                     "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1",
                     "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-g", "15", "-pix_fmt", "yuv420p", out])
            if n.returncode == 0:
                report["sources"][f"yt {vid}@{v['t']}"] = "ok"
                return out
            err = n.stderr[-400:]
        else:
            err = (r.stderr or "")[-400:]
        wait = 30 if "429" in err else 5
        time.sleep(wait * (attempt + 1))
    report["failures"].append({"source": f"yt {vid}@{v['t']}", "error": err.strip()})
    return None


def yt_thumb(v):
    vid = vid_id(v["url"])
    out = C("cache/page", f"thumb_{vid}.png")
    if os.path.exists(out):
        return out
    for q in ("maxresdefault", "sddefault", "hqdefault"):
        try:
            data = urllib.request.urlopen(urllib.request.Request(
                f"https://i.ytimg.com/vi/{vid}/{q}.jpg", headers={"User-Agent": UA}), timeout=30).read()
            p = C("tmp", f"thumb_{vid}.jpg"); open(p, "wb").write(data)
            im = Image.open(p).convert("RGB")
            if im.width < 400:
                continue
            im = cover(im, W, H); im.save(out)
            return out
        except Exception:
            continue
    return None


def cover(im, w, hh):
    s = max(w / im.width, hh / im.height)
    im = im.resize((math.ceil(im.width * s), math.ceil(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - hh) // 2
    return im.crop((x, y, x + w, y + hh))


def chrome_shot(target, png, width=1440, height=3600, dsf=1.3334, budget=15000):
    return run([CHROMIUM, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio",
                f"--user-agent={UA}", "--lang=en-US", f"--window-size={width},{height}",
                f"--force-device-scale-factor={dsf}", f"--virtual-time-budget={budget}",
                "--run-all-compositor-stages-before-draw", f"--screenshot={png}", target], timeout=180)


def trim_bottom(im):
    """Drop blank space at the bottom of a tall capture."""
    g = im.convert("L").resize((64, im.height // 20 or 1))
    rows = [ImageStat.Stat(g.crop((0, y, 64, y + 1))).stddev[0] for y in range(g.height)]
    last = max([i for i, s in enumerate(rows) if s > 3] or [g.height - 1])
    return im.crop((0, 0, im.width, min(im.height, (last + 2) * 20 + H)))


def tweet_embed(url, png):
    """Render a clean post card from X's public oEmbed (no login, no widgets.js)."""
    import html as H_
    api = "https://publish.twitter.com/oembed?" + urllib.parse.urlencode({"url": url, "dnt": "true", "omit_script": "true"})
    d = json.loads(urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": UA}), timeout=30).read())
    m = re.search(r"<p[^>]*>(.*?)</p>.*?&mdash;\s*(.*?)<a[^>]*>([^<]*)</a>", d["html"], re.S)
    body = re.sub(r"<br\s*/?>", "\n", m.group(1)); body = re.sub(r"<a[^>]*>(.*?)</a>", r"<span class=l>\1</span>", body)
    body = re.sub(r"<(?!/?span)[^>]+>", "", body).replace("\n", "<br>")
    who, date = m.group(2).strip(), m.group(3).strip()
    handle = "@" + d.get("author_url", "").rstrip("/").rsplit("/", 1)[-1]
    name = H_.escape(d.get("author_name", who))
    page = C("tmp", f"tw_{h(url)}.html")
    open(page, "w").write(f"""<!doctype html><html><head><meta charset=utf-8><style>
html,body{{margin:0;background:#000;font-family:'Liberation Sans',Arial,sans-serif;color:#e7e9ea}}
.w{{width:{W}px;height:{H}px;display:flex;align-items:center;justify-content:center}}
.c{{width:1180px;border:2px solid #2f3336;border-radius:36px;padding:56px 64px;background:#0a0a0a}}
.n{{font-weight:700;font-size:44px}} .h{{color:#71767b;font-size:36px;margin-top:6px}}
.t{{font-size:46px;line-height:1.38;margin:36px 0}} .l{{color:#1d9bf0}} .d{{color:#71767b;font-size:32px}}
.a{{display:flex;gap:28px;align-items:center}} .av{{width:110px;height:110px;border-radius:55px;background:#1d9bf0;
display:flex;align-items:center;justify-content:center;font-size:56px;font-weight:700;color:#fff}}
.x{{margin-left:auto;font-size:64px;font-weight:700}}</style></head><body><div class=w><div class=c>
<div class=a><div class=av>{name[:1]}</div><div><div class=n>{name}</div><div class=h>{H_.escape(handle)}</div></div><div class=x>&#120143;</div></div>
<div class=t>{body}</div><div class=d>{H_.escape(date)}</div></div></div></body></html>""")
    chrome_shot("file://" + page, png, width=W, height=H, dsf=1, budget=3000)


def fetch_page(v):
    url = v["url"]
    out = C("cache/page", f"{h(url)}.png")
    if os.path.exists(out):
        report["sources"][f"page {url}"] = "cached"
        return out
    raw = C("tmp", f"{h(url)}_raw.png")
    ok = False
    try:
        if re.match(r"https?://(x|twitter)\.com/", url):
            tweet_embed(url, raw)
            ok = os.path.exists(raw) and ImageStat.Stat(Image.open(raw).convert("L").resize((96, 120))).stddev[0] > 8
        else:
            r = run(["node", os.path.join(HERE, "capture.mjs"), url, raw], timeout=150,
                    env={**os.environ, "EV_NODE_MODULES": NODE_MODULES})
            info = json.loads((r.stdout or "{}").strip().splitlines()[-1] if r.stdout.strip() else "{}")
            ok = info.get("ok") and not info.get("blocked") and os.path.exists(raw)
            if not ok:
                report["failures"].append({"source": url, "error": info.get("error") or f"blocked: {info.get('title','')}"[:200]})
    except Exception as e:  # noqa
        report["failures"].append({"source": url, "error": repr(e)[:300]})
    if not ok:
        if re.match(r"https?://(x|twitter)\.com/", url):
            report["failures"].append({"source": url, "error": "tweet render failed"})
        return None
    im = Image.open(raw).convert("RGB")
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    im = trim_bottom(im)
    if im.height < H:
        bg = Image.new("RGB", (W, H), (11, 13, 18)); bg.paste(im, (0, 0)); im = bg
    im.save(out)
    report["sources"][f"page {url}"] = "ok"
    return out


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w_
    return lines + ([cur] if cur else [])


def card(title, sub=""):
    out = C("cache/card", f"{h(title + '|' + sub)}.png")
    if os.path.exists(out):
        return out
    im = Image.new("RGB", (W, H), (11, 13, 18))
    d = ImageDraw.Draw(im)
    for i in range(H):  # subtle vertical gradient
        d.line([(0, i), (W, i)], fill=(11 + i // 60, 13 + i // 70, 22 + i // 30))
    d.rectangle([(140, 360), (156, 720)], fill=(255, 196, 0))
    ft, fs = ImageFont.truetype(FONT_B, 92), ImageFont.truetype(FONT_R, 46)
    lines = wrap(d, title, ft, W - 400)[:4]
    y = 540 - (len(lines) * 108 + (70 if sub else 0)) // 2
    for ln in lines:
        d.text((200, y), ln, font=ft, fill=(245, 245, 245)); y += 108
    if sub:
        d.text((200, y + 20), sub, font=fs, fill=(170, 180, 200))
    im.save(out)
    return out


# ---------------------------------------------------------------- shots
def label_filter(label, idx):
    if not label:
        return ""
    f = C("tmp", f"label_{idx}.txt"); open(f, "w").write(label)
    return (f",drawtext=fontfile={FONT_B}:textfile={f}:fontsize=36:fontcolor=white:"
            f"y_align=font:box=1:boxcolor=black@0.62:boxborderw=16:x=72:y=h-140,"
            f"drawbox=x=48:y=ih-156:w=8:h=74:color=0xFFC400@1:t=fill")


ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-g", str(FPS * 2), "-profile:v", "high", "-an"]


def zoom_expr(frames, z0, z1):
    return f"zoompan=z='{z0}+({z1}-{z0})*on/{max(frames-1,1)}':d=1:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':s={W}x{H}:fps={FPS}"


def render_shot(shot):
    i, frames, src, kind, k, label = shot["i"], shot["frames"], shot["src"], shot["kind"], shot["use"], shot["label"]
    out = C("shots", f"{i:03d}.mp4")
    dur = frames / FPS
    lf = label_filter(label, i)
    punch = (k % 2 == 0)
    if kind == "yt":
        clip_len = YT_AFTER + YT_BEFORE - 0.5
        off = (YT_BEFORE + 3.2 * k) % max(clip_len - dur, 0.5)
        z = zoom_expr(frames, 1.0, 1.10) if punch else zoom_expr(frames, 1.14, 1.14)
        vf = f"scale={W*2}:{H*2}:flags=bicubic,{z}{lf},format=yuv420p"
        cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-ss", f"{off:.2f}", "-i", src, "-vf", vf,
               "-frames:v", str(frames), *ENC, out]
    else:  # still image: page capture or card
        im = Image.open(src); ih_ = im.height
        if kind == "card":
            vf = f"scale={W*2}:{H*2},{zoom_expr(frames, 1.0, 1.06)}{lf},format=yuv420p"
        else:
            span = 260
            y0 = (k * 900) % max(ih_ - H - span, 1)
            if punch or ih_ <= H + 40:
                vf = f"crop={W}:{H}:0:{min(y0, ih_-H)},scale={W*2}:{H*2},{zoom_expr(frames, 1.0, 1.12)}{lf},format=yuv420p"
            else:
                y1 = min(y0 + span, ih_ - H)
                vf = f"crop={W}:{H}:0:'{y0}+({y1}-{y0})*t/{dur:.3f}'{lf},format=yuv420p"
        cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-i", src,
               "-vf", vf, "-frames:v", str(frames), *ENC, out]
    r = run(cmd, timeout=900)
    if r.returncode != 0:
        raise RuntimeError(f"shot {i} failed: {r.stderr[-600:]}")
    return out


def tc(sec):
    return f"{int(sec // 60):02d}:{sec % 60:04.1f}"


def main():
    edition, segs = parse(C("script.md"))
    # resolve every distinct source once (downloads sequential to stay polite with YouTube)
    resolved = {}
    for s in segs:
        for v in s["visuals"]:
            key = json.dumps(v, sort_keys=True)
            if key in resolved:
                continue
            if v["kind"] == "yt":
                p = fetch_yt(v); time.sleep(2)
                if p:
                    resolved[key] = ("yt", p, v["label"])
                else:
                    t = yt_thumb(v)
                    resolved[key] = ("page", t, v["label"]) if t else ("card", card(v["label"], "YouTube"), "")
                    report["substitutions"].append({"source": v["url"], "used": "thumbnail" if t else "card"})
            elif v["kind"] == "page":
                p = fetch_page(v)
                if p:
                    resolved[key] = ("page", p, v["label"])
                else:
                    resolved[key] = ("card", card(v.get("fallback") or v["label"], v["label"]), "")
                    report["substitutions"].append({"source": v["url"], "used": "title card"})
            else:
                resolved[key] = ("card", card(v["title"], v["sub"]), v["label"])
    # timeline
    shots, timeline, t_frames, uses = [], [], 0, {}
    for s in segs:
        words = len(s["narration"].split())
        seg_frames = round((words / WPS + PAD) * FPS)
        n = max(1, round(seg_frames / (SHOT * FPS)))
        base, extra = divmod(seg_frames, n)
        timeline.append({"num": s["num"], "title": s["title"], "start": t_frames / FPS,
                         "duration": seg_frames / FPS, "words": words, "shots": n,
                         "sources": sorted({resolved[json.dumps(v, sort_keys=True)][0] for v in s["visuals"]})})
        for j in range(n):
            v = s["visuals"][j % len(s["visuals"])]
            kind, path, label = resolved[json.dumps(v, sort_keys=True)]
            k = uses.get(path, 0); uses[path] = k + 1
            shots.append({"i": len(shots), "frames": base + (1 if j < extra else 0), "src": path,
                          "kind": kind, "use": k, "label": label, "seg": s["num"]})
        t_frames += seg_frames
    with ThreadPoolExecutor(JOBS) as ex:
        outs = list(ex.map(render_shot, shots))
    with open(C("tmp", "concat.txt"), "w") as f:
        for o in outs:
            f.write(f"file '{o}'\n")
    total = t_frames / FPS
    r = run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", C("tmp", "concat.txt"),
             "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
             "-t", f"{total:.3f}", "-movflags", "+faststart", C("final.mp4")], timeout=1800)
    if r.returncode != 0:
        raise SystemExit(r.stderr[-1500:])
    # teleprompter
    tp = [f"# Teleprompter: {os.path.basename(WD)}", "",
          f"Total {tc(total)} · read at about {int(WPS*60)} words a minute · each segment ends with a short breath.", ""]
    for s, tl in zip(segs, timeline):
        tp += [f"## [{tc(tl['start'])}] {s['num']} · {s['title']}", "", s["narration"], ""]
    open(C("teleprompter.md"), "w").write("\n".join(tp))
    json.dump({"total_seconds": total, "segments": timeline, "shots": len(shots)}, open(C("timeline.json"), "w"), indent=1)
    report["total_seconds"] = total; report["segments"] = len(segs); report["shots"] = len(shots)
    json.dump(report, open(C("report.json"), "w"), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
