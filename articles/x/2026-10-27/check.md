# Check: 2026-10-27 X Article

## Rules (docs/X_ARTICLE_STYLE.md, STYLE checklist, WRITING_GUIDE section 6)
- [x] format.txt line 1 "roundup", line 2 reason, line 3 caption (matches article.md front matter)
- [x] Classic full roundup: whole edition, 15 linked story paragraphs, ~1,634 words (dry run, 21 paragraphs), no headings, bullets or tables (grep '^(#|[-*] |\|)' empty)
- [x] Led by the broadest story (Claude refutes ETH; primary source hexagonmath.org)
- [x] Title names three items with numbers and verbs, "A, B, and C" form, 95 chars
- [x] Caption "MCP tip: ..." + "Meanwhile" surprise, 190 chars, ends with "..."
- [x] No "$<digit>" anywhere in the edition folder; no "Mind Blow"
- [x] No platform framing or engagement counts (grep for on X / tweet / bookmark / likes / saves / posted / trend / viral / followers: no hits)
- [x] WRITING_GUIDE ban-list grep clean (dry run reports no banned words; "massive" rephrased twice)
- [x] Cold open, intro line, items, reply question, sign-off
- [x] 3 images, all still frames from cited videos, each on its own line right after the paragraph citing that timestamp; alt names channel and video
- [x] `./run.sh x-article 2026-10-27 --dry-run` prints SOURCE: articles/x/2026-10-27/article.md

## Images (each viewed; labels read from full-resolution crops)
- /workspace/2026-10-27-1-optiver-platform.png: aGIUg8zKI8A at 318s (5:18), slide "The Optiver AI Platform". Verified labels: "Agent gateway: one conversation layer for everything", "Inference gateway: every model call, one door", Routing ("Workloads ask for a capability and a budget, not a model"), Resilience ("automatic failover"), Economics, Keys & budgets. Speaker visible in corner inset only; slide fills the frame.
- /workspace/2026-10-27-2-oracle-injection-leak.png: v9Y3Lw_I9o4 at 777s (12:57), HR agent demo. Verified: guardrail refusal "Security guardrails will not allow me to show you that.", balloon prompt, "I can calculate that from the employee dataset.", table "Marketing Balloon Calculation" (first row Valerie Jones 154,000). No figures from the table are used in the text.
- /workspace/2026-10-27-3-oracle-deep-data-security.png: v9Y3Lw_I9o4 at 808s (13:28). Verified: same prompt, all four rows 0, access panel "Compensation for other employees is blocked."
- Capture method: yt-frame's remote host was unreachable and its local fallback was bot-checked, so frames were taken by seeking and pausing the public YouTube embed in a headless browser on the box (1920x1080, captions and player chrome hidden). No cookies used.

## Numbers and sources
- ETH: 2^{o(n)}, #3-SAT, Lean 4, Oct 16, 14M output tokens, no human input: hexagonmath.org/2610.00577; method (sparsify, grid divide and conquer, eight square identity, 6 to 4.5, exp(O(n/sqrt(log n)))), OpenAI concurrent preprint, workshops: minilek post
- PSI: 58 million seed, September launch, OQP 2/12/27/38/43, 2(d-1) PPT maps, OpenAI two-map result: AndrewCurran_ post + psi.inc page
- Optiver: 10M+ trades, million+ instruments (45-47s); hours (92s); ZDR (293s); gateways (318s frame); same day + golden sets (429s); 200K tokens (649s); fixes 668/670/680/695s; scope agents (1346s)
- GMO: 26,739 servers, 50 million dollar demand, 5,000 yen, six months, ~20 companies, ARTEX, Kumagai quote: The Register 27 Oct; unplug + ransomware threat: AndrewCurran_ post
- Oracle: refusal 754s; balloon leak 774-779s; deep data security 783-820s; SQL assertion under 21 (868-880s); no additional charge (2299s); NL2SQL 1315-1360s (about 31,000 gross revenue; 7th after returns per transcript)
- IBM: Statement of Direction, "eliminate the leading cause of unplanned z/OS outages": The Register 27 Oct
- Elvis: 274 songs, N.D. Cal., 150,000 per work, 41.1 million, 1.5 billion books fund, float today: The Register 27 Oct
- Qwen3.8-27B: 82/114/138/381 tok/s, 4.6x, RTX 3090 24GB, 16-token blocks, ~15 accepted: Oluwaphilemon1 post ("reportedly" kept)
- Hermes: Teknium post (quotes merged PR); Clypmint: clypmint post (1 cent per search); checklist: shubh19 post (45 min, 0.1x)
- X posts cited by link only; no counts used
