---
title: "NatWest's judge correlates 0.04, AMD eyes 17 billion, and Devin runs nine cloud Macs"
dek: "A judge that misses humans by only 0.2 can still be useless, and a bank's agent can still reach fewer than half its customers' turns."
---
NatWest's LLM judge missed human scores by only about 0.2 on average, yet [its correlation with those humans was 0.04](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=600s). Meanwhile Nader Dabit [had nine Macs building and testing nine iPhone Duo apps at once, and none of them were physical](https://x.com/dabit3/status/2117817857706746223).

Here is what happened in AI and DevOps this cycle.

NatWest lead AI engineer Jonathan Osborne says building the agent was the easy part of moving the Cora assistant, which serves [about 100,000 conversations a day for about 19 million customers](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=49s), from scripts to AI. The bank first shrank what the model sees: a [routing funnel](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=300s) of button filters, plain rules, a gated LLM step, an MLP intent classifier and policy rules, so fewer than half of all turns ever reach a language model. Every routing decision carries a code for auditors, and the rules keep working if the model is down. [The scary part isn't the model, it's the blast radius](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=110s).

The same talk shows how a score can lie. Three human scorers rated 111 conversations, and [one 83% pass rate hid 97% on happy paths and 43% on topic changes](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=490s), while the humans agreed with each other only 64% of the time on what customers wanted. On a complaints agent with about 14,000 human-labeled cases, the LLM judge scored almost everything near 0.97, and swapping only the judge model [cut the headroom over the same 0.89 pass mark from 0.08 to 0.02](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=640s). NatWest now [picks its judge from a different model family than the agent](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=654s), samples [5% of traffic plus every handoff, failure and angry customer](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=680s), and ships [shadow first, then brand by brand](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=908s).

AMD grew Q3 revenue 45% to 13.4 billion dollars, with [data center sales up 97% to 8.5 billion](https://www.theregister.com/systems/2026/11/04/amd-on-track-to-overtake-intel-as-biggest-x86-outfit/5307448). It expects about 17 billion next quarter, against Intel's guidance of 15 to 16 billion, and Lisa Su says the company will grow more than 80% in 2027. If that holds, AMD would out-earn Intel on chip sales, possibly for the first time.

Red Hat's Derek Carr says agent code is now [sometimes written live on production systems and run without ever being reviewed](https://www.youtube.com/watch?v=v489tFAlrHY&t=151s). OpenShell, the sandbox he worked on with NVIDIA, makes [network policy deny by default and lets it grow while the agent runs](https://www.youtube.com/watch?v=v489tFAlrHY&t=593s), so a novel request is blocked or held for approval. He would keep the Slack-facing gateway in a trusted zone and [hand only the untrusted tool step to a confined sandbox](https://www.youtube.com/watch?v=v489tFAlrHY&t=716s). Shared agents that several people use at once can even [de-duplicate the token bill](https://www.youtube.com/watch?v=v489tFAlrHY&t=863s).

Nader Dabit of Cognition calls [Devin "Lambda for engineering work"](https://x.com/dabit3/status/2117817857706746223): an agent and its computer exist only while the job runs, and with your own AWS credentials they run in your account, on EC2 for builds or GPU boxes for games and ML. He works on Devin, so it's a pitch, but nine iPhone apps tested with zero Macs on the desk changes what a laptop is for.

Anthropic's Addy Osmani says a short rule in Claude Code's Opus 5.5 prompt, meant to stop copies of existing games, [also blocked people who named a game to describe the mechanics they wanted](https://x.com/addyosmani/status/2117848568535106001). Version 2.1.317 fixes it: name a game and Claude builds an original one in that genre; ask for a copy and it offers something similar.

Guillermo Rauch wants every tool builder to [ship doctor subcommands in their CLIs](https://x.com/rauchg/status/2117802827519250568), starting with `vercel doctor`, which checks five things from your CLI install to active incidents. It never prompts or logs in, so a coding agent can run it before guessing at a fix.

Joe Harris of Alloy says a robotics field engineer [maxes out at 4 to 5 sites but needs to cover 15 to 20](https://x.com/_joe_harris_/status/2117817324313149773). His playbook has an agent triage every ticket first, so one team with 50 to 125 tickets a week sends only 5 to 10 to engineering. It's a vendor's pitch, but robots per support person is the number that decides whether a fleet scales.

Vercel Labs' agent-desktop gives a coding agent [computer use without screenshots](https://x.com/RoundtableSpace/status/2117825412462240136) by reading the accessibility tree on macOS, Windows and Linux, so the agent clicks a named button instead of a pixel. It installs with one npm command and has no model inside; your agent runs the loop.

Someone built Screenplay so your agent can [film a polished product demo from one prompt](https://x.com/RoundtableSpace/status/2117802763262591481): it explores your site or desktop app, writes the scenario and returns an MP4 with a smooth cursor, auto zooms and captions. It needs no model key, because your agent does the thinking.

Prefrontal AI's Latent Sparse Attention, [relayed for Qwen3.8-27B](https://x.com/Oluwaphilemon1/status/2117812727301259642), reportedly makes single-layer attention prefill 72.4x faster at context windows reaching 10 million tokens. The developers say ordinary sparse attention spends about 98% of its time deciding which tokens to examine, which is the step LSA attacks.

That's the cycle. Go check your judge's spread, hand your agent a doctor command, and see you tomorrow.
