# Research: edition 2026-10-19-1708 (X Article, roundup)

## Lead candidate: Evan Kormos (Coinbase), "How to Know When an AI Agent Can Work Unsupervised"
Source: https://www.youtube.com/watch?v=_4Ph2dhmUFI (AI Engineer NYC 2026 talk "Trusting Agents in Policy-Driven Workflows", https://ai.engineer/nyc/2026/talks/coinbase)
- Policy = "the original system prompt" of the organization (t=60s).
- Workflows as a DAG (fixed, gated stages, e.g. Airflow) with loops inside each node (DCG, e.g. LangGraph) (t=245s, t=396s).
- Agents shift volume through the flow: faster code review means design and security scans must keep up; "operational visibility of the process is extremely important, much more important than the authoring and the building of your workflow tool" (t=462s-511s).
- Inject the DAG state into the agent so it knows where it fits (t=611s).
- "The loop is really only as trustworthy as the check" (t=652s); agents are probabilistic, so exact-output comparisons are not enough; use representative datasets, repeated eval runs, traces (t=715s-768s).
- Four questions per node: checkable against policy, bounded loop, traceable, can fall back to a human (t=819s). The final lending decision stays human (t=854s).
- Rollout: supervised day one (t=877s), sampling once measured confidence reaches a policy threshold (t=907s), then humans handle exceptions (t=931s).
- Takeaway: "deterministic on the outside, adaptive on the inside" (t=965s).

Coverage check (web search): conference recap pages (ai.engineer, swyx talk pages, ainotes.us) restate the three-step rollout. Nobody pulls out the volume-shift point: speeding up one node moves the bottleneck downstream, so the process dashboard matters more than the workflow tool. The ai.engineer page also notes the threshold is a policy decision, not a universal score.

## Other items (facts from the website edition sources)
- Bedrock structured outputs for all Claude models: constrained decoding, grammar compiled on first request and cached 24 h, name/description edits keep the cache, strict tool use on bedrock-mantle. https://aws.amazon.com/blogs/machine-learning/structured-outputs-for-anthropic-claude-models-on-amazon-bedrock/
- AWS Transform Kafka-to-MSK business case: weeks by hand, minutes now; sizes Express brokers from throughput; flagged missing throughput in the demo; workbook, report, presentation; usable via MCP server. https://www.youtube.com/watch?v=nQX30d3ETB8
- DiscoveryRSI: 6.3% match with post-cutoff research vs 2.5% GPT-6 and 2.3% Claude Opus 5; quality 4.86 to 5.39 after two rounds. https://x.com/omarsar0/status/2112295238664696237
- Codex CLI refresh (fork conversation into a worktree, talk to terminal), Codex Cloud, GPT Live One full duplex. https://www.youtube.com/watch?v=DQHtmW9ZlIs
- Claude Code three-model setup (Sonnet works, Haiku subagents search, Opus advises at three moments); post also plugs an unrelated product. https://x.com/thedelost/status/2112294434780131625
- FastVideo FastH3-QAD-v2: 768p video with audio, 8 steps, two DGX Sparks. https://x.com/haoailab/status/2112305087225983427
- SageMaker Studio in about 20 s, no credit card for most, 100 dollars in credits. https://aws.amazon.com/blogs/machine-learning/developers-can-now-access-sagemaker-studio-through-the-new-aws-experience/

## Candidates
| Story | Why lead | Coverage | Verdict |
|---|---|---|---|
| Coinbase autonomy ladder | Actionable rollout pattern for any agent | Recaps only, bottleneck point missed | Lead |
| Bedrock structured outputs | Practical, but a feature launch | Vendor blog | Item |
| DiscoveryRSI | Striking number | One summary thread | Item |
| Claude Code three-model setup | Tip, but one person's promo-tinged post | Viral thread | Item, flagged |

Angle: don't flip an agent from supervised to autonomous; move it up a ladder only when evals prove it, and watch where the bottleneck moves when you do.
