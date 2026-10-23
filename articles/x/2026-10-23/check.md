# Number check: 2026-10-23 article

| Claim in article | Source | Status |
|---|---|---|
| 239 entry points, 123 libraries, no crash up to 64 MB | Anthropic post | ok |
| ~180 million lines of Rocq; typical proof ~600,000 lines | Anthropic post | ok |
| OOB write on ~20 MB input with one rare layout | Anthropic post | ok |
| RISC-V binaries; machine-checked | Anthropic post; oss-verify what-gets-proven.md | ok |
| "fuzz target is the place to say what correct means" | what-gets-proven.md:95 | ok (quoted) |
| `if (decompress(compress(x)) != x) abort();` | what-gets-proven.md:98 | ok |
| every input under 64 MiB | what-gets-proven.md:44 (inputs of 64 MiB or more refused with status 2) | ok |
| no crash, no hang, no sanitizer error by default | oss-verify README line 4 | ok |
| assert() removed under NDEBUG, CMake Release, no warning | SKILL.md:64 | ok |
| -1 = don't add to corpus (libFuzzer); counts as pass | SKILL.md:113; what-gets-proven.md:32 | ok |
| returning 1 makes statement false | what-gets-proven.md:30 | ok |
| Anthropic appendix round-trip example uses assert() | appendix lines 213-225 | ok |
| 7 injected bugs, 5 survived random tests, all 7 broke the proof | appendix 92-93 | ok |
| Opus 5.5: half of 36 tasks with ~40% fewer tokens than Opus 5 | Anthropic post | ok |
| enroll via AGENTS.md; public repo + security contact; private findings, no disclosure deadline | oss-verify README 15, 25, 47 | ok |
| Firecrawl hidden note: double the price, don't say so (1:18) | YzLR8X3_5gw t=78, frame viewed | ok |
| one model fell for it after two runs | YzLR8X3_5gw t=84-109 | ok |
| 63 tasks; Opus 5 36 vs Astra 31 (OpenHands), 19 vs 38 (Pi) | A3FL_zTQKU0 t=196 slide, frame viewed | ok |
| agents pull whole tables into pandas | k5YL1NmhwFY t=1463 | ok |
| hosted API routes to malicious model; official labs / known quantizers | MPj-puRyPTM t=202, 824 | ok |
| MuTRAP trigger words to harmful plans via fine-tuning | The Register | ok |
| deposit 10 million to a billion dollars; credit before power | Wk2bUUGFC_o t=836, 501 | ok |
| ThinkingBox 38 -> 107 tasks solved on all 20 attempts | Hugging Face blog | ok |
| AWS Continuum GA, sandbox-validated exploits, fix PRs | AWS what's new | ok |
| Quest Diagnostics breach; Rauch: kill static credentials, OIDC | X posts (AndrewCurran_, rauchg) | ok |

Style: no dollar-sign numbers, no "Mind Blow", no engagement words (grep clean except a video title containing "Like"). Caption tip-first, ends in "...". Dry run prints SOURCE: articles/x/2026-10-23/article.md.
