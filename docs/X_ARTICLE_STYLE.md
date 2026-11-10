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
- **Caption, rotating shapes (2026-11-10, overrides tip-first and `STYLE.md` "X share caption"):** pick one of the four shapes in "Algorithm-informed rules" below, never the same shape as the previous posted Article (`caption_shape` of the latest entry in `state/x_posts.json`), and end with `...`. Tip-first remains one of the four shapes. Data (Oct 19): the 3 tip-led Articles averaged 868 impressions and about 11 replies; the rotation exists to avoid a templated-account look (`llm_slop_user`, duplicate-content rules), not because tips stopped working.
- **Timing:** the Hard rules below (at most 2 per PT day, at least 4 hours apart, 8:00 AM-5:30 PM PT during the 2026-11-10 window experiment). Full rule: `docs/HANDOFF.md` section 4b. Data (Oct 19): after-9 PM PT Articles averaged about 65 impressions vs about 640 for 12-4 PM PT; a second Article within about 30 minutes of another tanked (69 vs 328, 35 vs 128).
- **Close (both formats, 2026-11-10):** the Article ends with, in order: one short first-person take, a reply-inviting question, a share prompt, a follow line (details in "Algorithm-informed rules").
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
- **Close:** the four-part close (shared rules): take, reply question, share prompt, follow line.
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
   - End with the four-part close: a one-line first-person take, a reply-inviting question, a share prompt, a follow line ("Algorithm-informed rules").
   - Line breaks for readability, **bold** key phrases where it helps. Cut anything overloaded or redundant.
   - Deep-dive: ~400–800 words for the lead story. Roundup: a few short paragraphs for the lead item, then one short paragraph per other story.
