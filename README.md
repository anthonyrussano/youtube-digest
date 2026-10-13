# YouTube AI & DevOps daily digest

This pipeline turns Anthony's YouTube subscriptions (`subscriptions.csv`, 144 channels) into a daily Markdown digest of new AI and DevOps videos, summarized from their transcripts. Everything lives under `/home/box/youtube-digest`, which survives box updates.

## Layout
| Path | What it is |
|---|---|
| `subscriptions.csv` | YouTube subscriptions export (Channel Id, Channel Url, Channel Title) |
| `run.sh` | Entry point: makes sure the venv and yt-dlp exist, then runs `digest.py all` |
| `digest.py` | Stage `rss`, stage `transcripts`, or `all` |
| `.venv/` | uv venv containing yt-dlp |
| `state/seen.json` | Video IDs already processed, so later runs skip them |
| `data/videos.json` | Every video in the window, with Short/candidate flags and RSS errors |
| `data/selected.json` | (optional) The judged relevant list `{video_id: "AI" or "DevOps"}`. If present, it replaces the keyword candidates |
| `data/relevant.json` | Relevant videos with `transcript_status`, duration, and transcript path |
| `data/transcripts/<id>.txt` | `[seconds] text` lines parsed from English captions |
| `articles/YYYY-MM-DD.md` | The LLM-written longform article (front matter `title`, `dek`, plus body), following `STYLE.md` |
| `scripts/render_article.py` | Checks citations, appends "Also on the radar", and writes `reports/YYYY-MM-DD.md` |
| `reports/YYYY-MM-DD.md` | The published article (a Jekyll page) |
| `index.md`, `_config.yml`, `_layouts/`, `assets/` | GitHub Pages site (Jekyll, minima theme) |
| `STYLE.md` | Article style rules |
| `config/x_queries.txt` | Topic queries for the daily X search, derived from the subscription topics (no channel list) |
| `data/x_raw/*.json` | Raw `search_posts_all` responses saved by the routine (private, not committed) |
| `scripts/x_filter.py` / `./run.sh x` | Bookmarks > likes filter, at least 10 bookmarks, last 24 h, spam/crypto excluded, de-duplicated, ranked by bookmarks then ratio, written to `data/x_selected.json` |
| `scripts/render_report_legacy.py`, `scripts/summaries_2026-10-12.py` | The old bullet-digest format, kept for reference |

## How it works
1. **RSS** (`digest.py rss --hours N`, default 24): fetches `https://www.youtube.com/feeds/videos.xml?channel_id=<ID>` for every channel, 4 at a time, with retries. The endpoint is flaky: about 70% of channels returned 404/500 on the first run. Those channels fall back to `yt-dlp --flat-playlist` on the channel's `/videos` tab (15 newest, with approximate day-level dates). Shorts are flagged by their `/shorts/` link and skipped. A keyword regex (AI and DevOps vocab in `digest.py`) marks candidates.
2. **Judgment:** a keyword prefilter is noisy. It catches JRE episodes and Oracle healthcare marketing, and it misses things like a Postgres migration talk. A judge (LLM) should read `data/videos.json` and write `data/selected.json`. If that file is missing, the transcripts stage uses the keyword candidates.
3. **Transcripts** (`digest.py transcripts`): runs serially, calling `yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs en --sub-format vtt` with sleeps between requests. Results:
   - `ok`: the transcript is in `data/transcripts/`.
   - `needs Whisper`: no English captions. Whisper is not run on this box.
   - `rate limited (retry later)`: YouTube returned HTTP 429. These are carried forward and retried on the next run.

   After this stage, every video in the window goes into `state/seen.json`.
4. **Article and report (current):** see the daily flow below and `STYLE.md`. *(Legacy:* an LLM reads `data/transcripts/*.txt` and writes `scripts/summaries_<date>.py`. Each video gets 3–5 bullets drawn only from the transcript and 1–3 `(seconds, label)` key moments, and there are 3–5 `THEMES` across all videos. Then run `.venv/bin/python scripts/render_report_legacy.py scripts/summaries_<date>.py <date>`. The report groups videos into AI and DevOps, deep-links key moments with `&t=<s>s`, and lists videos without a transcript at the end.*)

