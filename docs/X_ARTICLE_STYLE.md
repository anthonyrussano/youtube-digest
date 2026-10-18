# X Article formats: roundup and deep-dive

The **website edition** (`articles/<EDITION>.md` -> `reports/<EDITION>.md`) is **always the roundup** in `STYLE.md`; nothing here changes it. The **X Article** on @russano comes in two named formats, and every edition picks one (selection rule below). Both are kept on purpose so we can compare them with data (`./run.sh x-stats`).

## Formats

| | **roundup** | **deep-dive** |
|---|---|---|
| What | The classic digest Article: the edition's rapid-fire cold open + one paragraph per item | One lead story in depth + "Also this cycle" |
| Used | Every X Article through edition `2026-10-17` (posted 11:00 AM PT Oct 17) | First used on edition `2026-10-17-1644` (Sat Oct 17, 2026 ~5 PM PT) |
| Source | `reports/<EDITION>.md` (the website page as is) | `articles/x/<EDITION>/article.md`, written with the four steps below; `research.md`, `outline.md`, `check.md` committed next to it |
| Structure | `STYLE.md` "Shape": cold open (1–2 linked hits), one-line intro, ~5–25 items of 2–4 sentences, sign-off; dek omitted on X | Hook on the overlooked angle, the lead in short lines (~400–800 words), takeaway, reply-inviting question, `## Also this cycle` with 4–6 linked one-liners |
| Title | The report's `title:` (teases 2–3 items) | Front matter `title:` naming the lead idea, never a list of three stories |
| Caption | `caption:` line in `articles/x/<EDITION>/format.txt`, typed at posting | Front matter `caption:` |
| Tool | `./run.sh x-article <ED> --format roundup` | `./run.sh x-article <ED> --format deep-dive` (the default when `article.md` exists) |
| Model | `2026-10-14-1211`, `2026-10-15-1212` (`docs/HANDOFF.md` section 7) | Oct 15 Claude Code single-idea post (`2026-10-15-1705`, https://x.com/russano/status/2110889513455321578); sample `articles/x/2026-10-17-sample/`; first live `articles/x/2026-10-17-1644/` |

### Selection rule (decide per edition, in ROUTINE_PROMPT step 8)
1. **Deep-dive fits** only if the edition has **one lead story** with a **genuinely overlooked angle** (most coverage missed or under-explained it), an **actionable takeaway** (a how-to, pattern or fix, ideally dev/DevOps/agent tooling) and **enough primary-source material for ~400–600 words** (a full thread, paper, repo, transcript or post, not a one-line summary). Otherwise use **roundup**. Thin editions with no strong lead always get roundup.
2. **When both fit, alternate** to build comparison data: if the last posted Article in `state/x_posts.json` (highest `posted_at_utc`) has `"format": "deep-dive"`, prefer roundup this time; if it was roundup, prefer deep-dive.
3. Record the choice in `articles/x/<EDITION>/format.txt` (committed, public text only): line 1 `roundup` or `deep-dive`, line 2 a one-line reason, and for roundup line 3 `caption: ...`. `./run.sh x-article <EDITION>` then defaults to that format (and guards the roundup caption), so the 10:37 routine posts what the 6:04 run picked. After posting, record `"format": "roundup" | "deep-dive"` on the post in `state/x_posts.json` (`x-article` prints the value) and in the routine report.

### Shared rules (both formats)
- **Caption, tip-first:** lead with the single most useful **actionable tip** for developers/DevOps (preferably agent/coding tools such as Claude Code, Cursor, Codex), not spec numbers or model sizes; end with `...`.
- **Never "Mind Blow"** in a title, body or caption (`x-article` drops body lines containing it and refuses such a title; for deep-dive it also refuses such a caption).
- **No `$` followed by a number** in a title or caption (write "3 dollars"). In the body, `x-article` inserts an invisible word joiner after `$` so X doesn't make a cashtag link.
- **Header:** a fresh high-resolution public-domain NASA image not used before (`header` in `state/x_posts.json`), per the `docs/HANDOFF.md` playbook.
- Same sourcing rules as `STYLE.md`: link the claim text, attribute vendor numbers, no platform framing or engagement counts, never link or name the newsletter.

# Deep-dive format in detail
## Structure
- **Front matter:** quoted `title:` that names the lead idea (not a list of three stories), quoted `caption:` (rules below), `edition:` and `lead_source:` (primary URL).
- **Lead story:** roughly **400–800 words**. Pick the most overlooked or most practical story of the edition, preferably an actionable dev/DevOps/agent-tooling idea (a how-to, pattern or fix a reader can apply). Big launches everyone already covered rarely make the lead.
- **`## Also this cycle`:** 4–6 one-line bullets (`- `), each with its link, drawn from the same edition.
- Short `##` section labels in the lead are fine (they render as bold lines). One line = one paragraph; use blank lines freely. Bold key phrases where it helps.
- Sourcing: the shared rules above. Outside facts found in research are fine if each is linked to its source.

## Caption
The shared caption rule, written as front matter `caption:`. `./run.sh x-article` refuses an `article.md` whose title or caption breaks the rules.

## The four-step process (artifacts committed under `articles/x/<EDITION>/`)
All of it is public-source material. Never put `data/`, `state/`, subscriptions or the newsletter text in these files (quote/link the original sources instead).

1. **`research.md`.** Gather the raw facts from the cited sources: transcripts, articles, X posts (read the full thread and author replies), AINews summaries (pointing to their original sources). Do a quick web/X search to see what most creators already covered and what they overlooked or under-explained. Prioritize overlooked technical details, implications and nuances. End with the chosen angle in one sentence. Keep a short candidates table (why lead / coverage / verdict).
2. **`outline.md`.** A simple, logical structure that explains **one core idea at a time** in plain language. Drop jargon or define it right away. Focus on why it matters and what people are missing. Include the "Also this cycle" picks.
3. **`article.md`.** Write from the outline:
   - Short, direct sentences.
   - Open with a strong hook built on the overlooked angle.
   - A technically curious non-expert can follow it without rereading.
   - End with a short takeaway, then a clear question or call to action that invites replies.
   - Line breaks for readability, **bold** key phrases where it helps. Cut anything overloaded or redundant.
   - ~400–800 words for the lead story.
4. **`check.md` (final check).** Review the research summary, tighten the outline, check clarity, and confirm the overlooked angle is **real, sourced and explained simply**. Check the rules (title names the idea, caption, no `$<number>`, no "Mind Blow", word count, 4–6 extras). Fix `article.md` if anything fails and record what changed, then run `./run.sh x-article <EDITION> --format deep-dive` and confirm it prints `FORMAT: deep-dive` and `SOURCE: articles/x/<EDITION>/article.md`.

Then post via the `docs/HANDOFF.md` "X Article playbook".
