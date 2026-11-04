# Check: 2026-11-04 (classic full roundup)

## Rules
- [x] Format: classic full roundup; `format.txt` line 1 `roundup`, line 3 caption identical to `article.md` front matter.
- [x] Title: "NatWest's AI judge correlates 0.04, AMD eyes 17 billion dollars, and Devin runs 9 cloud Macs" (92 characters): three named brands, each with a number and its own verb, Oxford comma, no `$`.
- [x] Caption (226 characters): tip first ("Agent eval tip: check your LLM judge's correlation with human scores..."), then "Meanwhile" + the edition's surprise, ends with `...`, no `$<digit>`, no banned name.
- [x] Body: cold open with two linked hits, the fixed intro line, 13 story paragraphs across 10 stories, "A few quick ones." line, reply question with three choices, sign-off. About 1,110 words of prose (x-article dry run: 23 paragraphs, ~1,262 words incl. markers). No `##`, no bullets, no "Mind Blow", no `$` before a digit (grep clean).
- [x] Ban list and platform-framing greps clean (no "on X", "posted", counts).
- [x] No repeats: Hindsight Models (2026-11-03-1211) and the Qwen3.8-27B 367.9 tokens/s item (2026-10-30) were dropped after grep against `reports/`.
- [x] `./run.sh x-article 2026-11-04 --dry-run` prints `FORMAT: roundup` and `SOURCE: articles/x/2026-11-04/article.md`.
- [x] Lead angle real and sourced: NatWest's slides show error vs human ~0.2 next to correlation 0.04; explained in plain words (a judge that gives almost everything ~0.97 can't separate good from bad).

## Claims checked against sources
- 19 million customers (t=49), 100,000 conversations a day (t=61), a third of journeys (t=84), blast radius (t=110): transcript.
- Funnel stages, "fewer than half of all turns", MLP not an LLM, codes for auditability, rules survive an ML outage: slide frame t=300.
- 111 conversations, three scorers, 97/76/43, single 83% pass rate, 64% intent agreement: slide frame t=490 (transcript says "80%" once, a Whisper error; slide and description say 83%).
- Judge mean ~0.97, error vs human ~0.2, correlation 0.04, 0.89 pass mark, 0.08 vs 0.02 headroom, different model family: slide frame t=600 and transcript t=594-654. "about 14,000" cases: transcript t=581.
- 5% sample plus handoffs/fails/long/angry, every 4 hours, regression gate every merge request: slide t=705, transcript t=680/730. Shadow first, brand by brand, rollback in seconds: slide t=900, transcript t=908-939.
- OpenShell quotes: transcript t=151, 593-679, 716; policy advisor (propose rule, human review by default): NVIDIA docs; keys injected at the boundary (diagram only): Red Hat blog.
- AMD numbers (45%, 13.4, 8.5, 97%, about 17, 15 to 16, more than 80%), "possibly for the first time", foundry: The Register.
- Devin quote, nine Macs/nine iPhone Duo apps, AWS credentials, EC2/GPU: dabit3 post; flagged as a pitch (he works at Cognition).
- Claude Code: two sentences (Oct 30 post), 2.1.317 fix and behavior: Addy Osmani's posts; release exists (GitHub, published 2026-11-03).
- vercel doctor five checks, never prompts or logs in, `--json`: Vercel changelog; "ship doctor subcommands": Rauch.
- Alloy: 4-5 vs 15-20 sites, 50-125 tickets/week -> 5-10 to engineering, MCAP in one bucket, SwarmFarm 1-2 h -> ~10 min "with Alloy": Harris's article; flagged as vendor pitch.
- agent-desktop: accessibility tree, three OSes, ref per element, STALE_REF, no model inside, npm install: repo README.
- Screenplay: JSON scenario, `check` before filming, 1920x1080 at 30 fps default, no model key: repo/listing and author write-up.
- LSA: 98% selection time, 72.4x attention-layer prefill at 10M on one H200, 9.2x end-to-end TTFT, LongBench v2 70.0 -> 65.0: Prefrontal's page.

## Images (each looked at; every label and number checked)
1. `/workspace/2026-11-04-1-natwest-funnel.png`, video frame, https://www.youtube.com/watch?v=5UgnatzpZ9E&t=300s : slide as shown; the text beside it links the same timestamp. Native 1024 px wide (source video is 1024 wide at best on the box fallback).
2. `/workspace/2026-11-04-2-natwest-broken-judge.png`, video frame, https://www.youtube.com/watch?v=5UgnatzpZ9E&t=600s : slide values (0.97/0.04, 0.83/0.26, ~0.2, 0.04, 0.89, 0.08/0.02) match the transcript; adjacent paragraph links t=600.
3. `/workspace/2026-11-04-3-natwest-safety-spine.png`, original pele diagram: every label from slides t=300/705/900 (contextual filter, rules no ML, LLM step gated, MLP classifier, policy rules; 5% plus handoffs, fails, long, angry; judge from another model family; every 4 h; regression gate every merge request; shadow with Watson answering; smallest brand; percentage ramp; rollback global/backend/brand).
4. `/workspace/2026-11-04-4-openshell-trust-zones.png`, original pele diagram: trusted gateway/harness vs untrusted step (Red Hat video t=716-811), deny-by-default egress matched on host, port and binary, denial with reason, agent proposes a narrow rule, human review by default, rule loads without restart (NVIDIA OpenShell policy docs and policy advisor page), no keys inside, proxy injects them (Red Hat blog).
5. `/workspace/2026-11-04-5-amd-intel-guidance.png`, chart-generator bar chart. Data file values: AMD Q3 actual 13.4; AMD next Q (about) 17; Intel next Q (low) 15; Intel next Q (high) 16; billions of US dollars; source The Register, Nov 4 2026. Blind-spots report: none.
Five inline images is above the winning formula's 1-3; kept on purpose per Anthony's Nov 3 ask for more diagrams and frames. The 10:37 poster may drop #3 or #5 if the editor struggles.

## Changes made in this check
- "small neural network" -> "plain neural network (an MLP, not an LLM)" (slide says MLP; "small" was not sourced).
- AMD line softened to "possibly for the first time" (The Register says "potentially").
- Added the t=600 link next to the judge frame so the frame sits right after a paragraph citing its timestamp.
- Added "at 10 million tokens" to the LSA speedup (the 72.4x is a 10M-token figure).
- Replaced the Hindsight cost chart with the AMD chart after finding Hindsight was already published.
- format.txt caption synced to article.md ("not only", "iPhone Duo").


## 6:04 run update
- Added one Langfuse paragraph (top-five bank: 60% to about 95% numeric accuracy with a calculate tool, compliance zero shuts the gate; transcript t=181, 664, 919) after the Devin item. Numbers checked against the transcript.
- Removed nothing else; images, title and caption unchanged. `x-article --dry-run` re-run: FORMAT roundup, SOURCE article.md, ~1276 words.
