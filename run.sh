#!/usr/bin/env bash
# Daily YouTube AI/DevOps digest.
#   ./run.sh [--hours 24]          rss + transcripts with keyword candidates (no judge)
#   ./run.sh rss [--hours 24]      stage 1: fetch feeds -> data/videos.json
#   ./run.sh transcripts           stage 3: captions for data/selected.json (retries earlier 429s)
#   ./run.sh render [DATE]         articles/DATE.md -> reports/DATE.md (checks citations)
#   ./run.sh publish [DATE]        git add reports/ articles/ site files, commit, push to GitHub
set -euo pipefail
cd "$(dirname "$0")"
ensure_venv() {
  [ -x .venv/bin/yt-dlp ] || { uv venv -q .venv && uv pip install -q --python .venv/bin/python yt-dlp; }
  .venv/bin/pip install -q -U yt-dlp 2>/dev/null || uv pip install -q -U --python .venv/bin/python yt-dlp || true
}
TODAY=$(TZ=America/Los_Angeles date +%F)
case "${1:-all}" in
  rss) shift; ensure_venv; .venv/bin/python digest.py rss "$@" ;;
  transcripts) shift; ensure_venv; .venv/bin/python digest.py transcripts "$@" ;;
  render) D=${2:-$TODAY}; python3 scripts/render_article.py "articles/$D.md" "$D" ;;
  publish)
    D=${2:-$TODAY}
    git add -- reports/ articles/ index.md _config.yml _layouts assets STYLE.md README.md .gitignore 2>/dev/null || true
    if git diff --cached --quiet; then echo "Nothing to publish"; exit 0; fi
    # safety net: refuse to publish private files even if .gitignore was edited
    if git diff --cached --name-only | grep -Eq '(^|/)(data|state|\.venv)/|subscriptions|\.csv$|cookie'; then
      echo "Refusing to publish: private file staged"; git diff --cached --name-only; exit 1; fi
    git commit -q -m "Report $D" && git push -q origin HEAD:main
    echo "Published: https://anthonyrussano.github.io/youtube-digest/reports/$D.html" ;;
  all|--*) [ "${1:-}" = all ] && shift; ensure_venv; rm -f data/selected.json; .venv/bin/python digest.py all "$@"
    echo "Data ready. Next: write articles/$TODAY.md (STYLE.md), ./run.sh render, ./run.sh publish" ;;
  *) echo "unknown command $1"; exit 2 ;;
esac
