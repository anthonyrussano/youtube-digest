#!/usr/bin/env bash
# Box-side orchestration only: ship script + tools to the render host, build there, copy results back.
# Nothing heavy runs on the box. Usage:
#   tools/edition-video/remote.sh EDITION_ID [path/to/script.md] [--segment 09] [--no-dark] ...
# Host comes from config/whisper.json "remote" (gitignored) or $EDITION_VIDEO_HOST.
# Optional sidecars next to script.md (or in $OUT): xposts.json, handles.json.
set -euo pipefail
ED="${1:?usage: remote.sh EDITION_ID [script.md] [build flags...]}"
shift
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT=""
if [[ "${1:-}" != "" && "${1:-}" != --* && -f "${1:-}" ]]; then
  SCRIPT="$1"
  shift
fi
SCRIPT="${SCRIPT:-/workspace/edition-video/$ED/script.md}"
HOST="${EDITION_VIDEO_HOST:-$(python3 -c "import json;print(json.load(open('$ROOT/config/whisper.json'))['remote'])")}"
OUT="/workspace/edition-video/$ED"
SSH=(ssh -o ControlMaster=auto -o "ControlPath=$HOME/.ssh/cm-grokbot-%r@%h:%p" -o ControlPersist=2h -o ConnectTimeout=15 -o BatchMode=yes -i "$HOME/.ssh/id_ed25519_iphedeiah" -o IdentitiesOnly=yes "$HOST")
SCP=(scp -o ControlMaster=auto -o "ControlPath=$HOME/.ssh/cm-grokbot-%r@%h:%p" -o ControlPersist=2h -o ConnectTimeout=15 -o BatchMode=yes -i "$HOME/.ssh/id_ed25519_iphedeiah" -o IdentitiesOnly=yes)
mkdir -p "$OUT"
"${SSH[@]}" "mkdir -p ~/Projects/edition-video/bin ~/Projects/edition-video/$ED"
"${SCP[@]}" -q "$ROOT/tools/edition-video/build.py" "$ROOT/tools/edition-video/build.sh" "$ROOT/tools/edition-video/capture.mjs" "$ROOT/tools/edition-video/attribute.py" "$ROOT/tools/edition-video/auto_xposts.py" "$HOST:Projects/edition-video/bin/"
"${SCP[@]}" -q "$SCRIPT" "$HOST:Projects/edition-video/$ED/script.md"
# Sidecars live next to the script or in the output folder.
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT")" && pwd)"
for side in xposts.json handles.json; do
  if [[ -f "$SCRIPT_DIR/$side" ]]; then
    "${SCP[@]}" -q "$SCRIPT_DIR/$side" "$HOST:Projects/edition-video/$ED/$side"
  elif [[ -f "$OUT/$side" ]]; then
    "${SCP[@]}" -q "$OUT/$side" "$HOST:Projects/edition-video/$ED/$side"
  fi
done
"${SSH[@]}" "bash ~/Projects/edition-video/bin/build.sh $ED $*"
for f in final.mp4 teleprompter.md timeline.json report.json post-attribution.md attribution.json; do
  "${SCP[@]}" -q "$HOST:Projects/edition-video/$ED/$f" "$OUT/" 2>/dev/null || true
done
# If --output named something else, try to bring that back too (best-effort).
ls -lh "$OUT"
