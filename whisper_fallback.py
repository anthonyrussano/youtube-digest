#!/usr/bin/env python3
"""Whisper fallback for relevant videos without English captions. See README.md "Whisper fallback".

Backends are tried in order; the first that is available and succeeds wins:
  1. remote  - whisper.cpp (Vulkan GPU) in Docker on a home server over ssh (WHISPER_REMOTE=user@host[:port]).
               Skipped when unset or unreachable (one TCP connect, short timeout); any failure falls through to local.
  2. local   - faster-whisper on CPU (int8), each video in its own subprocess with a wall-time
               cap and an RSS cap (polled; process group killed). Audio is downloaded with yt-dlp and deleted after.
Only data/relevant.json and data/transcripts/ are written; state/ (seen/published) is never touched.
"""
import argparse, json, os, resource, shlex, signal, socket, subprocess, sys, time
import ytrun   # yt-dlp on the box, or over ssh on the remote host (config/whisper.json "ytdlp_remote")
ROOT = os.path.dirname(os.path.abspath(__file__))
PY = f"{ROOT}/.venv/bin/python"; YTDLP = f"{ROOT}/.venv/bin/yt-dlp"
REL = f"{ROOT}/data/relevant.json"; AUDIO = f"{ROOT}/data/audio"
CFG = f"{ROOT}/config/whisper.json"   # optional: {"remote": "host:port", "model": ..., ...}

def cfg():
    try: c = json.load(open(CFG))
    except Exception: c = {}
    if os.environ.get("WHISPER_REMOTE") is not None: c["remote"] = os.environ["WHISPER_REMOTE"]
    return c

def load(): return json.load(open(REL))
def update(vid, fields):
    """Re-read and patch one entry so concurrent edits to other entries are kept."""
    rel = load()
    for v in rel:
        if v["id"] == vid: v.update(fields)
    tmp = REL + ".tmp"; json.dump(rel, open(tmp, "w"), indent=1); os.replace(tmp, REL)

def write_transcript(vid, segs):
    os.makedirs(f"{ROOT}/data/transcripts", exist_ok=True)
    with open(f"{ROOT}/data/transcripts/{vid}.txt", "w") as fh:   # same "[seconds] text" format as captions
        for t, txt in segs:
            if txt.strip(): fh.write(f"[{int(t)}] {txt.strip()}\n")

def _rss_mb(pid):
    try:
        for l in open(f"/proc/{pid}/status"):
            if l.startswith("VmRSS:"): return int(l.split()[1]) // 1024
    except Exception: pass
    return 0

def run_capped(cmd, timeout, mem_mb=None):
    """Run cmd in its own process group; SIGKILL it at the wall-time cap or when its RSS exceeds mem_mb
    (polled every 0.25 s; RLIMIT_AS is unusable here because ctranslate2/OpenMP reserve far more virtual
    memory than they touch). Returns (rc, None on timeout, "MEM" on memory kill; peak RSS MB; stdout; stderr)."""
    import tempfile
    o, e = tempfile.TemporaryFile("w+"), tempfile.TemporaryFile("w+")
    p = subprocess.Popen(cmd, stdout=o, stderr=e, text=True, start_new_session=True)
    t0, peak, rc = time.time(), 0, None
    while p.poll() is None:
        peak = max(peak, _rss_mb(p.pid))
        if time.time() - t0 > timeout: rc = None; break
        if mem_mb and peak > mem_mb: rc = "MEM"; break
        time.sleep(0.25)
    else: rc = p.returncode
    if p.poll() is None: os.killpg(p.pid, signal.SIGKILL); p.wait()
    o.seek(0); e.seek(0); out, err = o.read(), e.read()
    try: peak = max(peak, json.loads(out.strip().splitlines()[-1]).get("peak_rss_mb") or 0)   # worker's own ru_maxrss
    except Exception: pass
    return rc, peak, out, err

# ---------------- backends ----------------
class Backend:
    name = "base"
    def available(self): return False, "not implemented"
    def transcribe(self, v, opts): raise NotImplementedError   # -> dict(ok, segs|error, model, peak_rss_mb)

REMOTE_DIR = "grokbot-whisper"   # on the GPU host, relative to the ssh user's home
REMOTE_IMAGE = "grokbot-whisper:vulkan"
SSH_OPTS = ytrun.SSH_OPTS   # BatchMode + multiplexed connection

