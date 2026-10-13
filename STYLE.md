# Article style guide: "Mind Blow" format

Every daily report reads like an episode of Vsauce2's *Mind Blow*: a fast run of short, self-contained items, each a small jolt of wonder. The writer (the scheduled Grok Bot routine) writes `articles/YYYY-MM-DD.md` from the day's transcripts (`data/relevant.json`, `data/transcripts/`) and the qualifying X posts (`data/x_selected.json`). `./run.sh render` turns it into `reports/YYYY-MM-DD.md`.

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

## Sources and citations
- **YouTube:** link the video when introducing it, and give the key moment a timestamped link (`https://www.youtube.com/watch?v=ID&t=<seconds>s`) on the sentence that describes it. Every video with a transcript must be cited at least once; `render_article.py` fails otherwise. Keep the substance: an item may hold 2–4 timestamped links.
- **X:** only posts from `data/x_selected.json` (last 24 h, bookmarks > likes, at least 10 bookmarks; that filter is for selection only). Write X-sourced items exactly like video items: who did, built or said what, the striking detail, and why it matters, with the post URL linked inline on the natural phrase. Never use platform framing: no "on X", no "posted", no "people saved", and no bookmark, like or save counts. X items mix into the run alongside the videos, ordered by story, and several small ones may share one item.
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
4. There are about 12–25 items of 2–4 sentences, each with who, what, one concrete number and why it matters, ordered by wow and importance.
5. Every transcribed video is linked, with key moments as `&t=<s>s` links (`./run.sh render` enforces this).
6. Every X item is drawn from `data/x_selected.json` and written like a video item. `grep -niE 'on x\b|bookmark|saves?\b|saved|likes?\b|posted' articles/<date>.md` prints nothing (check any hit by hand).
7. Every number and claim appears in a transcript or post and is attributed. Dubious claims are flagged, and there is no spam or crypto.
8. After `./run.sh publish`, the report URL returns HTTP 200 (allow about 1–2 minutes for Pages).
