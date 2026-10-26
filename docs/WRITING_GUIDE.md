# Writing guide: diction, contrast, rhythm, formatting (living document)

This is the **craft layer** on top of the specs. `STYLE.md` (website edition) and `docs/X_ARTICLE_STYLE.md` (X Article, including its **Hard rules** and **Winning formula**) define *what* ships; this guide covers *how it reads*. If anything here seems to conflict with those two files, they win; fix this guide. Every writer (edition routine, overnight prep, X Article drafting) reads this before drafting, and the weekly impressions review appends to the **Lessons log** at the bottom.

Never write the internal format name ("Mind Blow") anywhere in published text. Never put private raw data (`state/`, `data/`, subscriptions) in this file: aggregates only.

## 1. Diction

**Prefer** concrete nouns and strong verbs: *ships, cuts, breaks, leaks, beats, moves, caps, reverts, replays, drops*. Name the actor: "Grafana cut its tool definitions from 54,500 tokens to ..." not "Tool definitions were reduced".

**Verbs over adjectives.** Delete the adjective and let the number do the work.
- "a huge speedup" -> "cut a 565-second load to 93 seconds"
- "an incredibly large model" -> "a trillion-parameter open-weight model"

**Concrete numbers.** One per item minimum (STYLE.md rule 3). Give the unit and the comparison: "20% either way", "1 in 5 PRs", "5 to 8 billion dollars apart". Round only when the source rounds. Attribute vendor numbers ("GitHub claims ..."). In titles and captions write "3 dollars", never `$3`.

**Ban list** (cut on sight; `x-article` warns on these):
- Hype: *revolutionary, game-changer/game-changing, groundbreaking, mind-blowing, insane, unprecedented, cutting-edge, next-level, massive, huge* (use the number instead).
- Filler: *basically, essentially, incredibly, literally, really, very, just* (as filler), *it's worth noting, it's important to note, in today's world, at the end of the day, needless to say, in order to* (-> "to").
- Corporate/AI-tell: *leverage, seamless(ly), robust, delve, unlock, empower, supercharge, landscape, ecosystem* (unless literal), *harness the power*.
- Platform framing (STYLE.md): *on X, posted, bookmarks, likes, saves, went viral, according to a newsletter, in a blog post*.

**Jargon policy.** A technically curious non-expert must follow without rereading. Keep standard terms the audience uses (MCP, WAL, CVE, microVM, PR, eval); define anything narrower in a clause the first time ("logical replication, which streams row changes from one database to another"). One undefined term per paragraph, maximum. Spell out an acronym only if a DevOps reader wouldn't know it.

**Second person:** fine in the "why it matters" line and the closing question ("check your cache hit rate"); never marketing-style ("You won't believe ...").

## 2. Juxtaposition and contrast

Contrast is the engine of the wonder. Use at least three of these per edition:
- **Big vs small number:** "Robots that could do 34% of the work but pay off on 0.3%." Put the two numbers in one sentence.
- **Claim vs reality:** state the pitch, then the catch, with attribution: "He says it understands your whole life overnight. The demo shows one calendar."
- **X but Y hooks:** "Your browser already blocked the stolen keys. Your containers didn't." Two short sentences beat one with a comma.
- **Before/after:** "565 seconds -> 93 seconds", "20-40 hour snapshot -> 15-minute batches".
- **Neighbor ordering:** order by wow and importance first (STYLE.md), then swap adjacent items so neighbors differ: a security item next to a hardware item, a giant launch next to a one-person hack, a model release next to an ops fix. Never three model launches in a row.
- **Transitions:** link items with a single connecting phrase only when there is a real link: "A startup is chasing the same idea on the desktop.", "The opposite problem shows up in ...", "Meanwhile ...". Otherwise start the next paragraph cold with the actor's name. Don't use "Next up", "In other news", "Moving on", "Also".

## 3. Rhythm and paragraph shape

- **Cold open:** 1-2 linked hits, a sentence each, the most surprising fact first, no setup, no date, no "This week". Pair two unrelated hits with "Meanwhile" for an instant contrast. Then the fixed line "Here is what happened in AI and DevOps this cycle."
- **One-detail rule:** each item has one star detail. Supporting numbers may follow, but the reader should be able to repeat one fact from each paragraph. If you have two stars, split the item or cut one.
- **Sentence rhythm:** mix one short punch (under 10 words) with longer explaining sentences. Open each paragraph with who + verb. Never open two paragraphs in a row with the same word.
- **Landing the "why it matters" line:** last sentence, concrete consequence or next step, not a moral. Good: "If it works as pitched, the always-on agent moves off the cloud and onto your own machine." Bad: "This is a big deal for the industry." Test: could this line end any other item? If yes, rewrite.
- **Sign-off:** one playful line that callbacks 1-2 items as actions ("Go encrypt a drive, check your cache hit rate, and see you tomorrow.").

## 4. Formatting

**Website edition (`articles/<EDITION>.md`):** quoted `title:` teasing 2-3 items, one-line quoted `dek:` that uses a contrast; cold open, intro line, item paragraphs, sign-off. No headers, bullets or tables (STYLE.md). Link the claim words themselves, with `&t=<s>s` on the sentence describing that moment; 3-8 words of link text, never "here" or a bare URL.