class RemoteBackend(Backend):
    """whisper.cpp (Vulkan) in a Docker image on a GPU host reached over ssh (WHISPER_REMOTE=user@host[:port]).
    The box downloads audio, converts it to 16 kHz mono WAV, scp's it to ~/grokbot-whisper/in/, runs
    `docker run --rm` over ssh, pulls the JSON back and deletes the remote audio and transcript."""
    name = "remote"
    def __init__(self, target, timeout=2.0, model="large-v3-turbo"):
        self.target, self.timeout, self.model = target, timeout, model
        self.dest, _, port = target.rpartition(":") if target and ":" in target else (target, "", "22")
        self.port = port or "22"
    def available(self):
        if not self.target: return False, "WHISPER_REMOTE unset"
        # `ssh true`, not a bare TCP connect: preauth disconnects trip sshd PerSourcePenalties on the host
        rc, _, _, err = run_capped(["ssh", *SSH_OPTS, "-o", f"ConnectTimeout={max(int(self.timeout), 2)}", "-p", self.port,
                                    self.dest, "true"], max(self.timeout, 2) + 10)
        if rc != 0: return False, f"unreachable ({(err.strip().splitlines() or [str(rc)])[-1][:100]})"
        return True, "reachable"
    def ssh(self, cmd, timeout):
        return run_capped(["ssh", *SSH_OPTS, "-p", self.port, self.dest, cmd], timeout)
    def transcribe(self, v, opts):
        vid = v["id"]; wav = f"{AUDIO}/{vid}.wav"; js = f"{AUDIO}/{vid}.json"; m = opts.remote_model
        rin, rout = f"{REMOTE_DIR}/in/{vid}.wav", f"{REMOTE_DIR}/out/{vid}"
        try:
            yt = ytrun.target()
            if yt and yt[0] == self.dest and yt[1] == self.port:
                # yt-dlp runs on the GPU host itself: download + convert straight into ~/grokbot-whisper/in/,
                # so no audio crosses the tunnel (the box is bot-blocked by YouTube anyway)
                src = f"{REMOTE_DIR}/in/{vid}.src"
                dl = (f"cd ~ && for i in 1 2; do {ytrun.rbin(yt)} -f {shlex.quote(AUDIO_FMT)} --no-playlist -q --no-warnings "
                      f"-o '{src}.%(ext)s' {shlex.quote(v['url'])} && break; sleep 10; done; "
                      f"f=$(ls {src}.* 2>/dev/null | grep -v -e '\\.part$' -e '\\.ytdl$' | head -1); "
                      f"[ -n \"$f\" ] || {{ echo 'audio download failed' >&2; exit 3; }}; "
                      f"ffmpeg -v error -y -i \"$f\" -ac 1 -ar 16000 {rin}; rc=$?; rm -f {src}.*; exit $rc")
                rc, _, out, err = self.ssh(dl, opts.dl_timeout + 600)
                if rc != 0:
                    e = (err or out).strip()
                    return {"ok": False, "model": m, "error": "remote audio download " + ("timed out" if rc is None else
                            ("429" if "429" in e else e.splitlines()[-1][-200:] if e else f"rc={rc}"))}
            else:
                audio, err = download_audio(v, opts)
                if not audio: return {"ok": False, "error": err, "model": m}
                rc, _, _, err = run_capped(["ffmpeg", "-v", "error", "-y", "-i", audio, "-ac", "1", "-ar", "16000", wav], 600)
                if rc != 0: return {"ok": False, "error": f"ffmpeg rc={rc}: {err.strip()[-200:]}", "model": m}
                rc, _, _, err = run_capped(["scp", *SSH_OPTS, "-q", "-P", self.port, wav, f"{self.dest}:{rin}"], 900)
                if rc != 0: return {"ok": False, "error": f"scp upload rc={rc}: {err.strip()[-200:]}", "model": m}
            run = (f"cd ~/{REMOTE_DIR} && docker run --rm --name grokbot-whisper-{vid.replace('_','x').lstrip('-')} "
                   f"--device /dev/dri --group-add $(getent group video | cut -d: -f3) "
                   f"--group-add $(getent group render | cut -d: -f3) --user $(id -u):$(id -g) "
                   f"-v $PWD:/w {REMOTE_IMAGE} -m /w/models/ggml-{m}.bin -f /w/in/{vid}.wav -l en -t 8 "
                   f"-oj -of /w/out/{vid} 2>&1 >/dev/null | grep -E 'ggml_vulkan: 0 =|using Vulkan|error' | head -3")
            rc, _, out, err = self.ssh(run, opts.timeout)
            if rc != 0: return {"ok": False, "error": f"remote run rc={rc}: {(err or out).strip()[-200:]}", "model": m}
            print(f"  remote: {out.strip().splitlines()[0] if out.strip() else 'no vulkan line'}", flush=True)
            rc, _, _, err = run_capped(["scp", *SSH_OPTS, "-q", "-P", self.port, f"{self.dest}:{rout}.json", js], 300)
            if rc != 0: return {"ok": False, "error": f"scp download rc={rc}: {err.strip()[-200:]}", "model": m}
            segs = [(t["offsets"]["from"] / 1000, t["text"]) for t in json.load(open(js, errors="replace"))["transcription"]]
            er = english_ratio(segs)
            if er < opts.min_english:
                return {"ok": False, "error": f"audio not English (function-word ratio {er:.2f})", "model": m}
            return {"ok": True, "segs": segs, "model": m}
        except Exception as e:
            return {"ok": False, "error": f"{e.__class__.__name__}: {e}"[:200], "model": m}
        finally:
            try: self.ssh(f"rm -f ~/{rin} ~/{rout}.json ~/{REMOTE_DIR}/in/{vid}.src.*", 30)   # never keep audio/transcripts on the host
            except Exception: pass
            cleanup(vid)

