#!/usr/bin/env bash
# Box-side orchestration only: ship script + tools to the render host, build there, copy results back.
# Nothing heavy runs on the box. Usage: tools/edition-video/remote.sh EDITION_ID [path/to/script.md]
# Host comes from config/whisper.json "remote" (gitignored) or $EDITION_VIDEO_HOST.
set -euo pipefail
ED="${1:?usage: remote.sh EDITION_ID [script.md]}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="${2:-/workspace/edition-video/$ED/script.md}"
HOST="${EDITION_VIDEO_HOST:-$(python3 -c "import json;print(json.load(open('$ROOT/config/whisper.json'))['remote'])")}"
OUT="/workspace/edition-video/$ED"
SSH=(ssh -o ControlMaster=auto -o "ControlPath=$HOME/.ssh/cm-grokbot-%r@%h:%p" -o ControlPersist=2h "$HOST")
mkdir -p "$OUT"
"${SSH[@]}" "mkdir -p ~/Projects/edition-video/bin ~/Projects/edition-video/$ED"
scp -o "ControlPath=$HOME/.ssh/cm-grokbot-%r@%h:%p" -q "$ROOT/tools/edition-video/build.py" "$ROOT/tools/edition-video/build.sh" "$ROOT/tools/edition-video/capture.mjs" "$HOST:Projects/edition-video/bin/"
scp -o "ControlPath=$HOME/.ssh/cm-grokbot-%r@%h:%p" -q "$SCRIPT" "$HOST:Projects/edition-video/$ED/script.md"
"${SSH[@]}" "bash ~/Projects/edition-video/bin/build.sh $ED"
for f in final.mp4 teleprompter.md timeline.json report.json; do
  scp -o "ControlPath=$HOME/.ssh/cm-grokbot-%r@%h:%p" -q "$HOST:Projects/edition-video/$ED/$f" "$OUT/"
done
ls -lh "$OUT"
