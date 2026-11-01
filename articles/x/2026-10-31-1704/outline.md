# Outline (roundup)

Lead: the slow part of agent coding is now the wait, not the writing.
1. Agents push dozens of PRs a day; each one waits on CI. Vox cut that wait from up to 40 minutes to 2.
2. First move is measurement, not tuning: split 150 runs into queue, setup, run. Found half the test jobs missing the cache for a year.
3. The nine checks in plain words; the prompt's best line is "report first, don't change anything." Separate money-costing fixes for a human.
4. Chart: before/after waits (CI and database copy).
5. Same wait from the data side: Snorkel's 20-minute database restores become under-a-minute copy-on-write branches with expiry times. Define copy-on-write in one clause. Agents get disposable production copies too.

Other items:
- Google's Elephant-Goldfish: memory-free reviewers grade the plan (attribute claims).
- AnyScene: one image to an editable Blender scene.
- SDPO: learning from its own failed attempt, about 6x faster than GRPO; caveats.
- Quinten Farmer: US open-model margins 45-60% vs Zhipu 24.6%; back-of-envelope caveat.

Close: question offering three choices (CI audit, branch-per-PR database, goldfish reviewer), then sign-off.
