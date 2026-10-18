# Research: 2026-10-18 deep-dive

## Primary source
DeepSeek API docs, "Search & Fetch": https://api-docs.deepseek.com/guides/search/ (also the pricing page https://api-docs.deepseek.com/quick_start/pricing/)

Raw facts (from the docs):
- Two raw JSON endpoints, same bearer key as the DeepSeek model API: `POST /v1/tools/search` and `POST /v1/tools/fetch` on api.deepseek.com.
- Search runs on DeepSeek's in-house search engine. Fields: `query` (1-128 chars, supports operators), `count` (1-50, default 10), `ori_question` (the user's original question, to improve query understanding), `localization` (IP), `need_content` (return page content, default false).
- Query operators pass through: `site:`, `-site:`, `-term`, `"exact"`, `-"phrase"`, `lang:zh,en`, `after:`, `before:`.
- Each result: `rerank_score` 0-3 (1.5+ = high quality), `title`, `url`, `snippet` (100-200 chars, for UI), `summary` (600-800 chars, "intended to be read by a model"), `content` (if need_content), `site_name`, `date`, `authority` 0-4 (3+ = highly authoritative, -1 unknown).
- Fetch: one URL (max 8192 chars, http/https, no credentials) -> `title` + Markdown `content`. 403 = rejected by security policy, 404 = no usable content.
- Billing: 0.75 dollars per 1,000 successful requests for each API. Billed only on HTTP 200 with a result (non-empty `results` / page content). Failed requests, empty results and timeouts are not billed. `count` does not affect price.
- Via DeepSeek Harness, Claude Code or Codex, server-side tool calls already hit these APIs; free now, billed from 00:00 Beijing time Nov 1, 2026 (16:00 UTC Oct 31).
- Rate limits: 5 QPS for Search and 5 QPS for Fetch, per account regardless of API key, separate from model concurrency. Fetch also has a per-domain QPS limit. Over-limit = 429. Retry 408/429/5xx after waiting; top up on 402; don't blindly retry other 4xx.

## What coverage said
- DeepSeek's own announcement (third post of a thread that led with DeepSeek-V4.1-Flash-1017) gave the price and the Oct 31 billing date (via https://www.spke.com/en/ai/article/3618).
- PPC Land's long piece (https://ppc.land/deepseek-prices-web-search-for-ai-agents-at-0-75-per-1-000-calls/) led with price, the comparison to Microsoft and the free-until-Oct-31 window.
- Hacker News thread (https://news.ycombinator.com/item?id=50138531) focused on price and latency.

## Overlooked / under-explained
- The price unit: per successful request, not per result or token. So `count: 50` costs the same as `count: 1`, and `need_content: true` can replace a follow-up Fetch call. Agents that search narrow and then fetch each result pay several times more than agents that search wide once.
- The `summary` field is written for models (600-800 chars) and `rerank_score`/`authority` give a free filter, so an agent can drop low-score results before spending context or Fetch calls.
- The 5 QPS cap is per account, across all keys. A team running parallel subagents on one account shares those 5 slots; the 429s, not the bill, are the first wall. Fetch has an extra per-domain cap.
- The free window is covered; the habit change it requires (budget and rate-limit search calls in agent configs before Nov 1) is not.

## Candidates
| Story | Why lead | Coverage | Verdict |
|---|---|---|---|
| DeepSeek Search & Fetch | Primary docs, concrete billing rules, hits Claude Code/Codex users, open-models trend | Price and date widely covered; billing mechanics and shared rate limit not | **Lead** |
| Sphinx Git hook | Very actionable agent-tooling idea | Only a landing page; thin for 400+ words | Also this cycle |
| JOSIE-Voice local voice agent | Interesting | Single post, details behind link | Also this cycle |
| Fine-tune recipe (evals first) | Actionable | Four lines | Also this cycle |

Angle: DeepSeek bills agent web search per successful call, not per result, and caps it at 5 calls a second per account, so the cheap, fast pattern is one wide search with content and a score filter, not many narrow searches and fetches.
