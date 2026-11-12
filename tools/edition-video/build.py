#!/usr/bin/env python3
"""Build a silent, voiceover-ready 1080p30 edition video from script.md.

Runs ON the render host (never on the box). Usage:
    python3 build.py WORKDIR
        [--segment 09] [--include-edition] [--include-open-close]
        [--no-dark] [--output final.mp4]
Env: YTDLP, CHROMIUM, JOBS, EV_DARK=0, EV_INCLUDE_EDITION=1,
     EV_INCLUDE_OPEN_CLOSE=1, EV_SEGMENTS=09, EV_OUTPUT=final.mp4

script.md format (see tools/edition-video/README.md):
    Edition: <github pages url>
    ## NN Title
    Narration: one paragraph
    Camera: self                  # optional; also auto for Cold open / Sign-off
    Visuals:
    - yt <url> @<seconds> | <label>
    - page <url> | <label> [| fallback title]
    - xpost <url-or-id> | <label>
    - card <title> | <subtitle>
    - edition | <label>           # skipped unless --include-edition

Outputs: final.mp4, teleprompter.md, timeline.json, report.json,
         post-attribution.md, attribution.json
Optional sidecars in WORKDIR: xposts.json (auto-fill 3-6 posts/segment),
                               handles.json (confirmed X handles for credits).
"""
import argparse, hashlib, json, math, os, re, shutil, subprocess, sys, time, urllib.parse, urllib.request
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
NODE_MODULES = os.path.expanduser(os.environ.get("EV_NODE_MODULES", os.path.expanduser("~/Projects/edition-video/node_modules")))
FONT_B = "/usr/share/fonts/liberation/LiberationSans-Bold.ttf"
FONT_R = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/142.0.0.0 Safari/537.36")
ON_CAM_TITLES = re.compile(r"^(cold open|sign-?off|outro)$", re.I)
X_STATUS = re.compile(r"(?:status|statuses)/(\d+)")
X_HANDLE = re.compile(r"https?://(?:x|twitter)\.com/([^/]+)/status/(\d+)", re.I)
CAM_RE = re.compile(r"^(?:Camera|On camera):\s*(self|yes|on camera|none)\s*$", re.I | re.M)
CAM_VIS = re.compile(r"^Visuals:\s*(on camera|none|self)\s*$", re.I | re.M)
FORCE_VIDEO = re.compile(r"^(?:Camera|On camera):\s*(video|include)\s*$", re.I | re.M)

# theme (set in main after flags)
DARK = True
BG = (11, 13, 18)
THEME_TAG = "dark"

WD = None
C = None
report = {"sources": {}, "failures": [], "substitutions": [], "xposts": [], "unresolved": []}


def run(cmd, timeout=600, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kw)


def h(s):
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def post_id(url_or_id):
    s = str(url_or_id).strip()
    m = X_STATUS.search(s)
    if m:
        return m.group(1)
    return s if re.fullmatch(r"\d+", s) else None


def post_url(url_or_id, handle=None):
    s = str(url_or_id).strip()
    m = X_HANDLE.search(s)
    if m:
        return f"https://x.com/{m.group(1)}/status/{m.group(2)}", m.group(1), m.group(2)
    pid = post_id(s)
    if not pid:
        return None, handle, None
    who = handle or "i"
    return f"https://x.com/{who}/status/{pid}", who if who != "i" else None, pid


def dark_env(env=None):
    e = {**(env or os.environ), "EV_NODE_MODULES": NODE_MODULES}
    e["EV_DARK"] = "1" if DARK else "0"
    return e


# ---------------------------------------------------------------- parse
def is_on_camera(title, body, include_open_close):
    if FORCE_VIDEO.search(body or ""):
        return False
    if CAM_RE.search(body or "") or CAM_VIS.search(body or ""):
        return True
    if include_open_close:
        return False
    return bool(ON_CAM_TITLES.match((title or "").strip()))


