# Research: edition 2026-10-19-1211

## Lead candidate: Grafana's six Assistant improvements (what they learned building an agent)
Source: https://grafana.com/blog/six-improvements-that-make-grafana-assistant-better-at-helping-your-workflows/ (Grafana Labs blog, Oct 19, 2026, ahead of ObservabilityCon 2026)

Raw facts from the post:
- Dashboarding mode was 27% of Assistant conversations by mid-2026. Users reported slow operations, too many tokens, and unwanted changes.
- Over roughly 10 weeks: reported dashboarding error rate 2.47% -> 0.65%; p95 latency per operation 63 s -> 28.8 s; cost per request -18%.
- Method: find failures in production, reproduce them as evaluation scenarios, fix the root problem, check after rollout. Test catalog grew from 78 scenarios to nearly 200.
- "An AI agent can produce a convincing response even when its underlying work is wrong" (panel renders with wrong aggregation). Graders examine queries, tool calls, saved state and conclusions, not only the final answer. Repeated runs expose inconsistent behavior; comparisons track quality with cost and latency.
- gcx, a CLI designed for agents: watching agents use the CLI showed guessing flags, retrying failed commands, requesting too much output. Fixes: commands describe their capabilities, errors explain how to recover, agents can inspect fields and filter results before they enter context. "What should the interface tell the agent so it can take the next step correctly?"
- Progressive tool discovery: start with compact entry points, fetch the detailed manual only when needed. Initial tool definitions shrank from ~54,500 estimated tokens to 504 (99.1% reduction in that overhead; real savings depend on what is used). They still measure the full workflow, since discovery can add steps.
- Search: embedding raw panel JSON pulled attention to rendering details; representing a panel by folder, dashboard, row, description and queries worked better. Permissions are checked at retrieval time, because access changes after indexing.
- Investigations on real resolved incidents: one agent inferred too much from an alert's name (fetching the alert definition fixed it); another skipped a useful tool because its instructions described the wrong query language. Difficult-incident suite score 52% -> 69% in a week.
- Evaluator rebuild: the old evaluator focused on response text and missed failures on long runs. New one sees more of the agent's work and recognizes partial completion, checked against a stronger reference reviewer. Jev (a typed decision model) was faster and cheaper but agreed with the reference much less, so the stronger judge stays for the main score; Jev is optional for trace triage.

## Coverage check
X search (Oct 12-19) for "Grafana Assistant", "progressive tool discovery", gcx: no posts about this write-up. Progressive tool discovery shows up only as a passing reply about MCP in general. The numbers (54,500 -> 504 tokens, 2.47% -> 0.65%) and the agent-CLI lessons were not covered.

## Candidates
| Story | Why lead | Coverage | Verdict |
|---|---|---|---|
| Grafana Assistant lessons | Concrete, transferable patterns for anyone building agents or MCP tools; numbers from production | Not covered | Lead (deep-dive) |
| Cua Spaces SDK | Bring-your-own-computer for Claude Code/Codex; practical | Launch thread widely seen | Also this cycle |
| Cloudflare Clairic | New model class, typed extraction | Fresh launch, one source | Also this cycle |
| vLLM bi-directional KV transfer (AWS) | Agent TTFT up to 3.3x | Niche infra | Also this cycle |
| DeepSeek V4.1 Flash local (Unsloth) | Big open model on 128 GB RAM | Widely shared | Also this cycle |

## Chosen angle
Most agent failures Grafana fixed were not model problems but interface problems: too many tool schemas up front, CLIs that let agents guess, and graders that only read the final answer. Their fixes are copyable by anyone writing MCP servers or agent tools.
