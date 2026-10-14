# YouTube AI & DevOps daily digest ("Mind Blow" edition)

This repo is Anthony's daily pipeline. It reads new videos from his YouTube subscriptions, filters them to AI and DevOps, pulls transcripts, adds high-signal X posts, and publishes a Vsauce2 *Mind Blow*-style article to GitHub Pages: https://anthonyrussano.github.io/youtube-digest/. A fresh agent should read this README, then `STYLE.md`, then follow `docs/ROUTINE_PROMPT.md`.

## Layout
| Path | What it is |
|---|---|
| `subscriptions.csv` | **Private, never committed.** The YouTube subscriptions export (see Setup) |
| `run.sh` | Entry point with subcommands `fetch` (alias `rss`), `transcripts`, `x`, `x-reset`, `render` and `publish` |
| `digest.py` | Stages `fetch` (alias `rss`), `transcripts` and `all` (yt-dlp channel listing, keyword prefilter, exact dates, captions) |
| `requirements.txt` | Pinned Python deps (yt-dlp). Installed into `.venv/` |
| `config/x_queries.txt` | Topic queries for the daily X search (topics only, no channel list) |
| `scripts/x_filter.py` | Applies the X rules to `data/x_raw/*.json` and writes `data/x_selected.json` |
| `scripts/render_article.py` | Checks citations, appends "Also on the radar", and writes `reports/<date>.md` |
| `articles/<date>.md` | The written article (source). `reports/<date>.md` is the published page |
| `STYLE.md` | The Mind Blow format: rules, annotated example and pre-publish checklist |
| `docs/ROUTINE_PROMPT.md` | Paste-ready prompt for the scheduled daily routine |
| `index.md`, `_config.yml`, `_layouts/`, `assets/` | Jekyll site (minima theme) for GitHub Pages |
| `state/seen.json` | **Private.** Video IDs already fetched |
| `state/published.json`, `state/last_edition.json`, `state/current_edition.json` | **Private.** IDs already published, the last publish time (next window start) and the open edition |
| `scripts/edition.py` | Edition bookkeeping (`./run.sh edition-start`, `./run.sh edition`) |
| `data/` | **Private.** `videos.json`, `selected.json`, `relevant.json`, `transcripts/`, `x_raw/` and `x_selected.json` |
| `scripts/render_report_legacy.py`, `scripts/summaries_2026-10-12.py` | Old bullet format, kept for reference only |