4. **`check.md` (final check).** Review the research summary, tighten the outline, check clarity, and confirm the overlooked angle is **real, sourced and explained simply**. Check the rules (title names the idea, caption in an allowed shape that differs from the previous post's `caption_shape` and ends in `...`, no `$<number>`, no "Mind Blow", no sentence reused from earlier Articles or captions, four-part close present with share and follow wording not identical to the previous post; deep-dive: word count and 4–6 extras; roundup: lead item first, one short paragraph per other story, closing question/CTA). Fix `article.md` if anything fails and record what changed, then run `./run.sh x-article <EDITION>` (or `--dry-run`) and confirm it prints the chosen `FORMAT` and `SOURCE: articles/x/<EDITION>/article.md`.

Then post via the `docs/HANDOFF.md` "X Article playbook".

## Winning formula (adopted 2026-10-24; overrides the 2026-10-20 "Format default" and the lead-first roundup above)
Data (state/x_impressions.csv, 25 measured Articles, Oct 13-23): the only 1,000+ posts were edition `2026-10-17` (1,021, Sat 11:00 AM PT) and `2026-10-18-1341` (1,332, Sun 2:41 PM PT). The next three (917, 725, 693) were also this shape. All five were the **classic full roundup**: the whole website edition (`reports/<EDITION>.md`, ~1,100-2,000 words, 12-20 stories) posted as is. Classic roundups (13) averaged 523 impressions; the four-step lead-first roundups with a short "Also this cycle" list (6) averaged 222, and deep dives (6) averaged 190. Small sample; the two winners were weekend posts, and classic roundups also produced 32s, so this is a strong lean, not a law.

**Default X Article = classic roundup.** Checkable rules:
1. **Body = the full edition.** `article.md` carries the same stories as `reports/<EDITION>.md`: a cold open with 1-2 hard numbers, "Here is what happened in AI and DevOps this cycle.", then **every story as its own 2-4 sentence paragraph** with the claim text linked (timestamped video links), a "A few quick ones." line for small items. At least **10 story paragraphs** and **1,000+ words** (`x-article` warns below that); aim for **10-14 tight items** and cut stories only loosely related to AI or DevOps rather than padding (a "not interested" or mute costs far more than a like earns; see "Algorithm-informed rules"). **No `##` sections and no bulleted "Also this cycle" list.** Lead with the edition's strongest/broadest story (big named brand + hard number), not a niche angle.
2. **Title = three-item list** naming brands/tools with numbers, `A, B, and C` (Oxford comma), 75-100 characters, e.g. "Agents ship 60% of Vercel deploys, DeepSeek Flash cuts tokens 44%, and 1,000 Claudes tackle an OS". Never a single-idea essay title.
3. **Caption = one of the four rotating shapes** ("Algorithm-informed rules"; changed 2026-11-10 from tip-first only), never the previous post's shape, drawn from the stories, ends with `...`. Never blank. The old 120-250 character habit is fine but is not a rule (the ranking code has no caption-length logic).
4. **Images:** NASA header plus at least one cited-video still frame (`[[IMG: ...]]` on its own line right after the paragraph that cites it), 1-3 total. The winners had no inline images, so keep them few.
5. **Timing:** weekday 6:04 Article at 10:37 AM; 12:04 and 5:04 PM Articles right after publish when the Hard rules allow (5:30 PM PT window experiment). Weekend editions are the strongest slots. Log posting hour in the impressions analysis.
6. The four-step artifacts are optional for the classic roundup: write `check.md` with the rules above ticked. Deep-dive only on Anthony's request or a truly exceptional single story.
7. **Close:** the four-part close (take, reply question, share prompt, follow line), replacing the old sign-off as the last lines. The take is one short first-person line in @russano's voice.

**Craft:** draft and check every Article against `docs/WRITING_GUIDE.md` (title/caption shapes, contrast, ban list; `x-article` warns on banned words). It never overrides the rules here.

## Hard rules (never change without Anthony; last changed 2026-11-10 with his approval)
- No "Mind Blow" anywhere. Titles 100 characters or fewer. No `$` followed by a digit in title or caption. Caption ends in `...`. Fresh NASA Earth header. At least one cited-video still frame. Caption never blank.
- **At most 2 Article posts per PT day, at least 4 hours apart, only between 8:00 AM and 5:30 PM PT.** The 5:30 PM end is an **experiment** (2026-11-10; was 3 PM): a 5:04 PM edition's Article posts right after publish if it is before 5:30 PM PT and 4+ hours after the last post, otherwise it is held for the next valid slot. Compare by posting hour in the impressions review before keeping it. Anthony's "post now" overrides timing.
- **Caption shape rotates** among the four shapes below; never the same `caption_shape` on two consecutive posts. Record `caption_shape` on every new `state/x_posts.json` entry.
- **Four-part close** on every Article: first-person take, reply question, share prompt, follow line. Share and follow wording rotates (never identical to the previous post).
- **No bookmark goals.** Bookmarks carry zero weight in the ranking code; optimize for shares, replies, quotes and follows.
- **Not adopted, on purpose:** no switch to video (video-watch weight is 0), and no caption-length or link-avoidance rules (the code has neither).

## Algorithm-informed rules (2026-11-10, from xai-org/x-algorithm; evidence in `docs/HANDOFF.md` "Algorithm notes")
**Goal:** a post's rank is the sum of each viewer's predicted chance of an action times that action's weight. Copy-link share (20), reply (5, plus 15 on original posts between mutual follows), quote (5), DM share (5) and follow (4) dominate; like is about 0.7; bookmark and video watch are 0; report (-234), mute (-58.8), "not interested" (-53) and block (-31) are heavy negatives. So write for **shares, replies, quotes and follows**, and avoid anything that makes a reader mute us.

**Caption shapes** (record as `caption_shape`; never repeat the previous post's shape; all end in `...`):
- `tip` : tip-first plus "Meanwhile" + the edition's most surprising fact (the old default).
- `question` : opens with a question a practitioner would want to answer, then one concrete fact from the edition.
- `number` : opens with one striking number from a story, then the takeaway in plain words.
- `contrarian` : one opinion or contrarian line grounded in the cited facts, then the evidence.
Write every caption fresh: never reuse a sentence from an earlier caption or Article (duplicate-content and `llm_slop_post` risk).

**Four-part close** (last lines of every Article, both formats):
1. **Take:** one short first-person line in @russano's voice ("My take: ...", "I'd start with ...", "If I ran a platform team, I'd ..."), an opinion or recommendation grounded in facts the Article cites. Never an invented fact, experience, employer or result.
2. **Reply question:** offers 2-3 concrete choices from the edition (replies weigh 5, plus 15 between mutual follows).
3. **Share prompt:** names who should get it, e.g. "Send this to the teammate who runs your CI.", "Forward this to whoever owns your on-call rotation." Rotate the wording; never repeat the previous post's exact phrasing.
4. **Follow line:** a short reason to follow, e.g. "I post one of these most weekdays: the AI and DevOps news that changes how you build. Follow to get the next one." Rotate the wording; never "Mind Blow".

**Story selection:** 10-14 tight AI or DevOps items; cut loosely related stories (negative feedback outweighs many likes). Keep the 10+ linked-story roundup minimum.

**First two hours:** original posts from authors with 50,000 or fewer followers get a cold-start boost while under about 2 hours old and under 200 Home views. Our own replies are not shown to non-followers, so the poster's message to Anthony suggests he reply to early commenters within about 2 hours.

**Future test (not scheduled):** a separate native post (not an Article) at a different hour, to compare reach; only on Anthony's go-ahead.
