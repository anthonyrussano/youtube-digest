---
title: "AI now finds the bugs for free. Your threat model decides whether that helps."
caption: "Maintainer tip: before an AI scanner touches your repo, write a threat_model.md that says where untrusted input enters and how you rate severity. OpenSSH and Valkey already did..."
edition: "2026-10-20"
lead_source: "https://red.anthropic.com/oss-scanner"
---
curl just fixed [one of its worst vulnerabilities in a long time](https://daniel.haxx.se/blog/2026/10/14/a-uaf-turned-rce/). An AI scanner found it.

Six days later, curl announced it is [moving low and medium vulnerability reports into public GitHub issues](https://daniel.haxx.se/blog/2026/10/20/do-minor-curl-vulnerabilities-in-the-open/), because a flood of vulnerability reports, many of them found by AI, is wearing out its maintainers.

Both things are true at once. That is the real story behind Anthropic's new **OSS Scanner**.

## What launched

[OSS Scanner](https://x.com/ClaudeDevs/status/2112299602510749992) gives critical open-source projects **free, periodic vulnerability scans** from Anthropic's strongest models. Each finding comes with a **proof of concept** (a small program that proves the bug is real) and a patch where possible.

In its first 11 days, [about 650 projects applied and 114 were accepted](https://x.com/thepunit/status/2112267286237384738). The scans have already reported **77 critical and 803 high findings**.

Note the fine print: those are **model-rated**. The model chose the severity. No human has checked these reports.

## How it works

A maintainer opens a pull request that adds a small config file to [Anthropic's enrollment repo](https://github.com/anthropics/oss-scanner). It must include a **Dockerfile** that builds the whole project with every dependency, because the audit runs **with the Internet cut off**.

Then agents audit the code, double-check each bug, trace its root cause and propose a patch. Reports arrive by email. Most of the first ones [bounced, likely flagged as malware](https://x.com/thepunit/status/2112269363835490450) because of the exploit code inside, so now every report is encrypted.

[[IMG: /workspace/2026-10-20-1-oss-scanner-flow.png | Flow diagram of OSS Scanner: a maintainer's pull request, a human check, an online Docker build, an offline audit by Claude agents guided by the project's threat_model.md, then a proof of concept, patch and encrypted email with no 90-day disclosure clock]]

There is **no 90-day disclosure clock** on these reports, [Anthropic says](https://red.anthropic.com/oss-scanner), because nobody at Anthropic has reviewed them yet.

## The part most coverage skipped

Finding bugs is no longer the hard part. **Checking them is.**

Over six months, Anthropic's models found [over 29,000 candidate vulnerabilities](https://www.anthropic.com/research/launching-opt-in-vuln-finding-service-for-open-source). Its people could review about 6,000. Nearly 5,000 went out unreviewed, because maintainers asked for everything.

[[IMG: /workspace/2026-10-20-2-found-vs-reviewed.png | Column chart: over 29,000 candidate vulnerabilities found by Anthropic's models in six months, about 6,000 reviewed by humans, and nearly 5,000 sent unreviewed at maintainers' request]]

The quality is real. When expert testers checked 97 high and critical findings, **85 met Anthropic's bar** and only one was a false positive. But maintainers also said severity ratings can be **inflated**, or that the scanner **misunderstood the project's threat model**.

curl's maintainer Daniel Stenberg sees the volume problem from the other side. He says [over 90% of submissions turn out to be below HIGH](https://daniel.haxx.se/blog/2026/10/20/do-minor-curl-vulnerabilities-in-the-open/), and many AI-found reports are strange option combinations unlikely to ever be used in the real world.

## The lever you control: threat_model.md

OSS Scanner reads one optional file before it starts: **threat_model.md**. It is plain text. You write down where untrusted input enters, which code matters, how to run it, **how you rate severity**, and what to leave alone.

Big projects have already written theirs, and they are worth reading:

- [OpenSSH](https://github.com/anthropics/oss-scanner/blob/main/projects/openssh/threat_model.md): any buffer overflow or use-after-free is **high at minimum**. A controlled overflow that may lead to remote code execution is critical.
- [Valkey](https://github.com/anthropics/oss-scanner/blob/main/projects/valkey/threat_model.md): every finding needs a **CVSS score with its vector**, and medium and low bugs are fixed publicly.
- [Argo CD](https://github.com/anthropics/oss-scanner/blob/main/projects/argo-cd/threat_model.md): it names the attackers to consider and who is fully trusted, like admins who can edit its config.

[[IMG: /workspace/2026-10-20-3-threat-model.png | Screenshot of the threat_model.md template in Anthropic's oss-scanner repository on GitHub, with sections for where untrusted input enters, components that matter, how to exercise the code, how you rate severity, and anything to leave alone]]

That one file is how a maintainer turns a firehose into a queue.

## The takeaway

You don't need to enroll to use this idea. Any AI agent you ask for a security review guesses your threat model unless you write it down.

So add a **threat_model.md** with a severity rubric, and make your project **build offline from one Dockerfile**. Your next AI bug report gets cheaper to check either way.

Would you let a model rate severity for your project, or does triage stay human?

## Also this cycle

- Claude worked out where the NIST elliptic curve seeds came from: [C's old lrand48 generator seeded with a Unix timestamp](https://www.anthropic.com/research/ecdsa-curve-origins), which makes backdoor theories much less plausible.
- An audit of Terminal Bench 4 found [60 of 65 tasks had at least one issue and 44 could be passed by cheating](https://x.com/chem_safety/status/2112212879734947937).
- Coinbase's Lincoln Murr says x402 aimed for 25,000 agent transactions by year end, and by then [one was happening every 17 seconds](https://www.youtube.com/watch?v=f_HwzoYrZ7s&t=202s).
- Meta published a report on [Muse Glimmer, a 30B open-weight agent model](https://x.com/AIatMeta/status/2112265822274302066) that runs at 4-bit on a single consumer GPU.
- DeepSeek open-sourced [DeepInfer](https://github.com/deepseek-ai/DeepInfer), the inference engine behind DeepSeek-V4.1-Flash, with deterministic sampling; the KV cache and load balancing are not included.
- [vLLM v0.32.0](https://x.com/vllm_project/status/2111814711956168760) shipped 814 commits, three security fixes and up to 85% more requests per second with multi-API workers.
