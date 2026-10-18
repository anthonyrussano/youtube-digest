# YouTube AI & DevOps daily digest ("Mind Blow" edition)

> **New agent taking this over?** Start with [`docs/HANDOFF.md`](docs/HANDOFF.md): setup from scratch, the routines (weekday and weekend editions, the 10:37 morning X post, the impressions tracker; full prompts and cron times), the X Article publishing playbook, hard rules and engagement lessons.

This repo is Anthony's daily pipeline. It reads new videos from his YouTube subscriptions, filters them to AI and DevOps, pulls transcripts, adds high-signal X posts, and publishes a Vsauce2 *Mind Blow*-style article to GitHub Pages: https://anthonyrussano.github.io/youtube-digest/. A fresh agent should read this README, then `STYLE.md`, then follow `docs/ROUTINE_PROMPT.md`.

## Layout
| Path | What it is |
|---|---|
| `subscriptions.csv` | **Private, never committed.** The YouTube subscriptions export (see Setup) |
| `subscriptions.example.csv` | Committed, sanitized starter list: the public AI/DevOps/tech channels only, same format. `cp subscriptions.example.csv subscriptions.csv` to bootstrap |
| `state/x_posts.json`, `state/x_impressions.csv` | **Private.** Every X Article post (ids, caption, NASA header used) and the impressions log (see `docs/HANDOFF.md`) |
| `run.sh` | Entry point with subcommands `edition-start`, `edition`, `fetch` (alias `rss`), `feeds`, `ainews`, `transcripts`, `whisper`, `trends`, `x-reset`, `x-accounts`, `x`, `render`, `publish`, `x-article` and `all` |
| `whisper_fallback.py` | Whisper fallback stage (`./run.sh whisper`): pluggable backends, remote GPU host (whisper.cpp/Vulkan over ssh) then local CPU faster-whisper |
| `digest.py` | Stages `fetch` (alias `rss`), `transcripts` and `all` (yt-dlp channel listing, keyword prefilter, exact dates, captions) |
| `requirements.txt` | Pinned Python deps (yt-dlp). Installed into `.venv/` |
| `config/feeds.txt`, `scripts/feeds.py` | RSS/Atom feeds (`./run.sh feeds`): `url \| name \| tier \| filter`, fetched since the edition window -> `data/feeds.json` (see "Feeds") |
| `scripts/ainews.py` | AINews newsletter stage (`./run.sh ainews`): the daily [AINews] issue(s) in the edition window, read through the box-private mail bridge, parsed into stories with their original sources -> `data/ainews.json` (see "AINews") |
| `config/x_queries.txt` | Topic queries for the daily X search (topics only, no channel list) |
| `config/x_accounts.txt`, `scripts/x_accounts.py` | Followed-account sources (32 accounts Anthony follows, audited 2026-10-15); `./run.sh x-accounts` prints the OR'd `from:` queries |
| `scripts/x_filter.py` | Applies the X rules to `data/x_raw/*.json` and writes `data/x_selected.json` |
| `config/x_trends.txt`, `scripts/x_trends.py` | Daily keyword trends (`./run.sh trends`): category post counts today vs 7-day average -> `data/x_trends.json` |
| `scripts/x_article_html.py` | `./run.sh x-article <edition> [--format roundup\|deep-dive]` -> `/tmp/x-article/<edition>.html` for the X Article. **roundup** = `reports/<edition>.md` (classic, unchanged output); **deep-dive** = `articles/x/<edition>/article.md` (one `<p>` per line, bold kept, title/caption guards). Default: `articles/x/<edition>/format.txt`, else deep-dive if `article.md` exists, else roundup. Prints format, title, caption and the localhost serve command (`docs/X_ARTICLE_STYLE.md`) |
| `scripts/x_stats.py` | `./run.sh x-stats`: impressions by X Article format from the private `state/x_posts.json` + `state/x_impressions.csv` (stdout only) |
| `articles/x/<edition>/` | X Article choice and artifacts per edition: `format.txt` (roundup or deep-dive + reason); for deep-dive also `research.md`, `outline.md`, `article.md`, `check.md` |
| `scripts/render_article.py` | Checks citations, appends "Also on the radar", and writes `reports/<date>.md` |
| `articles/<date>.md` | The written article (source). `reports/<date>.md` is the published page |
| `STYLE.md` | The Mind Blow format: rules, annotated example and pre-publish checklist |
| `docs/ROUTINE_PROMPT.md` | Paste-ready prompt for the scheduled daily routine |
| `index.md`, `_config.yml`, `_layouts/`, `assets/` | Jekyll site (minima theme) for GitHub Pages |
| `state/seen.json` | **Private.** Video IDs considered by a published edition (written only by `publish`; videos without a usable transcript go to `state/retry.json` instead) |
| `state/retry.json` | **Private.** Videos waiting for a usable transcript: retried by later editions, dropped after 3 failed editions or 7 days |
| `state/published.json`, `state/last_edition.json`, `state/current_edition.json` | **Private.** IDs already published, the last publish time (next window start) and the open edition |
| `scripts/edition.py` | Edition bookkeeping (`./run.sh edition-start`, `./run.sh edition`) |
| `data/` | **Private.** `videos.json`, `selected.json`, `relevant.json`, `transcripts/`, `x_raw/` and `x_selected.json` |
| `scripts/render_report_legacy.py`, `scripts/summaries_2026-10-12.py` | Old bullet format, kept for reference only |

