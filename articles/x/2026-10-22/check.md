# Check: edition 2026-10-22 (roundup)

## Research summary
- Lead source is primary (CNCF blog by Radar's CPO, with Radar's own write-up and per-fault replay). Coverage on
  Oct 22 morning is the vendor + CNCF post; quoted numbers are the 3x speed-up. The destructive-while-investigating
  finding (own pods on 13 faults, exec/cp/port-forward/debug on 21, Secrets pulled on 4, drop() on two MongoDB
  collections) and the view-only-identity recipe are under-covered. Angle is real and sourced.
- Caveats carried into the article: vendor-run, one run per fault, arms also differed in write access, both
  missed the same three faults.

## Outline tightened
- One idea per section: (1) context changes speed not accuracy, (2) what context means, (3) the example,
  (4) what the agent did with write access, (5) what to do this week, (6) caveats. Jargon defined in place
  ("view" role, "context").

## Rule checks
- Title names the lead idea (not a list): PASS.
- Caption tip-first ("Kubernetes agent tip: ... give Claude Code a view-only identity plus read-only ... tools"),
  ends with "...": PASS. No "$<number>": PASS. No banned internal style name: PASS.
- Roundup shape: in-depth lead first (~466 words), short bulleted "Also this cycle" (7 one-liners), closing
  question inviting replies: PASS.
- No platform framing or engagement counts; claims linked on the text; vendor numbers attributed: PASS.
- No story repeated from earlier editions (php2shell, Duet, API version, GitHub Git infra, OTel, Postmark MCP,
  Air Canada evals are all new this window): PASS.
- `./run.sh x-article 2026-10-22 --dry-run` prints FORMAT: roundup and SOURCE: articles/x/2026-10-22/article.md: PASS.

## Number checks (article vs source)
| Claim | Source value | OK |
|---|---|---|
| 45 vs 46 correct | CNCF table: 45 / 46 | yes |
| within 2 min 60% vs 86% | CNCF table | yes |
| within 5 min 78% vs 90% (chart) | CNCF table | yes |
| mean time 191 s vs 64 s | CNCF table | yes |
| 58 tool calls / ~12 min (701.6 s) vs 7 calls / 35 s (34.8 s) | CNCF transcript excerpt | yes |
| first call on all 50, change timeline second on 35 | CNCF text | yes |
| pods on 13, exec/cp/port-forward/debug on 21, Secrets on 4, drop() on two MongoDB collections | CNCF "What it runs as" | yes |
| php2shell: Calif with GPT-5.6 Sol; Wiz independently found both | OpenAI post | yes |
| PHP runtime, updating plugins alone does not fix | Cloudflare post | yes |
| Postmark MCP v1.0.16 one-line BCC | freeCodeCamp video, 216-294 s; slide at 266 s | yes |
| API 2026-10-21 removes temperature/top_p/top_k; new SDKs default to it | ClaudeDevs post | yes |
| Duet: proactive agent, waitlist, can watch Slack/prepare questions | mikeyk post | yes |
| GitHub per-reference ordering, 3-4x write throughput (internal testing) | GitHub blog | yes |
| 181 records / 289 KB JSON for one small Claude Code task | CNCF OTel post | yes |
| Air Canada "write the answer first", broken signed contracts | video at 1138 s and 838-876 s | yes |

## Images
| File | Kind | Source | Timestamp | Check |
|---|---|---|---|---|
| /workspace/2026-10-22-2-radar-context-chart.png | chart (chart-generator on iphedeiah, dark, 2400 px) | https://www.cncf.io/blog/2026/10/21/before-you-evaluate-an-ai-sre-give-your-existing-agent-context/ | n/a | data.csv values 60/86 (2 min) and 78/90 (5 min) copied from the CNCF table; units %; chart has no value labels, numbers are in the text; blindspots report clean |
| /workspace/2026-10-22-1-postmark-mcp-bcc.png | video-frame | https://www.youtube.com/watch?v=gYXLRMycVMk&t=266s (freeCodeCamp.org, "MCP Security Fundamentals Course") | 266 | slide with the sendEmail code and highlighted `Bcc: 'phan@giftshop.club'` line; small presenter inset, mostly slide (not a talking head); alt names channel and video; adjacent bullet links the timestamped video |

## Changes made during the check
- Caption: "It was right inside 2 minutes" -> "With that context it was right within 2 minutes" (clear subject).
- Lead: "view role reads almost everything" -> "lets it read cluster state" (only claim the source supports).
- php2shell bullet: corrected attribution (Calif found a flaw with GPT-5.6 Sol; Wiz independently found both).
- GitHub bullet: "per branch reference" -> "per Git reference (a branch or tag)".
