# Research: 2026-11-04-1211 (classic full roundup)

Window: 2026-11-04 14:19:20Z to 20:18Z (6:19 AM to 12:18 PM PT). Sources: 4 transcribed videos (captions), 7 feed articles, 12 AINews stories (cited to original sources), 15 qualifying X posts (9 used).

## Lead: Kimi K3.1 Pro open weights (Moonshot)
- Model card (https://huggingface.co/moonshotai/Kimi-K3.1-Pro): MoE, 2.8T total / 104B active, 896 experts, 16 per token, 2 shared; 93 layers (69 KDA + 24 Gated DSA); 1,048,576-token context; MXFP4 weights / MXFP8 activations via quantization-aware training; recommended engines vLLM, SGLang, TokenSpeed.
- Moonshot's table (max effort): SWE Marathon v1.1 51.7 vs Opus 5.5 46.3; DeepSWE v1.1 75.5 vs 74.2; Terminal-Bench 4.0 65.7 vs 66.4; ProgramBench 31.5 vs 65.0. Most agentic scores run inside the Claude Code harness. OfficeQA runs that fetch reference answers online score zero.
- Vercel AI Gateway (https://vercel.com/changelog/kimi-k3-1-pro-now-has-more-zdr-providers-on-ai-gateway): more ZDR providers; `zeroDataRetention` makes requests fail rather than reach a non-ZDR provider.
- Coverage check (web): most write-ups repeat the benchmark table. Under-covered: the repo is 1.56 TB in 96 shards (not the 5.6 TB BF16 figure quoted for 11 days) because MXFP4 is the native precision, and the custom license has a 20 million dollar revenue line for API sellers (https://artificialwatch.com/wire/kimi-k3-1-pro-open-weights-out, https://www.orcarouter.ai/blog/kimi-k3-1-pro-weights-released-self-hosting-cost). Added one sentence on that to the Article.

## Other stories (facts used)
- OpenAI acquires Pierre (https://openai.com/index/openai-to-acquire-pierre): Trees and Diffs already in Codex app; Code Storage; Highlights; tied to Pando; open source stays open; closing subject to approvals.
- Warp, Zach Lloyd article (https://x.com/zachlloydtweets/status/2118043142259888383): factories as code, "Terraform for all of the coding agent workflows"; Sentry workflow checklist (20+ questions counted); pre-warm sandboxes for prompt-triggered runs. Vendor pitch, flagged.
- Ubuntu APT CVE-2026-109518 (Ubuntu blog): CVSS 4.0 7.7, on-path HTTP attacker, signature-check bypass on retry, root via .deb scripts; 22.04+ default retries; TLS or Acquire::Retries=0 mitigates.
- Lauren Tan (https://x.com/poteto/status/2118017093677494706): ~30x code without reading it, perf as good or better, ~230 people landed a PR in October; AI Engineer talk.
- Stack Overflow blog .NET: 42.1 s -> 83.6 s for 200 records, two CPUs -> one; ProcessorCount cap.
- Phone Harness (https://x.com/shawn_pana/status/2118010388621000770), Atomic Local AI Server (https://x.com/atomic_chat_hq/status/2118038974996373719).
- Kevin Roose video (IOp5N4GxE6E): council of Claudes t=1537, caught errors t=1604, quote t=1616, 150 people t=668, big blob of compute memo t=931.
- FlashProve (jaminball post), benchmark audit (HamelHusain post).
- Siemens/AWS video (PyO9FAJ3Vtg): 70 projects in 8 years vs 400 in 6 months t=126-135, 39 platforms t=88, agent in a day t=145.
- GitHub Copilot Verified Proficiency video (aXK0wctLk5U): no exam t=113, five levels t=145 (frame), Pro badge t=284, usage signals not code or prompts t=338.
- Amp tool rename 53% -> 79% (nicolaygerold); AWS Deep Insight ~95% / ~97% / under 25K tokens.
- Microsoft Agent Framework skills (devblogs), Firecrawl Ad Finder video (5uy7anLyT58: 60 lines t=37, HelloFresh t=24, harness t=128, four columns t=267 frame).
- Ballots: ~40 localities, 13 states (jdcapelouto); 43-1, ~77% (AndrewCurran_). Revolut ~2,000 engineers, 1/10 cost, 70% faster (cohere post); Hy4 55 cents vs 1.46 dollars a task (arena post). OpenAI models as soon as Friday (steph_palazzolo, a report).
- Quick ones: AA-Robotics 22 minutes; ISTA GSQ 72.1 GB vs 138.2 GB, 94.8% SWE-bench retained; LSA 72.4x prefill at 10M tokens; Qwen4 names likely fixtures; LongCat-2.5 1.6T/48B, 28 vs 82 cents; Mollick paper; Claude Code October; Teachable Code.

## Candidates for the lead
| Story | Why lead | Coverage | Verdict |
|---|---|---|---|
| Kimi K3.1 Pro weights | biggest named model, hard numbers, open | wide, but the 1.56 TB / license angle is thin | lead |
| OpenAI buys Pierre | big brand | no numbers | #2 |
| Amp tool rename | best tip | tiny | caption tip |

Chosen: lead with Kimi K3.1 Pro's open 2.8T weights and the "wins on marathon coding, half the score on ProgramBench" contrast; caption tip from the Amp rename.