def cleanup(vid):
    for f in os.listdir(AUDIO) if os.path.isdir(AUDIO) else []:   # audio, wav, segs json, chunk wav
        if f.startswith(vid + "."): os.remove(f"{AUDIO}/{f}")   # never keep audio

AUDIO_FMT = "wa[format_note*=original][protocol^=http]/wa[language^=en][protocol^=http]/wa[protocol^=http]/wa"

def download_audio(v, opts):
    """-> (path, None) or (None, error). Lowest-bitrate audio-only DASH stream of the ORIGINAL track: many
    videos carry auto-dubbed tracks (ar, de, ...) and plain "worstaudio" can pick one of those or a slow m3u8 variant."""
    os.makedirs(AUDIO, exist_ok=True); base = f"{AUDIO}/{v['id']}"
    remote = ytrun.target()   # remote yt-dlp host: download there, scp the audio back for local CPU whisper
    for attempt in range(2):   # YouTube's media CDN returns sporadic 403s; one retry usually clears it
        if remote:
            try:
                r = ytrun.run_files(["-f", AUDIO_FMT, "--no-playlist", "-q", "--no-warnings", "-o", "{OUT}/" + v["id"] + ".%(ext)s",
                                     v["url"]], AUDIO, opts.dl_timeout + 300)
                rc, err = r.returncode, r.stderr
            except subprocess.TimeoutExpired: rc, err = None, ""
        else:
            rc, _, _, err = run_capped([YTDLP, "-f", AUDIO_FMT, "--no-playlist", "-q", "--no-warnings",
                                        "-o", base + ".%(ext)s", v["url"]], opts.dl_timeout)
        if rc == 0 or "403" not in err: break
        time.sleep(10)
    files = [f for f in os.listdir(AUDIO) if f.startswith(v["id"] + ".") and not f.endswith((".part", ".ytdl", ".wav", ".json"))]
    if rc != 0 or not files:
        return None, "audio download " + ("timed out" if rc is None else
               ("429" if "429" in err else err.strip().splitlines()[-1][-200:] if err.strip() else f"rc={rc}"))
    return f"{AUDIO}/{files[0]}", None

class LocalCPUBackend(Backend):
    name = "local"
    def available(self):
        try: import faster_whisper  # noqa
        except Exception: return False, "faster-whisper not installed in .venv"
        return True, "ok"
    def transcribe(self, v, opts):
        base = f"{AUDIO}/{v['id']}"
        try:
            audio, err = download_audio(v, opts)
            if not audio: return {"ok": False, "error": err}
            out = f"{base}.segs.json"
            rc, rss, _, err = run_capped([PY, __file__, "_worker", audio, out, opts.model, str(opts.threads)],
                                         opts.timeout, opts.mem_mb)
            if rc != 0:
                why = f"timed out after {opts.timeout}s" if rc is None else \
                      (f"killed: RSS over {opts.mem_mb} MB" if rc == "MEM" else f"worker rc={rc}: {err.strip()[-200:]}")
                return {"ok": False, "error": why, "model": opts.model, "peak_rss_mb": rss}
            segs = json.load(open(out)); er = english_ratio(segs)
            if er < opts.min_english:
                return {"ok": False, "error": f"audio not English (function-word ratio {er:.2f})", "model": opts.model, "peak_rss_mb": rss}
            return {"ok": True, "segs": segs, "model": opts.model, "peak_rss_mb": rss}
        finally:
            cleanup(v["id"])

EN = set("the a an and or but of to in on for with is are was were be it that this you i we they he she not have has do".split())
def english_ratio(segs):
    """Share of common English function words. .en models 'transliterate' foreign speech into gibberish
    (seen on an Arabic video: ~0.05); real English speech scores ~0.3+."""
    w = [x.strip(".,!?\"'").lower() for _, t in segs for x in t.split()]
    return sum(x in EN for x in w) / max(len(w), 1)

