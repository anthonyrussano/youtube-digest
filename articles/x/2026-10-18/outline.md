# Outline

1. Hook: everyone saw the price (0.75 dollars per 1,000). The unit is the story: you pay per call, not per result.
2. What shipped, plainly: Search (find pages) and Fetch (read one page as Markdown), same DeepSeek key. Define RAG/agent use in one line.
3. Idea 1, the unit: billed only on a successful, non-empty call; count 1-50 same price; empty results/timeouts free. Consequence: search wide once.
4. Idea 2, skip the fetch: need_content returns page content in the search call; summary field is written for a model.
5. Idea 3, filter before you read: rerank_score (1.5+ good) and authority (3+ authoritative) let the agent drop junk before it costs context or calls.
6. Idea 4, the real wall: 5 calls/second per account across all keys, plus per-domain Fetch caps; parallel subagents share it; 429 handling (wait and retry on 408/429/5xx, not other 4xx).
7. Why now: Claude Code/Codex with DeepSeek models already call these server-side; free until Nov 1 Beijing time (Oct 31 16:00 UTC).
8. Takeaway: one wide search with content, filter by score, fetch only what's left, throttle to 5/s. Question: how many search calls does your agent make per task?
9. Also this cycle: Sphinx, JOSIE-Voice, evals-first fine-tune recipe, Blender skills repo, Fable 5.1 Borges.
