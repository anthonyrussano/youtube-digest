# Research: 2026-11-10 (overnight prep, classic full roundup)

Window: 2026-11-10 01:47 UTC to 08:32 UTC (about 7 hours, overnight). Sources: 6 transcribed videos (all on the GPU host with Whisper large-v3-turbo; captions were rate limited), 5 feed articles, 7 X posts, 0 AINews stories (the one issue in the window had nothing new).

## Lead: Anthropic's Fable 5.2 prompting guide, "Say who owns the code"
Primary: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2 (read in full)
- Without an ownership statement, or with the code presented as someone else's, the model adds to the existing structure even when that repeats code, and reports nearby problems instead of fixing them.
- Suggested sentence: "This codebase is yours: what it's for and how it's built are your call, and you'll keep building on it."
- Small coding tasks: merged repeated code in about half of tries with the sentence, under a tenth without. Rate varied by task; held inside a long system prompt; requested feature worked in nearly every try either way.
- Costs: about 1.5x output tokens; several unrequested changes (many new tests and docs); changed existing feature behavior in one try in six to ten (more at higher effort); closing summary named large changes but often left out small ones -> "review the diff and not only the summary".
- "No drive-by refactors, renames or cleanups" earlier in the prompt does not cancel it: still merged repeated code in about a third of tries.
- Leave it out where the user owns the code and wants minimal change.
- Same guide, "Finish the whole task": with a version of the "Finishing work" text, about half as many replayed sessions ended with doable work left; output tokens rose about 30 percent.
- Supporting: Simon Willison quote post https://simonwillison.net/2026/Nov/10/prompting-claude-fable-52/ and post https://x.com/simonw/status/2120029347948220500 ("always worth taking a look at their updated prompting guide").
- Ethan Mollick https://x.com/emollick/status/2120000888974766501: Fable 5.2 above the already steep trendline on three unsaturated benchmarks (ECI, Remote Labor, RoboDojo). Chart values not used (image only).

What coverage did: explainx.ai, notesbylex.com, ecosistemastartup.com and Simon Willison all lead with the merge rate (about half vs under a tenth). notesbylex mentions "review the diff". Mostly missed: the 1.5x token cost, the behavior changes in one try in six to ten, and that a "no drive-by refactors" rule does not cancel the sentence. That is the angle.

