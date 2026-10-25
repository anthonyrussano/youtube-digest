---
title: "Copilot reviews 1 in 5 PRs, BugBot's 44,000 rules, and Tailscale's allow-all default"
caption: "Tailscale tip: replace the default allow-all policy with restrictive grants, then look up your home IP on Shodan to see what's exposed. Meanwhile agents write 741% more code but ship only 30% faster..."
edition: "2026-10-24-1706"
lead_source: "https://www.youtube.com/watch?v=kspZP5BgkEU&t=178s"
---
Developers who turn on autonomous coding agents write [741% more code, and ship only 30% faster](https://www.youtube.com/watch?v=kspZP5BgkEU&t=178s). Laurie Voss, the npm co-founder who now runs developer relations at Arize AI, says the missing speed is stuck in one place: humans reading diffs, because review accuracy [collapses after about 450 lines an hour](https://www.youtube.com/watch?v=kspZP5BgkEU&t=219s).

[[IMG: /workspace/2026-10-24-1706-1-code-vs-speed.png | Slide "Coding 8x faster to ship 1.3x faster" listing NBER, LinearB, Cisco/SmartBear, Faros and Anthropic figures, from Laurie Voss's talk "AI Writes the Code. So What's Left for Engineers?" (AI Engineer, YouTube)]]

The slide behind that line is worth a screenshot of its own. The 741% figure comes from an NBER study of [more than 100,000 GitHub developers](https://www.youtube.com/watch?v=kspZP5BgkEU&t=190s). LinearB's data on 8 million pull requests says agent-written PRs wait 4.6 times longer for a reviewer, and Faros, tracking 22,000 developers, found time in review up 440%, incidents per PR up 240%, and PRs merged with no review at all up 31%. Every one of those numbers points at the same queue: the human who has to say yes.

Here is what happened in AI and DevOps this cycle.

Voss's AI Engineer talk walks through who is trying to make review run at agent speed. He says GitHub Copilot now does [more than one in five code reviews on GitHub](https://www.youtube.com/watch?v=kspZP5BgkEU&t=280s), and can even be given approval rights. But when four AI reviewers checked the same code, they all found [real bugs and not a single one in common](https://www.youtube.com/watch?v=kspZP5BgkEU&t=301s). Dex Horthy spent six months telling people to stop reading code, then [went on stage to say it was a disaster](https://www.youtube.com/watch?v=kspZP5BgkEU&t=343s), and after a string of outages Amazon now has [senior engineers sign off on agent-written code](https://www.youtube.com/watch?v=kspZP5BgkEU&t=384s). His takeaway is to run several reviewers, never just one.

The sharpest number in the talk comes from Cognition, the team behind Devin. Agents pass about 80% of a coding benchmark's tests, but when the question becomes "would a maintainer merge this PR?", the success rate [drops to 54%](https://www.youtube.com/watch?v=kspZP5BgkEU&t=425s). The gap is style, side effects and history that live in a maintainer's head. Voss points to Cursor's BugBot, which turns every thumbs-down from your team into a rule and now holds [about 44,000 of them](https://www.youtube.com/watch?v=kspZP5BgkEU&t=931s). That's what it looks like when the maintainer's taste finally gets written down.

[[IMG: /workspace/2026-10-24-1706-2-merge-bench.png | Slide "Agents can pass 80% of a coding benchmark's tests, but only 54% if those same PRs are judged by a maintainer", from Laurie Voss's talk (AI Engineer, YouTube)]]

So what's left for people? Voss bets it's deciding what to build and what "good" means, and calls the job the product engineer. He cites openings for customer-facing engineers [growing 800% in the first nine months of 2025](https://www.youtube.com/watch?v=kspZP5BgkEU&t=1051s) at an average of about $240,000. Meanwhile employment for engineers aged 22 to 25 is [falling fast](https://www.youtube.com/watch?v=kspZP5BgkEU&t=1255s), and Google's APM program trains about 50 people a year when he says [the industry needs 10,000](https://www.youtube.com/watch?v=kspZP5BgkEU&t=1296s). His advice for leads is concrete: isolate the critical code and review only that, then [measure how often review comments get acted on](https://www.youtube.com/watch?v=kspZP5BgkEU&t=1544s), not how much code you wrote.

Apollo's Daily Spark says the payoff hasn't shown up anywhere else yet. [Revenue per worker and profit margins are rising for the Mag 7 but flat for the S&P 493](https://www.apollo.com/wealth/insights-news/insights/daily-spark/no-signs-of-ai-payoff-outside-the-tech-sector), and there's still no sign of AI lifting productivity. Apollo argues mainstream companies are starting to treat token spending as a cost center rather than growth, which is the same gap Voss sees between more code and more shipped.

Alain Meier's weekend homework is a [two-hour personal opsec list](https://x.com/alain/status/2114086821722526144) you can hand to your agent. Look up your home IP on Shodan or Censys for exposed NAS boxes, cameras and dev servers, move IoT gear to a guest network, and replace Tailscale's default allow-all policy with restrictive grants. Then put a hardware key on your primary email, delete the other MFA methods and freeze your credit. Your homelab is only as safe as the camera nobody updated.

Guillermo Rauch says the [#0 skill he hires for](https://x.com/rauchg/status/2114085432749347086) is knowing when you're over-guiding the AI and when you're under-guiding it. Sometimes it knows better than you, and sometimes it misses context or brings the wrong biases. Lauren (poteto) replied that she covers exactly this in [her pstack guide](https://x.com/poteto/status/2114095305910280363), so there's a longer read if you want one.

Brian Roemmele described how he runs [one long-lived coordinator agent on top of HarnessRouter](https://x.com/BrianRoemmele/status/2114128789349490731). It's an open-source Apache-2.0 project that exposes one OpenAI Responses-compatible API to drive Codex, Claude Code, Hermes, Pi and about two dozen other agent harnesses in their own runtimes. It runs as one docker container on a machine you control, so switching harnesses is a metadata change instead of a rewrite.

Hermes Release Watch showed off [Hermes Projects](https://x.com/HermesWatcher/status/2114084529673752970), which tackles the "six folders, three repos, no clue where anything lives" problem. One command groups a web repo, an API repo and a docs folder into a single named project without moving a file. Your agent then gets a clear scope, and the project's rules live in one place.

Vas at Varick argues [almost nobody is doing real AI transformation](https://x.com/vasuman/status/2114092422112432553). By his account most "applied AI" firms sell skill files, a few Claude jobs and prompting workshops. The real thing, he says, is redesigning whole departments around background agents, with human review, audit trails and evals built in. That's a hiring pitch, but it lines up neatly with Apollo's flat S&P 493 chart.

One last one. Corey Ganim's [seven takeaways from 48 hours with 25 founders](https://x.com/coreyganim/status/2114124810322379096) include an anecdote of a founder going from $1,000 in monthly revenue to $57,000 by rebuilding his site for AI search with coding agents. The more durable tip is to keep your context in one central knowledge base any agent can read, so you never get locked into a single agent.

What's the one piece of review you'd never hand to an agent? Tell me below.

That's the cycle. Review less code, review the right code, and go check what Shodan knows about your house. See you next time.