**X Article (`articles/x/<EDITION>/article.md`, classic full roundup by default):**
- **Title:** three named brands/tools, each with a number, `A, B, and C`, 75-100 characters. Lead with the biggest brand + hardest number. Each clause gets its own verb ("cuts", "ships", "beats").
- **Caption:** `<Tool> tip:` + one action a dev can do today, 120-250 characters, ending `...`. Best shape so far: tip, then "Meanwhile" + the edition's most surprising fact. Never blank, no `$<digit>`.
- **Images:** NASA header; 1-3 inline `[[IMG: ...]]` lines, each on its own line directly after the paragraph that cites it, at least one cited-video frame showing a slide/demo/code (never a talking head); alt names channel and video.
- **Close:** a reply question offering 2-3 concrete choices from the edition, then the sign-off.

## 5. Before and after (real past copy)

**Title.** Before (101 impressions, no caption): "Wrong AI races, biology meets agents, and builders budgeting context overnight". After (pattern): "<Brand> <verb> <number>, <Brand> <verb> <number>, and <Brand> <verb> <number>". Why: named brands and numbers in every clause; the winner "Agents ship 60% of Vercel deploys, DeepSeek Flash cuts tokens 44%, and 1,000 Claudes tackle an OS" has three verbs and three numbers.

**Title (single idea vs list).** Before: "OpenAI's red-team agents broke out of microVMs and talked through a CPU cache. Here's what that means for your agent hosts." (over the 100-char budget, narrow). After (illustrative, mixing the same week's stories): "OpenAI agents escape microVMs, Kaggle finds 20% score swings, and a 12 GB GPU runs 10x faster".

**Caption.** Before (32 impressions): a truncated "Forml". Before (numbers-led): "Mistral just previewed a trillion-parameter open-weight model, and a 155 GB DeepSeek loads ...". After (the 781-impression pattern): "Claude Code tip: ask it for a full security audit of each server, then have it write Tailscale policies so no box can reach another. Meanwhile Kaggle caught a model stealing API keys to cheat a benchmark..."

**Paragraph (adjective -> number).** Before: "Ethan Mollick points to a paper showing small accuracy gains compound over long-horizon tasks, creating huge differences in outcomes." After: "Ethan Mollick points to a paper where small accuracy gains compound: a few points per step become a different outcome over a long task. His takeaway: frontier models are hard to swap for cheaper ones."

**Paragraph (claim vs reality).** Before: "Vercel open sourced a fast HTML artifact builder powered by libfx, which makes the agent durable." After (rewrite only from facts in the source): "Vercel open-sourced the plumbing that kept v0 alive through server crashes and flaky models. Guillermo Rauch says it makes the agent durable; the repo shows what that took."

**Cold open.** Strong (2026-10-25): "While auditing benchmarks, Kaggle caught a model that found another model's API keys inside the eval container, called that model and handed in its answer." One actor, one shocking act, no setup.

## 6. Pre-publish checklist (craft; run after the STYLE.md / X_ARTICLE_STYLE.md checklists)
1. `grep -niwE 'revolutionary|game.?chang\w*|groundbreaking|insane|unprecedented|cutting.edge|massive|huge|basically|essentially|incredibly|literally|leverag\w*|seamless\w*|robust|delve|unlock\w*|supercharg\w*' <file>` prints nothing (or each hit is literal and justified).
2. Every paragraph opens with an actor + verb and has exactly one star detail with a unit.
3. The edition has 3+ contrast devices (big/small, claim/reality, X-but-Y, before/after); no two adjacent items share a topic.
4. Each "why it matters" line passes the "could end any other item?" test.
5. Title: three named items with numbers and verbs, 75-100 characters (X); dek uses a contrast (web).
6. Caption: `<Tool> tip:` + action, ideally "Meanwhile" + surprise, 120-250 chars, ends `...`.
7. Images sit right after the paragraph that cites them; link text is the claim, never "here".
8. Read the cold open and the first sentence of each paragraph aloud in sequence: it should sound like a fast list of surprises.

## 7. How this guide improves

- **Weekly (Monday impressions tracker, `docs/HANDOFF.md` routine C):** append one dated entry to the Lessons log below: what the last ~7 days showed (aggregates: counts, averages, ranges; no post IDs, raw rows or captions copied wholesale), and a "Proposed tweak" line. Low-risk craft tweaks (ban-list words, examples, transition phrases) may be applied to sections 1-6 in the same commit. Anything touching the **Hard rules** or the **Winning formula** is proposed only and goes to Anthony.
- Any writer who spots a repeated weakness while drafting may add a one-line entry too.
- Keep entries short; when the log passes ~25 entries, fold settled lessons into sections 1-6 and trim.

## 8. Lessons log

- **2026-10-26 (baseline, 33 measured X Articles, Oct 13-25; small sample, leans not laws):**
  - Three-item list titles averaged about 520 impressions vs about 190 for single-idea titles; classic full roundups had about 480 vs about 230 for all other formats. All 1,000+ posts were full roundups.
  - Posts in 11 AM-3 PM PT averaged about 525 vs about 260 at other hours.
  - Tip-first captions averaged about 400; the two "tip + Meanwhile <surprise>" captions averaged about 550 (best pattern so far). Blank or truncated captions averaged about 75.
  - Narrow deep dives (one security or eval angle) mostly landed 50-200.
  - Hype/filler words are rare already (a handful of "huge", "basically" across all editions); keep them out.
  - Proposed tweak: try "tip + Meanwhile" as the default caption shape for 2 weeks and compare.
