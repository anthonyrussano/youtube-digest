---
title: "NatWest's AI judge correlates 0.04, AMD eyes 17 billion dollars, and Devin runs 9 cloud Macs"
caption: "Agent eval tip: check your LLM judge's correlation with human scores, not only its average error, and pick a judge from another model family. Meanwhile Devin built and tested nine iPhone Duo apps on nine cloud Macs at once..."
edition: "2026-11-04"
lead_source: "https://www.youtube.com/watch?v=5UgnatzpZ9E"
---
NatWest's LLM judge missed human scores by only about 0.2 on average, yet [its correlation with those humans was 0.04](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=600s). Meanwhile Nader Dabit [had nine Macs building and testing nine iPhone Duo apps at once, and none of them were physical](https://x.com/dabit3/status/2117817857706746223).

Here is what happened in AI and DevOps this cycle.

NatWest is moving its assistant Cora from scripts to AI agents, and lead AI engineer Jonathan Osborne says building the agent was the easy part. The bank has [about 19 million retail customers](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=49s), Cora handles [about 100,000 conversations a day](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=61s), and roughly a third of its journeys are moving to AI answers and agents that can make a payment or change an address. His point: [the scary part isn't the model, it's the blast radius](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=110s). A wrong answer about one customer's mortgage is real money, not a bug ticket.

So the first move was to shrink what the model ever sees. NatWest's [routing funnel](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=300s) filters out button presses, then runs plain rules with no ML, then a gated LLM step, then an intent classifier that is a plain neural network (an MLP, not an LLM), then policy rules. Fewer than half of all turns ever reach a language model. Every routing decision carries a code for the auditors, and the rules keep working if the model is down.

