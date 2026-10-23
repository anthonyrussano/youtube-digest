# Research: edition 2026-10-22-1207

## Lead candidate: skills, not models (Jellyfish data + Agent Skills joins the Linux Foundation)

Source 1: Nicholas Arcolano (head of AI and research, Jellyfish), "Better AI Models Won't Fix Your Engineering Team", AI Engineer New York, leadership session, Oct 14 2026. https://www.youtube.com/watch?v=Ve2bAarPA2I
- Jellyfish joins AI coding tool telemetry with engineering workflow data: hundreds of thousands of developers, about 1,300 companies (t=165).
- Natural experiment: when Cursor promoted Grok in its UI and changed auto mode, model share shifted faster than anything they had seen; change in merged PRs per engineer vs colleagues showed no correlation, "output didn't change" (t=240-271).
- Curated set: about 50,000 engineers at 447 companies, Cursor and Claude Code users, March-September 2026; output metric merged PRs per engineer per week; no quality metric in this analysis (t=296, t=430).
- Share of PR-throughput variation explained (slide "How much each one matters", t=385-410): the tool under 1%, how well you use it (skills, Cursor rules, harness customization) 3%, how much you use it 9%, where you work 12%, the individual 75%.
- Switching Opus/Sonnet/ChatGPT, Cursor to Claude Code, autocomplete to agentic: "kind of a nothing burger" (t=450-497). Slide: all-in on Opus -3.5%, Sonnet -2.0%, GPT/Codex -4.8%, confidence intervals crossing zero.
- Skills (t=505-600): slide "Heavy skill use is still rare" (Cursor, 28K engineers): September engineer-weeks: no skill use 46%, 1-9 runs 30%, 10-29 runs 13%, 30+ runs 12%. Slide "Skill use moves output more than model choice": 1-9 runs +0.3%, 10-29 runs +9.8%, 30+ runs +30.2% weekly merged PRs vs the same engineer's other weeks.
- Tokens (t=626-669): top 10% vs median roughly double output for about 10x tokens; diminishing returns.
- Company spread 2x top vs bottom 10% at fixed consumption; individual spread 3.5x; top-quartile churn 44% before AI vs 41% after (t=725-875).

Source 2: Anthropic, "Donating Agent Skills to the Agentic AI Foundation", Oct 22 2026. https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation
- A skill is a folder with a SKILL.md file plus any scripts or reference material.
- 70+ platforms including ChatGPT, Cursor, GitHub Copilot, VS Code; 1 million skills published, nearly 280 million installed.
- Donated to AAIF under the Linux Foundation (co-founded with Block and OpenAI; also hosts MCP). Contributing does not require AAIF membership. Lead maintainers David Soria Parra and Mahesh Murag.
- Roadmap proposal: versioned releases, formal proposal process, security guidance for people who write and install skills.
- Simon Willison's write-up: https://simonwillison.net/2026/Oct/22/donating-agent-skills/

Supporting example (outside the window, linked): Walden Yan built /walden-review, a review skill generated from his last six months of GitHub comments and agent sessions, and runs it before reading any PR. https://x.com/walden_yan/status/2112610802830381394
Jellyfish's own post says code review is the most-invoked skill category in Cursor: https://x.com/_jellyfish_co/status/2112911845472207239

## Coverage check (X search, Oct 22)
- The Agent Skills donation is everywhere: Anthropic's post, Rohan Paul, many recaps repeating 70+ platforms / 280M installs / "same as MCP" / governance.
- Almost nobody connected it to usage data. The Jellyfish talk got near-zero pickup; the one Jellyfish-data post found was about agent PR review bottlenecks, not skills.
- Overlooked: the standard everyone is celebrating is the lever most engineers are not pulling. Nearly half of engineer-weeks use no skills, yet heavy skill use moves output about 30%, roughly ten times anything model switching did.

## Candidates
| Story | Why lead | Coverage | Verdict |
|---|---|---|---|
| Skills vs models (Jellyfish + AAIF) | Actionable, big-name tools (Cursor, Claude Code, Copilot), strong slides for frames | Donation widely covered, data angle missed | LEAD |
| CrowdStrike 27-second pivot | Striking number | Moderate | Also |
| Vanguard mainframe via MCP | Practical | Low | Also |
| CloudFormation forced rollback | Practical DevOps | Low | Also |
| Gemini agent CLI | Big name | Moderate | Also |
| Postgres hybrid search | Practical | Low | Also |

Chosen angle: everyone is covering Agent Skills getting a neutral home, but Jellyfish's data on 50,000 engineers shows switching models barely moves output while heavy skill use moves it about 30%, and almost half of engineer-weeks use no skills at all, so the move is to write a few skills for your team's repeated work instead of chasing the next model.
