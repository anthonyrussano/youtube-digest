"""Run yt-dlp either on this box or, when configured, over ssh on a remote host (home server) whose IP
YouTube does not bot-block. See README "Remote yt-dlp".

Config (gitignored config/whisper.json, never committed):
  "ytdlp_remote": true            -> use the same user@host[:port] as "remote" (the Whisper GPU host)
  "ytdlp_remote": "user@host:22"  -> a different host
  "ytdlp_remote_bin": "~/grokbot-whisper/bin/yt-dlp"   (default)
Env YTDLP_REMOTE overrides ("" disables, "1" = same as "remote"). If the host is unreachable (one `ssh true`,
~5 s), every call falls back to the box's own .venv/bin/yt-dlp and says so on stderr.
"""
import json, os, shlex, subprocess, sys, uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
LOCAL_BIN = f"{ROOT}/.venv/bin/yt-dlp"
# one multiplexed ssh connection per host: dozens of short ssh sessions in a row can trip sshd's
# per-source limits (PerSourcePenalties / MaxStartups) and get the box refused for a while
SSH_OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5", "-o", "ServerAliveInterval=30",
            "-o", "ControlMaster=auto", "-o", "ControlPath=~/.ssh/cm-grokbot-%C", "-o", "ControlPersist=120"]
_state = {}

def _cfg():
    try: return json.load(open(f"{ROOT}/config/whisper.json"))
    except Exception: return {}

def target():
    """-> (dest 'user@host', port, remote_bin) or None when remote yt-dlp is off or unreachable (cached)."""
    if "t" in _state: return _state["t"]
    c = _cfg(); t = c.get("ytdlp_remote")
    if os.environ.get("YTDLP_REMOTE") is not None: t = os.environ["YTDLP_REMOTE"] or None
    if t in (True, "1", "true"): t = os.environ.get("WHISPER_REMOTE") or c.get("remote")
    res = None
    if t:
        dest, _, port = t.rpartition(":") if ":" in t else (t, "", "22")
        port = port or "22"
        try:
            # a real ssh login, not a bare TCP connect: sshd counts preauth disconnects against the source
            # (OpenSSH PerSourcePenalties) and starts refusing the box after a few of them
            r = subprocess.run(["ssh", *SSH_OPTS, "-o", "ConnectTimeout=4", "-p", port, dest, "true"],
                               capture_output=True, text=True, timeout=15)
            if r.returncode != 0: raise ConnectionError((r.stderr.strip().splitlines() or ["ssh failed"])[-1][:120])
            res = (dest, port, c.get("ytdlp_remote_bin", "~/grokbot-whisper/bin/yt-dlp"))
            print("yt-dlp: running on remote host", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"yt-dlp: REMOTE HOST UNREACHABLE ({e.__class__.__name__}: {e}); falling back to box-local yt-dlp "
                  "(YouTube may bot-block this box)", file=sys.stderr, flush=True)
    _state["t"] = res
    return res

def ssh(cmd, timeout, t=None):
    dest, port, _ = t or target()
    return subprocess.run(["ssh", *SSH_OPTS, "-p", port, dest, cmd], capture_output=True, text=True, timeout=timeout)

def scp_from(remote_paths, local_dir, timeout=600, t=None):
    dest, port, _ = t or target()
    return subprocess.run(["scp", *SSH_OPTS, "-q", "-P", port, *[f"{dest}:{p}" for p in remote_paths], local_dir + "/"],
                          capture_output=True, text=True, timeout=timeout)

def rbin(t=None):
    b = (t or target())[2]
    return "$HOME/" + b[2:] if b.startswith("~/") else shlex.quote(b)

def ssh_failed(r):
    """True when ssh itself failed (rc 255: refused, timeout, auth), not yt-dlp."""
    return r.returncode == 255 and "yt-dlp" not in r.stderr and "ERROR:" not in r.stderr

def run(args, timeout):
    """yt-dlp ARGS whose result is stdout only (-J, --print, ...). Returns CompletedProcess."""
    t = target()
    if not t: return subprocess.run([LOCAL_BIN, *args], capture_output=True, text=True, timeout=timeout)
    return ssh(f"{rbin(t)} {' '.join(shlex.quote(a) for a in args)}", timeout, t)

def run_files(args, local_dir, timeout):
    """yt-dlp ARGS that write files. Use the literal token {OUT} in args for the output directory: it's a fresh
    remote temp dir (files are scp'd into local_dir, then the temp dir is removed) or local_dir on the box."""
    t = target(); os.makedirs(local_dir, exist_ok=True)
    if not t: return subprocess.run([LOCAL_BIN, *[a.replace("{OUT}", local_dir) for a in args]],
                                    capture_output=True, text=True, timeout=timeout)
    rd = f"/tmp/grokbot-ytdlp-{uuid.uuid4().hex[:10]}"
    q = " ".join(shlex.quote(a).replace("{OUT}", rd) for a in args)
    try:
        r = ssh(f"mkdir -p {rd} && {rbin(t)} {q}; rc=$?; echo @@FILES@@; ls -1 {rd}; exit $rc", timeout, t)
        files = [f for f in r.stdout.rpartition("@@FILES@@")[2].splitlines() if f and not f.endswith((".part", ".ytdl"))]
        if files:
            c = scp_from([f"{rd}/{f}" for f in files], local_dir, timeout, t)
            if c.returncode != 0: r.stderr += f"\nscp back failed: {c.stderr.strip()[-200:]}"
        return r
    finally:
        try: ssh(f"rm -rf {rd}", 60, t)
        except Exception: pass
