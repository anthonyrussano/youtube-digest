# Handoff: running this project as a new Grok Bot

This guide is for a Grok Bot on a different account, with none of the original box, memory or routines. Read it, then `README.md` (pipeline spec), `STYLE.md` (website writing spec), `docs/X_ARTICLE_STYLE.md` (the two X Article formats, roundup and deep-dive, and how to pick one) and `docs/ROUTINE_PROMPT.md` (per-edition steps).

## 1. What this is and the goal
A pipeline that turns Anthony Russano's YouTube subscriptions, curated X searches and 44 RSS/Atom feeds plus the daily AINews email newsletter into short AI & DevOps "editions" (three per weekday, two per weekend day). Each edition is published to GitHub Pages (https://anthonyrussano.github.io/youtube-digest/) as a rapid-fire roundup **and as an X Article on @russano** in one of two named formats: **roundup** (the edition itself) or **deep-dive** (a single-lead piece derived from it), chosen per edition (section 4a). The goal is to **maximize impressions on @russano**: good stories, good timing, a concrete hook caption.

Anthony gave **full authority over project decisions** (sources, filters, format, schedule tweaks). Use it, and tell him what you changed.

## 2. Setup from scratch
1. `git clone https://github.com/anthonyrussano/youtube-digest /home/box/youtube-digest` and set up push auth (`gh auth login`). Grok Bot also pushes whisper/report commits, so always `git pull --rebase` before pushing.
2. Python 3.10+, `uv` (or venv), `ffmpeg`. `./run.sh fetch` creates `.venv/` and installs `requirements.txt` (yt-dlp, faster-whisper, trafilatura, ...). Bump the yt-dlp pin when listing or captions break everywhere.
3. **Subscriptions** (`subscriptions.csv`, private, gitignored): either a Google Takeout export (YouTube and YouTube Music -> `subscriptions/subscriptions.csv`, header `Channel Id,Channel Url,Channel Title`), or `cp subscriptions.example.csv subscriptions.csv` (70 public tech channels, sanitized) and edit.
4. **Whisper**: optional GPU backend, whisper.cpp (Vulkan, in docker) on a home server reached over ssh. Set `WHISPER_REMOTE=user@host[:port]` in the environment (or `"remote"` in gitignored `config/whisper.json`). Ask Anthony for the host and an ssh key; never commit either, and never set it on your own guesswork. If unset or unreachable (2 s TCP check), `./run.sh whisper` falls back to local CPU faster-whisper `base.en` (45 min cap). Host setup is in README "Whisper fallback".
5. **Connectors**: MCP namespace `x` (search_posts_all, get_posts_counts_recent, get_users_posts) for search and impressions reads; a browser with **@russano signed in by Anthony himself** (never ask for or type his password); a messaging channel to Anthony.
6. **AINews mail (optional)**: `./run.sh ainews` reads the AINews newsletter through a mail bridge that is **private to Anthony's original box**: a Proton Bridge container in `/home/box/mail-bridge`, credentials in Vault (AppRole ids in `~/.config/mail-bridge/env.sh`), reached over WireGuard (`~/.config/wireguard/ensure-up.sh`). None of it is in the repo and none of it carries over. A new bot gets access only from Anthony: ask him to either (a) provision this bridge setup for your box (his Vault AppRole role/secret id with read access to the mail secret, the WireGuard config, and the `mail-bridge` client), or (b) subscribe an inbox you control (e.g. your own Grok Bot inbox) to AINews and adapt `fetch_issues()` in `scripts/ainews.py` to read it. Never ask for his mailbox password, never send mail from the bridge, never mark messages read (keep `readonly=True` + `BODY.PEEK[]`) and never commit credentials or mail. Without it the step fails softly and editions run without AINews.
7. **Pages**: Settings -> Pages -> deploy from `main` / root.
8. Smoke test: `bash -n run.sh && ./run.sh feeds --hours 6 && ./run.sh x-accounts && ./run.sh ainews --hours 30`.

