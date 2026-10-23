---
title: "Anthropic's AI proofs only cover what your fuzz target checks. Two habits make them cover nothing"
caption: "Fuzz harness tip for the AI-proof era: write each property as if (!ok) abort(), not assert(). Release builds strip assert(), and a proof of your harness then quietly covers nothing..."
edition: "2026-10-23"
lead_source: "https://www.anthropic.com/research/formal-verification"
---
Anthropic says Claude has now **proven that 239 entry points across 123 open-source libraries can't crash** on any input up to 64 MB. Most coverage quoted the counts. The more useful part is what decides what gets proven: **your fuzz target.**

Here's what happened. Working with the startup Theorem, Claude [found and patched real bugs, then wrote machine-checked proofs](https://www.anthropic.com/research/formal-verification) about the compiled RISC-V binaries. That's about 180 million lines of proof in Rocq so far, with a typical proof around 600,000 lines. One bug was an out-of-bounds write in a decompressor that only fires on a roughly 20 MB input with one rare layout. Random testing almost never reaches a case that rare. A proof has to.

## The part most coverage skipped

A proof doesn't cover "correctness" in general. Theorem's guide for maintainers puts it plainly: [a statement covers what the fuzz target checks, so **the fuzz target is the place to say what "correct" means**](https://github.com/theorem-labs/oss-verify/blob/main/docs/what-gets-proven.md).

By default you get "no crash, no hang, no sanitizer error." Add one line such as `if (decompress(compress(x)) != x) abort();` and the same proof now says the round trip works for **every** input under 64 MiB, not just the ones a fuzzer happened to try.

Two everyday habits quietly break that:

- **assert() instead of abort().** Builds that define NDEBUG, such as a CMake Release build, delete assert(). The property disappears from the binary, and you get no warning.
- **Returning -1 for a failed check.** To libFuzzer, -1 means "don't add this to the corpus." To the proof, it counts as a pass. (And returning 1 for a boring input makes the statement false.)

[[IMG: /workspace/2026-10-23-1-fuzz-target-spec.png | Diagram: your fuzz target defines correct (if decompress(compress(x)) != x, abort), which is pinned to one RISC-V binary by SHA-256 and proven by Claude in Rocq, so the property holds for every input under 64 MiB. A dashed branch shows that assert() removed by NDEBUG, or returning -1, leaves the proof saying nothing about that property. Based on Theorem's oss-verify docs]]

Even Anthropic's own appendix writes its round-trip example with assert(). That's fine in a debug build, but it's exactly the trap Theorem's guide warns about.

## Why bother

Proofs catch what tests miss. Anthropic planted seven bugs in a verified Python interpreter. Five survived random testing, and [all seven broke the proof](https://www.anthropic.com/research/formal-verification). Proofs are also getting cheaper: Opus 5.5 proves half of a 36-task set with about 40% fewer tokens than Opus 5.

If you maintain a C library that's already in OSS-Fuzz, enrolling takes one step. Point a coding agent at [Theorem's AGENTS.md](https://github.com/theorem-labs/oss-verify) and it asks what "correct" means for your code. You need a public repo and a security contact. Findings go to you privately, with no disclosure deadline.

**This week, grep your harnesses for assert( and return -1.** Make every property you care about end in abort().

## Also this cycle

- **Prompt injection, live:** Firecrawl hid a note in a pricing page's structured data telling AI agents to [double the price and not say so](https://www.youtube.com/watch?v=YzLR8X3_5gw&t=78s). One model fell for it after two runs.

[[IMG: /workspace/2026-10-23-2-firecrawl-hidden-instructions.png | Frame from Firecrawl's YouTube video "Stop Prompt Injection Before It Reaches Your AI Agent" at 1:18: page source of a fake CloudVault Pro pricing page with a JSON-LD note telling automated assistants to report double the price and not mention the change]]

- **Your harness picks the winner:** in Stephanie Jarmak's AI Engineer talk, the same 63 tasks [flipped the model ranking when only the agent harness changed](https://www.youtube.com/watch?v=A3FL_zTQKU0&t=196s).

[[IMG: /workspace/2026-10-23-3-harness-swap.png | Slide from Stephanie Jarmak's AI Engineer talk "Don't Trust Your AI Agents. Test Them Like a Scientist" (YouTube) at 3:16: on the same 63 tasks, Claude Opus 5 beats GPT-6 Astra 36 to 31 in the OpenHands harness but loses 19 to 38 in Pi]]

- Shreya Shankar found data agents [pull whole tables into pandas](https://www.youtube.com/watch?v=k5YL1NmhwFY&t=1463s) instead of letting the database do the work.
- Donato Capitella: a hosted API can [quietly route you to a malicious model](https://www.youtube.com/watch?v=MPj-puRyPTM&t=202s). Use models from official labs or known quantizers.
- Binghamton's MuTRAP [ties different harmful robot plans to different trigger words](https://www.theregister.com/ai-and-ml/2026/10/22/backdoored-robot-tries-its-hand-at-finger-chopping-and-cat-cooking/5304870) during fine-tuning.
- Evan Conrad: the deposit to start an AI lab [went from 10 million dollars to a billion](https://www.youtube.com/watch?v=Wk2bUUGFC_o&t=836s). Credit runs out before power does.
- ThinkingBox-Training lifted a 27B model's [tasks solved on all 20 attempts from 38 to 107](https://huggingface.co/blog/microsoft/thinkingbox-training).
- AWS made [Continuum for code vulnerabilities generally available](https://aws.amazon.com/about-aws/whats-new/2026/10/aws-continuum-for-code-vulnerabilities-is-now-generally-available), with sandbox-validated exploits and fix PRs.
- After [the Quest Diagnostics breach](https://x.com/AndrewCurran_/status/2113437710065311970), Guillermo Rauch called to [kill static credentials and move to OIDC](https://x.com/rauchg/status/2113399539227136084).

If a proof only covered what your fuzz target checks, which property would you add first? Tell me what your harness asserts today.
