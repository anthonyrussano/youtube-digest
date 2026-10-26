# Overnight prep mode (weekdays ~12:30 AM PT)

Decided Oct 19, 2026 by Anthony: all research and transcription for the weekday morning edition happen overnight, so the 6:04 AM run has time to publish polished content and the 10:37 AM X Article carries inline images, screenshots and diagrams. First run: the night of Mon Oct 19 -> Tue Oct 20, 2026 (edition `2026-10-20`).

Two routines share one contract file, `articles/x/<EDITION>/overnight.json`. `<EDITION>` is the PT date the overnight run starts on (`YYYY-MM-DD`): the first edition of that PT day, which the 6:04 AM run then publishes.

## 1. Overnight run: cron `30 0 * * 1-5` (weekdays ~12:30 AM PT)
No time pressure. **No publishing, no X posting, no messages** (quiet hours 10 PM-5:30 AM PT).

1. **Open the edition:** `./run.sh edition-start`. It must print `EDITION=<today's PT date>`, with START = the last published edition's publish time (`state/last_edition.json`), so the window covers everything since the last published edition. Note START as `window_start`. Note the collection cutoff as `window_end` (ISO UTC, taken right before `fetch`).
2. **Collect** exactly as `docs/ROUTINE_PROMPT.md` steps 1-4 (fetch, judge, feeds, AINews, X trends and searches, `./run.sh x`). YouTube runs on **iphedeiah** (the home GPU host: remote yt-dlp, and the Whisper remote backend with `large-v3-turbo`; README "Remote yt-dlp" and "Whisper fallback").
3. **Transcribe everything:** `./run.sh transcripts`, then `./run.sh whisper`, then `./run.sh whisper --include-rate-limited <ids>` for **every** selected video still without a transcript and **every** video in `state/retry.json` (read it; do not edit it), not only those with 2+ failed editions. Remote cap is 180 min per video.
4. **Judge and shortlist** the stories (feeds, AINews, X, videos) as in step 5, then **draft the website edition** per `STYLE.md` and `docs/WRITING_GUIDE.md` (decision below on where it lives). Do **not** run `./run.sh publish`.
5. **X Article, full four-step process** in `articles/x/<EDITION>/` (`docs/X_ARTICLE_STYLE.md`): `format.txt`, `research.md`, `outline.md`, `article.md`, `check.md`. With the extra time, research goes deeper than a daytime run (full threads, primary docs, what others missed).
6. **Rich inline images** (section 3) at their places in `article.md`.
7. **Header:** pick a high-resolution public-domain NASA image from https://images.nasa.gov whose id is **not** in any `header` field of `state/x_posts.json`, and save the original/large file to `/workspace/x-header-<EDITION>.jpg`.
8. **Check:** `./run.sh x-article <EDITION> --dry-run` must print `SOURCE: articles/x/<EDITION>/article.md`; run the `STYLE.md` checklist on the draft report (render cannot run on the draft path; the 6:04 run renders).
9. **Write `articles/x/<EDITION>/overnight.json`** (schema below).
10. **Commit by path only:** `git add -- articles/x/<EDITION> && git commit -m "Overnight prep <EDITION>" -- articles/x/<EDITION>`, then `git pull --rebase --autostash origin main && git push origin HEAD:main`. Never commit `/workspace` images, `data/`, `state/`, `config/`, `subscriptions.csv` or secrets.
11. **Leave the edition open** (`state/current_edition.json`, and `data/` as collected). The 6:04 run continues it.

### Where the draft report lives: `articles/x/<EDITION>/draft-report.md`
GitHub Pages builds `reports/` (`_config.yml` gives `reports/` the report layout and `index.md` lists every page under `reports/`), so committing `reports/<EDITION>.md` would publish it. `articles/` (and `articles/x/`) is in the Jekyll `exclude` list, so the draft is committed as **`articles/x/<EDITION>/draft-report.md`**: the full `STYLE.md` article source (front matter `title:`/`dek:`, cold open, items, sign-off), **not** rendered. The overnight run writes neither `articles/<EDITION>.md` nor `reports/<EDITION>.md`. The 6:04 run copies the draft to `articles/<EDITION>.md`, then renders and publishes it.

