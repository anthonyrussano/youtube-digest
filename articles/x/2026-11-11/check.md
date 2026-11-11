# Check: 2026-11-11 (overnight prep, classic full roundup)

- [x] Body = full edition: cold open with hard numbers (over 1,000 hours, more than 213 merged fixes), "Meanwhile" contrast (about 100 malicious skills), intro line, lead in three paragraphs, 12 more story paragraphs, a "A few quick ones." paragraph with 5 small items, four-part close. About 1,360 words of prose (x-article counts ~1,520 incl. markers). No ## sections, no bullets, no tables.
- [x] Title: "OpenAI's CI agent merged 213+ fixes, Codex Security cut 36% duplicates, and AMD packs 256 cores" (94 characters, three named items with numbers, "A, B, and C"). No `$`+digit, no "Mind Blow".
- [x] Caption shape: **contrarian** ("Hot take: more scanners won't fix your security backlog", then the 36% duplicates and verify-fix evidence, then a Meanwhile fact). Previous posted Article (2026-11-10-1206) used `question`; 2026-11-10 used `number`; the held 2026-11-10-1707 caption is `tip`. Ends in `...`, no `$`+digit, no "Mind Blow". format.txt line 3 matches the front matter.
- [x] Lead first (Codex Security, lead_source = the DevDay talk). Overlooked angle is real and sourced: coverage leads with 0.81% / under 1% and Daybreak access. The 36% duplicate rate (615s), security.md ownership files (433s) and the patch benchmark (984s) are mostly missing elsewhere.
- [x] 0.81% left out on purpose: Ian calls it a false-positive rate (162s), Kyle ties it to rollbacks (846s). Only "rollback rate under 1%" is used, which both say.
- [x] DevDay was in late September. The talk videos are new this window, so the text says "OpenAI posted its DevDay talks" and avoids "launched today".
- [x] Every number checked against its transcript block or page (see research.md for timestamps). Vendor and speaker claims are attributed ("OpenAI says", "by Tether's numbers", "AMD also frames").
- [x] All 27 transcribed videos are cited in both draft-report.md and article.md. Z9k5oI3Paoc has no speech and is not cited (render skips it).
- [x] Four-part close with fresh wording. Take: copy OpenAI's dull steps (dedup, owners) first. Reply question: flaky tests, security findings or on-call queue. Share: "Send this to the engineer who triages your scanner alerts." Follow: "Every few days I sort the AI and DevOps news down to what a team can use..." Neither the share nor the follow line matches 2026-11-10-1707 or 2026-11-10-1206.
- [x] STYLE.md checklist greps on draft-report.md and article.md: no headers, bullets or tables; platform-words grep hits only "posted its DevDay talks" and "like" as a comparison; no semicolons, no em-dashes, no "Mind Blow", no `$`+digit.

## Plain English pass (`./run.sh plain-lint 2026-11-11`)
- Before: draft-report.md 7 REVIEW hits (all sentence_over_limit, longest 29 words); article.md 6 (all sentence_over_limit, longest 29).
- After: 0 REVIEW hits in both files. Longest sentence 25 words. Mean 13.9 (draft) and 13.8 (article).
- Wording only: split long sentences at "and" / "so". Facts, links and image markers unchanged.

## Images (all looked at; numbers checked)
1. diagram `/workspace/2026-11-11-1-codex-security-loop.png` (pele, dark): Codex Security loop. Find: security.md threat models + knowledge base -> deep scan by hundreds of agents -> dedup (36% duplicates). Fix: validate -> patch -> verify-fix (adversarial check) -> PR + normal review (rollback under 1%). Labels from 162s, 388-433s, 524s, 615s, 846s. A first render said "attacks the patch"; changed to "an adversarial check on the patch" to match the talk.
2. video-frame `/workspace/2026-11-11-2-ci-agent-stats.png`, https://www.youtube.com/watch?v=U1IVZy9FhVQ&t=525s : "100+ PRs created per week, 1000+ commits pushed, 600+ Slack messages to human team members to coordinate merging fixes". Matches the transcript (479-525s).
3. video-frame `/workspace/2026-11-11-3-patchbench.png`, https://www.youtube.com/watch?v=gUQN7juxvVI&t=984s : "Patch benchmark", score vs cost per case. GPT-6 Astra medium about 62.7% at about 2.4 dollars, GPT-5.6 Sol xhigh about 61.4% at about 4.9 dollars, so "less than half the cost" holds.
4. video-frame `/workspace/2026-11-11-4-zenity-skills.png`, https://www.youtube.com/watch?v=_7P580m4kPY&t=483s : "Thousands of skills exercised, ~100 skills removed after review". Matches the transcript (433-483s).
Four images, one over the winning formula's 1-3, in line with the Nov 3 ask for more diagrams and frames. The poster may drop the PatchBench slide if the editor struggles.

## Header
NASA iss073e0983131 (Sept. 21, 2025): a partly cloudy Korean Peninsula with sun glint on the Sea of Japan and the Yellow Sea, seen from the ISS. Original 8256x5504, public domain, saved to /workspace/x-header-2026-11-11.jpg. Id not in any header field of the post log, any earlier overnight.json, or the known-used list.

## Dry run
`./run.sh x-article 2026-11-11 --dry-run` -> FORMAT: roundup, SOURCE: articles/x/2026-11-11/article.md, 27 paragraphs, ~1512 words.
