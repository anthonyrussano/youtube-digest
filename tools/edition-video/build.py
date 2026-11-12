#!/usr/bin/env python3
"""Build a silent, voiceover-ready 1080p30 edition video from script.md.

Runs ON the render host (never on the box). Usage:
    python3 build.py WORKDIR
        [--segment 09] [--include-edition] [--on-camera-open-close]
        [--no-dark] [--no-music] [--output final.mp4]
Env: YTDLP, CHROMIUM, JOBS, EV_DARK=0, EV_INCLUDE_EDITION=1,
     EV_ON_CAMERA_OPEN_CLOSE=1, EV_NO_MUSIC=1, EV_SEGMENTS=09, EV_OUTPUT=final.mp4

script.md format (see tools/edition-video/README.md):
    Edition: <github pages url>
    ## NN Title
    Narration: one paragraph
    Style: montage                # optional; default for Cold open (beats in order, no cycle)
    Camera: self                  # opt-in only; omit that section from the MP4
    Visuals:
    - yt <url> @<seconds> | <label>
    - page <url> | <label> [| fallback title]
    - xpost <url-or-id> | <label>
    - card <title> | <subtitle>
    - stat <number> | <caption>
    - endcard <title> | <subtitle>
    - edition | <label>           # skipped unless --include-edition

Outputs: final.mp4, teleprompter.md, timeline.json, report.json,
         post-attribution.md, attribution.json, music.wav, music-license.txt
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
def _font(*paths):
    for pth in paths:
        if pth and os.path.exists(pth):
            return pth
    return paths[-1]

FONT_B = _font("/usr/share/fonts/noto/NotoSans-Bold.ttf",
               "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
FONT_R = _font("/usr/share/fonts/noto/NotoSans-Regular.ttf",
               "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
FONT_M = _font("/usr/share/fonts/noto/NotoSans-Medium.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", FONT_R)
FONT_L = _font("/usr/share/fonts/noto/NotoSans-Light.ttf", FONT_R)
FONT_K = _font("/usr/share/fonts/noto/NotoSans-Black.ttf", FONT_B)
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
def is_on_camera(title, body, on_camera_open_close=False):
    """On-camera is opt-in. Cold open / sign-off stay in the video unless
    --on-camera-open-close is set or the segment says Camera: self."""
    if FORCE_VIDEO.search(body or ""):
        return False
    if CAM_RE.search(body or "") or CAM_VIS.search(body or ""):
        return True
    if on_camera_open_close:
        return bool(ON_CAM_TITLES.match((title or "").strip()))
    return False


def parse(path, include_edition=False, on_camera_open_close=False, include_open_close=None):
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
        # historical alias: include_open_close meant "put open/close in the video"
        if include_open_close is not None and include_open_close:
            on_camera_open_close = False
        on_cam = is_on_camera(title, body, on_camera_open_close)
        vis = []
        skipped_edition = []
        style = ""
        sm = re.search(r"^Style:\s*(\w+)", body, re.I | re.M)
        if sm:
            style = sm.group(1).lower()
        if re.search(r"^Visuals:\s*montage\b", body, re.I | re.M):
            style = style or "montage"
        if not style and ON_CAM_TITLES.match((title or "").strip()):
            style = "montage" if re.search(r"cold open", title, re.I) else "end"
        vpart = body.split("Visuals:", 1)[1] if "Visuals:" in body else ""
        if vpart.lower().lstrip().startswith("montage"):
            vpart = re.sub(r"^\s*montage\s*", "", vpart, count=1, flags=re.I)
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
                elif kind in ("card", "endcard", "stat"):
                    st = "end" if kind == "endcard" or style == "end" else ("stat" if kind == "stat" else "title")
                    vis.append({"kind": "card", "title": parts[0], "sub": parts[1] if len(parts) > 1 else "",
                                "label": "", "style": st})
        segs.append({"num": num, "title": title, "narration": nar, "visuals": vis,
                     "on_camera": on_cam, "skipped_edition": skipped_edition, "style": style})
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



GOLD = (255, 196, 0)
INK = (245, 245, 245)
MUTED = (168, 178, 196)
HAIR = (255, 196, 0)

def _center(d, text, font, y, fill, width=W):
    """Draw left-top anchored, horizontally centered text. Returns the ink bbox."""
    w = d.textlength(text, font=font)
    x = (width - w) // 2
    d.text((x, y), text, font=font, fill=fill, anchor="lt")
    return d.textbbox((x, y), text, font=font, anchor="lt")


def _vignette_overlay(im, strength=0.42):
    """Darken the edges of a card so it sits in the same world as the grade."""
    import numpy as _np
    arr = _np.asarray(im, dtype=_np.float32)
    h, w = arr.shape[:2]
    ys, xs = _np.ogrid[:h, :w]
    r = _np.sqrt((xs - w / 2) ** 2 + (ys - h / 2) ** 2) / math.hypot(w / 2, h / 2)
    f = 1.0 - strength * _np.clip(r - 0.35, 0, None) ** 2
    arr *= f[..., None]
    return Image.fromarray(_np.clip(arr, 0, 255).astype("uint8"), "RGB")


def card(title, sub="", style="title"):
    out = C("cache/card", f"{h(title + '|' + sub + '|' + style + '|' + THEME_TAG)}.png")
    if os.path.exists(out):
        return out
    if DARK:
        top, bot = (10, 12, 16), (20, 24, 32)
        bar, ft_c, fs_c, kick_c = GOLD, INK, MUTED, GOLD
    else:
        top, bot = (244, 246, 250), (226, 230, 238)
        bar, ft_c, fs_c, kick_c = (30, 90, 200), (18, 20, 28), (70, 80, 100), (30, 90, 200)
    im = Image.new("RGB", (W, H), top)
    d = ImageDraw.Draw(im)
    for i in range(H):
        u = i / max(H - 1, 1)
        col = tuple(int(top[c] + (bot[c] - top[c]) * u) for c in range(3))
        d.line([(0, i), (W, i)], fill=col)
    style = (style or "title").lower()
    if style == "end":
        ft = ImageFont.truetype(FONT_B, 80)
        fs = ImageFont.truetype(FONT_L, 34)
        lines = wrap(d, title, ft, W - 360)[:3] or [title]
        sub_lines = wrap(d, sub, fs, W - 480)[:2] if sub else []
        line_h, sub_h, gap, rule_gap = 94, 48, 28, 28
        block_h = len(lines) * line_h + (gap + len(sub_lines) * sub_h if sub_lines else 0)
        y = (H - block_h) // 2
        rw = 140
        d.rectangle([(W - rw) // 2, y - rule_gap - 3, (W + rw) // 2, y - rule_gap], fill=bar)
        for ln in lines:
            _center(d, ln, ft, y, ft_c)
            y += line_h
        if sub_lines:
            y += gap - 8
            for ln in sub_lines:
                _center(d, ln, fs, y, fs_c)
                y += sub_h
    elif style == "stat":
        fs = ImageFont.truetype(FONT_L, 38)
        size = 168
        fn = ImageFont.truetype(FONT_K, size)
        while d.textlength(title, font=fn) > W - 260 and size > 96:
            size -= 12
            fn = ImageFont.truetype(FONT_K, size)
        sub_lines = wrap(d, sub, fs, W - 360)[:2] if sub else []
        # Measure first so the block can be vertically centered.
        dummy = ImageDraw.Draw(Image.new("RGB", (W, H)))
        tb = dummy.textbbox((0, 0), title, font=fn, anchor="lt")
        num_h = tb[3] - tb[1]
        sub_h = 50
        gap, rule = 22, 3
        block_h = num_h + ((gap + 16 + len(sub_lines) * sub_h) if sub_lines else 0)
        y = (H - block_h) // 2
        bbox = _center(d, title, fn, y, bar if DARK else ft_c)
        if sub_lines:
            ry = bbox[3] + gap
            rw = 88
            d.rectangle([(W - rw) // 2, ry, (W + rw) // 2, ry + rule], fill=bar)
            y2 = ry + rule + 16
            for ln in sub_lines:
                _center(d, ln, fs, y2, fs_c)
                y2 += sub_h
    else:
        ft, fs = ImageFont.truetype(FONT_B, 84), ImageFont.truetype(FONT_L, 38)
        lines = wrap(d, title, ft, W - 440)[:4] or [title]
        sub_lines = wrap(d, sub, fs, W - 480)[:2] if sub else []
        line_h, sub_h = 100, 50
        block_h = len(lines) * line_h + (36 + 16 + len(sub_lines) * sub_h if sub_lines else 0)
        y = (H - block_h) // 2
        # Gold index bar, sized to the type block.
        bar_top = y - 16
        bar_bot = y + block_h + 8
        d.rectangle([(140, bar_top), (154, bar_bot)], fill=bar)
        last = None
        for ln in lines:
            last = d.textbbox((200, y), ln, font=ft, anchor="lt")
            d.text((200, y), ln, font=ft, fill=ft_c, anchor="lt")
            y += line_h
        if sub_lines:
            ry = (last[3] if last else y) + 18
            d.rectangle([(200, ry), (320, ry + 3)], fill=bar)
            y2 = ry + 16
            for ln in sub_lines:
                d.text((200, y2), ln, font=fs, fill=fs_c, anchor="lt")
                y2 += sub_h
    im = _vignette_overlay(im, 0.38 if style == "end" else 0.32)
    im.save(out)
    return out


# ---------------------------------------------------------------- shots
def _ff_textfile(name, text):
    f = C("tmp", name)
    open(f, "w").write(text)
    return f


def label_filter(label, idx):
    if not label:
        return ""
    f = _ff_textfile(f"label_{idx}.txt", label)
    # Clean dark pill, gold tick, fades in over the first 0.3 s.
    return (
        f",drawbox=x=64:y=ih-128:w=8:h=48:color=0xFFC400@0.95:t=fill"
        f",drawtext=fontfile={FONT_M}:textfile={f}:fontsize=28:fontcolor=white:"
        f"y_align=font:box=1:boxcolor=black@0.48:boxborderw=18:"
        f"x=88:y=h-124:alpha='if(lt(t,0.30),t/0.30,1)'"
    )


def chapter_filter(num, title, idx):
    if not title:
        return ""
    f = _ff_textfile(f"chapter_{idx}.txt", f"{num}    {title}")
    # Fades in, holds, fades out over the first ~2.2 s of a segment's opening shot.
    alpha = "if(lt(t,0.22),t/0.22,if(lt(t,1.80),1,if(lt(t,2.25),(2.25-t)/0.45,0)))"
    return (
        f",drawtext=fontfile={FONT_M}:textfile={f}:fontsize=26:fontcolor=white@0.92:"
        f"x=72:y=68:box=1:boxcolor=black@0.45:boxborderw=14:alpha='{alpha}'"
    )


ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-g", str(FPS * 2), "-profile:v", "high", "-an"]

FINISH = ("eq=contrast=1.05:brightness=-0.016:gamma=0.98:saturation=0.94,"
          "vignette=angle=PI/5:mode=forward,noise=alls=2:allf=t")


def ken_burns(frames, kind, use):
    """Subtle push, pull, or pan. Varies with how many times this source has been used."""
    # z0, z1, x0, x1, y0, y1  (x/y are fractions of the leftover pan window)
    modes = [
        (1.00, 1.10, 0.50, 0.50, 0.50, 0.50),  # push in, centered
        (1.12, 1.02, 0.50, 0.50, 0.50, 0.50),  # pull out
        (1.08, 1.08, 0.28, 0.72, 0.50, 0.50),  # pan right
        (1.08, 1.08, 0.72, 0.28, 0.50, 0.50),  # pan left
        (1.06, 1.12, 0.50, 0.50, 0.62, 0.32),  # drift up
        (1.02, 1.10, 0.35, 0.60, 0.40, 0.60),  # diagonal
    ]
    if kind == "card":
        # Keep typography readable — a gentle 4–6% push, no hard pans.
        modes = [
            (1.00, 1.05, 0.50, 0.50, 0.50, 0.50),
            (1.05, 1.00, 0.50, 0.50, 0.50, 0.50),
            (1.00, 1.04, 0.50, 0.50, 0.55, 0.42),
            (1.02, 1.06, 0.48, 0.54, 0.50, 0.50),
        ]
    elif kind == "xpost":
        # Mild push or a short lateral drift; 80px letterbox pad keeps the tweet in frame.
        modes = [modes[0], modes[2], modes[3], modes[1]]
    z0, z1, x0, x1, y0, y1 = modes[use % len(modes)]
    n = max(frames - 1, 1)
    return (
        f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':d=1:"
        f"x='(iw-iw/zoom)*({x0}+({x1}-{x0})*on/{n})':"
        f"y='(ih-ih/zoom)*({y0}+({y1}-{y0})*on/{n})':"
        f"s={W}x{H}:fps={FPS}"
    )


def edge_fades(dur, fade_in, fade_out):
    parts = []
    if fade_in and fade_in > 0:
        parts.append(f"fade=t=in:st=0:d={fade_in:.3f}:c=black")
    if fade_out and fade_out > 0:
        st = max(dur - fade_out, 0.0)
        parts.append(f"fade=t=out:st={st:.3f}:d={fade_out:.3f}:c=black")
    return "," + ",".join(parts) if parts else ""


def render_shot(shot):
    i, frames, src, kind, k, label = shot["i"], shot["frames"], shot["src"], shot["kind"], shot["use"], shot["label"]
    out = C("shots", f"{i:03d}.mp4")
    dur = frames / FPS
    lf = "" if shot.get("no_label") or kind == "card" else label_filter(label, i)
    # Pages already have their own chrome; a chapter label collides with site nav.
    ch = chapter_filter(shot.get("chap_num") or "", shot.get("chap_title") or "", i) if (shot.get("chapter") and kind != "page") else ""
    fades = edge_fades(dur, shot.get("fade_in") or 0, shot.get("fade_out") or 0)
    # Cards already have a baked vignette; a second ffmpeg vignette crushes the edges.
    if kind == "card":
        finish = (f",eq=contrast=1.03:brightness=-0.006:gamma=1.0:saturation=0.98,"
                  f"noise=alls=1:allf=t{fades}{ch},format=yuv420p")
    else:
        finish = f",{FINISH}{fades}{ch},format=yuv420p"
    if kind == "yt":
        clip_len = YT_AFTER + YT_BEFORE - 0.5
        off = (YT_BEFORE + 3.2 * k) % max(clip_len - dur, 0.5)
        z = ken_burns(frames, "yt", k)
        vf = f"scale={W*2}:{H*2}:flags=bicubic,{z}{lf}{finish}"
        cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-ss", f"{off:.2f}", "-i", src, "-vf", vf,
               "-frames:v", str(frames), *ENC, out]
    else:
        im = Image.open(src); ih_ = im.height
        if kind in ("card", "xpost") or ih_ <= H + 40:
            z = ken_burns(frames, kind if kind in ("card", "xpost") else "page", k)
            vf = f"scale={W*2}:{H*2},{z}{lf}{finish}"
        else:
            span = 280
            y0 = (k * 900) % max(ih_ - H - span, 1)
            # Slow scroll, then a gentle push on alternate uses, already graded at the end.
            if k % 2 == 0 and ih_ > H + 80:
                y1 = min(y0 + span, ih_ - H)
                vf = (f"crop={W}:{H}:0:'{y0}+({y1}-{y0})*t/{dur:.3f}'{lf}{finish}")
            else:
                vf = f"crop={W}:{H}:0:{min(y0, ih_-H)},scale={W*2}:{H*2},{ken_burns(frames,'page',k)}{lf}{finish}"
        cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-i", src,
               "-vf", vf, "-frames:v", str(frames), *ENC, out]
    r = run(cmd, timeout=900)
    if r.returncode != 0:
        # Retry without grain if this ffmpeg build rejects the noise filter.
        if "noise" in (r.stderr or "") or r.returncode != 0:
            vf2 = vf.replace("noise=alls=2:allf=t", "null")
            if vf2 == vf or "vignette" in (r.stderr or ""):
                vf2 = vf.replace("," + FINISH, ",eq=contrast=1.05:brightness=-0.016:gamma=0.98:saturation=0.94")
            cmd[cmd.index("-vf") + 1] = vf2
            r = run(cmd, timeout=900)
        if r.returncode != 0:
            raise RuntimeError(f"shot {i} failed: {r.stderr[-600:]}")
    return out


def vis_key(v):
    return json.dumps({k: v[k] for k in v if not k.startswith("_")}, sort_keys=True)


def schedule_shots(vis, n, style, resolved):
    """Pick n visuals. Montage: one pass in script order, no cycle.
    Otherwise cycle, but never let the same kind run more than twice in a row
    when another kind is available (insert a title card if we have to)."""
    if not vis:
        return []
    kinds = []
    for v in vis:
        kinds.append(resolved[vis_key(v)][0])
    if style in ("montage", "end") or n <= len(vis):
        # Even split, stay in order, do not wrap back to earlier beats.
        count = min(n, len(vis)) if style in ("montage", "end") else n
        if style in ("montage", "end"):
            return [vis[j] for j in range(len(vis))]  # caller splits time across all beats
    # Regular cycle with a 2-in-a-row cap.
    used = [0] * len(vis)
    order, seq_kinds = [], []
    for j in range(n):
        last2 = seq_kinds[-2:] if len(seq_kinds) >= 2 else []
        ranked = sorted(range(len(vis)), key=lambda i: (used[i], i if (j % len(vis)) <= i else i + len(vis)))
        # prefer the next in the original cycle if it is legal
        prefer = j % len(vis)
        ranked = [prefer] + [i for i in ranked if i != prefer]
        pick = None
        for i in ranked:
            knd = kinds[i]
            if len(last2) == 2 and last2[0] == last2[1] == knd:
                continue
            pick = i
            break
        if pick is None:
            pick = ranked[0]
        used[pick] += 1
        order.append(vis[pick])
        seq_kinds.append(kinds[pick])
    return order



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
            seen = {e["handle"].lower() for e in s["entries"]}
            for item in extras:
                if isinstance(item, str):
                    continue
                handle = str(item.get("handle") or "").lstrip("@")
                if not handle:
                    continue
                if handle.lower() in seen:
                    continue
                seen.add(handle.lower())
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
    p.add_argument("--on-camera-open-close", action="store_true",
                   help="Leave Cold open / Sign-off out of the MP4 so they can be filmed. Off by default.")
    p.add_argument("--no-dark", action="store_true", help="Capture pages and cards in light mode.")
    p.add_argument("--no-music", action="store_true",
                   help="Silent AAC bed instead of the procedural chillwave music.")
    p.add_argument("--output", default="final.mp4", help="Output filename inside the workdir.")
    args = p.parse_args()
    env_segs = os.environ.get("EV_SEGMENTS", "")
    if env_segs:
        args.segments.extend([s.strip() for s in re.split(r"[,\s]+", env_segs) if s.strip()])
    if os.environ.get("EV_INCLUDE_EDITION") in {"1", "true", "yes"}:
        args.include_edition = True
    if os.environ.get("EV_ON_CAMERA_OPEN_CLOSE") in {"1", "true", "yes"}:
        args.on_camera_open_close = True
    if os.environ.get("EV_DARK") in {"0", "false", "no"} or os.environ.get("EV_NO_DARK") in {"1", "true"}:
        args.no_dark = True
    if os.environ.get("EV_NO_MUSIC") in {"1", "true", "yes"}:
        args.no_music = True
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
              "dark": DARK, "include_edition": args.include_edition, "music": None}

    edition, segs = parse(C("script.md"), include_edition=args.include_edition,
                          on_camera_open_close=args.on_camera_open_close)
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
            style = "end" if (s.get("style") == "end" or re.search(r"sign-?off|outro", s["title"], re.I)) else "title"
            s["visuals"] = [{"kind": "card", "title": s["title"], "sub": "", "label": "", "style": style}]
        for v in s["visuals"]:
            key = vis_key(v)
            if key in resolved:
                if v["kind"] == "yt" and not v.get("_channel"):
                    v["_channel"] = yt_channel_meta(v["url"], vid_id(v["url"]))
                continue
            if v["kind"] == "yt":
                pth = fetch_yt(v); time.sleep(2)
                if pth:
                    resolved[key] = ("yt", pth, v["label"])
                else:
                    th = yt_thumb(v)
                    resolved[key] = ("page", th, v["label"]) if th else ("card", card(v["label"], "YouTube"), "")
                    report["substitutions"].append({"source": v["url"], "used": "thumbnail" if th else "card"})
            elif v["kind"] == "xpost":
                pth = fetch_xpost(v)
                if pth:
                    resolved[key] = ("xpost", pth, v["label"])
                else:
                    resolved[key] = ("card", card(v.get("label") or "X post", v.get("handle") or ""), "")
                    report["substitutions"].append({"source": v.get("url") or v.get("id"), "used": "title card"})
            elif v["kind"] == "page":
                pth = fetch_page(v)
                if pth:
                    resolved[key] = ("page", pth, v["label"])
                else:
                    resolved[key] = ("card", card(v.get("fallback") or v["label"], v["label"], "title"), "")
                    report["substitutions"].append({"source": v["url"], "used": "title card"})
            else:
                resolved[key] = ("card", card(v["title"], v.get("sub") or "", v.get("style") or "title"), v.get("label") or "")
    # timeline
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
        style = s.get("style") or ""
        seg_frames = round((words / WPS + PAD) * FPS)
        if style in ("montage", "end"):
            order = schedule_shots(vis, len(vis), style, resolved)
            n = max(1, len(order))
        else:
            n = max(1, round(seg_frames / (SHOT * FPS)))
            order = schedule_shots(vis, n, style, resolved)
            n = max(1, len(order))
        base, extra = divmod(seg_frames, n)
        src_kinds = []
        for v in order:
            src_kinds.append(resolved[vis_key(v)][0])
        timeline.append({"num": s["num"], "title": s["title"], "start": t_frames / FPS,
                         "duration": seg_frames / FPS, "words": words, "shots": n,
                         "on_camera": False, "in_video": True, "sources": sorted(set(src_kinds)),
                         "style": style})
        for j, v in enumerate(order):
            kind, path, label = resolved[vis_key(v)]
            k = uses.get(path, 0); uses[path] = k + 1
            shots.append({"i": len(shots), "frames": base + (1 if j < extra else 0), "src": path,
                          "kind": kind, "use": k, "label": label, "seg": s["num"],
                          "no_label": (kind == "card" or style == "end")})
        t_frames += seg_frames
    if not shots:
        raise SystemExit("no video segments to render (all on camera, or --segment matched none)")
    # Dip-to-black between segments (uses the breath at the end of each), longer
    # fade on the first and last shots of the whole video. Chapter title on the
    # first picture shot of a regular story.
    by_seg = {}
    for sh in shots:
        by_seg.setdefault(sh["seg"], []).append(sh)
    video_nums = [s["num"] for s in segs if s.get("in_video")]
    styles = {s["num"]: (s.get("style") or "", s["title"]) for s in segs}
    for si, num in enumerate(video_nums):
        group = by_seg[num]
        mid = 0.33
        group[0]["fade_in"] = 0.80 if si == 0 else mid
        group[-1]["fade_out"] = 1.50 if si == len(video_nums) - 1 else mid
        st, title = styles[num]
        if st not in ("montage", "end") and not ON_CAM_TITLES.match(title.strip()):
            for sh in group:
                if sh["kind"] != "card":
                    sh["chapter"] = True
                    sh["chap_num"] = num
                    sh["chap_title"] = title
                    break
    with ThreadPoolExecutor(JOBS) as ex:
        outs = list(ex.map(render_shot, shots))
    with open(C("tmp", "concat.txt"), "w") as f:
        for o in outs:
            f.write(f"file '{o}'\n")
    total = t_frames / FPS
    out_mp4 = C(args.output)
    if not args.no_music:
        sys.path.insert(0, HERE)
        from music import render_bed
        minfo = render_bed(total + 0.4, C("music.wav"), C("music-license.txt"),
                           fade_in=2.0, fade_out=4.5)
        report["music"] = minfo
        concat = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error",
                  "-f", "concat", "-safe", "0", "-i", C("tmp", "concat.txt"),
                  "-i", C("music.wav"),
                  "-map", "0:v", "-map", "1:a",
                  "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                  "-t", f"{total:.3f}", "-movflags", "+faststart", out_mp4]
    else:
        report["music"] = {"disabled": True}
        concat = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error",
                  "-f", "concat", "-safe", "0", "-i", C("tmp", "concat.txt"),
                  "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
                  "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
                  "-t", f"{total:.3f}", "-movflags", "+faststart", out_mp4]
    r = run(concat, timeout=1800)
    if r.returncode != 0:
        raise SystemExit(r.stderr[-1500:])
    # teleprompter — video clock starts at 00:00.0, including the cold open.
    tp = [f"# Teleprompter: {os.path.basename(WD)}", "",
          f"Video {tc(total)} · read at about {int(WPS*60)} words a minute · each segment ends with a short breath.",
          "Voiceover only. A quiet music bed sits under the picture; music.wav is saved next to the video so you can adjust it.",
          ""]
    if args.no_music:
        tp[3] = "Voiceover only. This cut has no music bed."
    for s, tl in zip(segs, timeline):
        if tl.get("on_camera") or not tl.get("in_video"):
            if s["on_camera"]:
                est = tc(tl["duration"])
                tp += [f"## [on camera · no video] {s['num']} · {s['title']}", "",
                       f"Film this yourself. About {est} if you read at {int(WPS*60)} words a minute.", "",
                       s["narration"], ""]
        else:
            tp += [f"## [{tc(tl['start'])}] {s['num']} · {s['title']}", "", s["narration"], ""]
    open(C("teleprompter.md"), "w").write("\n".join(tp))
    json.dump({"total_seconds": total, "segments": timeline, "shots": len(shots), "dark": DARK,
               "output": args.output, "music": report.get("music")}, open(C("timeline.json"), "w"), indent=1)
    write_attribution(segs, C("handles.json"))
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