## Setup from scratch
1. **Clone:** `git clone https://github.com/anthonyrussano/youtube-digest /home/box/youtube-digest`
2. **Python deps:** you need Python 3.10+ and [uv](https://github.com/astral-sh/uv) (or plain venv). `./run.sh fetch` creates `.venv/` and installs `requirements.txt` automatically. To do it by hand, run `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt`. Nothing else is needed: `render_article.py` and `x_filter.py` use only the standard library. When caption downloads start failing across the board, bump the yt-dlp pin.
3. **Subscription list (private):** export your subscriptions from Google Takeout (YouTube and YouTube Music, then `subscriptions/subscriptions.csv`). Place the file at `/home/box/youtube-digest/subscriptions.csv`. It is a CSV with a header row `Channel Id,Channel Url,Channel Title` and one channel per row (Channel Id is the `UC…` ID). It is gitignored, `publish` refuses to stage it, and its contents must never be copied into commits, articles or issues.
4. **GitHub auth:** `gh auth login` (or a `GITHUB_TOKEN` with `repo` scope) so that `git push` to `anthonyrussano/youtube-digest` works. Never commit the token.
5. **Pages:** in repo Settings, open Pages, choose "Deploy from a branch" and set it to `main` and `/ (root)`. Jekyll builds with the minima theme from `_config.yml`, which excludes the scripts, docs and private paths. Each push rebuilds the site in about 1–2 minutes.
6. **X search:** this needs the MCP namespace `x` (tool `search_posts_all`) connected for the agent. There is no API key in this repo.

## Editions (several per day)
The routine runs at about 6:04 AM, noon and 5 PM PT on weekdays, plus on demand. Each run is one **edition**:
- **Id and page:** the first edition of a PT day is `YYYY-MM-DD` (`articles/2026-10-13.md` becomes `reports/2026-10-13.html`). Later editions add the PT start time, `YYYY-MM-DD-HHMM` (`articles/2026-10-13-1158.md` becomes `reports/2026-10-13-1158.html`), so they never overwrite the morning page. The index lists every edition newest first, labeled with its date and "h:mm AM/PM PT edition".
- **Window:** `./run.sh edition-start` sets the window start to the previous edition's publish time (`state/last_edition.json`). With no state it falls back to now-24h, and it never goes back more than 72 h. `--hours H` forces a window. The result goes to `state/current_edition.json`, which `fetch`, `x`, `render` and `publish` all read by default.
- **No repeats:** `state/seen.json` holds every video already fetched. `state/published.json` holds every video and X post ID cited in a published edition, recorded by `publish`. `fetch` and `transcripts` skip published videos, and `x` drops published posts. `render` refuses a new edition that cites anything already published. Flat yt-dlp listings have only day-level dates, so `fetch` widens its pre-filter by 36 h, then gets exact timestamps for keyword matches; seen-tracking removes any overlap.
- **Publish:** `./run.sh publish` pushes, then records the cited IDs and the publish time, which is the next edition's window start, and closes the edition. If the push fails, the state isn't advanced.
- **Skip rule:** an edition needs new transcribed videos, **or** at least 5 good X items for an X-only edition. Otherwise `render` exits with `SKIP:` and nothing is published. Leave the edition open; the next `edition-start` reopens with the same window start.

## Daily flow (one edition; for the scheduled routine)
```bash
cd /home/box/youtube-digest
./run.sh edition-start           # 0. prints EDITION=<id>, START=<ISO UTC window start>, HOURS
./run.sh fetch                   # 1. videos published since START -> data/videos.json (seen/published skipped)
#  2. JUDGE: read data/videos.json (non-Shorts, "seen": false) and write
#     data/selected.json = {"<video_id>": "AI" | "DevOps", ...}  (see Relevance criteria; may be {})
./run.sh transcripts             # 3. captions -> data/transcripts/; also retries earlier 429 videos
./run.sh x-reset                 # 4. X: clear data/x_raw/, then for EVERY non-# line Q of config/x_queries.txt call
#     MCP x.search_posts_all {"query":"Q -is:retweet -is:reply lang:en","max_results":25,
#       "sort_order":"relevancy","start_time":"<START from step 0>",
#       "post.fields":"public_metrics,created_at,author_id","expansions":"author_id",
#       "user.fields":"username,name"}  (write_to_file) and copy each result to data/x_raw/qNN.json
./run.sh x                       #     -> data/x_selected.json (window START, unpublished posts only)
#  5. WRITE articles/<EDITION>.md per STYLE.md (Mind Blow format) from the new transcripts + data/x_selected.json.
#     If there are no new transcribed videos and fewer than 5 good X items, stop here (nothing to publish).
./run.sh render                  # 6. -> reports/<EDITION>.md (citation check, no-repeat check, X-only minimum)
./run.sh publish                 # 7. push, record published IDs and publish time; then check the URL returns HTTP 200
```
`render` and `publish` default to the open edition's ID. An explicit ID (`./run.sh render 2026-10-12`) re-renders or republishes an older page without touching edition state. An on-demand edition uses the same sequence. `./run.sh edition-start --hours 6` forces a 6-hour window.

## Relevance criteria (step 2)
The keyword regex in `digest.py` (`AI` and `DEVOPS`) only proposes candidates, and it is noisy: it catches podcasts and marketing that merely mention "AI" and misses things like a Postgres migration talk. The judge reads every non-Short video title and channel and selects a video when its main subject is one of these:
- **AI:** models and launches, agents and coding assistants, ML research and explainers, local or open models and the hardware for them, AI dev tooling (MCP, evals, fine-tuning, RAG).
- **DevOps:** CI/CD, IaC, Kubernetes and containers, cloud services, databases and migrations, observability and incidents, networking, VPN and routers, homelabs, self-hosting, SBCs and servers, security, encryption and backups.

Exclude videos where AI or tech is incidental (general politics, comedy, sermons, finance or health talk), plus music, kids' content, Shorts and pure product ads with no technical content. Label each selected video `"AI"` or `"DevOps"` by its main subject. If `data/selected.json` is absent, the keyword candidates are used.

## X filter rules (step 4)
- The window is the open edition's START. Pass `start_time` = START to every call.
- Queries come from `config/x_queries.txt` (about 24 topics from the subscriptions' AI/DevOps themes), which means about 24 calls a run. Limits are 30 calls a minute and 1000 a day.
- `-is:retweet -is:reply lang:en` are accepted. **`min_faves:N` is silently ignored**, so engagement filtering happens locally.
- `scripts/x_filter.py` (via `./run.sh x [--min-bookmarks 10] [--hours 24] [--top 15]`) keeps a post only if `bookmark_count > like_count`, it has at least 10 bookmarks, and it was created since the edition's window START (or the last 24 hours with no open edition), and not already published. It drops crypto and spam patterns, de-duplicates by ID and normalized text, ranks by bookmarks and then the bookmark/like ratio, and keeps the top 15. Expect roughly 5–15 qualifying posts out of about 600 scanned.
- The writer still applies judgment: drop off-topic or promotional posts, and flag dubious claims. Bookmark and like counts are for selection only and never appear in the article.

## Failure handling
- **YouTube RSS is dead:** since October 2026, `https://www.youtube.com/feeds/videos.xml` returns 404 (sometimes 500) for every channel, from every network. `fetch` uses yt-dlp instead; `--rss` re-enables the old feed as a first attempt if it ever comes back.
- **Channel listing errors:** the run lists them in `errors` in `data/videos.json` (typically terminated/removed channels or channels with no Videos tab). Prune those from the subscriptions export.
- **Full-lookup errors:** listed in `lookup_errors`; those videos keep their approximate date.
- **Caption 429s:** videos get `transcript_status = "rate limited (retry later)"` and are retried automatically on the next `./run.sh transcripts`. Until then they appear in "Also on the radar". If 429s persist, raise `--sleep-subtitles` in `digest.py`. Passing browser cookies to yt-dlp needs Anthony's approval, and cookies are never committed.
- **No English captions:** the status is `needs Whisper` and the video goes to "Also on the radar" (see Whisper below).
- **Render citation check:** `./run.sh render` exits 1 and lists any transcribed video not cited. Add it to an item and re-run.
- **No new transcripts:** an X-only edition is allowed if at least 5 good X items qualify. Otherwise skip steps 5–7 and publish nothing (`render` prints `SKIP:` if you try).
- **X tool unavailable or rate-limited:** write the article from videos only. That's allowed, but note it in the run report.
- **Pages:** if the URL isn't 200 after about 3 minutes, check the repo's Actions or Pages build status.

## Privacy rules
`subscriptions.csv` (and any `*.csv`), `data/`, `state/`, `.venv/`, cookies, `.env` and secrets are gitignored. `./run.sh publish` only stages known site, code and doc paths, and it aborts if anything under `data/`, `state/` or `.venv/`, or any CSV or cookie file, is staged. Don't name the subscribed channels list in commits or docs. Channels may be mentioned in articles only as the source of a cited video.

## How it works
1. **Fetch** (`digest.py fetch --hours N`, default: the open edition's START, else 24 h; `rss` is an alias):
   - Lists each channel's 15 newest uploads with `yt-dlp --flat-playlist --extractor-args youtubetab:approximate_date` on `/channel/<ID>/videos` (4 channels at a time; the Videos tab has no Shorts). About 25 s for 144 channels.
   - Drops seen/published IDs and anything whose approximate (day-level) date is more than 36 h before START.
   - Runs the keyword regex (AI and DevOps vocab in `digest.py`). Only new keyword matches get a full `yt-dlp -J --skip-download` lookup (2 at a time) for the exact `timestamp`, full description and duration; they are then filtered strictly against START. These have `date_exact: true` and a `HH:MM PT` date.
   - Non-matching new videos are kept for the judge with an approximate date (`date_exact: false`, `(approx)`), and are not candidates.
   - `--out FILE` writes elsewhere for a dry run (`fetch` never writes `state/`). `--rss` tries the legacy RSS feed first. The summary line reports channels ok/failed, lookups, exact dates and runtime; the same counts are in `data/videos.json`.
2. **Judgment:** a keyword prefilter is noisy. It catches JRE episodes and Oracle healthcare marketing, and it misses things like a Postgres migration talk. A judge (LLM) should read `data/videos.json` and write `data/selected.json`. If that file is missing, the transcripts stage uses the keyword candidates.
3. **Transcripts** (`digest.py transcripts`): runs serially, calling `yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs en --sub-format vtt` with sleeps between requests. Results:
   - `ok`: the transcript is in `data/transcripts/`.
   - `needs Whisper`: no English captions. Whisper is not run on this box.
   - `rate limited (retry later)`: YouTube returned HTTP 429. These are carried forward and retried on the next run.

   After this stage, every video in the window goes into `state/seen.json`.
4. **Article and report:** see the daily flow above and `STYLE.md`. *(Legacy:* an LLM reads `data/transcripts/*.txt` and writes `scripts/summaries_<date>.py`. Each video gets 3–5 bullets drawn only from the transcript and 1–3 `(seconds, label)` key moments, and there are 3–5 `THEMES` across all videos. Then run `.venv/bin/python scripts/render_report_legacy.py scripts/summaries_<date>.py <date>`. The report groups videos into AI and DevOps, deep-links key moments with `&t=<s>s`, and lists videos without a transcript at the end.*)

**Who summarizes:** on the first run (2026-10-12, 7-day window) Grok Bot wrote the summaries by hand during the run. On later runs, a scheduled Grok Bot routine does steps 2 and 4: it runs `./run.sh` (or `fetch`, then judges, then `transcripts`), reads the transcripts, writes the summaries file, and renders the report. `digest.py` makes no LLM calls itself.

## Adding Whisper later
This box has 8 CPUs, about 3 GB of free RAM, and no GPU. That's too small for Whisper turbo, so it isn't run here. Videos marked `needs Whisper` can go to Anthony's repo **wikip-co/whisper-youtube-transcriber** (yt-dlp audio download, then openai-whisper `turbo`, built for AMD ROCm GPUs, writing `transcript.txt` / `transcript.json`). It would run on the GPU server on his LAN, which this box reaches over the WireGuard tunnel. A possible setup:
1. Run the transcriber on the GPU host behind a small HTTP endpoint, or call it over SSH: `ssh gpu-host 'cd whisper-youtube-transcriber && ./transcribe <url>'`.
2. Add a `whisper` stage to `digest.py` that takes `needs Whisper` entries, sends their URLs to the GPU host on the LAN, pulls back `transcript.json`, converts its segments (`start` and `text`) to the same `[seconds] text` format in `data/transcripts/<id>.txt`, and sets `transcript_status = "ok (whisper)"`.
3. Everything downstream (summaries and timestamped links) then works unchanged.
