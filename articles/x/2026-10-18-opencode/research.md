# Research: OpenCode Console breach (deep-dive, 2026-10-18-opencode)

All times converted to PT (UTC-7). Sources are public posts, pages and threads; X posts read via the X API on Oct 18, 2026.

## Starting point: David Sacks
- [Sacks, Oct 18 10:10 AM PT](https://x.com/DavidSacks/status/2111867605388493282): "OpenCode (and earlier Hugging Face) hit the same wall mid-attack: frontier models refused to analyze the very exploits needed for defense because the payloads tripped safety filters. The guardrails backfired." Also: "Chinese models are only about 6–9 months behind the American frontier in cyber" and "The only durable response is decentralized: make powerful models available so defenders can build and run their own cyber defenses."
- He is quoting [Andrew Curran, 8:13 AM PT](https://x.com/AndrewCurran_/status/2111837963214794940), who quoted [dax (thdxr), 7:46 AM PT](https://x.com/thdxr/status/2111831348336091179): "yes that was a bit frustrating mid incident when trying to investigate. they did quite a bit and then started refusing / we got access to daybreak blue now so it's better" — a reply to [Rhys Sullivan](https://x.com/RhysSullivan/status/2111831027824160865) asking about cyber safeguards.
- Same thread, [dax 8:13 AM PT](https://x.com/thdxr/status/2111838044940550257): "we coincidentally applied for it a few days ago and it got approved yesterday / i don't think anyone is refusing to help us".
- Root: [dax 5:04 AM PT](https://x.com/thdxr/status/2111790511409258796): "they've been non stop trying to attack our systems for the past 48 hours ... we basically need agents going 24/7 because that's what they have".
- Sacks's earlier related posts: [Jul 19, Hugging Face + GLM 5.2](https://x.com/DavidSacks/status/2078991100057141620); [Oct 13, Anthropic distillation defenses](https://x.com/DavidSacks/status/2109849209742450696).
- Counterpoint reply: [Lani Refiti](https://x.com/LaniRefiti/status/2111988899723812993): breach "started with stolen API keys from a legacy system, not a refusal."
- Earlier precedent: [Hugging Face disclosure](https://huggingface.co/blog/security-incident-july-2026) says commercial frontier models blocked its forensic work, so it used open-weight GLM-5.2 locally; it says "This is not an argument against safety measures on hosted models." [OpenAI's HF report](https://openai.com/index/hugging-face-model-evaluation-security-incident/).

## OpenCode's own statements
- [OpenCode post, Oct 17 10:56 AM PT, edited 11:08 AM](https://x.com/opencode/status/2111519637049319818): "security breach last night related to a large scale distillation attack that impacted 1.4% of OpenCode Console users"; emailed all; "If you did not get an email you were not impacted, it was a subset of users who had external providers linked"; "incident is ongoing"; "working with Anthropic, OpenAI, and Google". Edit history via [On The Wire](https://onthewire.ai/article/opencode-says-a-breach-hit-1-4-of-its-console-users-an-email-shared-online-tells).
- Email (screenshot, reposted by Matt Johansen; quoted in [HN](https://news.ycombinator.com/item?id=50133401) and by [Carlos Miranda](https://x.com/CarlosMir/status/2111461859471565102)): "unauthorized access to a legacy system that we were in the process of decommissioning. Third party provider keys (eg OpenAI, Anthropic) saved in your workspace may have been exposed." Asks to revoke at the provider and review usage.
- [dax 2:38 PM PT](https://x.com/thdxr/status/2111572618340188393): "this is the OpenCode Console, not OpenCode itself, those keys never come to us" (i.e. keys in the local app).
- Local keys: [OpenCode docs](https://opencode.ai/docs/providers/): `/connect` keys stored in `~/.local/share/opencode/auth.json`. [dax](https://x.com/thdxr/status/2111633979074031801): logging in through opencode defaults to OAuth tokens, not long-lived keys.
- [dax 11:41 AM PT](https://x.com/thdxr/status/2111528031072461114): "my personal accounts are being attacked now too".
- Refunds: [dax 5:01 PM PT](https://x.com/thdxr/status/2111608620441817449) "refunds are already underway"; [dax](https://x.com/thdxr/status/2111826335387578435) reimbursing a user.
- [dax 4:31 PM PT](https://x.com/thdxr/status/2111601065569448378), on a suspended workspace: "not related that's our usual anti fraud / distillation stuff".
- [dax Oct 18 9:13 PM PT](https://x.com/thdxr/status/2112034420366684562): "daybreak was critical (and is now continuously running)".
- Status page [status.dev.opencode.ai](https://status.dev.opencode.ai/) lists Console API ("Dashboard, workspaces, and keys") incidents Oct 17-18 but no breach notice. No blog/postmortem found as of 9:40 PM PT Oct 18.

## Providers
- Anthropic, [Lydia Hallie (Claude Code @AnthropicAI), 2:04 PM PT Oct 17](https://x.com/lydiahallie/status/2111563956666110287): "have revoked Claude API keys we believe were affected."
- Google, [Evan Otero (Google DeepMind / AI Studio / Gemini API), 3:53 PM PT](https://x.com/EvanOtero/status/2111591525876474100): "We've blocked exposed API keys"; create new key in AI Studio, delete old, review usage, contact Cloud Billing support.
- OpenAI, [Tibo (Codex & ChatGPT @OpenAI), Oct 18 9:12 PM PT](https://x.com/thsottiaux/status/2112034063934742720): worked with OpenCode to get affected OpenAI API customers "back in business and any credits refunded which would have been drawn in the attack"; plugs Daybreak Blue.
- [OpenAI Daybreak help page](https://help.openai.com/en/articles/20001258-openai-daybreak-trusted-access-for-cyber-overview): Daybreak Blue = "Reduced refusals on supported mainline models ... for verified defensive work", incl. incident response; requires approval.

## User reports (claims, unverified individually)
- [Colin Parsons, 6:36 AM PT Oct 17](https://x.com/colinparsonscom/status/2111451256426250580): OpenAI key "$281", Anthropic "$168", starting 2am ET (11 PM PT Oct 16); keys only used in OpenCode; Discord "filled with bot signups".
- Replies: [Preston Zeller $1700](https://x.com/prestonzeller/status/2111464850748776751), [santi $700](https://x.com/santiayz/status/2111515961321033900), [Alejandro García Iglesias: OpenAI account suspended](https://x.com/aiglesias_/status/2111502768246804921), [Chris Sinco: OpenAI, then Anthropic, then Gemini alert](https://x.com/csinco/status/2111462188775051733), [tuna: 3k bill](https://x.com/tunahorse21/status/2111529235492049196), [Tony Dinh: 1.7k, "Luckily I set a limit"](https://x.com/tdinh_me/status/2111613809014325588), [Max Weinbach: balances drained, Google account limited](https://x.com/mweinbach/status/2111518053662064829).
- [Matt Johansen 8:18 AM PT](https://x.com/mattjay/status/2111476982580211851) and [8:30 AM PT "Confirmed ... Keys stolen"](https://x.com/mattjay/status/2111480005435719885) — first public alert, before OpenCode posted.

## Coverage / analysis
- [The Latent](https://thelatent.co/models/opencode-says-breach-tied-to-distillation-attack-exposed-users-ai-provider-keys): Console stores BYOK keys on its servers per docs; OpenCode "did not explain how it linked the leaked keys to the 'large scale distillation attack.'" Notes US agencies in September accused six Chinese firms of extracting tokens.
- [Cyera](https://www.cyera.com/research/opencode-breach-what-happened-and-how-to-rotate-exposed-ai-api-keys): unknown how attackers got in, how keys were stored, whether misused; "No one has publicly attributed the OpenCode attack."; revoke at provider, go to dashboards directly (phishing), check usage from Oct 16, hard caps; Console budgets don't cap direct provider use.
- [AiLookout](https://ailookout.news/blog/opencode-breach-exposed-saved-ai-provider-keys-console-users-distillation-attack/), [Rogue Security](https://www.rogue.security/blog/opencode-console-breach-api-key-custody) (gateway-only limits can't stop a copied raw key), [agentbeam claimed-vs-verified](https://www.agentbeam.com/blog/opencode-console-breach-provider-keys-claimed-vs-verified), [safeguard.sh rotation steps](https://safeguard.sh/resources/blog/opencode-console-breach-provider-api-keys).
- HN: [944-point thread](https://news.ycombinator.com/item?id=50133401) (Console ≠ CLI confusion; "how can a distillation attack leak credentials"; some users say keys revoked mid-session), [second thread](https://news.ycombinator.com/item?id=50139083).
- Distillation background: [Anthropic Sept 2026 threat report](https://www.anthropic.com/threat-intelligence-report-september-2026) — stolen AI keys give attackers "Loot", "Compute", "Cover"; criminal resellers rotate stolen keys. (Not about OpenCode.)

## What "distillation attack" means here
Distillation = collecting a strong model's outputs to train another model. OpenCode used the label; it has not explained the link. Plausible reading (HN, AiLookout): stolen keys used to pull frontier-model outputs at volume on victims' bills. Alternative reading (HN): key resale. **Unconfirmed either way.** Attribution: none published. Sacks's China line is a general claim about model capability, not an attribution of this attack.

## Coverage check: what most people covered vs missed
| Candidate angle | Coverage | Verdict |
|---|---|---|
| Guardrails refused defenders (Sacks/Curran) | Huge reach, policy fight | Real but secondary; dax got Daybreak Blue within a day and says nobody refused to help |
| "1.4% of users breached, rotate keys" | Widely covered | Necessary, not new |
| **Key custody: the breach was a stored-key problem; protection lived at the provider (spend caps, provider revocation), not in OpenCode** | Under-explained in the viral debate | **Lead** |

**Angle:** The viral fight is about AI guardrails, but the damage came from keys pasted into a hosted console, and the only controls that helped users were the ones at the provider: spend limits, revocation, and refunds.
