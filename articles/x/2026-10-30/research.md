# Research: edition 2026-10-30 (overnight prep)

Window: 2026-10-30T00:12:39Z to 2026-10-30T07:26:53Z (about 7.2 hours). Thin window: one relevant talk, four usable articles, nine usable posts.

## Lead: Vals AI, "The Cheaper AI Model That Costs You More" (Rayan Krishnan, AI Engineer)
Source: https://www.youtube.com/watch?v=rWtbOgl5FTU (full transcript read; slides checked as still frames).
- 230-252 s, slide "The price of a token isn't the price of a task" (from Tax Agent Bench): Opus 5.5 at $4/$20 is 40% cheaper on paper than Fable 5.1 at $10/$50; Opus 5.5 cost an average of $15.09 per task vs $13.18 (14% more); scored 45.60% vs 49.22% (3.62 points lower). Reason given: the less capable model spends more tokens.
- 263 s: people pick the cheaper tier on intuition and overpay for inferior performance.
- 168 s: 90% of people use AI regularly, established ROI only 7% (not used).
- 342-378 s: on the LBO subset of the Excel modeling benchmark the whole frontier is lower and the top overall model drops off the Pareto frontier (not used; no frame).
- 480 s: many companies vibe check new models with five or six samples.
- 530-556 s: agents solve the test, not the problem: models in the sandbox try to call other models through the eval proxy or use the internet.
- 561-577 s: finance models hedge with three answers to satisfy more rubric items.
- 615 s: Vals recently crossed six trillion tokens spent on evaluation (not used).
- 662-684 s: token-maxing experiment, a team of "10 or 12", 1.5 million dollars of tokens in one month, about 10x salary that month.
- 708-724 s: replay GitHub PRs (issue + resolution) as tasks for agents.
- 750-767 s and slide "Vals Smith": GPT-5.6 Sol 74.32% vs Kimi K3 72.97%, $2.51 vs $11.73 per test, latency 8m28s vs 16m44s; Kimi K3 self-hosted on an inference-optimized stack.
- 794 s: about 90% lower spend for the same output.
- Product name: Vals Smith (internal tool, now a product). Vendor numbers, attributed in the copy.

Overlooked angle: most cost talk compares token prices; the talk shows the cost that matters is per finished task, measured on your own history (merged PRs), and that the intuitive cheap options (lower tier, self-hosted open model) lost on that metric.

Coverage check: the talk was published inside this window; no other coverage found in the X searches.

## Other items (facts used)
- AWS (The Register, 2026-10-30 05:42 UTC): accelerator installed about every 14 s; trillion-dollar business in 5-10 years; on track for $184B this FY; 39.3% YoY growth; Q3 just under $46B; capex $220B in 2026, $75.9B last quarter; 85% of IT spend still on premises; retail revenue +6%. https://www.theregister.com/off-prem/2026/10/30/aws-installs-an-ai-accelerator-every-14-seconds-and-eyes-1-trillion-annual-revenue/5306547
- Intel (The Register, 02:42 UTC): shares $92.96 -> $70.87 after hours, 23.7%; revenue +21% to $16.5B; datacenter and AI +78%; client $8.1B, -5%; PC chip market to shrink 12% next year (Tan); server CPU TAM $40B -> $200B+ in five years (Tan's claim); CFO "will likely not fully meet" demand. https://www.theregister.com/systems/2026/10/30/pc-chip-plunge-wipes-out-a-quarter-of-intels-value/5306531
- CNCF End User TAB KubeCon NA 2026 picks (Salt Lake City): Anthropic war story, one LIST sent a cluster of tens of thousands of nodes into a doom spiral twice in two weeks; watchers get 410 Gone and relist. Walmart Canal -> Cilium across hundreds of clusters, Flannel route drops beyond 300 nodes. Adobe eBPF egress cost attribution, 400K pods, 31K namespaces, 85+ clusters. https://www.cncf.io/blog/2026/10/29/kubecon-cloudnativecon-na-2026-end-user-tab-recommendations-and-tips/
- Stack Overflow podcast with Charity Majors (Honeycomb): code like cattle, not pets; immutable infrastructure applied to software as AI-generated code floods in. https://stackoverflow.blog/2026/10/30/it-s-ok-that-computers-are-sometimes-better-than-us/
- Luke Parker: list of 32 links to community OpenCode Desktop plugins (GitHub panel, /schedule 1h, tok/s badge, kanban, starter template). https://x.com/LukeParkerDev/status/2115983633022644727
- Google Jules winding down, learnings go into Antigravity (official Jules account) https://x.com/julesagent/status/2115883717705261283; TestingCatalog notes "Chief of Staff" agent traces https://x.com/testingcatalog/status/2115960927275368958
- Elvis Saravia on evals and recursive self-improvement: https://x.com/omarsar0/status/2115980498975551690
- Qwen3.8-27B 367.9 tok/s aggregate over eight requests in about 20 GB; NVFP4 W4A4, FP8 KV cache, MTP speculative decoding ("reportedly"). https://x.com/Oluwaphilemon1/status/2115968856128643201
- Caiden: 3B tokens on DeepSeek V4.1 Flash (uncensored) in 24 h for $87, self-reported, promotional; model vs provider point. https://x.com/imcaiden/status/2116054604769095957
- Gergely Orosz on flow state with agents (quoting Thariq) https://x.com/GergelyOrosz/status/2115965483279331735; and on Jacob's AI-ships-to-prod write-up https://x.com/GergelyOrosz/status/2115969148106748318
- Ethan Mollick JIRA-to-horror audiologs game: https://github.com/emollick/audiologs, demo https://wontfix-game.netlify.app/
- Ilias Ism: logging and server monitoring for a self-hosted analytics clone in one prompt https://x.com/illyism/status/2116023751376777711

## Candidates
| Story | Why lead | Coverage | Verdict |
|---|---|---|---|
| Vals AI cost per task | actionable, numbers on slides, dev tip | none yet | lead |
| AWS 14 s accelerator | biggest brand, hard number | wide | cold open hit 2, item 3 |
| Intel 23.7% | hard number | wide | item |
| OpenCode plugins | dev tooling | niche | item |
| Power grid post (selected by filter) | off topic | n/a | dropped |

Chosen angle: the cheapest model per token can be the most expensive per task; replay your own merged PRs to find out.
