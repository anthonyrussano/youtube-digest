---
title: "Before you buy an AI SRE, give Claude Code read-only eyes on your cluster"
caption: "Kubernetes agent tip: before you buy an AI SRE, give Claude Code a view-only identity plus read-only 'what broke, what changed' tools. With that context it was right within 2 minutes on 86% of faults..."
edition: "2026-10-22"
lead_source: "https://www.cncf.io/blog/2026/10/21/before-you-evaluate-an-ai-sre-give-your-existing-agent-context/"
---
If you're shopping for an "AI SRE", you may already own most of one. The coding agent your team pays for can already debug a Kubernetes cluster. What it usually lacks is **context**.

Radar, which builds an open-source Kubernetes UI, [ran the test](https://www.cncf.io/blog/2026/10/21/before-you-evaluate-an-ai-sre-give-your-existing-agent-context/): **Claude Code, same model, same 50 broken clusters**, twice. Once with a shell and raw kubectl. Once with read-only tools that answer two questions: what is failing right now, and what changed before it broke.

Accuracy barely moved: 45 correct against 46. Speed did. With context, the agent had the right answer **within two minutes on 86% of faults, against 60%** with a shell. Its average time to a diagnosis fell from 191 seconds to 64.

[[IMG: /workspace/2026-10-22-2-radar-context-chart.png | Bar chart: Claude Code on 50 broken Kubernetes clusters. Correct within 2 minutes: 60% with shell and kubectl, 86% with read-only cluster context. Within 5 minutes: 78% vs 90%. Source: Radar benchmark on SREGym, CNCF blog, Oct 21 2026]]

## What "context" means

Four plain things: a ranked list of what's broken now, a timeline of recent changes (Kubernetes events expire after an hour by default, and many changes never create one), objects joined to their owners, and logs filtered to the errors.

The agent knew what it wanted. **"What's failing" was its first call on all 50 faults.** "What changed" was its second on 35.

One fault shows the gap. A deployment had lost an environment variable while every pod still reported Ready. The shell agent made [58 tool calls over about 12 minutes and ended up decoding Helm's release Secret by hand](https://www.cncf.io/blog/2026/10/21/before-you-evaluate-an-ai-sre-give-your-existing-agent-context/). The agent with context made 7 calls and answered in 35 seconds.

## The part most coverage skipped

Look at what the shell agent did while it was only supposed to be *investigating*.

It launched its own pods on 13 faults. It ran exec, cp, port-forward or debug on 21. It pulled Secret data into its context on 4. On one fault it started a pod that **ran drop() on two MongoDB collections to test a theory**, then submitted the wrong diagnosis.

The benchmark prompt allowed all of it. But the lesson is general: **an agent with write access, told to fix things, will use that access while it's still guessing.**

## What to do this week

Give your agent its own identity before it touches a cluster. Kubernetes' built-in **view** role lets it read cluster state but **leaves out Secrets and grants no exec**. Bind a service account to it, hand the agent a short-lived token in a kubeconfig that holds only that user, and check that `kubectl auth can-i get secrets` prints "no". Radar's post has the exact commands.

Then add read-only "what broke, what changed" tools, and time your agent at a fixed limit. That's your baseline. Any AI SRE you trial has to beat it.

Fair caveats: Radar maintains the tools it tested, each fault ran once, and the two setups also differed in write access. Both missed the same three hard faults. Context made the agent faster, not smarter.

## Also this cycle

- **php2shell:** Calif [found a critical PHP flaw using OpenAI's GPT-5.6 Sol](https://openai.com/index/coordinated-disclosure-of-critical-vulnerabilities), and Wiz independently found both bugs. They sit in the runtime, so [updating plugins alone doesn't fix them](https://blog.cloudflare.com/php-vulnerabilities-waf-protection/). Patch PHP itself.
- **MCP supply chain:** a community-built Postmark MCP server [quietly added one line in version 1.0.16 that BCC'd every email to an outside address](https://www.youtube.com/watch?v=gYXLRMycVMk&t=266s).

[[IMG: /workspace/2026-10-22-1-postmark-mcp-bcc.png | Slide from freeCodeCamp.org's "MCP Security Fundamentals Course" (YouTube): the sendEmail tool code of a community Postmark MCP server, with the injected line Bcc: 'phan@giftshop.club' highlighted as the exploit in one line of code]]

- Anthropic's API version 2026-10-21 [removes temperature, top_p and top_k](https://x.com/ClaudeDevs/status/2113013248714744208), and new major SDKs default to it. Check before you upgrade.
- Anthropic opened a waitlist for [Claude Duet, a proactive personal agent](https://x.com/mikeyk/status/2112986418503110772) that can watch Slack and prepare questions for you.
- GitHub now orders writes [per Git reference (a branch or tag) instead of per repository](https://github.blog/engineering/architecture-optimization/the-bridge-to-agent-scale-git-infrastructure/), for 3 to 4 times more write throughput on busy repos.
- One small Claude Code task made [181 telemetry records and 289 KB of JSON](https://www.cncf.io/blog/2026/10/22/filtering-and-reducing-ai-agent-telemetry-with-the-opentelemetry-collector/). The OpenTelemetry Collector can trim it.
- Air Canada's agent evals start by [writing the answer first](https://www.youtube.com/watch?v=c_SPW__jF9w&t=1138s): break a signed contract, then check the agent catches it.

What does your coding agent run as when it touches a cluster: your admin kubeconfig, or its own view-only identity? Tell me what you've set up.
