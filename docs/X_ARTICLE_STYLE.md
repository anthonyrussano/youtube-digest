# X Article formats: roundup and deep-dive

The **website edition** (`articles/<EDITION>.md` -> `reports/<EDITION>.md`) is **always the roundup** in `STYLE.md`; nothing here changes it. The **X Article** on @russano comes in two named formats, and every edition picks one (selection rule below). Both are kept on purpose so we can compare them with data (`./run.sh x-stats`). **Both formats, roundups included, are written with the same four-step process** (`research.md`, `outline.md`, `article.md`, `check.md` in `articles/x/<EDITION>/`; decided Oct 19, 2026 by Anthony and his growth agent).

## Formats

| | **roundup** | **deep-dive** |
|---|---|---|
| What | Several stories, one short paragraph each, **led by one item** explained in plain language | One lead story in depth + "Also this cycle" |
| Used | Every X Article through edition `2026-10-17` (posted 11:00 AM PT Oct 17), then in the four-step form from Oct 19, 2026 | First used on edition `2026-10-17-1644` (Sat Oct 17, 2026 ~5 PM PT) |
| Source | `articles/x/<EDITION>/article.md`, written with the four steps below (`reports/<EDITION>.md` only as the `x-article` fallback when `article.md` is missing) | `articles/x/<EDITION>/article.md`, written with the four steps below |
| Structure | Lead item: its overlooked angle in plain language (a few short paragraphs); then one short linked paragraph per other story; closing question or call to action ("Roundup format in detail") | Hook on the overlooked angle, the lead in short lines (~400–800 words), takeaway, reply-inviting question, `## Also this cycle` with 4–6 linked one-liners |
| Title | Front matter `title:` leading with the lead item's idea (may tease 1–2 more) | Front matter `title:` naming the lead idea, never a list of three stories |
| Caption | Front matter `caption:` (same text on `format.txt` line 3) | Front matter `caption:` |
| Tool | `./run.sh x-article <ED> --format roundup` (renders `article.md`) | `./run.sh x-article <ED> --format deep-dive` (the default when `article.md` exists) |
| Model | Per-story paragraphs: `2026-10-14-1211`, `2026-10-15-1212` (`docs/HANDOFF.md` section 7) | Oct 15 Claude Code single-idea post (`2026-10-15-1705`, https://x.com/russano/status/2110889513455321578); sample `articles/x/2026-10-17-sample/`; first live `articles/x/2026-10-17-1644/` |

### Selection rule (decide per edition, in ROUTINE_PROMPT step 8)
1. **Deep-dive fits** only if the edition has **one lead story** with a **genuinely overlooked angle** (most coverage missed or under-explained it), an **actionable takeaway** (a how-to, pattern or fix, ideally dev/DevOps/agent tooling) and **enough primary-source material for ~400–600 words** (a full thread, paper, repo, transcript or post, not a one-line summary). Otherwise use **roundup**. Thin editions with no strong lead always get roundup.
2. **When both fit, alternate** to build comparison data: if the last posted Article in `state/x_posts.json` (highest `posted_at_utc`) has `"format": "deep-dive"`, prefer roundup this time; if it was roundup, prefer deep-dive.
3. Record the choice in `articles/x/<EDITION>/format.txt` (committed, public text only): line 1 `roundup` or `deep-dive`, line 2 a one-line reason, and for roundup line 3 `caption: ...` (the same caption as `article.md` front matter). `./run.sh x-article <EDITION>` then defaults to that format (and guards the roundup caption), so the 10:37 routine posts what the 6:04 run picked. After posting, record `"format": "roundup" | "deep-dive"` on the post in `state/x_posts.json` (`x-article` prints the value) and in the routine report.

### Shared rules (both formats)
- **Caption, tip-first:** lead with the single most useful **actionable tip** for developers/DevOps (preferably agent/coding tools such as Claude Code, Cursor, Codex), not spec numbers or model sizes; end with `...`. Data (Oct 19): the 3 tip-led Articles averaged 868 impressions and about 11 replies, against 368 impressions and 0.3 replies for the rest.
- **Timing:** at least 2 hours between any two Article posts (check the latest `posted_at_utc` in `state/x_posts.json`; if under 2 h, hold the committed Article for the next slot 2 h or more after the last post and report it), and no posts after 9 PM PT (queue for the next 12:04 PM PT slot unless Anthony explicitly says "post now"). Data (Oct 19): after-9 PM PT Articles averaged about 65 impressions vs about 640 for 12-4 PM PT; a second Article within about 30 minutes of another tanked (69 vs 328, 35 vs 128). Full rule: `docs/HANDOFF.md` section 4b.
- **Never "Mind Blow"** in a title, body or caption (`x-article` drops body lines containing it and refuses such a title or caption in `article.md`).
- **No `$` followed by a number** in a title or caption (write "3 dollars"). In the body, `x-article` inserts an invisible word joiner after `$` so X doesn't make a cashtag link.
- **Header:** a fresh high-resolution public-domain NASA photo of **Earth** (Anthony's standing choice since 2026-10-31; search images-api.nasa.gov for Earth views such as Blue Marble, ISS or Apollo Earth shots; no nebulae or other planets), not used before (`header` in `state/x_posts.json`), per the `docs/HANDOFF.md` playbook.
- **Inline images (both formats):** one per line in `article.md` as `[[IMG: /workspace/<file> | alt]]` where the image belongs: diagram-generator diagrams, **video frames** (still frames from cited YouTube videos at the cited timestamp, `./run.sh yt-frame`; at least one per Article that cites a video when a frame shows a slide, demo, diagram or code, never a talking head; alt names channel and video, nearby text links the timestamped video, 1-2 per video, credited), screenshots of key pages or charts, or source figures whose license allows reuse. Check every number in an image against its source. `x-article` keeps the marker as its own paragraph and the poster swaps it for the image (`docs/OVERNIGHT.md` section 3, `docs/HANDOFF.md` playbook step 4b). Weekday morning Articles get them from the overnight prep run.
- Same sourcing rules as `STYLE.md`: link the claim text, attribute vendor numbers, no platform framing or engagement counts, never link or name the newsletter.

# Roundup format in detail
## Structure
- **Front matter:** quoted `title:` leading with the lead item's idea (may tease one or two more stories), quoted `caption:` (shared rules), `edition:` and `lead_source:` (primary URL of the lead item).
- **Lead item first:** the edition's most overlooked or most practical story, preferably an actionable dev/DevOps/agent-tooling idea. Research its overlooked angle (step 1) and explain it in plain language in a few short paragraphs: what happened, what most coverage missed, why it matters.
- **Then the other items:** one short paragraph per story (2–3 sentences: who, what, one concrete detail, why it matters), linked on the claim, same sourcing as `STYLE.md`. No `##` sections needed.
- **Close:** a closing question or call to action that invites replies.
- The website edition `reports/<EDITION>.md` stays the classic roundup (`STYLE.md`), unchanged; the X roundup is written from the same edition's sources but is its own file.

# Deep-dive format in detail
## Structure
- **Front matter:** quoted `title:` that names the lead idea (not a list of three stories), quoted `caption:` (rules below), `edition:` and `lead_source:` (primary URL).
- **Lead story:** roughly **400–800 words**. Pick the most overlooked or most practical story of the edition, preferably an actionable dev/DevOps/agent-tooling idea (a how-to, pattern or fix a reader can apply). Big launches everyone already covered rarely make the lead.
- **`## Also this cycle`:** 4–6 one-line bullets (`- `), each with its link, drawn from the same edition.
- Short `##` section labels in the lead are fine (they render as bold lines). One line = one paragraph; use blank lines freely. Bold key phrases where it helps.
- Sourcing: the shared rules above. Outside facts found in research are fine if each is linked to its source.

## Caption
The shared caption rule, written as front matter `caption:`. `./run.sh x-article` refuses an `article.md` whose title or caption breaks the rules.

# The four-step process (both formats; artifacts committed under `articles/x/<EDITION>/`)
All of it is public-source material. Never put `data/`, `state/`, subscriptions or the newsletter text in these files (quote/link the original sources instead).

1. **`research.md`.** Gather the raw facts from the cited sources: transcripts, articles, X posts (read the full thread and author replies), AINews summaries (pointing to their original sources). Do a quick web/X search to see what most creators already covered and what they overlooked or under-explained. Prioritize overlooked technical details, implications and nuances. End with the chosen angle in one sentence (roundup: the lead item's angle, plus the facts for the other items). Keep a short candidates table (why lead / coverage / verdict).
2. **`outline.md`.** A simple, logical structure that explains **one core idea at a time** in plain language. Drop jargon or define it right away. Focus on why it matters and what people are missing. Deep-dive: include the "Also this cycle" picks. Roundup: the lead item's angle in a few plain points, then the order of the other items (one line each), then the closing question/CTA.
3. **`article.md`.** Write from the outline (read `docs/WRITING_GUIDE.md` first):
   - Short, direct sentences.
   - Open with a strong hook built on the overlooked angle.
   - A technically curious non-expert can follow it without rereading.
   - End with a short takeaway, then a clear question or call to action that invites replies.
   - Line breaks for readability, **bold** key phrases where it helps. Cut anything overloaded or redundant.
   - Deep-dive: ~400–800 words for the lead story. Roundup: a few short paragraphs for the lead item, then one short paragraph per other story.
4. **`check.md` (final check).** Review the research summary, tighten the outline, check clarity, and confirm the overlooked angle is **real, sourced and explained simply**. Check the rules (title names the idea, caption tip-first ending in `...`, no `$<number>`, no "Mind Blow"; deep-dive: word count and 4–6 extras; roundup: lead item first, one short paragraph per other story, closing question/CTA). Fix `article.md` if anything fails and record what changed, then run `./run.sh x-article <EDITION>` (or `--dry-run`) and confirm it prints the chosen `FORMAT` and `SOURCE: articles/x/<EDITION>/article.md`.

Then post via the `docs/HANDOFF.md` "X Article playbook".

## Winning formula (adopted 2026-10-24; overrides the 2026-10-20 "Format default" and the lead-first roundup above)
Data (state/x_impressions.csv, 25 measured Articles, Oct 13-23): the only 1,000+ posts were edition `2026-10-17` (1,021, Sat 11:00 AM PT) and `2026-10-18-1341` (1,332, Sun 2:41 PM PT). The next three (917, 725, 693) were also this shape. All five were the **classic full roundup**: the whole website edition (`reports/<EDITION>.md`, ~1,100-2,000 words, 12-20 stories) posted as is. Classic roundups (13) averaged 523 impressions; the four-step lead-first roundups with a short "Also this cycle" list (6) averaged 222, and deep dives (6) averaged 190. Small sample; the two winners were weekend posts, and classic roundups also produced 32s, so this is a strong lean, not a law.

**Default X Article = classic roundup.** Checkable rules:
1. **Body = the full edition.** `article.md` carries the same stories as `reports/<EDITION>.md`: a cold open with 1-2 hard numbers, "Here is what happened in AI and DevOps this cycle.", then **every story as its own 2-4 sentence paragraph** with the claim text linked (timestamped video links), a "A few quick ones." line for small items. At least **10 story paragraphs** and **1,000+ words** (`x-article` warns below that). **No `##` sections and no bulleted "Also this cycle" list.** Lead with the edition's strongest/broadest story (big named brand + hard number), not a niche angle.
2. **Title = three-item list** naming brands/tools with numbers, `A, B, and C` (Oxford comma), 75-100 characters, e.g. "Agents ship 60% of Vercel deploys, DeepSeek Flash cuts tokens 44%, and 1,000 Claudes tackle an OS". Never a single-idea essay title.
3. **Caption = tip-first**: `<Tool> tip:` + one concrete action a dev can do today (Claude Code / Codex / Cursor / agents preferred), drawn from one of the stories, 120-250 characters, ends with `...`. Never blank.
4. **Images:** NASA header plus at least one cited-video still frame (`[[IMG: ...]]` on its own line right after the paragraph that cites it), 1-3 total. The winners had no inline images, so keep them few.
5. **Timing:** prefer 11 AM-3 PM PT; weekend editions are the strongest slots. Hard limits below.
6. The four-step artifacts are optional for the classic roundup: write `check.md` with the rules above ticked. Deep-dive only on Anthony's request or a truly exceptional single story.

**Craft:** draft and check every Article against `docs/WRITING_GUIDE.md` (title/caption shapes, contrast, ban list; `x-article` warns on banned words). It never overrides the rules here.

## Hard rules (never change without Anthony)
- No "Mind Blow" anywhere. Titles 100 characters or fewer. No `$` followed by a digit in title or caption. Fresh NASA Earth header. At least one cited-video still frame. Caption never blank.
- **At most 2 Article posts per PT day, at least 4 hours apart, only between 8 AM and 3 PM PT.** An Article that misses the window is held for the next valid slot (this supersedes the older 2-hour gap / 9 PM cutoff).