def parse(path, include_edition=False, include_open_close=False):
    txt = open(path).read()
    m = re.search(r"^Edition:\s*(\S+)", txt, re.M)
    edition = m.group(1) if m else None
    segs = []
    for block in re.split(r"^## ", txt, flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        num, _, title = head.strip().partition(" ")
        nar_m = re.search(r"^Narration:\s*(.+)$", body, re.M)
        if not nar_m:
            continue
        nar = nar_m.group(1).strip()
        on_cam = is_on_camera(title, body, include_open_close)
        vis = []
        skipped_edition = []
        vpart = body.split("Visuals:", 1)[1] if "Visuals:" in body else ""
        if not on_cam:
            for line in vpart.splitlines():
                line = line.strip()
                if not line.startswith("- "):
                    continue
                line = line[2:].strip()
                kind, _, rest = line.partition(" ")
                parts = [p.strip() for p in rest.split("|")] if kind != "edition" else ["", *[p.strip() for p in line.split("|")[1:]]]
                if kind == "yt":
                    um = re.match(r"(\S+)\s+@(\d+)", parts[0])
                    if not um:
                        continue
                    vis.append({"kind": "yt", "url": um.group(1), "t": int(um.group(2)),
                                "label": parts[1] if len(parts) > 1 else "YouTube"})
                elif kind == "xpost":
                    url, handle, pid = post_url(parts[0], None)
                    if not pid:
                        continue
                    label = parts[1] if len(parts) > 1 else (f"@{handle}" if handle else "X post")
                    vis.append({"kind": "xpost", "url": url or parts[0], "id": pid,
                                "handle": handle, "label": label})
                elif kind == "page":
                    url = parts[0]
                    pid = post_id(url)
                    if pid:
                        canon, handle, _ = post_url(url)
                        label = parts[1] if len(parts) > 1 else (f"@{handle}" if handle else "X post")
                        vis.append({"kind": "xpost", "url": canon or url, "id": pid,
                                    "handle": handle, "label": label})
                    else:
                        vis.append({"kind": "page", "url": url, "label": parts[1] if len(parts) > 1 else "",
                                    "fallback": parts[2] if len(parts) > 2 else (parts[1] if len(parts) > 1 else "")})
                elif kind == "edition":
                    item = {"kind": "page", "url": edition, "label": parts[1] if len(parts) > 1 else "The edition",
                            "fallback": "Today's edition", "edition": True}
                    if include_edition and edition:
                        vis.append(item)
                    else:
                        skipped_edition.append(item)
                elif kind == "card":
                    vis.append({"kind": "card", "title": parts[0], "sub": parts[1] if len(parts) > 1 else "", "label": ""})
        segs.append({"num": num, "title": title, "narration": nar, "visuals": vis,
                     "on_camera": on_cam, "skipped_edition": skipped_edition})
    return edition, segs


def merge_xposts(segs, path):
    """Auto-fill about 3-6 related X posts per video segment from xposts.json."""
    if not path or not os.path.exists(path):
        return
    data = json.load(open(path))
    # allow {"09": [...]} or {"segments": {"09": [...]}}
    mapping = data.get("segments", data)
    for s in segs:
        if s["on_camera"]:
            continue
        raw = mapping.get(s["num"]) or mapping.get(str(int(s["num"])) if s["num"].isdigit() else "")
        if not raw:
            continue
        existing = {v.get("id") for v in s["visuals"] if v.get("kind") == "xpost"}
        added = 0
        for item in raw:
            if added >= 6:
                break
            if isinstance(item, str):
                item = {"url": item}
            url, handle, pid = post_url(item.get("url") or item.get("id"), item.get("handle"))
            if not pid or pid in existing:
                continue
            label = item.get("label") or (f"@{handle}" if handle else "X post")
            s["visuals"].append({"kind": "xpost", "url": url or item.get("url"), "id": pid,
                                 "handle": handle, "label": label})
            existing.add(pid)
            added += 1
            report["xposts"].append({"segment": s["num"], "id": pid, "url": url, "handle": handle,
                                     "label": label, "source": "auto"})


# ---------------------------------------------------------------- sources
def vid_id(url):
    q = urllib.parse.urlparse(url)
    return urllib.parse.parse_qs(q.query).get("v", [q.path.rsplit("/", 1)[-1]])[0]


def yt_channel_meta(url, vid):
    meta = C("cache/yt", f"{vid}.channel.json")
    if os.path.exists(meta):
        try:
            return json.load(open(meta))
        except Exception:
            pass
    r = run([YTDLP, "--skip-download", "--no-playlist", "--no-cookies", "--no-warnings",
             "--print", "%(channel)s\t%(uploader)s\t%(uploader_id)s\t%(channel_id)s",
             url], timeout=90)
    if r.returncode != 0 or not (r.stdout or "").strip():
        return {}
    ch, up, uid, cid = (r.stdout.strip().split("\t") + ["", "", "", ""])[:4]
    info = {"channel": ch or up, "uploader": up, "uploader_id": uid, "channel_id": cid}
    json.dump(info, open(meta, "w"))
    return info


def fetch_yt(v):
    vid = vid_id(v["url"])
    out = C("cache/yt", f"{vid}_{v['t']}.mp4")
    v["_channel"] = yt_channel_meta(v["url"], vid)
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


def contain_on_canvas(im, w, hh, bg):
    """Fit the whole image on a w x hh canvas with a themed letterbox."""
    canvas = Image.new("RGB", (w, hh), bg)
    if im.width == 0 or im.height == 0:
        return canvas
    pad = 80
    s = min((w - 2 * pad) / im.width, (hh - 2 * pad) / im.height, 1.0 * w / im.width)
    # allow upscale of small tweet cards so they fill the frame reasonably
    s = min((w - 2 * pad) / im.width, (hh - 2 * pad) / im.height)
    nw, nh = max(1, round(im.width * s)), max(1, round(im.height * s))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas.paste(im, ((w - nw) // 2, (hh - nh) // 2))
    return canvas


def chrome_shot(target, png, width=1440, height=3600, dsf=1.3334, budget=15000):
    flags = [CHROMIUM, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio",
             f"--user-agent={UA}", "--lang=en-US", f"--window-size={width},{height}",
             f"--force-device-scale-factor={dsf}", f"--virtual-time-budget={budget}",
             "--run-all-compositor-stages-before-draw", f"--screenshot={png}", target]
    if DARK:
        flags[2:2] = ["--enable-features=WebContentsForceDark", "--force-dark-mode",
                      "--blink-settings=forceDarkModeEnabled=true"]
    return run(flags, timeout=180)


def trim_bottom(im):
    """Drop blank space at the bottom of a tall capture."""
    g = im.convert("L").resize((64, im.height // 20 or 1))
    rows = [ImageStat.Stat(g.crop((0, y, 64, y + 1))).stddev[0] for y in range(g.height)]
    last = max([i for i, s in enumerate(rows) if s > 3] or [g.height - 1])
    return im.crop((0, 0, im.width, min(im.height, (last + 2) * 20 + H)))


def tweet_embed_card(url, png, handle=None):
    """Fallback dark (or light) post card from X's public oEmbed. No login, no widgets.js."""
    import html as H_
    api = "https://publish.twitter.com/oembed?" + urllib.parse.urlencode({"url": url, "dnt": "true", "omit_script": "true"})
    d = json.loads(urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": UA}), timeout=30).read())
    m = re.search(r"<p[^>]*>(.*?)</p>.*?&mdash;\s*(.*?)<a[^>]*>([^<]*)</a>", d["html"], re.S)
    body = re.sub(r"<br\s*/?>", "\n", m.group(1)); body = re.sub(r"<a[^>]*>(.*?)</a>", r"<span class=l>\1</span>", body)
    body = re.sub(r"<(?!/?span)[^>]+>", "", body).replace("\n", "<br>")
    who, date = m.group(2).strip(), m.group(3).strip()
    from_url = d.get("author_url", "").rstrip("/").rsplit("/", 1)[-1]
    handle = handle or from_url
    name = H_.escape(d.get("author_name", who))
    if DARK:
        bg, card, fg, mut, acc, border = "#000", "#0a0a0a", "#e7e9ea", "#71767b", "#1d9bf0", "#2f3336"
    else:
        bg, card, fg, mut, acc, border = "#e7ecf2", "#fff", "#0f1419", "#536471", "#1d9bf0", "#cfd9de"
    page = C("tmp", f"tw_{h(url)}.html")
    open(page, "w").write(f"""<!doctype html><html><head><meta charset=utf-8><style>
html,body{{margin:0;background:{bg};font-family:'Liberation Sans',Arial,sans-serif;color:{fg}}}
.w{{width:{W}px;height:{H}px;display:flex;align-items:center;justify-content:center}}
.c{{width:1180px;border:2px solid {border};border-radius:36px;padding:56px 64px;background:{card}}}
.n{{font-weight:700;font-size:44px}} .h{{color:{mut};font-size:36px;margin-top:6px}}
.t{{font-size:46px;line-height:1.38;margin:36px 0}} .l{{color:{acc}}} .d{{color:{mut};font-size:32px}}
.a{{display:flex;gap:28px;align-items:center}} .av{{width:110px;height:110px;border-radius:55px;background:{acc};
display:flex;align-items:center;justify-content:center;font-size:56px;font-weight:700;color:#fff}}
.x{{margin-left:auto;font-size:64px;font-weight:700}}</style></head><body><div class=w><div class=c>
<div class=a><div class=av>{name[:1]}</div><div><div class=n>{name}</div><div class=h>{H_.escape('@'+handle if handle else '')}</div></div><div class=x>&#120143;</div></div>
<div class=t>{body}</div><div class=d>{H_.escape(date)}</div></div></div></body></html>""")
    chrome_shot("file://" + page, png, width=W, height=H, dsf=1, budget=3000)
    return handle


def interesting(png):
    if not os.path.exists(png) or os.path.getsize(png) < 8000:
        return False
    try:
        return ImageStat.Stat(Image.open(png).convert("L").resize((96, 120))).stddev[0] > 8
    except Exception:
        return False


def fetch_xpost(v):
    pid, url = v["id"], v.get("url") or f"https://x.com/i/status/{v['id']}"
    out = C("cache/page", f"xpost_{pid}_{THEME_TAG}.png")
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        report["sources"][f"xpost {pid}"] = "cached"
        report["xposts"].append({**{k: v.get(k) for k in ("id", "url", "handle", "label")}, "render": "cached"})
        return out
    raw = C("tmp", f"xpost_{pid}_{THEME_TAG}_raw.png")
    mode = None
    try:
        r = run(["node", os.path.join(HERE, "capture.mjs"), "--xpost", pid, raw], timeout=150, env=dark_env())
        line = (r.stdout or "").strip().splitlines()[-1] if r.stdout and r.stdout.strip() else "{}"
        info = json.loads(line)
        if info.get("ok") and interesting(raw):
            mode = "embed"
        else:
            report["failures"].append({"source": url, "error": f"embed: {info.get('error') or 'blank'}"[:200]})
    except Exception as e:  # noqa
        report["failures"].append({"source": url, "error": f"embed: {repr(e)[:240]}"})
    if mode is None:
        try:
            handle = tweet_embed_card(url, raw, v.get("handle"))
            if handle and not v.get("handle"):
                v["handle"] = handle
            if interesting(raw):
                mode = "oembed-card"
            else:
                report["failures"].append({"source": url, "error": "oembed card failed"})
                return None
        except Exception as e:  # noqa
            report["failures"].append({"source": url, "error": f"oembed: {repr(e)[:240]}"})
            return None
    im = Image.open(raw).convert("RGB")
    # Official embeds are a tight tweet card; letterbox them on a themed 1080p canvas.
    # oembed-card already paints a full 1920x1080 frame.
    if mode == "embed":
        im = contain_on_canvas(im, W, H, BG)
    elif im.size != (W, H):
        if im.width != W:
            im = im.resize((W, max(1, round(im.height * W / im.width))), Image.LANCZOS)
        if im.height < H:
            canvas = Image.new("RGB", (W, H), BG); canvas.paste(im, (0, (H - im.height) // 2)); im = canvas
        elif im.height > H:
            im = contain_on_canvas(im, W, H, BG)
    im.save(out)
    report["sources"][f"xpost {pid}"] = mode
    report["xposts"].append({"id": pid, "url": url, "handle": v.get("handle"), "label": v.get("label"), "render": mode})
    return out


def fetch_page(v):
    url = v["url"]
    out = C("cache/page", f"{h(url + '|' + THEME_TAG)}.png")
    if os.path.exists(out):
        report["sources"][f"page {url}"] = "cached"
        return out
    raw = C("tmp", f"{h(url)}_{THEME_TAG}_raw.png")
    ok = False
    try:
        r = run(["node", os.path.join(HERE, "capture.mjs"), url, raw], timeout=150, env=dark_env())
        info = json.loads((r.stdout or "{}").strip().splitlines()[-1] if r.stdout and r.stdout.strip() else "{}")
        ok = info.get("ok") and not info.get("blocked") and os.path.exists(raw)
        if not ok:
            report["failures"].append({"source": url, "error": info.get("error") or f"blocked: {info.get('title','')}"[:200]})
    except Exception as e:  # noqa
        report["failures"].append({"source": url, "error": repr(e)[:300]})
    if not ok:
        return None
    im = Image.open(raw).convert("RGB")
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    im = trim_bottom(im)
    if im.height < H:
        bg = Image.new("RGB", (W, H), BG); bg.paste(im, (0, 0)); im = bg
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
    out = C("cache/card", f"{h(title + '|' + sub + '|' + THEME_TAG)}.png")
    if os.path.exists(out):
        return out
    if DARK:
        top, bot, bar, ft_c, fs_c = (11, 13, 18), (22, 26, 36), (255, 196, 0), (245, 245, 245), (170, 180, 200)
    else:
        top, bot, bar, ft_c, fs_c = (244, 246, 250), (226, 230, 238), (30, 90, 200), (18, 20, 28), (70, 80, 100)
    im = Image.new("RGB", (W, H), top)
    d = ImageDraw.Draw(im)
    for i in range(H):
        t = i / max(H - 1, 1)
        col = tuple(int(top[c] + (bot[c] - top[c]) * t) for c in range(3))
        d.line([(0, i), (W, i)], fill=col)
    d.rectangle([(140, 360), (156, 720)], fill=bar)
    ft, fs = ImageFont.truetype(FONT_B, 92), ImageFont.truetype(FONT_R, 46)
    lines = wrap(d, title, ft, W - 400)[:4]
    y = 540 - (len(lines) * 108 + (70 if sub else 0)) // 2
    for ln in lines:
        d.text((200, y), ln, font=ft, fill=ft_c); y += 108
    if sub:
        d.text((200, y + 20), sub, font=fs, fill=fs_c)
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
    else:  # still image: page capture, x post, or card
        im = Image.open(src); ih_ = im.height
        if kind in ("card", "xpost"):
            # X posts are already composed on a 1080p canvas; a gentle punch-in is enough.
            z0, z1 = (1.0, 1.06) if kind == "card" else (1.0, 1.08)
            vf = f"scale={W*2}:{H*2},{zoom_expr(frames, z0, z1)}{lf},format=yuv420p"
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


# ---------------------------------------------------------------- attribution
def load_handles(path):
    if not path or not os.path.exists(path):
        return {}
    raw = json.load(open(path))
    out = {}
    for k, v in raw.items():
        if not v:
            continue
        handle = str(v).lstrip("@").split("/")[-1].strip()
        if handle:
            out[str(k).strip()] = handle
            out[str(k).strip().lower()] = handle
    return out


def lookup_handle(name, handles):
    if not name:
        return None
    s = str(name).strip().lstrip("@")
    return handles.get(s) or handles.get(s.lower())


def build_attribution(segs, handles):
    """Write attribution.json + post-attribution.md. Only confirmed handles go in the markdown."""
    unresolved = []
    attr_segs = []
    md = ["# Credits", "",
          "Accounts to paste into the video post. Each line is an @handle and its X profile.",
          "Shown X posts also get a direct link. No YouTube, news-site, or GitHub Pages URLs.",
          ""]
    for s in segs:
        entries, seen = [], set()

        def add(handle, role, post=None, entity=None):
            if not handle:
                if entity:
                    unresolved.append({"segment": s["num"], "entity": entity, "reason": "no confirmed X handle"})
                return
            handle = handle.lstrip("@")
            key = (handle.lower(), post or "")
            if key in seen:
                return
            seen.add(key)
            entries.append({"handle": handle, "role": role, "post": post, "entity": entity})

        if s.get("on_camera") and not s.get("in_video"):
            # Still credit anything named in on-camera sections? Only if we have explicit sources.
            pass
        for v in s.get("visuals") or []:
            if v["kind"] == "xpost":
                handle = v.get("handle") or lookup_handle(v.get("label"), handles)
                url, handle2, pid = post_url(v.get("url") or v.get("id"), handle)
                handle = handle or handle2
                # A handle taken from the post URL is the account that posted it.
                if handle:
                    add(handle, "X post", url, v.get("label") or handle)
                else:
                    unresolved.append({"segment": s["num"], "entity": v.get("url") or v.get("id"),
                                       "reason": "X post URL has no handle"})
            elif v["kind"] == "yt":
                meta = v.get("_channel") or {}
                ch = meta.get("channel") or meta.get("uploader") or ""
                # uploader_id like @aiDotEngineer is a YouTube handle, not an X handle, unless confirmed.
                yt_h = (meta.get("uploader_id") or "").lstrip("@")
                handle = lookup_handle(ch, handles) or lookup_handle(yt_h, handles) or lookup_handle(v.get("label"), handles)
                # Also split labels like "AI Engineer · Duolingo"
                if not handle and v.get("label"):
                    for part in re.split(r"\s*[·|/,—-]\s*", v["label"]):
                        handle = lookup_handle(part, handles)
                        if handle:
                            break
                add(handle, "YouTube channel", None, ch or v.get("label") or "YouTube")
            elif v["kind"] == "page":
                label = v.get("label") or v.get("fallback") or ""
                handle = lookup_handle(label, handles) or lookup_handle(v.get("fallback"), handles)
                role = "edition" if v.get("edition") else "news outlet or page"
                add(handle, role, None, label or v.get("url"))
            elif v["kind"] == "card":
                for part in filter(None, [v.get("title"), v.get("sub"), v.get("label")]):
                    handle = lookup_handle(part, handles)
                    if handle:
                        add(handle, "headline card", None, part)
        # Extra confirmed entities listed under this segment in handles.json as
        # "09::Nvidia" or provided via an "entities" map on the sidecar.
        attr_segs.append({"num": s["num"], "title": s["title"], "on_camera": s.get("on_camera", False),
                          "in_video": s.get("in_video", not s.get("on_camera")), "entries": entries})
        if not entries and s.get("in_video", not s.get("on_camera")):
            # still emit the heading so the file follows video order
            pass
        heading = f"## {s['num']} · {s['title']}"
        if s.get("on_camera") and not s.get("in_video"):
            heading += " (on camera, not in this video)"
        if entries or s.get("in_video", True):
            md += [heading, ""]
            if not entries:
                md += ["(no confirmed X accounts for this segment)", ""]
            else:
                for e in entries:
                    line = f"- @{e['handle']} (https://x.com/{e['handle']})"
                    if e.get("post"):
                        line += f" — {e['post']}"
                    md.append(line)
                md.append("")
    # Extra entities: handles.json may include a special "_entities" map of
    # { "09": [{"entity": "Nvidia", "handle": "nvidia"}, ...] }
    extra = handles.get("_entities") if isinstance(handles.get("_entities"), dict) else None
    # We stored both lower and raw keys; skip if we used a flattened map only.
    text = "\n".join(md).rstrip() + "\n"
    return attr_segs, text, unresolved


def write_attribution(segs, handles_path):
    handles = load_handles(handles_path)
    # Allow an "_entities" file alongside: if handles.json has a nested dict, keep it.
    raw = json.load(open(handles_path)) if handles_path and os.path.exists(handles_path) else {}
    entities_by_seg = raw.get("_entities") or {}
    attr_segs, text, unresolved = build_attribution(segs, handles)
    # Merge extra confirmed entities (companies, people) per segment.
    if entities_by_seg:
        lines = text.splitlines()
        rebuilt = []
        i = 0
        segs_by_num = {s["num"]: s for s in attr_segs}
        while i < len(lines):
            rebuilt.append(lines[i])
            m = re.match(r"^## (\S+)", lines[i])
            if m and m.group(1) in entities_by_seg:
                num = m.group(1)
                s = segs_by_num.get(num)
                existing = {(e["handle"].lower(), e.get("post") or "") for e in (s["entries"] if s else [])}
                i += 1
                # copy existing bullet lines
                while i < len(lines) and not lines[i].startswith("## "):
                    rebuilt.append(lines[i]); i += 1
                # insert extras before the blank that precedes the next heading — do it by appending now
                # We already copied the block; append extras just before we continue.
                # Simpler: add to entries and regenerate. Do that instead.
                continue
            i += 1
        # Cleaner path: add extras to entries and regenerate once.
        for s in attr_segs:
            extras = entities_by_seg.get(s["num"]) or []
            seen = {(e["handle"].lower(), e.get("post") or "") for e in s["entries"]}
            for item in extras:
                if isinstance(item, str):
                    continue
                handle = str(item.get("handle") or "").lstrip("@")
                if not handle:
                    continue
                key = (handle.lower(), "")
                if key in seen:
                    continue
                seen.add(key)
                s["entries"].append({"handle": handle, "role": item.get("role") or "related",
                                     "post": None, "entity": item.get("entity")})
        # regenerate markdown from attr_segs
        md = ["# Credits", "",
              "Accounts to paste into the video post. Each line is an @handle and its X profile.",
              "Shown X posts also get a direct link. No YouTube, news-site, or GitHub Pages URLs.",
              ""]
        for s in attr_segs:
            heading = f"## {s['num']} · {s['title']}"
            if s.get("on_camera") and not s.get("in_video"):
                heading += " (on camera, not in this video)"
            md += [heading, ""]
            if not s["entries"]:
                md += ["(no confirmed X accounts for this segment)", ""]
            else:
                for e in s["entries"]:
                    line = f"- @{e['handle']} (https://x.com/{e['handle']})"
                    if e.get("post"):
                        line += f" — {e['post']}"
                    md.append(line)
                md.append("")
        text = "\n".join(md).rstrip() + "\n"
    open(C("post-attribution.md"), "w").write(text)
    json.dump({"segments": attr_segs, "unresolved": unresolved}, open(C("attribution.json"), "w"), indent=1)
    report["unresolved"] = unresolved
    return unresolved


# ---------------------------------------------------------------- main
def parse_args():
    p = argparse.ArgumentParser(description="Build an edition video on the render host.")
    p.add_argument("workdir")
    p.add_argument("--segment", action="append", dest="segments", default=[],
                   help="Only render this segment number (repeatable), e.g. --segment 09")
    p.add_argument("--include-edition", action="store_true",
                   help="Include GitHub Pages edition-page shots (off by default).")
    p.add_argument("--include-open-close", action="store_true",
                   help="Render Cold open / Sign-off instead of leaving them on camera.")
    p.add_argument("--no-dark", action="store_true", help="Capture pages and cards in light mode.")
    p.add_argument("--output", default="final.mp4", help="Output filename inside the workdir.")
    args = p.parse_args()
    env_segs = os.environ.get("EV_SEGMENTS", "")
    if env_segs:
        args.segments.extend([s.strip() for s in re.split(r"[,\s]+", env_segs) if s.strip()])
    if os.environ.get("EV_INCLUDE_EDITION") in {"1", "true", "yes"}:
        args.include_edition = True
    if os.environ.get("EV_INCLUDE_OPEN_CLOSE") in {"1", "true", "yes"}:
        args.include_open_close = True
    if os.environ.get("EV_DARK") in {"0", "false", "no"} or os.environ.get("EV_NO_DARK") in {"1", "true"}:
        args.no_dark = True
    if os.environ.get("EV_OUTPUT"):
        args.output = os.environ["EV_OUTPUT"]
    return args


def main():
    global WD, C, DARK, BG, THEME_TAG, report
    args = parse_args()
    WD = os.path.abspath(args.workdir)
    C = lambda *p: os.path.join(WD, *p)  # noqa
    DARK = not args.no_dark
    THEME_TAG = "dark" if DARK else "light"
    BG = (11, 13, 18) if DARK else (244, 246, 250)
    for d in ("cache/yt", "cache/page", "cache/card", "shots", "tmp"):
        os.makedirs(C(d), exist_ok=True)
    report = {"sources": {}, "failures": [], "substitutions": [], "xposts": [], "unresolved": [],
              "dark": DARK, "include_edition": args.include_edition}

    edition, segs = parse(C("script.md"), include_edition=args.include_edition,
                          include_open_close=args.include_open_close)
    merge_xposts(segs, C("xposts.json"))
    if args.segments:
        want = {s.lstrip("0") or "0" for s in args.segments} | set(args.segments)
        for s in segs:
            if s["num"] not in want and (s["num"].lstrip("0") or "0") not in want:
                s["_skip_render"] = True
    # resolve every distinct source once (downloads sequential to stay polite with YouTube)
    resolved = {}
    for s in segs:
        if s["on_camera"] or s.get("_skip_render"):
            continue
        if not s["visuals"]:
            # A video segment with no visuals gets a title card so the timeline still has picture.
            s["visuals"] = [{"kind": "card", "title": s["title"], "sub": "", "label": ""}]
        for v in s["visuals"]:
            key = json.dumps({k: v[k] for k in v if not k.startswith("_")}, sort_keys=True)
            if key in resolved:
                # keep channel meta if a later copy needs it
                if v["kind"] == "yt" and not v.get("_channel"):
                    v["_channel"] = yt_channel_meta(v["url"], vid_id(v["url"]))
                continue
            if v["kind"] == "yt":
                p = fetch_yt(v); time.sleep(2)
                if p:
                    resolved[key] = ("yt", p, v["label"])
                else:
                    t = yt_thumb(v)
                    resolved[key] = ("page", t, v["label"]) if t else ("card", card(v["label"], "YouTube"), "")
                    report["substitutions"].append({"source": v["url"], "used": "thumbnail" if t else "card"})
            elif v["kind"] == "xpost":
                p = fetch_xpost(v)
                if p:
                    resolved[key] = ("xpost", p, v["label"])
                else:
                    resolved[key] = ("card", card(v.get("label") or "X post", v.get("handle") or ""), "")
                    report["substitutions"].append({"source": v.get("url") or v.get("id"), "used": "title card"})
            elif v["kind"] == "page":
                p = fetch_page(v)
                if p:
                    resolved[key] = ("page", p, v["label"])
                else:
                    resolved[key] = ("card", card(v.get("fallback") or v["label"], v["label"]), "")
                    report["substitutions"].append({"source": v["url"], "used": "title card"})
            else:
                resolved[key] = ("card", card(v["title"], v["sub"]), v["label"])
    # timeline — on-camera and filtered segments do not consume video time
    shots, timeline, t_frames, uses = [], [], 0, {}
    for s in segs:
        words = len(s["narration"].split())
        if s["on_camera"] or s.get("_skip_render"):
            s["in_video"] = False
            timeline.append({"num": s["num"], "title": s["title"], "start": None,
                             "duration": words / WPS + PAD, "words": words, "shots": 0,
                             "on_camera": s["on_camera"], "in_video": False, "sources": []})
            continue
        s["in_video"] = True
        vis = s["visuals"]
        seg_frames = round((words / WPS + PAD) * FPS)
        n = max(1, round(seg_frames / (SHOT * FPS)))
        base, extra = divmod(seg_frames, n)
        src_kinds = []
        for v in vis:
            key = json.dumps({k: v[k] for k in v if not k.startswith("_")}, sort_keys=True)
            src_kinds.append(resolved[key][0])
        timeline.append({"num": s["num"], "title": s["title"], "start": t_frames / FPS,
                         "duration": seg_frames / FPS, "words": words, "shots": n,
                         "on_camera": False, "in_video": True, "sources": sorted(set(src_kinds))})
        for j in range(n):
            v = vis[j % len(vis)]
            key = json.dumps({k: v[k] for k in v if not k.startswith("_")}, sort_keys=True)
            kind, path, label = resolved[key]
            k = uses.get(path, 0); uses[path] = k + 1
            shots.append({"i": len(shots), "frames": base + (1 if j < extra else 0), "src": path,
                          "kind": kind, "use": k, "label": label, "seg": s["num"]})
        t_frames += seg_frames
    if not shots:
        raise SystemExit("no video segments to render (all on camera, or --segment matched none)")
    with ThreadPoolExecutor(JOBS) as ex:
        outs = list(ex.map(render_shot, shots))
    with open(C("tmp", "concat.txt"), "w") as f:
        for o in outs:
            f.write(f"file '{o}'\n")
    total = t_frames / FPS
    out_mp4 = C(args.output)
    r = run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", C("tmp", "concat.txt"),
             "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
             "-t", f"{total:.3f}", "-movflags", "+faststart", out_mp4], timeout=1800)
    if r.returncode != 0:
        raise SystemExit(r.stderr[-1500:])
    # teleprompter — on-camera sections first/last, video clock starts at 00:00.0
    tp = [f"# Teleprompter: {os.path.basename(WD)}", "",
          f"Video {tc(total)} · read at about {int(WPS*60)} words a minute · each video segment ends with a short breath.",
          "Cold open and sign-off are on camera with no video in this file, unless a segment says otherwise. The first story starts at 00:00.0.", ""]
    for s, tl in zip(segs, timeline):
        if tl.get("on_camera") or not tl.get("in_video"):
            if s["on_camera"]:
                est = tc(tl["duration"])
                tp += [f"## [on camera · no video] {s['num']} · {s['title']}", "",
                       f"Film this yourself. About {est} if you read at {int(WPS*60)} words a minute.", "",
                       s["narration"], ""]
            # skipped-by--segment sections are omitted from the teleprompter
        else:
            tp += [f"## [{tc(tl['start'])}] {s['num']} · {s['title']}", "", s["narration"], ""]
    open(C("teleprompter.md"), "w").write("\n".join(tp))
    json.dump({"total_seconds": total, "segments": timeline, "shots": len(shots), "dark": DARK,
               "output": args.output}, open(C("timeline.json"), "w"), indent=1)
    write_attribution(segs, C("handles.json"))
    # de-dup xposts list (auto merge + render both append)
    seen, uniq = set(), []
    for xp in report["xposts"]:
        k = (xp.get("id"), xp.get("render") or xp.get("source"))
        if k in seen:
            continue
        seen.add(k); uniq.append(xp)
    report["xposts"] = uniq
    report["total_seconds"] = total
    report["segments"] = len([s for s in segs if s.get("in_video")])
    report["shots"] = len(shots)
    report["output"] = args.output
    json.dump(report, open(C("report.json"), "w"), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
