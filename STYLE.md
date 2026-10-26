# Article style guide: "Mind Blow" format

Every daily report reads like an episode of Vsauce2's *Mind Blow*: a fast run of short, self-contained items, each a small jolt of wonder. The writer (the scheduled Grok Bot routine) writes `articles/<EDITION>.md` (`YYYY-MM-DD` or `YYYY-MM-DD-HHMM`) from the edition's new transcripts (`data/relevant.json`, `data/transcripts/`), the qualifying X posts (`data/x_selected.json`) and the selected feed articles (`data/feeds_selected.json`). `./run.sh render` turns it into `reports/YYYY-MM-DD.md`.

This guide covers the **website edition**, which is always this roundup. The X Article on @russano uses one of two named formats per edition: **roundup** (several stories led by one researched item) or **deep-dive** (a single-lead piece), both written with a four-step process in `articles/x/<EDITION>/`. This page is not the X Article source and does not change. See [`docs/X_ARTICLE_STYLE.md`](docs/X_ARTICLE_STYLE.md).

On weekdays the morning edition is drafted overnight as `articles/x/<EDITION>/draft-report.md` (same format; `docs/OVERNIGHT.md`) and the 6:04 AM run copies it to `articles/<EDITION>.md`, polishes and publishes it.

**Craft guide:** read [`docs/WRITING_GUIDE.md`](docs/WRITING_GUIDE.md) (diction, contrast, rhythm, formatting, before/after examples, Lessons log) before drafting; it never overrides this file.

"Mind Blow" is only the internal name of this format. **Never write "Mind Blow" in a title, dek, body or X caption.**

## Shape
- **Front matter:** `title:` is a short, punchy headline that teases two or three of the best items. `dek:` is one line. Both go in double quotes.
- **Cold open:** one or two quick, striking hits (a sentence each, linked) before any setup.
- **One-line intro,** for example "Here is what happened in AI and DevOps this cycle."
- **Items:** about 12–25 of them, one paragraph each, 2–4 sentences. Every item:
  1. names who did it (team, company or person),
  2. says plainly what they made, found or announced,
  3. gives one concrete jaw-dropping detail (a number, price, spec or result),
  4. ends with why it matters or what comes next.
  Related videos and posts on the same story merge into one item. Order items by how mind-blowing and important they are, not by source or theme.
- **Sign-off:** a brief, playful closing line.
- **Forbidden:** `##` headers, theme sections, bullet lists, tables, metadata lines (channel, date, length) and a separate X section. The renderer adds "*Also on the radar:*" itself as a plain final paragraph.

## Editions
- There are several editions a day (see README "Editions"). Each covers only what is new since the previous edition. Never repeat a story that is already published; `render` blocks reused video and post IDs.
- A later edition is shorter when the material is thin. Fewer items (as few as 5) are fine, and so is a one-hit cold open. Don't pad.
- **X-only or articles-only edition:** with no new transcribed videos, an edition may be built from X items if at least 5 good ones qualify, or from feed articles if at least 2 strong (tier 1–2, in `data/feeds_selected.json`) qualify. Use the same format and voice, with no mention of the platform. Otherwise `render` prints `SKIP:`.
- The `title:` should still tease the edition's best items. The page shows the date and edition time automatically, so don't put "noon edition" in the text.

## Sources and citations
- **YouTube:** link the video when introducing it, and give the key moment a timestamped link (`https://www.youtube.com/watch?v=ID&t=<seconds>s`) on the sentence that describes it. Every video with a transcript must be cited at least once; `render_article.py` fails otherwise. Keep the substance: an item may hold 2–4 timestamped links.
- **X:** only posts from `data/x_selected.json` (since the window start, at least 10 bookmarks and either bookmarks > likes or 30+ reposts / 5+ quotes; that filter is for selection only). Write X-sourced items exactly like video items: who did, built or said what, the striking detail, and why it matters, with the post URL linked inline on the natural phrase. Never use platform framing: no "on X", no "posted", no "people saved", and no bookmark, like or save counts. X items mix into the run alongside the videos, ordered by story, and several small ones may share one item.
- **Trending topics:** posts tagged with `trends` in `data/x_selected.json` match today's top categories in `data/x_trends.json`. at equal quality prefer them and open the cold open with the strongest trending story. Never mention trends, volumes or counts in the article.
- **Articles (feeds):** only items from `data/feeds_selected.json` (3–6 per edition). Write them like video items, with the article URL linked on the claim and no "in a blog post" framing. When a video or X post covers the same story, merge it into one item and use the primary article as the main citation.
- **AINews stories:** only items from `data/ainews_selected.json`. Write them like video items and link the original sources the item lists (X post, paper, repo, blog), never the newsletter, substack, latent.space or the email; no "according to a newsletter" framing. Merge with the same story from feeds, X or video. Use only facts in the item's summary.
- Link the claim text itself. No footnotes or "(source)" tails.