## Other items (facts used)
- Harvey, Joey Wang, "The Agents Were Fine. Everything Around Them Broke." https://www.youtube.com/watch?v=ktbAVYsAxpk : more than one agent started every minute (3s); 10,000 agent PRs (35s); follow-up loop, if you build only one stage build it; 4 of 5 agent PRs merged into backend had been through it (255-271s); bad release, one alert per workspace, workflow tagged the agent on each, normal day ~50 tasks, that day ~900 in ~4 h (461-492s); fix: repeat alert joins the open investigation (500s); October: ~950 tasks from the CLI in ~3 h (519s); fair launch queue four days later (537-567s). Slide at 567s: 40 slots held for people at a keyboard, 25 tasks per person (borrow up to 50), 300-task burst test, task list p95 1.7 s -> 71 ms. Slide at 486s: ~2k tasks Aug 14, ~1.3k by bots, 0 of 27 nodes free, 1,000+ failed pod schedules.
- Cloudflare security-audit skill https://github.com/cloudflare/security-audit-skill (README read): seeded Cloudflare's vulnerability discovery harness; six phases (reconnaissance, coverage-led hunting, candidate validation, structured output, independent record verification, target-neutral reporting); verdicts confirmed / needs_validation / rejected; "the agent that checks a finding is never the agent that found it"; "a single run found roughly half of the vulnerabilities that repeated runs found in total". Recipe from https://x.com/shiri_shh/status/2120003262799659071 (npx skills add, /model pick Fable 5.2, "security audit this codebase"); matches the README install and usage.
- Meta Muse Ember via Simon Willison https://simonwillison.net/2026/Nov/10/muse-ember/ : for agents' repeated work (tool calls, coding subtasks, routing, extraction, long document parsing); short-prompt price same as GPT-6 Luna and Claude Haiku 5.5, 0.10 / 0.50 dollars per million input/output; Fable 5.2 is 80x at 8 / 40; six reasoning levels; pelicans comparable to Muse Wonder, 40x the price.
- Kubernetes incident agent design, Akhilesh Mishra https://x.com/livingdevops/status/2120003767277945070 (full long post read): Alertmanager unchanged; SNS -> SQS (buffer, retries, DLQ, dedup, idempotency); Lambda thin trigger; agent on AgentCore; three read-only MCP servers (EKS, Grafana, CloudWatch) via gateway with OIDC; Bedrock knowledge base; actions: suppress noise, Slack + PagerDuty, known-safe auto, else approval; limits 10 s per tool call, 5 min per investigation, max 10 tool calls, max 3 retries; logs are data, never instructions. An interview design, not a production report.
- Modal, Jason Mancuso https://www.youtube.com/watch?v=3nDMYV-QHLs : ~2 inference GPUs per training GPU (876s); updates 100x-1000x sparse (933s); data to rollout engines down by a factor of 1,000 (940s); trainer in one cloud, rollouts across hyperscalers and neoclouds and GPU types (955-999s); rollouts 15% cheaper (1072s); up to 4-5x mismatch, stable training (1052s); H200 pools at BF16 and FP8 (1130-1141s).
- General Intuition, Pim de Witte https://www.youtube.com/watch?v=MpkARD5pq-M : Medal (spelling from the slide at 389s) sees ~1 billion videos uploaded per year, on track for 3 billion (384-389s); over 1.5 trillion action tokens per month (392s); frontier labs' total robotics training data collected in about half a day (399-405s); one model plays games and controls over 10 types of robots (627-634s).
- DeepSeek Harness jailbreak plugin, Thomas Roccia https://x.com/fr0gger_/status/2120026164391485551 : pushed on Telegram for cybercrime; installed via .cmd running PowerShell and "dsh plugin add"; prompt mode "replace" wipes the system prompt; bans 30 refusal phrases; 176-file exploit knowledge base.
- Snowflake Expedition keynote https://www.youtube.com/watch?v=AngQnpIfZKU : Iceberg table branching, private preview, for write-audit-publish of agent-driven changes (1795-1819s); hybrid tables 8x higher throughput, 2-3x lower latency, roughly 80% lower cost (1849-1857s); Snowflake on OCI as a first-party product (2218-2250s).
- Google Cloud Tech, Gemini Live vision https://www.youtube.com/watch?v=dNGchf4InU0 : camera, canvas, JPEG, blob, model (89s); snapshot to look, stream to watch (197s); frames cost tokens; streaming a browser can interrupt live audio (204-240s).
- ARLoop, Yuekun Yao https://x.com/yuekun_yao/status/2119982422259622086 : fully open looped transformers with Attention Residuals; ARLoop-1.2B outperforms Huginn-3.5B and Qwen3.5-2B Base on evaluated benchmarks (their claim); full recipe released.
- OpenAI education report https://openai.com/index/closing-ai-guidance-gap-education : ThinkYoung survey, 79% of students used AI for homework or assignments, 47% shown how.
- Kuken Industries (OpenAI customer video, Japanese audio) https://www.youtube.com/watch?v=FNTz0CdqL6g : drawing search over 70 years of data by part number (83s); a search sometimes took half a day (121s); about 60 minutes to about 10 (136s). The first minute of the Whisper transcript is garbled; only the clean Japanese lines were used.
- Microsoft Go 1.25.14-2 https://devblogs.microsoft.com/go/go-1-25-14-2-microsoft-build-now-available : one-off backport for CVE-2026-111943; Go 1.25 end of life; still has known unpatched vulnerabilities; upgrade to 1.26 or 1.27.
- Simon Willison, Yonkers Rises https://simonwillison.net/2026/Nov/10/yonkers-rises/ : Fable 5.2 Medium three.js mech animation with OpenStreetMap data; deduced "átomos" was a typo for "stomps".

## Dropped
- Boris Cherny "10 to 30 PRs a day" thread: secondhand promo thread, not the primary source.
- Listicles and roadmaps (system design roadmap, AWS services list, DevOps interview questions, beginner agent roadmap), a non-technical personal post and a growth-hacking interview.
- The Register Cisco item: the extracted text was the site's headline list, not the article.
- Stack Overflow Airbnb podcast: summary only, no concrete detail.

## Candidates
| Story | Why lead | Coverage | Verdict |
|---|---|---|---|
| Fable 5.2 ownership sentence | actionable agent-tool tip, top-trending brand | merge rate widely quoted; costs mostly missed | lead + caption |
| Harvey 900 agents | big hard number, ops lesson | single conference talk | cold open + 2nd item |
| Cloudflare security-audit skill | do-it-today tool | shared as a recipe | 3rd item |

Angle in one sentence: one ownership sentence changes how Fable 5.2 edits your code, and the trade is more tokens and unrequested changes, so review the diff, not the summary.
