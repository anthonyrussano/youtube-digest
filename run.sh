#!/usr/bin/env bash
# Daily YouTube AI/DevOps digest.
#   ./run.sh [--hours 24]          fetch + transcripts with keyword candidates (no judge)
#   ./run.sh fetch [--hours 24]    stage 1: list channel uploads via yt-dlp -> data/videos.json (alias: rss)
#                                  extra flags: --out FILE (dry run), --rss (legacy RSS first; 404s globally), --workers N
#   ./run.sh feeds [--hours H]     RSS/Atom feeds (config/feeds.txt) since the edition window -> data/feeds.json
#   ./run.sh ainews [--hours H]    AINews newsletter issue(s) in the edition window, via the box-private read-only
#                                  mail bridge -> data/ainews.json (fails softly: empty file, exit 0)
#   ./run.sh transcripts           stage 3: captions for data/selected.json (retries earlier 429s)
#   ./run.sh whisper [IDS] [--include-rate-limited] [--model tiny.en|base.en] [--max-minutes 45]
#                                  stage 3b: Whisper fallback for "needs Whisper" videos (remote backend if
#                                  WHISPER_REMOTE is set and reachable, else local CPU faster-whisper)
#   ./run.sh edition-start [--hours H]  open an edition: id + window (since last publish, else 24 h) -> state/current_edition.json
#   ./run.sh edition                   show the current edition
#   ./run.sh render [DATE]         articles/DATE.md -> reports/DATE.md (checks citations)
#   ./run.sh x [--min-bookmarks 10]  filter data/x_raw/*.json (saved X searches) -> data/x_selected.json
#   ./run.sh trends [plan|compute|show]  daily X keyword trends (plan prints CACHED when today's data/x_trends.json
#                                  exists; else the get_posts_counts_recent calls to save in data/x_counts/)
#   ./run.sh x-article [ID]        reports/ID.md -> /tmp/x-article/ID.html for the X Article (prints title, caption, serve cmd)
#   ./run.sh publish [DATE]        git add reports/ articles/ site files, commit, push to GitHub
set -euo pipefail
cd "$(dirname "$0")"
ensure_venv() {
  # deps pinned in requirements.txt; YouTube breaks old yt-dlp often, so bump the pin when captions start failing
  [ -x .venv/bin/python ] || uv venv -q .venv || python3 -m venv .venv
  [ -x .venv/bin/yt-dlp ] || uv pip install -q --python .venv/bin/python -r requirements.txt || .venv/bin/pip install -q -r requirements.txt
}
TODAY=$(TZ=America/Los_Angeles date +%F)
# default edition id: the open edition (state/current_edition.json), else today's date
CUR=$(python3 -c 'import json;print(json.load(open("state/current_edition.json"))["id"])' 2>/dev/null || true)
DEF=${CUR:-$TODAY}
case "${1:-all}" in
  fetch|rss) shift; ensure_venv; .venv/bin/python digest.py fetch "$@" ;;
  feeds) shift; ensure_venv; .venv/bin/python scripts/feeds.py "$@" ;;
  ainews) shift; ensure_venv
    # box-private mail bridge config (Vault AppRole); never committed. Missing/unreachable bridge is non-fatal.
    [ -f "$HOME/.config/mail-bridge/env.sh" ] && . "$HOME/.config/mail-bridge/env.sh"
    .venv/bin/python scripts/ainews.py "$@" || echo "ainews failed (non-fatal)"
    if grep -q '"ok": false' data/ainews.json 2>/dev/null && [ -x "$HOME/.config/wireguard/ensure-up.sh" ]; then
      echo "ainews: retrying after ~/.config/wireguard/ensure-up.sh"
      { "$HOME/.config/wireguard/ensure-up.sh" >/dev/null 2>&1 && .venv/bin/python scripts/ainews.py "$@"; } || echo "ainews failed (non-fatal)"
    fi ;;
  transcripts) shift; ensure_venv; .venv/bin/python digest.py transcripts "$@" ;;
  whisper) shift; ensure_venv; .venv/bin/python whisper_fallback.py "$@"
    # caption-429 videos that already failed 2+ published editions (state/retry.json) go to Whisper as well
    if [ $# -eq 0 ]; then
      RIDS=$(python3 -c 'import json
try: r=json.load(open("state/retry.json"))
except Exception: r={}
rel={v["id"]:v for v in json.load(open("data/relevant.json"))}
print(" ".join(i for i,e in r.items() if e.get("attempts",0)>=2 and rel.get(i,{}).get("transcript_status","").startswith("rate limited")))' 2>/dev/null || true)
      if [ -n "$RIDS" ]; then echo "whisper: retrying long-failing 429 videos: $RIDS"
        .venv/bin/python whisper_fallback.py --include-rate-limited $RIDS || echo "whisper retry failed (non-fatal)"; fi
    fi ;;
  edition-start) shift; python3 scripts/edition.py start "$@" ;;
  edition) python3 scripts/edition.py show ;;
  render) D=${2:-$DEF}; python3 scripts/render_article.py "articles/$D.md" "$D" ;;
  x) shift; python3 scripts/x_filter.py "$@" ;;
  trends) shift; python3 scripts/x_trends.py "${1:-plan}" ;;
  x-accounts) shift; python3 scripts/x_accounts.py "${1:-queries}" ;;
  x-article) shift; python3 scripts/x_article_html.py "${1:-$DEF}" ;;
  x-reset) rm -rf data/x_raw && mkdir -p data/x_raw && echo "cleared data/x_raw" ;;
  publish)
    D=${2:-$DEF}
    [ -f "reports/$D.md" ] || { echo "reports/$D.md missing: run ./run.sh render first"; exit 1; }
    git add -- reports/ articles/ config/ scripts/ docs/ requirements.txt digest.py whisper_fallback.py run.sh index.md _config.yml _layouts assets STYLE.md README.md .gitignore 2>/dev/null || true
    if git diff --cached --quiet; then echo "Nothing to publish"; exit 0; fi
    # safety net: refuse to publish private files even if .gitignore was edited
    if git diff --cached --name-only | grep -Eq '(^|/)(data|state|\.venv)/|subscriptions|\.csv$|cookie|config/whisper\.json'; then
      echo "Refusing to publish: private file staged"; git diff --cached --name-only; exit 1; fi
    git commit -q -m "Report $D" && git push -q origin HEAD:main
    # record published stories + publish time (window start for the next edition), only for the open edition
    [ "$D" = "$CUR" ] && python3 scripts/edition.py published
    echo "Published: https://anthonyrussano.github.io/youtube-digest/reports/$D.html" ;;
  all|--*) [ "${1:-}" = all ] && shift; ensure_venv; rm -f data/selected.json; .venv/bin/python digest.py all "$@"
    .venv/bin/python whisper_fallback.py || echo "whisper fallback failed (non-fatal)"
    echo "Data ready. Next: write articles/$TODAY.md (STYLE.md), ./run.sh render, ./run.sh publish" ;;
  *) echo "unknown command $1"; exit 2 ;;
esac