def worker(audio, out, model, threads, chunk_s=600):
    """Transcribe in chunk_s pieces so memory stays flat: faster-whisper decodes the whole file into RAM
    and RSS grew past 1.6 GB on a 36-min talk when done in one pass."""
    import numpy as np
    from faster_whisper import WhisperModel
    from faster_whisper.audio import decode_audio
    m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=int(threads))
    res, start = [], 0
    while True:
        seg = f"{out}.chunk.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(chunk_s), "-i", audio,
                        "-ac", "1", "-ar", "16000", seg], check=True)
        if os.path.getsize(seg) < 2000: os.remove(seg); break
        segs, _ = m.transcribe(seg, language="en", beam_size=1, vad_filter=True, condition_on_previous_text=False)
        n = len(res); res += [(start + s.start, s.text) for s in segs]; os.remove(seg)
        start += chunk_s
        if start > 6 * 3600: break
    json.dump(res, open(out, "w"))
    print(json.dumps({"peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024}))

def duration(v):
    if v.get("duration_s"): return int(v["duration_s"])
    try: return int(open(f"{ROOT}/data/subs/{v['id']}.dur").read().split()[0])   # written by the caption step
    except Exception: pass
    try: return int(float(ytrun.run(["--print", "duration", "-q", "--no-warnings", v["url"]], timeout=60).stdout.split()[0]))
    except Exception: return None

def main(a):
    c = cfg()
    want = {"needs Whisper"} | ({"rate limited (retry later)"} if a.include_rate_limited else set())
    todo = [v for v in load() if v.get("transcript_status") in want and (not a.ids or v["id"] in a.ids)]
    backends = [RemoteBackend(c.get("remote"), a.remote_timeout), LocalCPUBackend()]
    cap = {"remote": a.remote_max_minutes, "local": a.max_minutes}   # GPU host handles much longer videos
    active = []
    for b in backends:
        ok, why = b.available(); print(f"backend {b.name}: {'use' if ok else 'skip'} ({why})"); active += [b] if ok else []
    results = []
    for v in todo:
        d = duration(v); r = {"id": v["id"], "title": v["title"], "duration_s": d, "backend": None, "model": None,
                              "wall_s": None, "peak_rss_mb": None, "ok": False, "error": None}
        use = [b for b in active if d and d <= cap[b.name] * 60]
        if not use:
            r["error"] = (f"skipped: duration {d}s > max {max([cap[b.name] for b in active] or [a.max_minutes])} min"
                          if d else "skipped: unknown duration")
            update(v["id"], {"whisper_status": r["error"]}); results.append(r); print(json.dumps(r)); continue
        for b in use:
            t0 = time.time(); res = b.transcribe(v, a)
            r.update(backend=b.name, model=res.get("model"), wall_s=round(time.time() - t0, 1),
                     peak_rss_mb=res.get("peak_rss_mb"), ok=res["ok"], error=res.get("error"))
            if res["ok"]:
                write_transcript(v["id"], res["segs"])
                update(v["id"], {"transcript_status": "ok", "transcript_source": f"whisper:{b.name}:{r['model']}",
                                 "transcript_file": f"data/transcripts/{v['id']}.txt", "duration_s": d, "whisper_status": "ok"})
                break
        if not r["ok"]: update(v["id"], {"whisper_status": f"failed: {r['error']}"})
        results.append(r); print(json.dumps(r), flush=True)
    if a.log:
        with open(a.log, "a") as fh:
            for r in results: fh.write(json.dumps(r) + "\n")
    print(f"whisper: tried={len(todo)} ok={sum(r['ok'] for r in results)} "
          f"peak_rss_mb={max([r['peak_rss_mb'] or 0 for r in results] or [0])}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "_worker": worker(*sys.argv[2:6]); sys.exit()
    c = cfg(); ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="only these video ids")
    ap.add_argument("--model", default=c.get("model", "base.en"), choices=["tiny.en", "base.en"])
    ap.add_argument("--max-minutes", type=float, default=c.get("max_minutes", 45))
    ap.add_argument("--timeout", type=int, default=c.get("timeout_s", 1200), help="per-video transcribe wall cap (s)")
    ap.add_argument("--dl-timeout", type=int, default=300)
    ap.add_argument("--mem-mb", type=int, default=c.get("mem_mb", 1500), help="kill the worker if its RSS exceeds this (MB)")
    ap.add_argument("--threads", type=int, default=c.get("threads", 4))
    ap.add_argument("--min-english", type=float, default=0.12, help="reject transcripts below this English ratio")
    ap.add_argument("--remote-timeout", type=float, default=2.0)
    ap.add_argument("--remote-model", default=c.get("remote_model", "large-v3-turbo"), help="ggml model on the GPU host")
    ap.add_argument("--remote-max-minutes", type=float, default=c.get("remote_max_minutes", 180))
    ap.add_argument("--include-rate-limited", action="store_true", help="also do caption-429 videos (default: captionless only)")
    ap.add_argument("--log", default=f"{ROOT}/data/whisper_log.jsonl")
    main(ap.parse_args())
