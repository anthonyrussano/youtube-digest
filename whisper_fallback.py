#!/usr/bin/env python3
"""Whisper fallback for relevant videos without English captions. See README.md "Whisper fallback".

Backends are tried in order; the first that is available and succeeds wins:
  1. remote  - placeholder for a GPU transcriber on a home server (WHISPER_REMOTE=host[:port]).
               Skipped when unset or unreachable (one TCP connect, short timeout). Not implemented yet.
  2. local   - faster-whisper on CPU (int8), each video in its own subprocess with a wall-time
               cap and an RSS cap (polled; process group killed). Audio is downloaded with yt-dlp and deleted after.
Only data/relevant.json and data/transcripts/ are written; state/ (seen/published) is never touched.
"""
import argparse, json, os, resource, signal, socket, subprocess, sys, time
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

class RemoteBackend(Backend):
    """Placeholder for Anthony's GPU transcriber (whisper-youtube-transcriber) reached over WireGuard."""
    name = "remote"
    def __init__(self, target, timeout=2.0): self.target, self.timeout = target, timeout
    def available(self):
        if not self.target: return False, "WHISPER_REMOTE unset"
        host, _, port = self.target.rpartition(":") if ":" in self.target else (self.target, "", "22")
        try: socket.create_connection((host, int(port)), self.timeout).close()
        except Exception as e: return False, f"unreachable ({e.__class__.__name__})"
        return True, "reachable"
    def transcribe(self, v, opts):
        # TODO: send v["url"] to the GPU host, fetch transcript.json, map segments (start, text) -> segs.
        return {"ok": False, "error": "remote backend not implemented yet"}

class LocalCPUBackend(Backend):
    name = "local"
    def available(self):
        try: import faster_whisper  # noqa
        except Exception: return False, "faster-whisper not installed in .venv"
        return True, "ok"
    def transcribe(self, v, opts):
        os.makedirs(AUDIO, exist_ok=True); base = f"{AUDIO}/{v['id']}"
        try:
            # lowest-bitrate audio-only DASH stream of the ORIGINAL track: many videos carry auto-dubbed
            # tracks (ar, de, ...) and plain "worstaudio" can pick one of those or a slow m3u8 variant
            fmt = ("wa[format_note*=original][protocol^=http]/wa[language^=en][protocol^=http]"
                   "/wa[protocol^=http]/wa")
            dl = [YTDLP, "-f", fmt, "--no-playlist", "-q",
                  "--no-warnings", "-o", base + ".%(ext)s", v["url"]]
            for attempt in range(2):   # YouTube's media CDN returns sporadic 403s; one retry usually clears it
                rc, _, _, err = run_capped(dl, opts.dl_timeout)
                if rc == 0 or "403" not in err: break
                time.sleep(10)
            files = [f for f in os.listdir(AUDIO) if f.startswith(v["id"] + ".") and not f.endswith((".part", ".ytdl"))]
            if rc != 0 or not files:
                return {"ok": False, "error": "audio download " + ("timed out" if rc is None else
                        ("429" if "429" in err else err.strip().splitlines()[-1][-200:] if err.strip() else f"rc={rc}"))}
            audio = f"{AUDIO}/{files[0]}"; out = f"{base}.segs.json"
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
            for f in os.listdir(AUDIO) if os.path.isdir(AUDIO) else []:   # audio, segs json, chunk wav
                if f.startswith(v["id"] + "."): os.remove(f"{AUDIO}/{f}")   # never keep audio

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
    try: return int(float(subprocess.run([YTDLP, "--print", "duration", "-q", v["url"]], capture_output=True,
                                         text=True, timeout=60).stdout.split()[0]))
    except Exception: return None

def main(a):
    c = cfg()
    want = {"needs Whisper"} | ({"rate limited (retry later)"} if a.include_rate_limited else set())
    todo = [v for v in load() if v.get("transcript_status") in want and (not a.ids or v["id"] in a.ids)]
    backends = [RemoteBackend(c.get("remote"), a.remote_timeout), LocalCPUBackend()]
    active = []
    for b in backends:
        ok, why = b.available(); print(f"backend {b.name}: {'use' if ok else 'skip'} ({why})"); active += [b] if ok else []
    results = []
    for v in todo:
        d = duration(v); r = {"id": v["id"], "title": v["title"], "duration_s": d, "backend": None, "model": None,
                              "wall_s": None, "peak_rss_mb": None, "ok": False, "error": None}
        if d is None or d > a.max_minutes * 60:
            r["error"] = f"skipped: duration {d}s > max {a.max_minutes} min" if d else "skipped: unknown duration"
            update(v["id"], {"whisper_status": r["error"]}); results.append(r); print(json.dumps(r)); continue
        for b in active:
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
    ap.add_argument("--include-rate-limited", action="store_true", help="also do caption-429 videos (default: captionless only)")
    ap.add_argument("--log", default=f"{ROOT}/data/whisper_log.jsonl")
    main(ap.parse_args())
