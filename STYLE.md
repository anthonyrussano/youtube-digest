# Article style guide

Every daily report is a **longform news article**: a roundup of the latest AI and DevOps news, reported from the day's videos. The writer (the scheduled Grok Bot routine) writes `articles/YYYY-MM-DD.md`, and `./run.sh render` turns it into `reports/YYYY-MM-DD.md`.

## Shape
- **Front matter:** `title:` is the headline (specific and newsy, built around the day's biggest story) and `dek:` is a one-sentence subheadline. Both go in double quotes.
- **Lede:** the first paragraph has no subhead. It names the biggest development and why it matters, then sets up the second story.
- **Body:** organize by story or theme, not one video at a time. Merge related videos into a single narrative (for example, Google's and OpenAI's always-on agents in one section). Use 3–7 `##` section subheads. Put the most newsworthy items first and ideas and curiosities last.
- **No metadata:** no channel/date/length lines, no bullet lists, no tables, no "Key moments:" rows. Write flowing paragraphs only. Mention the channel or speaker in prose where it helps ("Jeff Geerling says…").
- **Also on the radar:** the renderer appends this automatically, as one paragraph linking the titles of relevant videos that have no usable transcript. Don't summarize them.

## Citations
- Link the claim text itself: `[found a latency regression](https://www.youtube.com/watch?v=ID&t=60s)`. Don't add footnotes or "(source)" tails.
- Use a timestamped link `&t=<seconds>s` for every key moment you have, at the sentence that describes it. Use the plain video URL when introducing a video.
- Every video with a transcript must be cited at least once. `render_article.py` fails if one is missing.

## Accuracy
- Report only what the transcript says. Don't add outside facts, prices, dates or specs, and don't fill gaps from memory.
- Attribute claims and vendor numbers to the speaker ("GitHub claims up to 67% lower cost"). Keep the original numbers and their units.
- Neutral news voice: short declarative sentences, no hype words, no second-person marketing.
- Length should follow the material, typically 1,500–3,000 words.

Reference example: `articles/2026-10-12.md`.