### `articles/x/<EDITION>/overnight.json`
Public text only (it is committed): no host addresses, `data/`/`state/` contents or subscription names.
```json
{
  "edition": "2026-10-20",
  "window_start": "2026-10-20T00:08:00Z",
  "window_end": "2026-10-20T07:31:00Z",
  "files": {
    "draft_report": "articles/x/2026-10-20/draft-report.md",
    "article": "articles/x/2026-10-20/article.md",
    "format": "articles/x/2026-10-20/format.txt",
    "research": "articles/x/2026-10-20/research.md",
    "outline": "articles/x/2026-10-20/outline.md",
    "check": "articles/x/2026-10-20/check.md"
  },
  "images": [
    {"path": "/workspace/2026-10-20-diagram-1.png", "alt": "...", "kind": "diagram|screenshot|figure",
     "source": "URL the content comes from", "license": "for figures", "numbers_checked": true}
  ],
  "header": {"id": "PIA12345", "description": "short description", "path": "/workspace/x-header-2026-10-20.jpg"},
  "caption": "Tip-first caption ending in ...",
  "title": "Article title",
  "format": "roundup|deep-dive",
  "status": "ready|partial|failed",
  "todo": ["what the 6:04 run must still do"],
  "notes": ["anything to report: failed transcripts, unreachable host, dropped images, ..."]
}
```
- `window_start`/`window_end`: ISO UTC. `window_end` is the collection cutoff: the 6:04 run collects only after it.
- `status`: **ready** = draft report, all four steps, images and header done and checked; **partial** = usable, but something is missing (list it in `todo`, e.g. an image or a header); **failed** = not usable (the 6:04 run ignores it and runs as normal). If the run fails before writing anything usable, still write `overnight.json` with `"status": "failed"` and the reason in `notes` when possible.
- `caption`, `title`, `format` must match `article.md` front matter and `format.txt`.

## 2. 6:04 AM run (weekdays): `4 6 * * 1-5` slot of routine A
At the start, check `articles/x/<today PT date>/overnight.json`.
- **Missing, or `"status": "failed"`:** run as normal (`docs/ROUTINE_PROMPT.md`, all steps; Article held for 10:37).
- **`ready` or `partial`:** continue the overnight edition:
  1. Do **not** run `edition-start` again. `./run.sh edition` must show the open edition `<today>`; if it does not (state was reset), run as normal and report it.
  2. **Collect only from `window_end` to now**, into separate files so the overnight data stays intact:
     `./run.sh fetch --since <window_end> --out data/videos.delta.json`, `./run.sh feeds --since <window_end> --out data/feeds.delta.json`, `./run.sh ainews --since <window_end> --out data/ainews.delta.json`; X searches with `"start_time": <window_end>` saved as `data/x_raw/dNN.json` (no `x-reset`; the overnight `qNN`/`aNN` files stay), then `./run.sh x`. Merge the deltas into the main files by id (append new `videos` / `items_list` entries whose `id` is not already present) so `publish` marks the whole window as seen. Add new picks to `data/selected.json` etc., then `./run.sh transcripts` and `./run.sh whisper` for them.
  3. **Fold in big new items only, briefly:** a short paragraph each in the draft and, if it really matters, one short paragraph in `article.md`. **Don't redo the research** or rewrite the lead.
  4. **Polish, publish:** copy `articles/x/<today>/draft-report.md` to `articles/<today>.md`, polish, run the `STYLE.md` checklist, `./run.sh render`, `./run.sh publish` (it stages `articles/x/<today>/` too), check HTTP 200.
  5. Re-run `./run.sh x-article <today> --dry-run`; update `overnight.json` (`todo`, `notes`) if anything changed. Leave the prepared Article for the **10:37** post as usual (do not post).
  6. **Report everything `overnight.json` flagged** (`status`, `todo`, `notes`), plus the usual edition report.

## 3. Inline images
- **Kinds:** (a) **diagrams** from diagram-generator, which lives on iphedeiah at `~/Projects/diagram-generator`. Its GHCR image is private, so **build it locally on iphedeiah** (`docker build` in that directory) instead of pulling; render there and `scp` the output to `/workspace/`. Never commit host addresses or keys. (b) **Screenshots**: by default this means **still frames from the cited YouTube videos** (`video-frame`, section 3b), plus screenshots of key pages or charts (box browser), cropped to the relevant part. (c) **Source figures** (paper or blog charts) only when the license allows reuse (public domain, CC BY with attribution in the alt/caption line, or explicit permission); otherwise make a diagram or screenshot instead.
- **Markers:** put each image on its own line in `article.md` exactly where it belongs: `[[IMG: /workspace/<file> | alt text]]`. File names: letters, digits, `.`, `-` and `_` only (prefer `<EDITION>-<n>-<slug>.png`). Alt text is a plain one-line description. Images stay on the box under `/workspace/` and are never committed.
- **Accuracy:** check **every number, label and name in an image** against its source (record it in `check.md` and set `numbers_checked` in `overnight.json`). Drop an image you cannot verify.
- **Rendering:** `./run.sh x-article` keeps a marker line verbatim as its own `<p>` (tested Oct 19, 2026, both formats). It shows up in the pasted body as that literal line.

## 3b. Image toolkit (tested Oct 19, 2026)
All four render on **iphedeiah** under `~/Projects/` (repos cloned, images built locally; `ssh`/`scp` with one reused connection, e.g. `-o ControlMaster=auto -o ControlPersist=30m`). Work in a scratch dir like `/tmp/imgs/`, then `scp` the PNG to `/workspace/<EDITION>-<n>-<slug>.png`. Look at every image before using it. X shows images ~1200 px wide on a dark page, so render 1200 CSS px at 2x and prefer dark themes.

