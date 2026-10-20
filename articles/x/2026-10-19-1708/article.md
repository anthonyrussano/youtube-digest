---
title: "Don't flip your agent to autonomous. Coinbase's three-step ladder, plus schema-locked Claude JSON"
caption: "Agent rollout tip: go supervised, then sampled, then exceptions-only, and move up a step only when your evals clear the bar..."
edition: "2026-10-19-1708"
lead_source: "https://www.youtube.com/watch?v=_4Ph2dhmUFI"
---
Most teams treat agent autonomy like a light switch. Off, then on. Coinbase treats it like a ladder.

Evan Kormos, a player coach at Coinbase, walked through [how to know when an AI agent can work unsupervised](https://www.youtube.com/watch?v=_4Ph2dhmUFI) in regulated workflows like lending.

**Rung one: supervised.** On day one, [people check everything the agent produces](https://www.youtube.com/watch?v=_4Ph2dhmUFI&t=877s), and experts define what "good" looks like.

**Rung two: sampled.** When measured confidence clears a threshold your policy sets, [humans review only a slice](https://www.youtube.com/watch?v=_4Ph2dhmUFI&t=907s), and traces and evals cover the rest.

**Rung three: exceptions only.** After the next threshold, [people step in only when something breaks](https://www.youtube.com/watch?v=_4Ph2dhmUFI&t=931s), and keep improving the test data.

Which steps get an agent at all? He asks four yes-or-no questions: can you [check it against policy, run it in a bounded loop, trace it, and hand it back to a human](https://www.youtube.com/watch?v=_4Ph2dhmUFI&t=819s)? The final lending decision stays human.

The reason is one line: [the loop is only as trustworthy as the check](https://www.youtube.com/watch?v=_4Ph2dhmUFI&t=652s). Agents can give different answers to the same request, so exact-match tests are not enough. You need real datasets and repeated eval runs.

**The part most recaps skip:** when an agent speeds up one step, [the work piles up at the next one](https://www.youtube.com/watch?v=_4Ph2dhmUFI&t=462s). Faster code review means design and security scans have to keep up. Kormos says seeing the whole process matters more than which workflow tool you pick.

His rule of thumb: [deterministic on the outside, adaptive on the inside](https://www.youtube.com/watch?v=_4Ph2dhmUFI&t=965s).

Amazon Bedrock now gives every Claude model [structured outputs that can't break your JSON schema](https://aws.amazon.com/blogs/machine-learning/structured-outputs-for-anthropic-claude-models-on-amazon-bedrock/). The schema is compiled once and cached for 24 hours, and a strict mode locks agent tool arguments too, so the retry-and-parse code can go.

AWS showed an agent that [builds the business case for moving Kafka to Amazon MSK](https://www.youtube.com/watch?v=nQX30d3ETB8) in minutes instead of weeks. It sizes brokers from real throughput and [caught missing throughput data](https://www.youtube.com/watch?v=nQX30d3ETB8&t=258s) in the demo.

A paper called DiscoveryRSI let a 27B model improve its own research loop, and it [proposed hypotheses matching papers published after its training cutoff 6.3% of the time](https://x.com/omarsar0/status/2112295238664696237), against 2.5% for GPT-6.

OpenAI's team showed a refreshed Codex CLI that can [fork a conversation into its own worktree](https://www.youtube.com/watch?v=DQHtmW9ZlIs&t=81s), plus [Codex Cloud, so the agent keeps working after you close your laptop](https://www.youtube.com/watch?v=DQHtmW9ZlIs&t=50s).

One Claude Code user shared a [setup where Sonnet writes, Haiku subagents search and Opus only reviews](https://x.com/thedelost/status/2112294434780131625) before a plan locks, after a repeated error, and before "done." The post also plugs an unrelated product, but the reviewer-only idea is easy to try.

Hao AI Lab [generated a 768p clip with audio in 8 steps on two DGX Spark desktops](https://x.com/haoailab/status/2112305087225983427).

And new AWS users can now [land in SageMaker Studio in about 20 seconds](https://aws.amazon.com/blogs/machine-learning/developers-can-now-access-sagemaker-studio-through-the-new-aws-experience/) with a Google or GitHub login and, for most, no credit card.

Which rung are your agents on right now, and what check would it take to move them up one?
