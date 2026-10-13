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

Reference example: `articles/2026-10-12.md`.
