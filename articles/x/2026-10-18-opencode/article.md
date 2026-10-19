---
title: "The OpenCode breach wasn't a guardrails story. It was a key-custody story"
caption: "Dev tip: if you ever pasted an OpenAI, Anthropic or Gemini key into a hosted AI coding tool, revoke it at the provider (not in the tool), make a new key per tool and set a hard spend cap..."
edition: "2026-10-18-opencode"
lead_source: "https://x.com/opencode/status/2111519637049319818"
---
David Sacks says the OpenCode breach shows that **AI guardrails backfired**.

[His post](https://x.com/DavidSacks/status/2111867605388493282) says frontier models refused to analyze the attack "because the payloads tripped safety filters."

That part happened. But it is not what cost people money.

What cost people money was simpler: **API keys saved in a hosted dashboard**.

## What OpenCode confirmed

OpenCode is a popular open-source coding agent. It also runs a hosted service called **OpenCode Console**.

In Console, a team can paste in its own OpenAI, Anthropic or Google key ("bring your own key"). Console then calls those models for you.

On Oct 17, OpenCode said [a breach "last night"](https://x.com/opencode/status/2111519637049319818) hit **1.4% of Console users**, all of them emailed. Only users "who had external providers linked" were affected. The incident is "ongoing."

The email, [quoted on Hacker News](https://news.ycombinator.com/item?id=50133401), says someone got into **"a legacy system that we were in the process of decommissioning."** Saved provider keys "may have been exposed."

If you only run OpenCode on your laptop, keys you add there are [stored in a local file](https://opencode.ai/docs/providers/). OpenCode's dax Raad [says](https://x.com/thdxr/status/2111572618340188393) "those keys never come to us."

[[IMG: img/normal-flow.png | Diagram: a developer's OpenCode app keeps keys in a local auth.json and calls providers directly, while keys pasted into the hosted OpenCode Console are saved there and used by its gateway to call Anthropic, OpenAI and Google.]]

## How it unfolded (PT)

**Oct 17, 6:36 AM:** Colin Parsons [reports](https://x.com/colinparsonscom/status/2111451256426250580) $281 on his OpenAI key and $168 on Anthropic overnight, keys he used only in OpenCode.

**8:30 AM:** security writer Matt Johansen [posts the breach email](https://x.com/mattjay/status/2111480005435719885).

**10:56 AM:** OpenCode goes public.

**2:04 PM:** Anthropic's Lydia Hallie [says](https://x.com/lydiahallie/status/2111563956666110287) it revoked Claude keys it believes were affected.

**3:53 PM:** Google's Evan Otero [says](https://x.com/EvanOtero/status/2111591525876474100) exposed Gemini keys are blocked.

**5:01 PM:** dax [says](https://x.com/thdxr/status/2111608620441817449) refunds are "already underway."

**Oct 18, 9:12 PM:** OpenAI's Tibo [says](https://x.com/thsottiaux/status/2112034063934742720) affected OpenAI customers had credits "drawn in the attack" refunded.

## What "distillation" means here

**Distillation** means collecting a strong model's answers to train another model.

OpenCode called this "a large scale distillation attack." It has **not explained the link**. The Latent [notes](https://thelatent.co/models/opencode-says-breach-tied-to-distillation-attack-exposed-users-ai-provider-keys) OpenCode did not say how the leaked keys tie to distillation.

The likely reading: stolen keys used to pull frontier-model output at volume, on the victims' bills. Users report charges like [$700](https://x.com/santiayz/status/2111515961321033900) and [$1,700](https://x.com/prestonzeller/status/2111464850748776751), and [one](https://x.com/tunahorse21/status/2111529235492049196) a "3k" bill. Those are **user claims**.

**Nobody has publicly attributed the attack**, as [Cyera notes](https://www.cyera.com/research/opencode-breach-what-happened-and-how-to-rotate-exposed-ai-api-keys). Sacks's line about Chinese models is about capability. It does not name the attacker.

[[IMG: img/attack-path.png | Diagram: an unidentified attacker reached OpenCode's legacy Console system, where saved provider keys for 1.4% of Console users may have been exposed; user reports say the keys were used to call models; the distillation link and the entry method are unconfirmed.]]

## Sacks's point, fairly

The refusals were real. dax [wrote](https://x.com/thdxr/status/2111831348336091179) the models "did quite a bit and then started refusing." Hugging Face [hit the same wall](https://huggingface.co/blog/security-incident-july-2026) in July.

But dax [also wrote](https://x.com/thdxr/status/2111838044940550257) they had applied for OpenAI's **Daybreak Blue** days earlier, got approved the day before, and "i don't think anyone is refusing to help us."

[Daybreak Blue](https://help.openai.com/en/articles/20001258-openai-daybreak-trusted-access-for-cyber-overview) is OpenAI's vetted tier with **fewer refusals for incident response**.

So the guardrail fight is real. It just isn't why keys leaked.

## The part most people missed

**A key saved anywhere works everywhere.**

Deleting it from a dashboard doesn't stop someone who copied it. Console budgets only cap spend through OpenCode, [Cyera says](https://www.cyera.com/research/opencode-breach-what-happened-and-how-to-rotate-exposed-ai-api-keys), not direct use.

The controls that helped sat at the provider. Revocation. Refunds. And spend limits: one user [lost 1.7k](https://x.com/tdinh_me/status/2111613809014325588) and wrote "Luckily I set a limit."

## What to do now

- **Revoke** any key you saved in a hosted AI tool, at the provider's dashboard. Go there directly, not via email links.
- **Make a new key per tool**, so one leak stays small.
- **Set a hard spend cap and an alert** at each provider.
- **Check usage since Oct 16** for spikes or odd models.
- Security teams: **apply for defender access before an incident**.

[[IMG: img/response.png | Diagram: what vendors did (OpenCode emailed users and started refunds, Anthropic revoked Claude keys, Google blocked Gemini keys, OpenAI refunded credits, OpenCode got Daybreak Blue) and four steps for you: revoke at the provider, new key per tool, hard spend cap plus alert, check usage since Oct 16.]]

**Takeaway:** treat every AI key like a production password. Its real guardrail is the cap you set at the provider.

Where do your AI keys live right now, and do they have a cap?

## Sources

- [OpenCode's breach post](https://x.com/opencode/status/2111519637049319818)
- [David Sacks's post](https://x.com/DavidSacks/status/2111867605388493282) and [dax on refusals and Daybreak](https://x.com/thdxr/status/2111838044940550257)
- [Anthropic](https://x.com/lydiahallie/status/2111563956666110287), [Google](https://x.com/EvanOtero/status/2111591525876474100) and [OpenAI](https://x.com/thsottiaux/status/2112034063934742720) responses
- [The Latent's report](https://thelatent.co/models/opencode-says-breach-tied-to-distillation-attack-exposed-users-ai-provider-keys) and [Cyera's rotation guide](https://www.cyera.com/research/opencode-breach-what-happened-and-how-to-rotate-exposed-ai-api-keys)
- [Hacker News thread](https://news.ycombinator.com/item?id=50133401)
- [Hugging Face's July incident disclosure](https://huggingface.co/blog/security-incident-july-2026)
