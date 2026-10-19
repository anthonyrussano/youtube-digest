# Outline (deep-dive)
1. Hook: Grafana cut its agent's starting tool list from about 54,500 tokens to 504. Most of their wins came from fixing the interface around the model, not the model.
2. Context: Grafana Assistant, dashboarding is 27% of chats; 10-week results (errors 2.47% -> 0.65%, p95 63 s -> 28.8 s, cost -18%).
3. Idea 1, progressive tool discovery: small entry points first, full manual on demand (define "tool schema"). Caveat: measure the whole task.
4. Idea 2, a CLI that talks back: errors that say how to recover, commands that describe themselves, filter before output reaches context.
5. Idea 3, grade the work, not the answer: graders read queries, tool calls, saved state; production failures become test scenarios (78 -> ~200).
6. Idea 4, small context fixes: fetch the alert definition instead of guessing from its name; fix wrong tool instructions (52% -> 69%).
7. Takeaway: audit your own MCP server or CLI: how many tokens do tool definitions cost before the first question, and do errors tell the agent what to do next?
8. Question for replies.
9. Also this cycle: Cua Spaces SDK, Cloudflare Clairic, vLLM bi-directional KV, DeepSeek V4.1 Flash local, CERN + Mistral.
