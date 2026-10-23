---
title: "Switching AI models barely moved developer output. Skills did."
caption: "Claude Code and Cursor tip: stop switching models and turn the three things you explain to your agent most into skills. Weeks with 30+ skill runs merged about 30% more PRs, while switching models barely registered..."
edition: "2026-10-22-1207"
lead_source: "https://www.youtube.com/watch?v=Ve2bAarPA2I&t=385s"
---
Today everyone is talking about Anthropic handing **Agent Skills to the Linux Foundation**. The more useful news is a week-old talk showing that most engineers barely use them.

Jellyfish, which tracks AI coding tool usage against engineering output, got a natural experiment for free. When Cursor started promoting Grok in its interface, engineers' model share jumped faster than anything Jellyfish had seen. Then it checked merged pull requests per engineer. [**Nothing moved.**](https://www.youtube.com/watch?v=Ve2bAarPA2I&t=240s)

## What actually predicts output

Nicholas Arcolano's team then took about **50,000 engineers at 447 companies** using Cursor and Claude Code, and split up what explains their weekly merged PRs. [The tool explains under 1%.](https://www.youtube.com/watch?v=Ve2bAarPA2I&t=385s) How well you use it explains 3%. How much you use it, 9%. Where you work, 12%. You, about 75%.

[[IMG: /workspace/2026-10-22-1207-3-variance-map.png | Slide from AI Engineer's "Better AI Models Won't Fix Your Engineering Team" (Nicholas Arcolano, Jellyfish, YouTube): how much each factor explains PR throughput for Cursor and Claude Code users, March to September 2026. The tool under 1%, how well you use it 3%, how much you use it 9%, where you work 12%, you 75%]]

Going all in on Opus, Sonnet or GPT landed within a few percent either way, inside the noise. Moving from Cursor to Claude Code, or from autocomplete to agents, was in his words ["kind of a nothing burger."](https://www.youtube.com/watch?v=Ve2bAarPA2I&t=488s)

## The lever nobody is pulling

"How well you use it" is mostly **skills**: a folder with a SKILL.md file that teaches the agent one task, plus any scripts it needs.

In Cursor's data, [almost half of engineer-weeks in September had no skill use at all](https://www.youtube.com/watch?v=Ve2bAarPA2I&t=542s). Only 12% ran 30 or more.

Those 30+ weeks merged **about 30% more PRs** than the same engineer's other weeks. None of the model families came close, and none of them was clearly different from zero.

[[IMG: /workspace/2026-10-22-1207-2-skill-effect.png | Slide from AI Engineer's "Better AI Models Won't Fix Your Engineering Team" (Nicholas Arcolano, Jellyfish, YouTube): change in weekly merged PRs versus the same engineer's other weeks. Going all in on Opus -3.5%, Sonnet -2.0%, GPT or Codex -4.8%; skill runs per week 1-9 +0.3%, 10-29 +9.8%, 30+ +30.2%. Cursor, 28K engineers]]

## Why today's news matters

That's where the donation comes in. [More than 70 platforms read the same format](https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation), including ChatGPT, Cursor, GitHub Copilot and VS Code, with nearly 280 million installs. Now it has a neutral home next to MCP.

So a skill you write today keeps working if your team switches tools next quarter. **The skill outlasts the model.**

## What to do this week

Pick the three things you explain to your agent most often. Your code review checklist. Your release steps. The exact command that runs your tests. Turn each one into a skill.

Walden Yan went further and [generated a review skill from six months of his own PR comments](https://x.com/walden_yan/status/2112610802830381394). He runs it before he reads any PR.

Read any skill before you install it. It runs with your agent's access, which is why the new roadmap promises security guidance for people who install them.

Fair caveats: Jellyfish measures merged PRs, not quality. The skills numbers compare engineers with themselves, not a controlled trial. And the person still matters most.

## Also this cycle

- CrowdStrike's George Kurtz says attackers now [pivot to the next system in as little as 27 seconds](https://www.youtube.com/watch?v=PST8yesYOSo&t=474s): "it's not malware anymore, it's prompts."
- Vanguard put its legacy mainframe code behind an MCP server, and questions that took seven days [now take 15 minutes](https://www.youtube.com/watch?v=uA4ah-dVHvU&t=156s).
- CloudFormation can now [force a stuck update rollback to finish in one operation](https://aws.amazon.com/about-aws/whats-new/2026/10/aws-cloudformation-cdk/), from the CLI, CDK or an agent.
- Google's Gemini team previewed a [command-line tool built for agents](https://x.com/LyalinDotCom/status/2113287431382601765) that generates images, video, speech and music.
- Replicating S3 with Object Lock across accounts? The default [aws/s3 key can't cross accounts](https://www.youtube.com/watch?v=o0rASDZgwXk&t=382s), so use a customer-managed key.
- freeCodeCamp builds [BM25 and vector search in one Postgres database](https://www.youtube.com/watch?v=kT7nXO32L-Q&t=2624s), merged with reciprocal rank fusion.

How many skills did your agent run last week? And which one would you write first?
