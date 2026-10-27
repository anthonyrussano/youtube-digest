# Research: 2026-10-27 (overnight)

Window: 2026-10-27T00:43:55Z to 2026-10-27T07:20:43Z (Monday 5:43 PM to Tuesday 12:20 AM PT).

## Videos (both transcribed with faster-whisper base.en on the assistant's box; the home GPU host was unreachable)
- aGIUg8zKI8A, AI Engineer, "How a Trading Firm Ships New AI Models the Same Day - Noyan Tokgozoglu, Optiver". 10M+ trades a day, million+ instruments, petabytes daily (45-47s); 10+ locations (53s); P&L visible within hours (92s); on-prem except third-party inference under zero-data-retention agreements (293-308s); AI platform slide (315-328s, frame at 318s: agent gateway, inference gateway with routing, resilience, economics, keys and budgets); same-day frontier model adoption benchmarked on golden sets with trading teams (429-445s); every interaction logged into evals (546s); fresh sessions at 200K tokens of context (649s); fixes: MCP tool search (668s), CLI wrapping MCPs (670s), cache invalidation tuning (680s), knowledge base instead of system prompt (695s); model routing (791s); OTel logging of tool calls (1178s); scope agents narrowly and connect via the agent gateway (1346s).
- v9Y3Lw_I9o4, Oracle, "Oracle AI Database Spotlight: AI Can Build It, But Can You Trust It? at Oracle AI World 2026" (Juan Loaiza). Autonomous Database patches (309s); security and patching tools free or discounted (458s); Deep Data Security, end-user privacy enforced in the database (630-644s); HR agent demo (702-820s): direct salary request refused (754s), balloon prompt injection leaks salary-derived numbers (764-779s, frame at 777s), with deep data security the database verifies a signed token and returns nothing the user can't see (783-820s, frame at 808s); SQL assertions, under-21 alcohol rule (856-880s); Deep NL2SQL demo (1315-1360s): "sold best" flagged ambiguous, harvest wreath about 31,000 in gross revenue, drops to 7th when returns excluded; APEX Lang vs React via Codex (1700-1900s); no additional charge (2299s).

## Feeds (The Register)
- GMO Onamae.com Desktop Cloud breach (Simon Sharwood, 27 Oct 01:06 UTC): FX-trading Windows VDI compromised, malicious programs, unauthorized trades, passwords likely seen; brokers asked to kill sessions/block trades from the service; up to 26,739 VDI servers; 50 million dollar demand refused; 5,000 yen condolence payment, losses covered, six months free alternative; CEO Masatoshi Kumagai: white-hat team flagged issues, "response lacked sufficient depth and speed"; blamed misuse of ARTEX (autonomous AI pentest tool) for attacks on about 20 Japanese companies.
- IBM z/OS AI mapping tool (27 Oct 04:07 UTC): Statement of Direction, "AI-native", maps the whole z/OS stack, aims to "eliminate the leading cause of unplanned z/OS outages" (changes not proven safe), change impact, testing, validation, humans keep decision authority.
- Elvis rights holders v Anthropic (27 Oct 05:39 UTC): 274 songs, N.D. Cal., filed last Friday; 150,000 per work, 41.1 million total; earlier books settlement fund 1.5 billion; float announced today.
- Skipped: Java history piece (no news hook).

## X (from the edition's selected posts)
- Jelani Nelson (minilek) on the Claude ETH result; primary source hexagonmath.org/2610.00577 (Anthropic, submitted by Nelson): deterministic 2^{o(n)} algorithm for 3-SAT, solves #3-SAT, Lean 4; found Oct 16 by an internal Claude research model, 14M output tokens, no human input; OpenAI internal model independent similar result (preprint "The Exponential Time Hypothesis is False"); method: sparsify, clause graph on grid, divide and conquer, eight square identity (octonions) cuts diagonal edge weight 6 to 4.5 on average; ~exp(O(n/sqrt(log n))); R. Williams organizing workshops with Impagliazzo and Paturi.
- Andrew Curran on Physical Superintelligence (58 million seed, launched September): OQP 2, 12, 27, 38, 43 with papers and Lean; psi.inc page (Oct 23) adds verification code; OpenAI preprint shows two PPT maps don't suffice for 38.
- Andrew Curran on GMO: 50m ransom refused; ransomware threat to logged-in PCs; users told to unplug.
- nodiligence essay on Anthropic IPO (debt to stock; wouldn't buy day one; suppliers/insiders selling into index buying); S-1 on SEC EDGAR.
- Oluwaphilemon1 on TeksEdge's Qwen3.8-27B: 82 -> 114 (MTP) -> 138 (DFlash2 + lookup) -> 381 tok/s (verification optimized), RTX 3090 24GB, blocks up to 16 tokens with ~15 accepted; "reportedly".
- Teknium: Hermes Agent main channel; quoted merged PR for Hermes webapp (chat, files, git, refresh-surviving terminal, remote sign-in).
- clypmint b-roll plugin: Claude Code/Codex/any agent, Internet Archive, Wikimedia, NASA, Library of Congress, YouTube moment search, 1 cent per search when it finds a shot, open source.
- shubh19 LLM system design checklist: bank support chatbot, 45 min; TTFT vs throughput, KV cache, vLLM, prefix/semantic/embedding caches, Anthropic cache reads 0.1x input price, small-model routing, provider fallback, OWASP Top 10 for LLM apps.
- Skipped: free-course clickbait.

## AINews
- No issue in the window.