[[IMG: /workspace/2026-11-04-1-natwest-funnel.png | Slide from "Building the AI Agent Is Easy. Proving It's Safe Isn't" (AI Engineer, YouTube): NatWest's routing funnel, where fewer than half of customer turns reach a model]]

The part most teams skip is measuring. Three human scorers rated 111 conversations, and [one 83% pass rate hid 97% on happy paths and 43% when customers changed topic](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=490s). The humans agreed with each other only 64% of the time on what the customer wanted, so "match the human" can't be the goal. Then came the LLM judge on a complaints agent, scored against about 14,000 human-labeled cases. Its average error looked fine. [Its correlation was 0.04](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=600s), because a judge that gives almost everything about 0.97 cannot tell good answers from bad. Swapping only the judge model [cut the headroom over the same 0.89 pass mark from 0.08 to 0.02](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=640s). The fix: treat the judge as config, and [pick it from a different model family than the agent](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=654s).

[[IMG: /workspace/2026-11-04-2-natwest-broken-judge.png | Slide from "Building the AI Agent Is Easy. Proving It's Safe Isn't" (AI Engineer, YouTube): an LLM judge pinned near 0.97 versus wider human scores, correlation 0.04]]

Shipping follows the same logic. NatWest scores [a 5% random sample plus every handoff, failure, long chat and angry customer](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=680s), runs offline scoring every four hours and blocks merges at a regression gate. New backends run in shadow first, classifying real traffic while the old system still answers, then go live [brand by brand, with a rollback that takes seconds](https://www.youtube.com/watch?v=5UgnatzpZ9E&t=908s). If your eval dashboard shows one number, NatWest's lesson is that it's probably hiding the one that matters.

[[IMG: /workspace/2026-11-04-3-natwest-safety-spine.png | Diagram: NatWest's route, score and ship steps for customer-facing agents, drawn from the talk's slides]]

Red Hat's Derek Carr says agent code is now [sometimes written live on production systems and run without ever being reviewed](https://www.youtube.com/watch?v=v489tFAlrHY&t=151s). His answer, built with NVIDIA, is OpenShell: [network policy that is deny by default and can grow while the agent runs](https://www.youtube.com/watch?v=v489tFAlrHY&t=593s), so a novel request is blocked or held for your approval. He would keep the Slack-facing gateway in a trusted zone and [hand only the untrusted tool step to a confined sandbox](https://www.youtube.com/watch?v=v489tFAlrHY&t=716s). NVIDIA's docs add that a blocked agent can [propose a narrow rule that waits for human review](https://docs.nvidia.com/openshell/how-it-works/policies/advisor), which turns denials into a reviewable to-do list.

[[IMG: /workspace/2026-11-04-4-openshell-trust-zones.png | Diagram: trusted gateway and harness versus an OpenShell sandbox that denies egress by default and turns denials into proposed rules, from Red Hat's video and NVIDIA's OpenShell docs]]

AMD grew Q3 revenue 45% to 13.4 billion dollars, with [data center sales up 97% to 8.5 billion](https://www.theregister.com/systems/2026/11/04/amd-on-track-to-overtake-intel-as-biggest-x86-outfit/5307448). It expects about 17 billion next quarter, against Intel's guidance of 15 to 16 billion. Lisa Su says the company will grow more than 80% in 2027. If the guidance holds, AMD would out-earn Intel on chip sales, possibly for the first time, and Intel would stay bigger overall only because of its foundry business.

[[IMG: /workspace/2026-11-04-5-amd-intel-guidance.png | Chart: AMD's Q3 2026 revenue of 13.4 billion dollars and next-quarter guidance of about 17 billion, against Intel's 15 to 16 billion guidance, per The Register]]

Nader Dabit of Cognition calls [Devin "Lambda for engineering work"](https://x.com/dabit3/status/2117817857706746223): you send a task, and an agent plus its computer exist only while the job runs. With your own AWS credentials, those cloud agents run in your account, on EC2 for builds or GPU boxes for games and ML. He works on Devin, so read it as a pitch, but nine iPhone apps tested with zero Macs on the desk is a real shift in what a laptop is for.

Langfuse's Doneyli De Jesus saw the same lesson at one of the top five banks, which told him [it certifies applications, not models](https://www.youtube.com/watch?v=-uBABM2AuFg&t=181s). Its earnings-call agent grounded 97% of its answers but got numbers right only about 60% of the time, until the team [gave it a Python calculate tool and accuracy rose to about 95%](https://www.youtube.com/watch?v=-uBABM2AuFg&t=664s). And [a zero on regulatory compliance shuts the gate](https://www.youtube.com/watch?v=-uBABM2AuFg&t=919s) no matter how good the average looks.

Anthropic's Addy Osmani says a two-sentence rule in Claude Code's Opus 5.5 prompt, meant to stop copies of existing games, [also blocked people who named a game to describe the mechanics they wanted](https://x.com/addyosmani/status/2117848568535106001). Version 2.1.317 fixes it: name a game and Claude builds an original one in that genre, ask for a copy and it offers something similar. If Claude turns down your own project, the team wants to hear about it.

Vercel CLI now ships [`vercel doctor`](https://vercel.com/changelog/vercel-cli-now-diagnoses-setup-problems-with-vercel-doctor), which checks five things: your CLI install, login and team, project link, `vercel.json` and active incidents, and prints the fix command for each problem. It never prompts or logs in, so a coding agent can run it before guessing, and `--json` gives the results as data. Guillermo Rauch's advice to every tool builder: [ship doctor subcommands in your CLIs](https://x.com/rauchg/status/2117802827519250568).

Joe Harris of Alloy says a robotics field engineer [maxes out at 4 to 5 sites but needs to cover 15 to 20](https://x.com/_joe_harris_/status/2117817324313149773). His playbook: an agent triages every ticket first, one team with 50 to 125 tickets a week sends only 5 to 10 to engineering, and every run lands as one MCAP file in one bucket. He claims SwarmFarm cut ticket time from 1 to 2 hours to about 10 minutes with Alloy. It's a vendor's pitch, but the metric he pushes, robots per support person, is the one to watch.

Vercel Labs' agent-desktop gives a coding agent [computer use without screenshots](https://x.com/RoundtableSpace/status/2117825412462240136). It reads the operating system's accessibility tree on macOS, Windows and Linux and returns [a ref for every button and field](https://github.com/vercel-labs/agent-desktop), and if the screen changes, a stale ref fails loudly instead of clicking the wrong thing. The tool has no model inside; your agent runs the loop.

A few quick ones.

Georges Petrov's Screenplay lets your agent [film a polished product demo from one prompt](https://x.com/RoundtableSpace/status/2117802763262591481). The agent writes a JSON scenario, a dry run catches broken selectors before filming, and [the default output is 1920x1080 at 30 frames per second](https://github.com/gmpetrov/agent-screenplay), with no model key needed.

Which one are you trying first: a correlation check on your LLM judge, an OpenShell-style sandbox for agent tool calls, or a doctor command your agents can run? Tell me in the replies.

That's the cycle. Go check your judge's spread, hand your agent a doctor command, and see you tomorrow.