**Who summarizes:** on the first run (2026-10-12, 7-day window) Grok Bot wrote the summaries by hand during the run. On later runs, a scheduled Grok Bot routine does steps 2 and 4: it runs `./run.sh` (or `rss`, then judges, then `transcripts`), reads the transcripts, writes the summaries file, and renders the report. `digest.py` makes no LLM calls itself.

## Daily flow (for the scheduled routine)
Repo: https://github.com/anthonyrussano/youtube-digest · Site: https://anthonyrussano.github.io/youtube-digest/

```bash
cd /home/box/youtube-digest
./run.sh rss --hours 24          # 1. new videos from the last 24 h -> data/videos.json
#  2. JUDGE: read data/videos.json (non-Shorts, not already seen) and write
#     data/selected.json = {"<video_id>": "AI" | "DevOps", ...}  (only genuinely AI/DevOps videos)
./run.sh transcripts             # 3. captions -> data/transcripts/; also retries earlier 429 videos
#  4. WRITE: read data/relevant.json + data/transcripts/<id>.txt for every status "ok" video and write
#     articles/$(date +%F).md following STYLE.md (headline, dek, lede, themed sections, inline
#     timestamped links, every transcribed video cited, nothing beyond the transcripts)
#  4b. X: ./run.sh x-reset; then for EVERY non-# line of config/x_queries.txt call MCP x.search_posts_all with
#     query="<line> -is:retweet -is:reply lang:en", max_results=25, sort_order=relevancy,
#     start_time=<now-24h ISO UTC>, post.fields=public_metrics,created_at,author_id,
#     expansions=author_id, user.fields=username,name (write_to_file) and copy each result to data/x_raw/qNN.json
./run.sh x                       #     -> data/x_selected.json (bookmarks > likes, >=10 bookmarks, ranked)
#     Weave the selected posts into articles/<date>.md per STYLE.md ("What people are saving on X"; prose, links, counts)
./run.sh render                  # 5. -> reports/<date>.md (fails if a transcribed video isn't cited)
./run.sh publish                 # 6. commit reports/ + articles/ and push; Pages rebuilds in ~1 min
```
The X step uses about 24 calls per run (limits: 30 per minute, 1000 per day). `min_faves:` is ignored by this search, so the engagement floor is applied in `x_filter.py`. If no relevant video has a transcript but X posts qualified, the article can still be built from X alone, but `render` requires `data/relevant.json`. If neither has content, skip steps 4–6 and publish nothing. `publish` stages only site, report and article files, and it refuses to commit anything under data/, state/ or .venv/, or any CSV or cookie file. `./run.sh` with no stage still runs rss and transcripts using keyword candidates. To reprocess everything, delete `state/seen.json`. Caption rate limits (429) are the main bottleneck. If they keep happening, slow down further (`--sleep-subtitles` in `digest.py`) or pass browser cookies to yt-dlp, which needs Anthony's approval. Never commit cookies.

## Adding Whisper later
This box has 8 CPUs, about 3 GB of free RAM, and no GPU. That's too small for Whisper turbo, so it isn't run here. Videos marked `needs Whisper` can go to Anthony's repo **wikip-co/whisper-youtube-transcriber** (yt-dlp audio download, then openai-whisper `turbo`, built for AMD ROCm GPUs, writing `transcript.txt` / `transcript.json`). It would run on the GPU server on his LAN, which this box reaches over the WireGuard tunnel. A possible setup:
1. Run the transcriber on the GPU host behind a small HTTP endpoint, or call it over SSH: `ssh gpu-host 'cd whisper-youtube-transcriber && ./transcribe <url>'`.
2. Add a `whisper` stage to `digest.py` that takes `needs Whisper` entries, sends their URLs to the GPU host on the LAN, pulls back `transcript.json`, converts its segments (`start` and `text`) to the same `[seconds] text` format in `data/transcripts/<id>.txt`, and sets `transcript_status = "ok (whisper)"`.
3. Everything downstream (summaries and timestamped links) then works unchanged.