## Setup from scratch
1. **Clone:** `git clone https://github.com/anthonyrussano/youtube-digest /home/box/youtube-digest`
2. **Python deps:** you need Python 3.10+ and [uv](https://github.com/astral-sh/uv) (or plain venv). `./run.sh fetch` creates `.venv/` and installs `requirements.txt` automatically. To do it by hand, run `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt`. Nothing else is needed: `render_article.py` and `x_filter.py` use only the standard library. When caption downloads start failing across the board, bump the yt-dlp pin.
3. **Subscription list (private):** export your subscriptions from Google Takeout (YouTube and YouTube Music, then `subscriptions/subscriptions.csv`). Place the file at `/home/box/youtube-digest/subscriptions.csv`. It is a CSV with a header row `Channel Id,Channel Url,Channel Title` and one channel per row (Channel Id is the `UC…` ID). No Takeout export? `cp subscriptions.example.csv subscriptions.csv` (70 public tech channels) and add/remove channels by their `UC…` id. `subscriptions.csv` is gitignored, `publish` refuses to stage it, and its contents must never be copied into commits, articles or issues.
4. **GitHub auth:** `gh auth login` (or a `GITHUB_TOKEN` with `repo` scope) so that `git push` to `anthonyrussano/youtube-digest` works. Never commit the token.
5. **Pages:** in repo Settings, open Pages, choose "Deploy from a branch" and set it to `main` and `/ (root)`. Jekyll builds with the minima theme from `_config.yml`, which excludes the scripts, docs and private paths. Each push rebuilds the site in about 1–2 minutes.
6. **X search:** this needs the MCP namespace `x` (tool `search_posts_all`) connected for the agent. There is no API key in this repo.

## Editions (several per day)
The routines run on weekdays at 6:04 AM, 12:04 PM and 5:04 PM PT (`4 6,12,17 * * 1-5`) and on Saturday and Sunday at 12:04 PM and 5:04 PM PT (`4 12,17 * * 0,6`), plus on demand. Each run is one **edition**:
- **Id and page:** the first edition of a PT day is `YYYY-MM-DD` (`articles/2026-10-13.md` becomes `reports/2026-10-13.html`). Later editions add the PT start time, `YYYY-MM-DD-HHMM` (`articles/2026-10-13-1158.md` becomes `reports/2026-10-13-1158.html`), so they never overwrite the morning page. The index lists every edition newest first, labeled with its date and "h:mm AM/PM PT edition".
- **Window:** `./run.sh edition-start` sets the window start to the previous edition's publish time (`state/last_edition.json`). With no state it falls back to now-24h, and it never goes back more than 72 h. `--hours H` forces a window. The result goes to `state/current_edition.json`, which `fetch`, `x`, `render` and `publish` all read by default.
- **No repeats:** `state/seen.json` holds every video fetched for an edition that was actually published; `publish` (via `scripts/edition.py published`) is its only writer, so a skipped edition leaves its in-window videos eligible for the next `fetch` (the window START also stays put, because it comes from the last *published* edition). `state/published.json` holds every video and X post ID (and feed article URL) cited in a published edition, recorded by `publish`. `fetch` and `transcripts` skip published videos, and `x` drops published posts. `render` refuses a new edition that cites anything already published. Flat yt-dlp listings have only day-level dates, so `fetch` widens its pre-filter by 36 h, then gets exact timestamps for keyword matches; seen/published tracking removes any overlap.
- **Retry queue:** at publish, selected videos that never got a usable transcript (caption 429 or Whisper failed/skipped) are **not** marked seen; `edition.py published` puts them in `state/retry.json` (`attempts`, `first_edition`, `last_edition`, `status`, `video`). `fetch` re-adds them to `data/videos.json` (`"retry": true`) and `transcripts` always retries them with their earlier category. `./run.sh whisper` (no args) also sends 429 videos with 2+ failed editions to Whisper with `--include-rate-limited`. A video leaves the queue once it is transcribed or cited, or is dropped (and marked seen) after 3 failed published editions or once it is 7 days old.
- **Publish:** `./run.sh publish` stages and commits **only the edition's own files by path** (`reports/<ed>.*`, `articles/<ed>.*`, `articles/x/<ed>/`, `index.md`; never whole `docs/` or `scripts/`, since other workers may be editing them; commit code and doc changes separately by explicit path), runs `git pull --rebase --autostash`, pushes, then records the cited IDs and the publish time, which is the next edition's window start, and closes the edition. If the push fails, the state isn't advanced.
- **Skip rule:** an edition needs new transcribed videos, **or** at least 5 good X items for an X-only edition, **or** at least 2 strong articles (tier 1–2 feeds, selected in `data/feeds_selected.json` and cited) for an articles-only edition. AINews items never count toward it on their own (see "AINews"). Otherwise `render` exits with `SKIP:` and nothing is published. Leave the edition open; the next `edition-start` reopens with the same window start.

## Daily flow (one edition; for the scheduled routine)
```bash
cd /home/box/youtube-digest
./run.sh edition-start           # 0. prints EDITION=<id>, START=<ISO UTC window start>, HOURS
./run.sh fetch                   # 1. videos published since START -> data/videos.json (seen/published skipped)
#  2. JUDGE: read data/videos.json (non-Shorts, "seen": false) and write
#     data/selected.json = {"<video_id>": "AI" | "DevOps", ...}  (see Relevance criteria; may be {})
./run.sh feeds                   # 2b. RSS/Atom feeds since START -> data/feeds.json; judge picks 3-6 articles
#     -> data/feeds_selected.json = {"<item id>": "AI" | "DevOps"}
./run.sh ainews                  # 2c. AINews issue(s) since START -> data/ainews.json; judge picks stories
#     -> data/ainews_selected.json = {"<item id>": "AI" | "DevOps"} (fails softly when the mail bridge is down)
./run.sh transcripts             # 3. captions -> data/transcripts/; also retries earlier 429 videos
./run.sh whisper                 # 3b. Whisper fallback for captionless (needs Whisper) videos
./run.sh trends                  # 4a. once per PT day: prints CACHED, or the get_posts_counts_recent calls to save as
#     data/x_counts/<name>.json; then ./run.sh trends compute -> data/x_trends.json
./run.sh x-reset                 # 4. X: clear data/x_raw/, then for EVERY non-# line Q of config/x_queries.txt call
#     MCP x.search_posts_all {"query":"Q -is:retweet -is:reply lang:en","max_results":25,
#       "sort_order":"relevancy","start_time":"<START from step 0>",
#       "post.fields":"public_metrics,created_at,author_id","expansions":"author_id",
#       "user.fields":"username,name"}  (write_to_file) and copy each result to data/x_raw/qNN.json;
#     then the same call for EVERY line printed by ./run.sh x-accounts -> data/x_raw/aNN.json (3 calls)
./run.sh x                       #     -> data/x_selected.json (window START, unpublished posts only)
#  5. WRITE articles/<EDITION>.md per STYLE.md (Mind Blow format) from the new transcripts + data/x_selected.json.
#     Skip rule: publish only with >= 1 new transcribed video, OR >= 5 good X items, OR >= 2 strong (tier 1-2)
#     selected articles; otherwise stop here (nothing to publish, nothing marked seen).
./run.sh render                  # 6. -> reports/<EDITION>.md (citation check, no-repeat check, X-only minimum)
./run.sh publish                 # 7. commit only this edition's files by path, pull --rebase, push, record published IDs and publish time; then check the URL returns HTTP 200
#  8. X Article on @russano via the signed-in browser (pick roundup or deep-dive per docs/X_ARTICLE_STYLE.md, ./run.sh x-article, then the docs/HANDOFF.md playbook; held until 10:37 for the weekday 6:04 run; weekend editions post immediately)
```
`render` and `publish` default to the open edition's ID. An explicit ID (`./run.sh render 2026-10-12`) re-renders or republishes an older page without touching edition state. An on-demand edition uses the same sequence. `./run.sh edition-start --hours 6` forces a 6-hour window.

## Relevance criteria (step 2)
The keyword regex in `digest.py` (`AI` and `DEVOPS`) only proposes candidates, and it is noisy: it catches podcasts and marketing that merely mention "AI" and misses things like a Postgres migration talk. The judge reads every non-Short video title and channel and selects a video when its main subject is one of these:
- **AI:** models and launches, agents and coding assistants, ML research and explainers, local or open models and the hardware for them, AI dev tooling (MCP, evals, fine-tuning, RAG).
- **DevOps:** CI/CD, IaC, Kubernetes and containers, cloud services, databases and migrations, observability and incidents, networking, VPN and routers, homelabs, self-hosting, SBCs and servers, security, encryption and backups.

Exclude videos where AI or tech is incidental (general politics, comedy, sermons, finance or health talk), plus music, kids' content, Shorts and pure product ads with no technical content. Label each selected video `"AI"` or `"DevOps"` by its main subject. If `data/selected.json` is absent, the keyword candidates are used.

## Feeds (step 2b)
`config/feeds.txt` lists 44 feeds as `url | name | tier | optional filter`: the 33 relevant, active feeds from the 2026-10-14 devops-newsfeeds audit plus verified AI-lab and tooling feeds (OpenAI, Google AI, DeepMind, Hugging Face, LangChain, Docker, Vercel, AWS ML, Simon Willison, Latent Space, Changelog). Anthropic has no RSS feed, so it is covered by X and video only. Tier 1 means a primary source (official blog, release notes), tier 2 a strong engineering blog or curated news, and tier 3 is useful but lower signal. `kw:<regex>` keeps only matching entries (AWS What's New uses it). Hacker News comes from `hnrss.org/newest?points=200`.

`./run.sh feeds` (`scripts/feeds.py`) fetches every feed concurrently (10 workers, 15 s timeout, one retry). It caches ETag/Last-Modified in `state/feeds_http.json`, with bodies in `data/feeds_cache/`. It keeps entries published since the edition START (the same window as `fetch`; `--hours H` or `--since ISO` override it) and drops URLs already in `state/feeds_seen.json` or `published.json` `"articles"`. URLs are canonicalized: `utm_*` parameters and the fragment are stripped. Items are scored on title and summary: tier (1:3, 2:2, 3:1), plus AI/DevOps keyword hits (the `digest.py` regexes, up to 3 each), times 1.5 when a top trend in `data/x_trends.json` matches. The top 40 items with a keyword hit (or from tier 1) are shortlisted and get full text via trafilatura, capped at about 6,000 characters and cached in `data/feeds_text/`. When extraction fails they fall back to the RSS summary. A run takes about 10–20 s.

**Selection:** the judge picks 3–6 articles per edition with the video/X rubric and prefers tier-1 primary sources. Stories merge across sources: an announcement covered by a video, an X post and a blog is one item, cited to the blog. **Dedup:** only `edition.py published` (run by `publish`) writes `state/feeds_seen.json`, marking every item in `data/feeds.json` as considered. It also adds cited article URLs to `published.json` `"articles"`, which `render` refuses to reuse. A skipped edition leaves its items eligible.

## AINews (step 2c)
[AINews](https://news.smol.ai/) (swyx, now a section of Latent Space) is a daily email digest of AI Twitter, Reddit and Discord, with every claim linked to its source. `./run.sh ainews` (`scripts/ainews.py`) reads it by email:
- **Mail access is box-private and read-only.** It goes through the mail bridge on this box (`/home/box/mail-bridge`, a Proton Bridge container; client `examples/agent_mail.py`) with credentials from Vault via AppRole, configured in `~/.config/mail-bridge/env.sh` (and reachable over WireGuard, `~/.config/wireguard/ensure-up.sh`; `run.sh` runs it once and retries when the first attempt fails). None of that lives in the repo. The script selects INBOX read-only and fetches bodies with `BODY.PEEK[]`, so nothing is marked read and no flags or folders change. It only searches and opens messages From `swyx+ainews@substack.com` with `[AINews]` in the subject, and it never sends mail. Never commit the env file, Vault ids/tokens or any mail content.
- **Window:** issues whose Date is since the edition START (`--hours H` or `--since ISO` override; `--latest N` takes the N newest issues regardless of window, for testing). Issues already in `state/ainews_seen.json` are skipped.
- **Parsing:** the lead (title story), each top-level bullet of the "AI Twitter Recap" (titled `Theme: Label`, with `theme` kept for grouping; the "Top tweets" list is dropped as a repeat) and each top-level item of the Reddit recaps become items with `title`, `summary` (bullet text plus up to three sub-points) and `sources`. Each `substack.com/redirect/...` link is unwrapped with one GET *without* the personal `?j=` token, reading only the `Location` header (cached in `data/ainews_cache/redirects.json`); t.co/bit.ly-style hops are followed too, and `utm_*`, `?s=` and similar params are stripped (twitter.com becomes x.com). Sources are ranked X posts, then papers/GitHub/Hugging Face, then blogs and videos, then news, then Reddit/HN; substack, latent.space and image links are dropped, so an item never points at the email. `primary_url` is the best source. A typical issue gives 45–60 items in about 15 s.
- **Dedup:** source URLs already in `state/ainews_seen.json`, `state/feeds_seen.json` or `published.json` `"articles"`, and X posts in `published.json` `"x"`, are removed; a story with no fresh source left is dropped. `ainews.py` never writes `state/`: `publish` (`edition.py published`) marks every issue and source URL in `data/ainews.json` as seen and adds cited non-X sources to `"articles"`, so a skipped edition keeps its items.
- **Selection and writing:** the judge picks AINews stories alongside feeds, X and video into `data/ainews_selected.json`. Items are written in the normal voice and linked to the original sources (the X post, paper, repo or blog), never to the newsletter or email, and with no "according to AINews" framing. The same story from feeds, X or a video is one merged item.
- **Skip rule:** AINews items do **not** count toward the skip rule. It is a secondary, once-a-day digest of yesterday's chatter that arrives with almost every window, so counting it would make every edition publishable and drift the site toward re-reporting a newsletter. `render` therefore leaves X posts known only from `data/ainews.json` (not in `data/x_selected.json`) out of the X-only count; AINews stories enrich editions that already qualify through videos, X or feed articles.
- **Failure:** if the bridge, Vault or the VPN is unreachable, `data/ainews.json` gets `"ok": false` and an `error`, the command exits 0 and the edition goes on without AINews.

## X filter rules (step 4)
- The window is the open edition's START. Pass `start_time` = START to every call.
- Queries come from `config/x_queries.txt`: 24 topics from the subscriptions' AI/DevOps themes, 5 launch queries (big-company AI, agent launches, knowledge-base tools, dev launches) and 4 curated-account queries (`from:` ~56 AI/DevOps builders). Followed accounts: `config/x_accounts.txt` holds 32 accounts Anthony follows on X that passed a 2026-10-15 audit (bio relevance score >= 2 of 5, plus at least 2 sampled posts with 5+ bookmarks or one with 20+). `./run.sh x-accounts` ORs them into 3 `from:` queries of about 11 handles each (small batches, because a call returns at most 25 posts). That is 36 calls a run (budget about 55), plus about 27 trend reads once a day. Limits are 30 calls a minute and 1000 a day; pace at 25/minute.
- `-is:retweet -is:reply lang:en` are accepted. Tested 2026-10-14: **`min_likes:N` works** (launch queries use `min_likes:5` to drop zero-engagement noise), `min_faves:` is silently ignored, `min_bookmarks:` is rejected, and `has:links` works but surfaces link spam, so it is unused.
- `scripts/x_filter.py` (via `./run.sh x [--min-bookmarks 10] [--hours 24] [--top 15]`) keeps a post only if it has at least 10 bookmarks and passes a route: **saves** (`bookmark_count > like_count`) or **shares** (at least 30 reposts or 5 quotes, and bookmarks at least 0.2x likes), Posts by followed accounts (any query) can instead pass the relaxed **followed** route: at least 5 bookmarks, bookmarks at least 0.1x likes (quality floor), and saves, or at least 10 reposts, or at least 3 quotes (flags `--followed-min-bookmarks/-reposts/-quotes/-ratio`). Every post must also have been created since the edition's window START (or the last 24 hours with no open edition), and not already published. It drops crypto and spam patterns, de-duplicates by ID and normalized text, ranks by bookmarks (x1.5 when the post matches a top category in `data/x_trends.json`) and then the bookmark/like ratio, and keeps the top 15. Expect roughly 15–30 qualifying posts before the top-15 cut.
- **Trends:** `./run.sh trends` caches `data/x_trends.json` once per PT day. Each line of `config/x_trends.txt` is `name | counts query | local regex`; noisy terms are disambiguated (MCP as "model context protocol"/"MCP server", Cursor as "Cursor AI/IDE"). "top" lists up to 5 categories at >= 1.1x their 7-day average with real volume (avg >= 200/day). The judge and writer favor those stories and the share caption leads with one.
- The writer still applies judgment: drop off-topic or promotional posts, and flag dubious claims. Bookmark and like counts are for selection only and never appear in the article.

## Failure handling
- **YouTube RSS is dead:** since October 2026, `https://www.youtube.com/feeds/videos.xml` returns 404 (sometimes 500) for every channel, from every network. `fetch` uses yt-dlp instead; `--rss` re-enables the old feed as a first attempt if it ever comes back.
- **Channel listing errors:** the run lists them in `errors` in `data/videos.json` (typically terminated/removed channels or channels with no Videos tab). Prune those from the subscriptions export.
- **Full-lookup errors:** listed in `lookup_errors`; those videos keep their approximate date.
- **Caption 429s:** videos get `transcript_status = "rate limited (retry later)"` and are retried automatically on the next `./run.sh transcripts`, including after a publish, via the retry queue (`state/retry.json`; see "No repeats"). Until then they appear in "Also on the radar". If 429s persist, raise `--sleep-subtitles` in `digest.py`. Passing browser cookies to yt-dlp needs Anthony's approval, and cookies are never committed.
- **No English captions:** the status is `needs Whisper`; `./run.sh whisper` transcribes it (see "Whisper fallback"). If that fails or the video is over the length cap, it goes to "Also on the radar".
- **Render citation check:** `./run.sh render` exits 1 and lists any transcribed video not cited. Add it to an item and re-run.
- **No new transcripts:** an X-only edition is allowed if at least 5 good X items qualify, and an articles-only edition if at least 2 strong (tier 1–2) selected articles qualify. Otherwise skip steps 5–7 and publish nothing (`render` prints `SKIP:` if you try).
- **Mail bridge unreachable:** `./run.sh ainews` writes `{"ok": false}` and the edition proceeds without AINews; note it in the run report.
- **X tool unavailable or rate-limited:** write the article from videos only. That's allowed, but note it in the run report.
- **Pages:** if the URL isn't 200 after about 3 minutes, check the repo's Actions or Pages build status.

## Privacy rules
`subscriptions.csv` (and any `*.csv`), `data/` (including `data/ainews.json`), `state/`, `.venv/`, cookies, `.env` and secrets are gitignored. `./run.sh publish` only stages known site, code and doc paths, and it aborts if anything under `data/`, `state/` or `.venv/`, or any CSV or cookie file, is staged. Don't commit the real subscriptions list. The only exception is `subscriptions.example.csv`, a hand-sanitized list of public tech channels (no personal, family, church or kids' channels). Channels may be mentioned in articles only as the source of a cited video.

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
   - `needs Whisper`: no English captions. Picked up by the Whisper fallback (3b).
   - `rate limited (retry later)`: YouTube returned HTTP 429. These are carried forward and retried on the next run.

   Rate-limited (429) videos stay in `data/relevant.json` and are retried by the next `transcripts` run. Nothing is marked seen here; that happens at publish.
4. **Article and report:** see the daily flow above and `STYLE.md`. *(Legacy:* an LLM reads `data/transcripts/*.txt` and writes `scripts/summaries_<date>.py`. Each video gets 3–5 bullets drawn only from the transcript and 1–3 `(seconds, label)` key moments, and there are 3–5 `THEMES` across all videos. Then run `.venv/bin/python scripts/render_report_legacy.py scripts/summaries_<date>.py <date>`. The report groups videos into AI and DevOps, deep-links key moments with `&t=<s>s`, and lists videos without a transcript at the end.*)

**Who summarizes:** on the first run (2026-10-12, 7-day window) Grok Bot wrote the summaries by hand during the run. On later runs, a scheduled Grok Bot routine does steps 2 and 4: it runs `./run.sh` (or `fetch`, then judges, then `transcripts`), reads the transcripts, writes the summaries file, and renders the report. `digest.py` makes no LLM calls itself.

## Whisper fallback
`./run.sh whisper` (`whisper_fallback.py`) runs after `transcripts` (also at the end of `./run.sh all`). By default it only takes videos with `transcript_status == "needs Whisper"`; caption-429 videos keep retrying captions on the next `transcripts` run. Pass `--include-rate-limited` to also transcribe 429 videos by hand, or list video ids to limit the run.

**Backends, tried in order** (the first that is available and succeeds wins):
1. **remote**: whisper.cpp built with Vulkan in a Docker image (`grokbot-whisper:vulkan`) on a home GPU server reached over ssh (tested on an AMD Radeon 890M iGPU via Mesa RADV; no ROCm needed on the host). Selected by `WHISPER_REMOTE=user@host[:port]` (env var, or `"remote"` in `config/whisper.json`, which is gitignored and refused by `publish`, so the address never lands in the repo; env wins, and an empty env value disables it). It's skipped when unset, or when one TCP connect fails within 2 s (`--remote-timeout`). Flow per video: yt-dlp downloads audio on this box, ffmpeg converts it to 16 kHz mono WAV, `scp` puts it in `~/grokbot-whisper/in/` on the host, `ssh` runs `docker run --rm --device /dev/dri --group-add <video> --group-add <render>` with `whisper-cli -m models/ggml-<model>.bin -oj`, the JSON is copied back, and the remote WAV and JSON are deleted (success or failure). Model `--remote-model` (default `large-v3-turbo`, file must exist in `~/grokbot-whisper/models/`). Length cap `--remote-max-minutes` (default 180) instead of the local 45. Any failure falls through to local. Host setup: put the Dockerfile in `~/grokbot-whisper/` (Ubuntu 24.04, `libvulkan-dev glslc spirv-headers`, `cmake -DGGML_VULKAN=1`; runtime `libvulkan1 mesa-vulkan-drivers`), `docker build -t grokbot-whisper:vulkan .`, and download the ggml model; no services run between jobs.
2. **local**: faster-whisper on CPU, `compute_type=int8`, model `base.en` (default) or `tiny.en`, 4 threads, VAD on, beam 1. yt-dlp downloads the lowest-bitrate audio-only format to `data/audio/`, which is deleted after every video, success or failure. Each transcription runs in its own process group, with a wall-time cap (`--timeout`, default 1200 s) and an RSS cap (`--mem-mb`, default 1500 MB; RSS is polled and the group is SIGKILLed past the cap). RLIMIT_AS isn't used because ctranslate2/OpenMP reserve far more virtual memory than they use, and a 2 GB AS limit kills even tiny jobs.

**Guards:** videos longer than `--max-minutes` (default 45) are skipped. The `.en` models turn non-English speech into gibberish, so a transcript whose English function-word ratio is below `--min-english` (0.12) is rejected (real English scores about 0.3–0.4).

**Output:** `data/transcripts/<id>.txt` in the same `[seconds] text` format as captions, plus `transcript_status = "ok"`, `transcript_source = "whisper:<backend>:<model>"` and `whisper_status` in `data/relevant.json`, so judge and render need no changes. Failures leave `transcript_status` as it was and set `whisper_status = "failed: ..."`. Per-video results (id, title, duration, backend, model, wall time, peak RSS, ok/error) are appended to `data/whisper_log.jsonl`. Defaults can go in `config/whisper.json` (`model`, `max_minutes`, `timeout_s`, `mem_mb`, `threads`, `remote`). It never writes `state/`, so seen/published still change only at publish.

**Cost on this box (8 CPU, ~3 GB free, no GPU):** first test (2026-10-14, base.en, 13 videos of 4–42 min): 9–58 s wall time per video (about 40× real time), peak RSS 516–932 MB. The worker transcribes in 10-minute ffmpeg chunks, because a single 36-minute pass reached 1.65 GB.

**Audio track:** many videos carry auto-dubbed tracks (Arabic, German, ...). The format selector picks the lowest-bitrate DASH stream of the *original* track (`wa[format_note*=original][protocol^=http]`, then English, then any). Plain `worstaudio` picked dubs and gave gibberish.
