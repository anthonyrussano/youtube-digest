#!/usr/bin/env python3
"""Still frame from a cited YouTube video at a timestamp -> PNG (X Article "video-frame" images).

  ./run.sh yt-frame <video_id|url> <seconds> <out.png>

Runs on the remote yt-dlp host (config/whisper.json, same as ytrun.py) so YouTube sees the home IP; falls back
to the box only when that host is unreachable. Never uses cookies. Downloads only "*T-2-T+3" (best video
<=1080p, no audio), grabs 9 frames from T-1 to T+1, picks the sharpest (ffmpeg blurdetect, lowest blur; PNG
size as fallback score), scales to 2400 px wide (never upscales), copies it to <out.png>, removes temp files.
"""
import os, re, shlex, subprocess, sys, tempfile, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import ytrun

# bash, run with: bash -s <ytdlp> <url> <T> <workdir>; prints "@@BEST@@ <path> <score>"
JOB = r'''
set -u; Y=$1; URL=$2; T=$3; D=$4; mkdir -p "$D"; cd "$D" || exit 1
S=$(awk -v t="$T" 'BEGIN{s=t-2; if(s<0)s=0; print s}'); E=$(awk -v t="$T" 'BEGIN{print t+3}')
$Y --no-playlist --no-cookies -q --no-warnings -f "bv*[height<=1080][vcodec!=none]/bv*[height<=1080]" \
   --download-sections "*$S-$E" --force-keyframes-at-cuts -o "clip.%(ext)s" "$URL" || exit 3
C=$(ls clip.* 2>/dev/null | grep -v -e '\.part$' -e '\.ytdl$' | head -1); [ -n "$C" ] || exit 4
O=$(awk -v t="$T" -v s="$S" 'BEGIN{print t-s}')   # offset of T inside the clip
best=""; bs=""
for d in -1.0 -0.75 -0.5 -0.25 0 0.25 0.5 0.75 1.0; do
  at=$(awk -v o="$O" -v d="$d" 'BEGIN{x=o+d; if(x<0)x=0; print x}'); f="f_$d.png"
  ffmpeg -nostdin -loglevel error -y -ss "$at" -i "$C" -frames:v 1 "$f" || continue
  b=$(ffmpeg -nostdin -hide_banner -i "$f" -vf blurdetect,metadata=print:file=- -f null - 2>/dev/null \
      | sed -n 's/.*lavfi.blur=\([0-9.]*\).*/\1/p' | head -1)
  [ -n "$b" ] || b=$(awk -v s="$(stat -c %s "$f")" 'BEGIN{print 1e9/s}')   # fallback: bigger PNG = more detail
  if [ -z "$bs" ] || awk -v a="$b" -v c="$bs" 'BEGIN{exit !(a<c)}'; then best=$f; bs=$b; fi
done
[ -n "$best" ] || exit 5
ffmpeg -nostdin -loglevel error -y -i "$best" -vf "scale='min(2400,iw)':-2:flags=lanczos" out.png || exit 6
echo "@@BEST@@ $best $bs"
'''

def main():
    if len(sys.argv) != 4: sys.exit(__doc__)
    vid, t, out = sys.argv[1:]
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", vid); vid = m.group(1) if m else vid
    if not re.fullmatch(r"[\w-]{11}", vid): sys.exit(f"bad video id: {vid}")
    t = str(float(t)); url = f"https://www.youtube.com/watch?v={vid}"
    tg = ytrun.target()
    if tg:
        rd = f"/tmp/grokbot-ytframe-{uuid.uuid4().hex[:10]}"
        try:
            r = subprocess.run(["ssh", *ytrun.SSH_OPTS, "-p", tg[1], tg[0], "bash -s " + " ".join(
                shlex.quote(a) for a in (ytrun.rbin(tg), url, t, rd)).replace(shlex.quote(ytrun.rbin(tg)), ytrun.rbin(tg))],
                input=JOB, capture_output=True, text=True, timeout=600)
            if "@@BEST@@" not in r.stdout: sys.exit(f"remote yt-frame failed rc={r.returncode}: {r.stderr.strip()[-400:]}")
            c = ytrun.scp_from([f"{rd}/out.png"], tempfile.mkdtemp(prefix="ytframe-"), 300, tg)
            src = c.args[-1] + "/out.png"
            if c.returncode != 0 or not os.path.exists(src): sys.exit(f"scp back failed: {c.stderr.strip()[-200:]}")
        finally:
            try: ytrun.ssh(f"rm -rf {rd}", 60, tg)
            except Exception: pass
    else:
        rd = tempfile.mkdtemp(prefix="ytframe-"); src = f"{rd}/out.png"
        r = subprocess.run(["bash", "-s", ytrun.LOCAL_BIN, url, t, rd], input=JOB, capture_output=True, text=True, timeout=600)
        if "@@BEST@@" not in r.stdout: sys.exit(f"local yt-frame failed rc={r.returncode}: {r.stderr.strip()[-400:]}")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    subprocess.run(["cp", src, out], check=True)
    subprocess.run(["rm", "-rf", os.path.dirname(src)])
    print(f"{out}  <- {url}&t={int(float(t))}s  (picked {r.stdout.split('@@BEST@@')[1].strip()})")

if __name__ == "__main__": main()
