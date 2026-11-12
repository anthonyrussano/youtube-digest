#!/usr/bin/env bash
# Runs ON the render host. Usage: build.sh EDITION_ID [build.py flags...]
# Expects ~/Projects/edition-video/EDITION_ID/script.md
set -euo pipefail
ED="${1:?usage: build.sh EDITION_ID [--segment 09] [--no-dark] ...}"
shift || true
HERE="$(cd "$(dirname "$0")" && pwd)"
WD="${EDITION_VIDEO_ROOT:-$HOME/Projects/edition-video}/$ED"
[ -f "$WD/script.md" ] || { echo "missing $WD/script.md" >&2; exit 2; }
ROOTD="${EDITION_VIDEO_ROOT:-$HOME/Projects/edition-video}"
[ -d "$ROOTD/node_modules/playwright-core" ] || (cd "$ROOTD" && { [ -f package.json ] || npm init -y >/dev/null; } && npm i --silent playwright-core)
nice -n 10 python3 "$HERE/build.py" "$WD" "$@"
ls -lh "$WD"/*.mp4 "$WD/teleprompter.md" "$WD/post-attribution.md" "$WD/music.wav" 2>/dev/null || ls -lh "$WD"/*.mp4 "$WD/teleprompter.md"