## Accuracy and tone
- Report only what the transcript or post says. Don't add outside facts, and attribute vendor numbers and claims ("GitHub claims up to 67%"). Flag promotional or dubious X claims in a short clause, and leave out spam and crypto promotion.
- Write punchy, plain and wonder-driven. Use short sentences and concrete numbers, with no hype words such as "revolutionary" and no second-person marketing. A light "and here's the wild part" energy is fine, but the facts carry the wonder.


## Annotated example (from `articles/2026-10-12.md`)

**Cold open.** Two quick hits, each linked, with no setup. One comes from an X post and one from a video:

> A tool called REA [claims to let an AI agent reverse engineer any app, down to the binary](https://x.com/0xCodila/status/2109623431763292649). Meanwhile [a robot arm in Texas was driven live from New York](https://www.youtube.com/watch?v=7sKHiuE7J-Y&t=3s) through a web browser.
>
> Here is what happened in AI and DevOps this cycle.

**Video item.** It names who (Neki Replicator), says what (moves huge Postgres databases), gives the jaw-dropping numbers (0.5–2 TB/h, five-second cutover), says why it matters (the known 20–40 h snapshot problem is avoided) and ends with what comes next (auto-revert). Each detail is a timestamped link:

> Neki Replicator [moves Postgres databases tens of terabytes in size](https://www.youtube.com/watch?v=Fw2Jy6of7MI) at about 0.5–2 TB per hour per shard. It works around a known problem: [logical replication holds one snapshot for 20–40 hours](https://www.youtube.com/watch?v=Fw2Jy6of7MI&t=124s) and bloats the WAL. Neki instead copies in [batches with snapshots of about 15 minutes](https://www.youtube.com/watch?v=Fw2Jy6of7MI&t=427s). The [cutover usually takes about five seconds](https://www.youtube.com/watch?v=Fw2Jy6of7MI&t=854s), is capped at 30, and reverts automatically if something goes wrong.

**X item, written the same way.** It has the same who/what/detail/why shape. The post is linked on the natural phrase, and there is no "on X", no counts and no "posted":

> A startup is chasing the same idea on the desktop. Aditya Vellanki introduced [Sentient OS](https://x.com/aditya_vellanki/status/2109699200682524921), on-device AI that he says "understands your whole life overnight" and picks up tasks on the computer with its own cursor. He says it is backed by Y Combinator, Afore Capital and Pioneer Fund. If it works as pitched, the always-on agent moves off the cloud and onto your own machine.

**Sign-off.** A brief and playful closing line:

> That's the cycle. Go encrypt a drive, check your cache hit rate, and see you tomorrow.

## Pre-publish checklist
1. The front matter has a quoted `title:` (short, teasing two or three items) and a quoted `dek:`.
2. The article has a cold open of one or two linked hits, then a one-line intro, then items, then a sign-off. Nothing else.
3. There are no `#` headers, bullets, tables or metadata lines (`grep -nE '^(#|[-*] |\|)' articles/<date>.md` prints nothing).
4. There are about 12–25 items (fewer in a thin later edition, at least 5 for X-only) of 2–4 sentences, each with who, what, one concrete number and why it matters, ordered by wow and importance.
5. Nothing from an earlier edition is repeated. Every new transcribed video is linked, with key moments as `&t=<s>s` links (`./run.sh render` enforces this).
6. Every X item is drawn from `data/x_selected.json` and written like a video item. `grep -niE 'on x\b|bookmark|saves?\b|saved|likes?\b|posted' articles/<date>.md` prints nothing (check any hit by hand).
7. Every number and claim appears in a transcript or post and is attributed. Dubious claims are flagged, and there is no spam or crypto.
8. The craft checklist in `docs/WRITING_GUIDE.md` section 6 passes.
9. After `./run.sh publish`, the report URL returns HTTP 200 (allow about 1–2 minutes for Pages).

## X share caption
Applies to both X Article formats (`caption:` in `articles/x/<EDITION>/article.md`; for roundup also line 3 of `articles/x/<EDITION>/format.txt`; see `docs/X_ARTICLE_STYLE.md`). The rules:
- Lead with the **single most useful, actionable takeaway for developers and DevOps people**: a how-to, a pattern or a tip, preferably about agent or coding tools (Claude Code, Cursor, Codex and the like). Example: `Anthropic's Claude Code tip: each agent gets its own repo copy so three edit without colliding...`
- **Don't lead with spec numbers or model sizes.** Numbers may support the takeaway but never are the hook.
- Always end with `...`. Never write "Mind Blow". Avoid `$` followed by a number (write "3 dollars").