## 3. Routines to recreate (timezone America/Los_Angeles)
Schedule at a glance (PT): **weekdays** 6:04 AM, 12:04 PM, 5:04 PM editions, with the 6:04 Article held to 10:37 AM; **Saturday and Sunday** 12:04 PM and 5:04 PM editions (made permanent by Anthony on Sat 2026-10-17), each posting its Article immediately (no held slot). Plus on-demand editions.
### A. Weekday digest editions: `4 6,12,17 * * 1-5`
Prompt: the full text in `docs/ROUTINE_PROMPT.md`, plus this preface:
```
If the current PT time is the 6:04 AM run, do steps 0-8d and 9 but DO NOT post the X Article (step 8e);
the 10:37 routine posts it. On the 12:04 and 17:04 runs, post the X Article right after publish.
Read docs/HANDOFF.md first (hard rules, X Article playbook). Quiet hours 10 PM-5:30 AM PT: no messages.
```
### A2. Weekend digest editions: `4 12,17 * * 0,6`
Saturday and Sunday, 12:04 PM and 5:04 PM PT. Prompt: the full text in `docs/ROUTINE_PROMPT.md`, plus this preface:
```
Weekend edition (Saturday or Sunday, 12:04 or 17:04 PT). Do every step 0-9, including step 8 (pick roundup or
deep-dive; for deep-dive write 8a-8d in articles/x/<EDITION>/) and 8e: post the X Article right after publish. There is no held slot on
weekends and the 10:37 routine does not run. Weekend material is often thin: apply the skip rule as usual and
keep the edition short rather than padding it. Read docs/HANDOFF.md first (hard rules, X Article playbook).
Quiet hours 10 PM-5:30 AM PT: no messages.
```
### B. Morning X post (weekdays only): `37 10 * * 1-5`
```
Repo /home/box/youtube-digest. Read docs/HANDOFF.md. Find today's first edition (reports/<YYYY-MM-DD>.md,
PT date). If it exists and has no entry in state/x_posts.json, publish its X Article on @russano following the
"X Article playbook" exactly, in the format the 6:04 run chose in articles/x/<YYYY-MM-DD>/format.txt
(./run.sh x-article <YYYY-MM-DD> reads it and prints FORMAT). If format.txt is missing, pick the format now per
docs/X_ARTICLE_STYLE.md "Selection rule" (and for deep-dive do the four steps first), then commit
articles/x/<YYYY-MM-DD>/ by path. Fresh NASA header, the tip-first caption (deep-dive: article.md front matter;
roundup: format.txt line 3; ends in "..."), read the live caption back, record in state/x_posts.json with
"format"). Then message Anthony: headline, X link, one sentence on the top
item. If there is no edition today (skipped) or it is already posted, do nothing and send no message.
```
### C. Impressions tracker: `13 9 * * *` (daily)
```
Repo /home/box/youtube-digest. For every post in state/x_posts.json, read its public_metrics with MCP x
get_posts_by_ids (post.fields=public_metrics,created_at; batches of up to 100 ids, one read). Upsert one row
per post_id in state/x_impressions.csv (columns: post_id,title,caption,posted_pt,impressions_24h,likes,
reposts,bookmarks,replies,quotes,measured_at_pt,age_hours_at_measure,note). Note when the age is not ~24 h.
Then run ./run.sh x-stats (impressions by X Article format, roundup vs deep-dive) and compare by format,
posting hour and caption type; if a pattern changed, update the "Engagement lessons" in
docs/HANDOFF.md and commit it (pull --rebase first). Message Anthony only if something notable changed.
Respect X limits: 30 reads/min, 1000/day across all routines.
```

## 4a. X Article formats: roundup and deep-dive
- **Two named formats, picked per edition** (full spec, side by side: `docs/X_ARTICLE_STYLE.md`). The website edition (`reports/`) is always the roundup and does not change.
  - **roundup:** the classic digest Article, `reports/<EDITION>.md` as is (rapid-fire cold open, one paragraph per item, `STYLE.md`). Every X Article through edition `2026-10-17` used it.
  - **deep-dive:** one lead story in depth (~400–800 words) + "Also this cycle" (4–6 linked one-liners), title naming the lead idea, written with the four steps in `articles/x/<EDITION>/`. First used on edition **`2026-10-17-1644`**, posted **Sat Oct 17, 2026 ~5 PM PT**.
