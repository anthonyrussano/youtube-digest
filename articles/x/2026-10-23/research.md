# Research: edition 2026-10-23 (overnight)

Window: 2026-10-22 19:07 UTC to 2026-10-23 07:18 UTC.

## Lead: Anthropic + Theorem, formal verification at scale
Primary: https://www.anthropic.com/research/formal-verification (Oct 22, 2026, Frontier Red Team with Theorem); appendix PDF linked from the post; Theorem's program repo https://github.com/theorem-labs/oss-verify (README, docs/what-gets-proven.md, .claude/skills/add-project/SKILL.md).

Facts from the post:
- Claude patched the bugs it found, then proved no crashes on any input up to 64 MB for 239 entry points across 123 OSS-Fuzz libraries.
- Proofs are about compiled RISC-V binaries; about 180 million lines of Rocq; a typical proof is about 600,000 lines; median binary 18,000 RISC-V instructions.
- Bugs: OOB write in a decompressor copy only on ~20 MB inputs with one rare layout; OOB read in an image decoder needing a 64 MB input and over 2 GB of memory; rediscovery of CVE-2026-56132 in libexpat (deeply nested input).
- seL4: two person-years to implement, 20 person-years to verify. Linux kernel recently had over 1,000 vulnerabilities disclosed.
- Trusted base: Rocq kernel, RISC-V and Linux semantics, and the theorem statements.
- Opus 5.5 proves half of 36 small verification tasks with about 40% fewer tokens than Opus 5. Shared workspace: 17% fewer tokens than working alone; solo cost higher in 30 of 34 completed proofs.
- Python interpreter in Rust (Verus): identical to CPython on 99.95% of 1.7 million random programs.
- PDF reader: as many security bugs in one week as are typically reported in a year.
- Mathlib grew to nearly 300,000 theorems from over 700 contributors (the reuse argument).
Appendix: cJSON's 391-line parser entry point got a 630,000-line proof, only about one tenth of it about cJSON; about one billion lines of Rocq written in total; seven injected interpreter bugs, five survived random tests, all seven broke the proof; median sanitizer spec about 110 lines; the LZO round-trip example is written with assert().

Facts from Theorem's oss-verify docs:
- "A statement covers what the fuzz target checks. Thus the fuzz target is the place to say what 'correct' means."
- Example property: `if (decompress(compress(x)) != x) abort();`
- WARNING: do not use assert(); builds that define NDEBUG (e.g. CMake Release) remove it and the property disappears with no warning.
- WARNING: do not return -1 for a failed property; -1 counts as a pass. Do not return 1 for an uninteresting input; that makes the statement false.
- Accepted exit statuses: 0 and 2. The driver refuses an input file of 64 MiB or more with status 2.
- Not checked: leaks (detect_leaks=0), UBSan vptr (trap mode). 
- Enrollment: point a coding agent at https://raw.githubusercontent.com/theorem-labs/oss-verify/refs/heads/main/AGENTS.md; it asks what "correct" means. Requirements include a public repo and a security contact. Findings go privately to the contact, no disclosure deadline, findings not published.

Coverage check: press and social coverage (e.g. madrobot.blog, Interesting Engineering) led with the counts (239 entry points, 180 million lines, the bugs). None explained that the proof is only as strong as the harness's checks, or the assert()/-1 traps. Related: @poteto's statechart skill that checks diagrams against formal-verification specs (https://x.com/poteto/status/2113398433977659654).

## Other items
- Firecrawl, "Stop Prompt Injection Before It Reaches Your AI Agent" https://www.youtube.com/watch?v=YzLR8X3_5gw : hidden JSON-LD note on a fake pricing page says to double the price (78 s); Sonnet-class model resisted, another model fell for it after two runs (84-109 s); CSS-hidden GitHub-issue trap: two models read the .env key, none sent it (113-157 s); Zscaler: library docs told models to pay 3 dollars to a Stripe account for a fake key, 4 of 26 models fell for it (167-183 s); checkPromptInjection scrape option runs a classifier and returns 403 (190-211 s). Promotional.
- Stephanie Jarmak (Omni Analytics), AI Engineer: https://www.youtube.com/watch?v=A3FL_zTQKU0 : slide "The ranking changes with the harness" (196 s): same 63 tasks, OpenHands Claude Opus 5 36/63 (57.1%) vs GPT-6 Astra 31/63 (49.2%); Pi harness 19/63 (30.2%) vs 38/63 (60.3%). 295 files returned vs 6 reference files (552 s). 1% false alarm rate -> 10,000 human reviews (680 s). Seeded security issues passed a hash check, caught by an independent record (739-769 s).
- Shreya Shankar with Tristan Handy (dbt Labs) https://www.youtube.com/watch?v=k5YL1NmhwFY : agents select * into pandas and join there (1463 s); benchmark took ~8 months (1577 s); best agent ~61% pass@1 (1654 s); AI SQL sends one HTTP request per row (2900 s); website note cut agent emails from ~5/day to ~3/week (136 s).
- Donato Capitella https://www.youtube.com/watch?v=MPj-puRyPTM : hosted API can route to a malicious model that adds vulnerabilities or appends malware to bash calls (202-235 s); trigger backdoors "even trivial" (472-483 s); run 5-6 models from official labs or known quantizers (824 s).
- Evan Conrad (San Francisco Compute) https://www.youtube.com/watch?v=Wk2bUUGFC_o : lab deposit 10M -> 100M -> 1B dollars (836-857 s); credit before power (501 s).
- MuTRAP (Binghamton) https://www.theregister.com/ai-and-ml/2026/10/22/backdoored-robot-tries-its-hand-at-finger-chopping-and-cat-cooking/5304870
- ThinkingBox-Training https://huggingface.co/blog/microsoft/thinkingbox-training : pass@1 51.70% -> 60.78%, 20/20 tasks 38 -> 107 after 50 GRPO steps.
- AWS Continuum GA https://aws.amazon.com/about-aws/whats-new/2026/10/aws-continuum-for-code-vulnerabilities-is-now-generally-available
- Quest Diagnostics breach https://x.com/AndrewCurran_/status/2113437710065311970 ; kill static credentials https://x.com/rauchg/status/2113399539227136084
- Opus 4.8 peer review study https://x.com/emollick/status/2113483068174692831
- Radical Numerics phages https://www.theregister.com/science/2026/10/22/human-receives-ai-designed-virus-for-the-first-time/5304874

## Candidates
| Candidate | Why lead | Coverage | Verdict |
|---|---|---|---|
| Anthropic/Theorem formal verification | Big, practical for any maintainer with fuzz targets | Counts covered widely; harness-as-spec angle missed | **Lead** |
| Firecrawl prompt injection | Actionable, has demo frames | Vendor demo | Also |
| Jarmak evals talk | Strong slides, actionable | Barely covered | Also |
| Shankar data agents | Good numbers | Podcast | Also |
| Conrad compute markets | Big-picture | Talk only | Also |

Angle: Anthropic's proofs are only as strong as the fuzz target's checks, so the fuzz target is now the spec, and two common habits (assert() and return -1) silently make the proof cover nothing.