| Need | Tool | Command (on iphedeiah) |
|---|---|---|
| **Number chart** from source data (bar, line, ...) | `chart-generator` (anthonyrussano) | `cd ~/Projects/chart-generator && ./scripts/build-container.sh` (once; image `chart-gen:local`), then `./scripts/run-container.sh chart --data <dir-in-repo>/data.csv --form bar --x <col> --y <col> --title "..." --unit <u> --theme dark --width 1200 --png --png-width 2400 --out-dir <dir-in-repo> --name <name>` (`--auto-form` picks the form; `recommend --data ...` suggests one). Input CSV/JSON/JSONL/YAML; the data must sit inside the repo dir (mounted as `/workspace`). Also writes `<name>.md` (every value) and `<name>.blindspots.md`: read both. |
| **Flow / sequence / simple architecture** from Mermaid text | `pele` (obsidianmd) | `cd ~/Projects/pele && npm ci && npm run build` and `cd ~/Projects/ferroprint && npm ci` (once), then `node scripts/img/pele-png.mjs in.mmd out.png` (copy `scripts/img/pele-png.mjs` from this repo to the host). Dark X-style palette, clean modern look; the default diagram tool. |
| **Blueprint-style sketch** (system diagram, flow, wireframe) | `ferroprint` (anthonyrussano) | `cd ~/Projects/ferroprint && npm ci` (once), then `npm run export -- in.mmd --out <dir> --theme blue` (PNG + SVG, 3000 px wide; input Mermaid or a Ferroprint JSON). Blue blueprint sheet with a title block; use when that look suits the story, at most once per Article. |
| **Infrastructure architecture** (cloud icons, clusters) | `diagram-generator` (anthonyrussano) | `cd ~/Projects/diagram-generator && docker build -f Containerfile -t diagram-gen:local .` (GHCR image is private; never pull), then `./scripts/run-container.sh spec --spec <spec>.yaml --out-dir output/<dir> --output <name> --format png` (spec format: `docs/SPECS.md`; `--check` validates). Light background. |
| **Video frame** (slide, demo, chart or code at a cited timestamp) | `scripts/img/yt-frame.py` (this repo; run on the box) | `./run.sh yt-frame <video_id> <seconds> /workspace/<file>.png`: over ssh on iphedeiah (`config/whisper.json` remote, one reused connection, no cookies ever) it fetches only `*T-2-T+3` (best video <=1080p, no audio), grabs 9 frames T-1..T+1, keeps the sharpest (ffmpeg `blurdetect`), scales to 2400 px wide (native if smaller), copies it back and removes the temp dir. Falls back to the box only if iphedeiah is unreachable (bot checks likely). ~20 s. Tested Oct 20, 2026. |
| Screenshots, source figures | box browser | Section 3 (b), (c). |

**Video frames (`video-frame`)**: every Article that cites a video gets at least one still frame from it when a frame actually shows something (a slide, demo screen, diagram, chart or code view); skip talking heads. Use the same timestamp the Article cites: `./run.sh yt-frame <video_id> <seconds> /workspace/<EDITION>-<n>-<slug>.png`. Alt text names the channel and the video (e.g. `Slide from "<title>" (<channel>, YouTube): ...`), and the text next to the image links to the timestamped video (`https://www.youtube.com/watch?v=<id>&t=<s>s`). Record each in `check.md` and in `overnight.json` `images` with `kind: "video-frame"`, `source_url` (timestamped) and `timestamp` (seconds). Fair use: one or two frames per video, credited, used for commentary.

**Every number in a chart must come from the sources** cited in `research.md`: put the data file's values and their source URL in `check.md`, never estimate, interpolate or invent a value, and label units and dates. Same for numbers and names in diagrams. If a number cannot be sourced, drop it (or the chart).

## 4. Posting at 10:37 (routine B) and timing
- The 10:37 poster follows the `docs/HANDOFF.md` playbook. After pasting the body, for each `[[IMG: path | alt]]` paragraph in order: put the cursor on that paragraph, delete the marker text, insert the image file from `path` with the Article editor's media button, and set its alt/description to `alt`. Check no `[[IMG` text remains before publishing. A missing file: remove the marker and note it in the report.
- **Header:** use the prepared `/workspace/x-header-<EDITION>.jpg` (`header` in `overnight.json`). Re-check that its id is still unused in `state/x_posts.json`; if it was used meanwhile, or the file is missing, pick a fresh one per the playbook. Record `header` (id plus description) in `state/x_posts.json` as usual.
- The **2-hour gap** and **no posts after 9 PM PT** rules (`docs/HANDOFF.md` section 4b) still apply to every post.