- **Selection rule:** deep-dive only when the edition has one lead story with a genuinely overlooked angle, an actionable takeaway and enough primary-source material for ~400–600 words; otherwise roundup (always for thin editions with no strong lead). When both fit, **alternate** against the `format` of the last posted Article in `state/x_posts.json`, to gather comparison data. The choice is written to `articles/x/<EDITION>/format.txt` (format, reason, and for roundup the caption) so the 10:37 routine posts what the 6:04 run picked.
- **Record it:** every post in `state/x_posts.json` carries `"format": "roundup" | "deep-dive"` (backfilled Oct 17: all editions before `2026-10-17-1644` = roundup, `2026-10-17-1644` = deep-dive). `./run.sh x-stats` breaks impressions down by format.
- **Deep-dive steps:** 1 `research.md` (raw facts from the cited sources + a quick web/X search for what others covered and missed), 2 `outline.md` (one core idea at a time, plain language), 3 `article.md` (hook on the overlooked angle, short sentences, takeaway + reply-inviting question), 4 `check.md` (review, tighten, confirm the overlooked angle is real, sourced and simple; fix the article if anything fails).
- **Model:** the Oct 15 Claude Code single-idea Article (edition `2026-10-15-1705`, https://x.com/russano/status/2110889513455321578, "each agent gets its own repo copy"): one actionable agent-tooling idea, 653 impressions in ~25 h, our best. Worked sample of the new process: `articles/x/2026-10-17-sample/` (built on edition 2026-10-17, never posted).
- **Comparison:** the baseline is every X Article **posted before `2026-10-17-1644`** (all roundup; last one edition `2026-10-17`, posted 11:00 AM PT). From `2026-10-17-1644` on, both formats run side by side, so compare **by `format`** (roundup vs deep-dive) at ~24 h with `./run.sh x-stats` (impressions, likes, replies, bookmarks), and against the pre-1644 baseline; record the result in section 6.

## 4. X Article playbook
The X API **cannot** create Articles, so this is done in the browser, which Anthony signed into @russano himself.
1. Run `./run.sh x-article <EDITION> [--format roundup|deep-dive]` (`scripts/x_article_html.py`). Default: the format in `articles/x/<EDITION>/format.txt`, else deep-dive if `articles/x/<EDITION>/article.md` exists, else roundup. **roundup** renders `reports/<EDITION>.md` exactly as before (one `<p>` per paragraph, dek omitted, links kept, `$`-digit guard) and suggests a caption from the first sentence (rewrite it tip-first, or use `format.txt` line 3). **deep-dive** renders `article.md` (every line its own `<p>`, **bold** kept, `- ` bullets as `•`, `##` labels as bold lines) and refuses it if the title or caption has `$<number>` or "Mind Blow" or the caption doesn't end in `...`. Both drop any line containing "Mind Blow" and print `FORMAT`, `SOURCE`, `TITLE`, `CAPTION` and the `SERVE` command: `python3 -m http.server 8765 --bind 127.0.0.1 -d /tmp/x-article` (file:// is blocked in the browser). Run that in the background.
2. Open `http://127.0.0.1:8765/<EDITION>.html`, select the body, and **copy with the right-click context menu -> Copy**. Do not trust the existing clipboard: a stale clipboard once pasted yesterday's article.
3. Go to **https://x.com/compose/articles**, create a new Article, type the title, click into the body and paste with **real keystrokes** (Ctrl+V), not by injecting DOM text.
4. **Check the body**: first and last paragraphs match this edition, links survived, nothing from an older edition.
5. **Header image**: a random high-resolution public-domain NASA image from https://images.nasa.gov (download the original/large, not a thumbnail) whose id is **not** in any `header` field of `state/x_posts.json`. Upload it as the Article header.
6. Publish, then add the **caption** to the post (deep-dive: `article.md` front matter; roundup: `format.txt` line 3). Tip-first applies to both formats: lead with the single most useful, actionable takeaway for developers and DevOps people (a how-to, a pattern or a tip, preferably about agent/coding tools such as Claude Code, Cursor or Codex), ending in `...`. Don't lead with spec numbers or model sizes; numbers may support the takeaway but are not the hook. No "Mind Blow", no `$<number>`. Example: `Anthropic's Claude Code tip: each agent gets its own repo copy so three edit without colliding...` (see section 6).
7. **Read the live caption back** (profile timeline or `x.get_posts_by_id`). It was once truncated to `Forml`; if it is cut, fix it.
8. Append to `state/x_posts.json` `posts`: `edition, posted_at_utc, post_id, article_id, url, article_url, title, caption, caption_note, format` (`roundup` or `deep-dive`, as printed by `x-article`), `header` (NASA id plus short description).
9. Message Anthony (outside quiet hours): headline, link, one sentence on the top item.

## 5. Hard rules
- Never use "Mind Blow" in Article titles, bodies or captions (it is only the internal style name).
- Quiet hours **10 PM to 5:30 AM PT**: send no messages.
- After each published edition, message Anthony with the headline, the link and one sentence on the top item.
- Messaging or emailing anyone other than Anthony needs his explicit confirmation first.
- Never commit secrets or private data (see section 9). Never commit `subscriptions.csv`.
- Anthony has full authority delegated to you over project decisions; act, then report.

## 6. Engagement lessons (from `state/x_impressions.csv`, `state/x_posts.json`)
- **Best (since Oct 15): actionable tip-led captions.** The Oct 15 5:24 PM PT tip hook ("Anthropic's Claude Code tip: each agent gets its own repo copy so three edit without colliding...") got 653 impressions, 5 likes and 3 replies in about 25 hours. The Oct 16 noon numbers-led hook got only 11 impressions in 6 hours. So captions now lead with the most useful developer/DevOps takeaway (how-to, pattern, tip; agent/coding tools preferred), never with spec numbers or model sizes.
- **Earlier:** midday/afternoon posts with specific, number-led teaser captions. Tue Oct 13 2:51 PM PT: 321 impressions. Wed Oct 14 12:29 PM PT: 358+. Thu Oct 15 ~12:30 PM PT: ~280 in 2 hours with a real comment.
- **Worst:** overnight posts (Oct 13 12:19 AM: 27), and missing or truncated captions (Oct 13 7:43 AM no caption: 101; Oct 14 6:26 AM caption "Forml": 32).
- Hence the weekday 6:04 AM edition's Article is **held until 10:37 AM** (weekend editions run at 12:04 and 5:04 PM and post immediately), and every caption is a concrete hook ending in "...". Keep measuring and revise this section with data.

## 7. Quality bar
X Articles: `docs/X_ARTICLE_STYLE.md` is the spec for both formats. Deep-dive models: `2026-10-15-1705` (single Claude Code idea), the worked sample `articles/x/2026-10-17-sample/` and the first live one `articles/x/2026-10-17-1644/`. Roundup models: the gold editions below.

Website editions: `STYLE.md` is the spec. Gold examples in `reports/` (source in `articles/`):
- `2026-10-14-1211`: dense, number-led items (a million output tokens, Credit Karma's 90% cut); its number-led caption did well at the time, but tip-led captions now beat it (section 6).
- `2026-10-15`: leads with the biggest concrete stories (Anthropic $16.8bn quarter, Modal $1B ARR), clean merging of video, X and blog sources.
- `2026-10-15-1212`: a strong later edition; specific title (Meta 816B open model, Cloudflare Void, OpenAI's billion for defenders), no padding.

## 8. Troubleshooting
- **YouTube RSS 404s**: the channel RSS feed is dead since Oct 2026; `fetch` uses yt-dlp listings (`--rss` only as a legacy try).
- **Caption 429s**: status `rate limited (retry later)`. At publish they go to `state/retry.json` (not seen.json) and are retried by later editions; after 2 failed editions `./run.sh whisper` takes them with `--include-rate-limited`; dropped after 3 failed editions or 7 days. Whisper covers "needs Whisper" videos.
- **Feed SSL errors/timeouts**: a few feeds fail occasionally (15 s timeout, one retry); non-fatal, they show in the `feeds` summary.
- **X limits**: 30 reads/minute, 1000/day. Pace at <= 25/min; one edition is ~36 search reads plus ~27 trend reads once a day.
- **Render exits** with a missing-citation, reuse or `SKIP:` message: fix the article or skip the edition (nothing gets marked seen).

## 9. State: where it lives, what to carry over
All of `state/` and `data/` are **gitignored** (private). Files that matter:
| File | Purpose |
|---|---|
| `state/seen.json` | video ids considered by published editions (written only at publish) |
| `state/retry.json` | videos still waiting for a usable transcript (retried; dropped after 3 failed editions or 7 days) |
| `state/published.json` | video, X post and article ids/URLs cited (blocks repeats) |
| `state/last_edition.json` | last publish time = next window start |
| `state/feeds_seen.json` | feed URLs considered at publish |
| `state/ainews_seen.json` | AINews issue Message-IDs and source URLs considered at publish |
| `state/x_posts.json` | every X Article post, caption, `format` (roundup/deep-dive), header (prevents header reuse) |
| `state/x_impressions.csv` | impressions log |
Migrate by copying the `state/` folder privately (e.g. `tar czf state.tgz state/` and a direct file transfer Anthony approves), never via git. **A fresh start is OK**: with no state, `edition-start` uses a 24 h window; the only costs are possible repeats of recent stories (check the last few `reports/` by hand) and NASA header reuse (rebuild the used-header list from the posts on @russano). `config/whisper.json` and `subscriptions.csv` are recreated per section 2.
- X turns `$<number>` into a stock-ticker link. `x-article` inserts an invisible word joiner after `$`; avoid `$<number>` in typed captions (write "3 dollars" or "16.8 billion dollars").
