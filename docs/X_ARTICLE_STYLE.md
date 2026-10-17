# X Article style and process (single lead story)

The **website edition** (`articles/<EDITION>.md` -> `reports/<EDITION>.md`) stays the rapid-fire roundup in `STYLE.md`. The **X Article** on @russano is a separate piece derived from each edition: **one lead story in depth**, then a short "Also this cycle" list. The first X Article on this format was edition `2026-10-17-1644` (posted Sat Oct 17, 2026 ~5 PM PT; see `docs/HANDOFF.md` section 4a).

Model: the Oct 15 Claude Code single-idea Article (edition `2026-10-15-1705`, https://x.com/russano/status/2110889513455321578). One concrete, actionable agent-tooling idea (each agent gets its own repo copy) carried the post: 653 impressions, 5 likes and 3 replies in ~25 h, our best so far. Worked sample of this process: `articles/x/2026-10-17-sample/`.

## Format
- **Front matter:** quoted `title:` that names the lead idea (not a list of three stories), quoted `caption:` (rules below), `edition:` and `lead_source:` (primary URL).
- **Lead story:** roughly **400–800 words**. Pick the most overlooked or most practical story of the edition, preferably an actionable dev/DevOps/agent-tooling idea (a how-to, pattern or fix a reader can apply). Big launches everyone already covered rarely make the lead.
- **`## Also this cycle`:** 4–6 one-line bullets (`- `), each with its link, drawn from the same edition.
- Short `##` section labels in the lead are fine (they render as bold lines). One line = one paragraph; use blank lines freely. Bold key phrases where it helps.
- Same sourcing rules as `STYLE.md`: link the claim text, attribute vendor numbers, no platform framing or engagement counts, never link or name the newsletter. Outside facts found in research are fine if each is linked to its source.

## Caption (typed into the post)
Lead with **one actionable tip**, end with `...`, no `$` followed by a number (write "3 dollars"), never "Mind Blow". Don't lead with spec numbers or model sizes. `./run.sh x-article` refuses an `article.md` whose title or caption breaks these rules.

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
4. **`check.md` (final check).** Review the research summary, tighten the outline, check clarity, and confirm the overlooked angle is **real, sourced and explained simply**. Check the rules (title names the idea, caption, no `$<number>`, no "Mind Blow", word count, 4–6 extras). Fix `article.md` if anything fails and record what changed, then run `./run.sh x-article <EDITION>` and confirm it prints `SOURCE: articles/x/<EDITION>/article.md`.

Then post via the `docs/HANDOFF.md` "X Article playbook".
