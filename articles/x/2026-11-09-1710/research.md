# Research: 2026-11-09-1710 (classic full roundup)

Sources are the edition's transcripts (YouTube, linked with timestamps), feed articles and X posts cited in reports/2026-11-09-1710.md. All facts below come from those sources.

## Lead: Robinhood's hybrid PR reviewer (AI Engineer talk, https://www.youtube.com/watch?v=MQiojLnK-E0)
- Problem (74 s): AI assistants open data-pipeline PRs at machine speed; review still runs at human speed.
- Design (206-272 s): layer 1 = deterministic scripts against a source of truth (schema registry, catalog tags, registered lineage, staging performance test at production volume); layer 2 = an agent whose rules say what layer 1 already checks, so it only spends tokens on judgment. Merge needs passing checks AND an approving review.
- Example (718-1000 s): int to bigint widening passed every script; the agent walked repo code and found a job lineage never registered that writes the value into an int column. Escalated; a human confirmed the job was live; downstream table fixed first; no incident.
- Honesty rule (844 s): "None found is not the same as none exist"; the agent never claims an all clear.
- Protected calls (1000-1067 s): sensitive-data grants, migrations that change intent, low-confidence verdicts always go to a person.
- Feedback (1099 s): replies collected daily, on-call updates rules weekly by hand.
- Results as of Aug 31, 2026 (1236, 1395-1431 s): miss rate about 2%; about 60% of pipeline PRs merge with no human review; about 75% less manual review; about 132 engineering hours a month; incidents tied to these PRs down about 30%.
- What they got wrong (1462 s): layers run separately and cannot see each other's state.

Quick web check (what others covered): public coverage of Robinhood's AI work centers on company-wide adoption figures (share of employees using AI, commits per engineer) and a storage-team schema-migration agent. The overlooked angle in this talk is the split of work: let scripts prove facts, tell the agent what they cover, and forbid it from ever declaring "no downstream consumers". Industry data (Jellyfish, an MSR study) shows AI PRs doubling while review becomes the bottleneck, which is the gap Robinhood describes.

## Other items (facts used)
- Careem (dbt videos eszZTWbwJ48, OCGVV_r9Rmk): ~95% of data pipelines AI generated (94 s); warehouse once ran 5,000 homegrown pipelines (0 s); metric onboarding 1-2 weeks to within a day (201 s); context layer = dbt lineage/descriptions/tests pushed to OpenMetadata, MCPs on top.
- PatchWeaver (USENIX Security, xNaq1xnAXiw): canary trap 34 of 50 episodes, +47% remediation time (163 s); LLM as untrusted proposer, 12 candidate plans simulated; step-level violation rate 4.73%, 52.5% below strongest static toolchain, 79.1% below unconstrained agent (488 s); 300 adversarial episodes, miss rate 0.33% vs 28.5% toolchain vs 90.3% LLM agent (562 s); 7.4 ms median admission latency (625 s).
- Levi Strauss (GitHub Universe, -GpxKKgoWWg): 2.5 months vs 9 months, 72% (131 s); 12 handoffs over six roles (344 s); 17 specialist agents on Copilot cloud agent (615 s); gates in fixed order, security last (854 s); AI-assisted PRs 26% to 69%, throughput +51% (1509-1619 s).
- Duolingo SRE (SREcon26 EMEA, b0PKuM6h2Qc): embedding (506 s); AI Slackbot helpful in ~40% then ~70% of incidents (850 s); AI risk-rated low-risk PRs auto-merge, days to minutes, one known incident (971 s).
- Linear (Xw9utONfhIY): code no longer the bottleneck, coherence is (366 s); triage agent reproduced a captions bug (662 s); review agent with product history flagged an incident risk from 6-7 month old changes Codex missed (957 s); surfaced a UI icon rejected over a year (992 s).
- Fable 5.2: Ethan Mollick, 25,000 agents and 450+ worlds (https://x.com/emollick/status/2119918307457577163); Alex Albert, da Vinci notebook PDF to interactive inventions (https://x.com/alexalbert__/status/2119916954337349737); Simon Willison llm-anthropic 0.31, max effort failed after 128,000 thinking tokens, xhigh best (https://simonwillison.net/2026/Nov/9/llm-anthropic/).
- Simon Willison Beep Locator (https://simonwillison.net/2026/Nov/9/mysterious-beeps/): multi-device triangulation, BeepBeep 2007 paper, ~40 cm, old CO detector.
- Audible/SAP admission control (ntVpbyDTYaQ): admission gate before GPU memory (549 s); 63% admitted, p95 TTFT ~2.5 s to ~1 s (2900 s); KV cache 0.5% vs queue 24; refuse-95% SLO trap (2455 s).
- AWS AI-DLC podcast (Zjx_F5EJZqI): CFO 30 million dollars in tokens vs 7-8 million measurable value (361 s); 50% coordination / 30% coding, doubling coding gives 15% (458 s); pages ~15 per on-call to about half (1259 s).
- Cisco tokenomics (KdG9OSOtJOA): ~100 companies (30 s); cheaper model 96% vs 99% evals (196 s); 100K invoice reconciled to 120K (434 s).
- Stripe Kai (LangChain blog): built in one week on Deep Agents; 1,000+ skills from 100+ teams; S3-backed virtual filesystem with sync in/out; sandbox as a tool.
- LinkedIn RSI (yH7_SIIgI-Y): judge agreement ~80% on strong vs ~55% on weak outputs (1530 s); rubric fixes 57% to 64%, error 0.96 to 0.74 (1743 s).
- Monzo (ATMcd9tkhhc): five principles (522 s); no arithmetic in tokens (2641 s); 99% instruction following and user-level CLAUDE.md conflicts (6287 s).
- Vercel Sandbox snapshots: median under 0.4 s from 4.4 s; restore 500 to 250 ms p50.
- AWS Bedrock AgentCore InvokeWebSearch: 7 dollars per 1,000 queries, domain/date filters, PrivateLink, CloudTrail.
- CloudWatch Logs account-level retention: up to 20 policies, prefix match, longest wins, no extra cost.
- Google Cloud Run GPUs: Dr. Cloud to transplant surgeons (6WjdZZL-FEI 33 s), prebuilt Gemma/Llama containers (95 s); Indian retailer 2,000-3,000 videos a day (d-EnAqBmyO8 32 s).
- Quick ones: Obsidian CEO's five Claude Code + Obsidian tools (third-party claim, flagged); ffmpeg skill with 42 FFmpeg tools (promotional thread, flagged).

## Candidates
| Story | Why lead | Coverage | Verdict |
|---|---|---|---|
| Robinhood PR reviewer | big brand, hard numbers (60%, 75%, 132 h, 30%), actionable pattern | adoption stats covered, this design not | LEAD |
| PatchWeaver | strong numbers, security | academic only | cold-open pair |
| Levi Strauss 17 agents | brand + 72% | GitHub Universe | title slot |
| Careem 95% | brand + 95% | dbt short | title slot |

Angle: let scripts prove facts, tell the review agent what they cover, and never let it claim "no downstream readers".
