---
title: "Blogbot drafts 85-90% of a post, a bedtime app ships in 4 hours, and Claude Code runs 3 models"
caption: "Agent tip: put your team's writing rules behind a Slack bot that drafts 85-90% of a post, then make a human sign every line. Meanwhile one dad built his toddlers a story app in four hours..."
edition: "2026-11-01-1711"
lead_source: "https://www.youtube.com/watch?v=1et3Lb_KLQo&t=319s"
---
WorkOS engineer Zack Proser built a Slack bot that hands colleagues [a blog draft 85 to 90% of the way done](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=319s). Then he built a second one for an audience of exactly two: [his toddlers, in four hours](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=858s).

Here is what happened in AI and DevOps this cycle.

Zack Proser, on the applied AI team at WorkOS, says what worries him isn't AI slop but [the stories that never get told](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=195s) because talented colleagues decide they aren't writers. So he packed 15 years of writing habits into [Blogbot, a system built on Cloudflare](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=256s) that anyone can call from Slack with a transcript and a request. It pulls in the meeting recordings, event photos and Slack chatter on its own, has [a tool to ask a human to confirm facts and an image endpoint styled after the design team](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=359s), and still [needs a person to read every line and put their name on it](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=402s). The pattern he's selling is a simple front end over a complicated system, which anyone with a repeatable craft could copy.

[[IMG: /workspace/2026-11-01-1711-2-blogbot.png | Zack Proser's slide showing a colleague asking Blog Bot in Slack to turn an event transcript into an editorial recap]]

Proser's answer to readers who now [read every sentence "with a flinch"](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=586s) is a blacksmith's metaphor: he's the spark that picks the story, the bellows that keeps shaping the draft, and [the quench that seals it and says publish](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=686s). He compares writing a post by hand with [two and a half to three hours and 14 rounds with an LLM](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=741s) and argues the reader can't tell the difference. His test for both is the same four questions: [is it true, is it useful, is it beautiful, and does it help anybody else](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=774s).

[[IMG: /workspace/2026-11-01-1711-1-rubric.png | Zack Proser's slide: Would I publish it? Is it true? Is it useful? Is it beautiful? Does it help anyone?]]

Then Proser shrank the audience to two. He built a bedtime-story app with [Opus 5.5 on extra-high effort in four hours](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=858s) that reads his toddlers' photos from the day and turns them into a narrated, animated story starring them. The first feature he added after launch was [real-time voice control, so "again, again, again" replays it](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=916s), and he says the kids ask for a repeat about [three times per story](https://www.youtube.com/watch?v=1et3Lb_KLQo&t=1021s). A tool built for two people used to be a joke; now it's an afternoon.

Obsidian's own CEO has a repo for agents. A curated thread points to [obsidian-skills](https://x.com/imryven/status/2117017504321282498), which teaches Claude Code, Codex and other agents to write notes, bases and canvases in a vault the way Obsidian expects, and lists 10 more projects that add memory and search on top. If your notes are already in Markdown, your agent can now edit them without breaking the app's formats.

A Claude Code setup making the rounds splits one job across three models: [Opus 5.5 for the big calls, Sonnet 5.5 and Haiku 5.5 for the routine work](https://x.com/0xKurro/status/2116990525773390322), so the expensive model's context isn't burned on chores. The account credits the trick to Anthropic, a claim it doesn't source. Even unverified, routing by job size is the cheapest tuning most agent setups haven't done.

Developer poteto wrapped [day 28 of a daily build streak with "tibo's game," made with Grok Bot and Cursor](https://x.com/poteto/status/2117004709198475365), full of easter eggs and, if it works as intended, playable inside X itself. The only cost mentioned is a domain at 5.99 dollars. A month of daily shipping is now a hobby, not a job.

Teknium says he spent the last two weeks on the desktop app, and [one new pull request should make it noticeably nicer for power users](https://x.com/Teknium/status/2117014324149666232) when the next full release lands later this week. He adds there's "still a long way to go." Open agent tools are starting to compete on the boring parts, the app around the model.

Guillermo Rauch made the case to [own your intelligence](https://x.com/rauchg/status/2117000819623243925): local models need to keep spreading, and anyone opposing that "has something to sell you." He concedes the largest models are out of reach on home hardware for now. The more capable small models get, the less of your stack has to rent its brain.

What would you build if the audience was two people? That's the Sunday cycle; see you tomorrow.
