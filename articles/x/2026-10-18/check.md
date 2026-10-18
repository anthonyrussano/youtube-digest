# Check

- Research reviewed: every fact in the lead comes from DeepSeek's Search & Fetch guide (billing, count 1-50, need_content, summary 600-800 chars, rerank_score 1.5+, authority 3+, 5 QPS per account across keys, per-domain Fetch cap, retry guidance, Nov 1 Beijing billing for Claude Code/Codex/Harness server-side calls).
- Overlooked angle is real: the price and the free window were widely covered (DeepSeek's announcement, PPC Land, HN). The billing unit (per successful call, count-independent, empty results free), skipping Fetch via need_content, score filtering and the shared account-wide rate limit were not explained as an agent design pattern.
- Clarity: Search, Fetch, RAG, rerank_score, authority and 429 are each defined in one line. One idea per section.
- Tightened: removed a speculative claim about competitor prices (not in primary source); kept "At these prices..." as an inference from the docs' own numbers.
- Caption first draft said "Claude Code and Codex tip" but readers of those tools don't set `count`; rewrote it as an API tip with the Claude Code/Codex billing date as the supporting fact.
- Rules: title names the lead idea (72 chars, no "$<digit>", no forbidden phrase); caption tip-first, ends in "...", no "$<digit>"; lead ~500 words; 5 "Also this cycle" picks, all from edition 2026-10-18.
- `./run.sh x-article 2026-10-18` -> FORMAT: deep-dive, SOURCE: articles/x/2026-10-18/article.md (see run log).
