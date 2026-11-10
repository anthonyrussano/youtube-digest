# Check: 2026-11-10 (overnight prep, classic full roundup)

- [x] Body = full edition: cold open with hard numbers (about 900 agents in about four hours), "Meanwhile" contrast, intro line, 14 story paragraphs covering 15 stories (lead in 3 paragraphs, Harvey in 2, a "A few quick ones." paragraph with 5), about 1,250 words of prose (x-article counts ~1,475 incl. markers), no ## sections, no bullets.
- [x] Title: "Harvey hit 900 agents on one bug, Muse Ember costs 80x less than Fable, and Modal cuts RL sync 1000x": three named brands, three numbers, three verbs, Oxford comma, 100 characters, no "$" before a digit, no internal format name. All three numbers are in the sources (Harvey talk 486-492s, Simon Willison's Ember post "80x that price", Modal talk 940s "goes down by a factor of a thousand").
- [x] Caption: "Claude Code tip:" + one action a dev can do today (add the ownership sentence on agent-owned repos, then review the diff), then "Meanwhile" + the most surprising fact (900 agents); 226 characters; ends in "..."; no "$"; no internal format name. Same text in format.txt line 3.
- [x] Lead angle is real and sourced: the Anthropic guide's merge rate is widely quoted; the 1.5x tokens, behavior changes in one try in six to ten, summaries that skip small changes and the "no drive-by refactors" result are in the guide but mostly missing from the coverage found (research.md).
- [x] Closing reply question with three choices from the edition, then a sign-off that calls back two items.
- [x] X-sourced items written like video items: no "on X", no counts, no "posted". Third-party claims attributed (Mollick, Mishra's design is labeled a design, Roccia's report, ARLoop's own benchmark claim, General Intuition's data claims "he says"/"he claims", Snowflake "the company says").
- [x] Greps clean on article.md and draft-report.md: ban list, platform framing ("priced like" and "like any other binary" rewritten so the platform-word grep stays clean), `$<digit>`, headers/bullets/tables.
- [x] draft-report.md: same stories in STYLE.md form (title, contrast dek, cold open, intro, 19 item paragraphs, sign-off; no images, no reply question). A scratch render (temporary id, file deleted right after) passed: 6 videos cited, 6 X posts cited, 0 on the radar. The 6:04 run still renders for real.

## Images (7 inline, each on its own line right after the paragraph that cites it)
1. diagram (pele) `/workspace/2026-11-10-1-cloudflare-audit-phases.png`: six phase names, the three verdicts, architecture.md, coverage-ledger.json, findings.json, REPORT.md, "isolated hunters", "a fresh verifier tries to disprove each finding": all from the repo README (https://github.com/cloudflare/security-audit-skill). numbers_checked: yes.
2. video-frame `/workspace/2026-11-10-2-harvey-900-agents.png`, https://www.youtube.com/watch?v=ktbAVYsAxpk&t=486s, timestamp 486 s, "One alert, nine hundred agents" slide (AI Engineer). Text links the same timestamp. On-slide numbers (~2k tasks Aug 14, ~1.3k by bots, 0 of 27 nodes, 1,000+ failed schedules) are the speaker's; the article uses only ~900 and ~50, which match the transcript.
3. video-frame `/workspace/2026-11-10-3-harvey-fair-queue.png`, https://www.youtube.com/watch?v=ktbAVYsAxpk&t=567s, timestamp 567 s, "Four days later: a fair launch queue" slide. Article quotes 300-task burst and task list p95 1.7 s -> 71 ms from the slide (transcript says "almost 2 seconds to 70 milliseconds"; slide values used).
4. diagram (ferroprint blueprint, the one blueprint this Article) `/workspace/2026-11-10-4-k8s-incident-agent.png`: every box and limit (SNS, SQS buffer/retries/DLQ/dedup/idempotency, Lambda, AgentCore, 10 s / 5 min / 10 calls, OIDC gateway, three read-only MCP servers, Bedrock knowledge base, four outcomes) from https://x.com/livingdevops/status/2120003767277945070. numbers_checked: yes.
5. diagram (pele) `/workspace/2026-11-10-5-modal-sparse-rl.png`: "100x to 1000x sparse" (933s), "about 1000x less data" (940s), hyperscalers and neoclouds (823s, 963s), H100/A100 rollouts (1005-1010s), H200 pools at BF16 and FP8 (1130-1141s). First render listed B200 among rollout GPUs; removed because the talk only names B200 as the trainer/homogeneous case. numbers_checked: yes.
6. video-frame `/workspace/2026-11-10-6-medal-clips.png`, https://www.youtube.com/watch?v=MpkARD5pq-M&t=389s, timestamp 389 s, "Medal is currently the fastest growing company in games" slide; caption on slide "on track to 3 billion uploaded videos per year" matches the transcript. Text link moved from 384s to 389s to match the frame.
7. video-frame `/workspace/2026-11-10-7-gemini-live-pipeline.png`, https://www.youtube.com/watch?v=dNGchf4InU0&t=89s, timestamp 89 s, "The pipeline" slide (Google Cloud Tech): camera, canvas, JPEG, Blob, model. Presenter is in a side panel; the slide is the subject.
Made but not used: a pele flow of Harvey's agent loop (two Harvey slides already carry that story) and a Modal "weight update is super sparse" frame (the diagram covers it).

## Header
NASA iss042e013697 (Expedition 42 Earth observation from the ISS, blue Earth limb), original 4928x3280, public domain, saved to /workspace/x-header-2026-11-10.jpg. Id not in any header field of the post log, nor in any earlier overnight.json header.

## Changes made during check
- Caption quotes changed from escaped straight quotes to curly quotes (the escapes rendered literally).
- "Wang's favorite single stage" -> "If you build only one stage, Wang says" (his actual wording).
- "sister company Medal" -> "It started with Medal" (relationship wording not in the talk).
- Gemini item credited to Google Cloud Tech (the publishing channel), ARLoop to Yuekun Yao and colleagues, the student survey to ThinkYoung.
- Harvey "about 900 in about four hours" now links t=486s next to its slide.
- Dek: replaced a derived "five times" with the guide's own "about half of tries instead of under a tenth".

## Dry run
`./run.sh x-article 2026-11-10 --dry-run` -> FORMAT: roundup, SOURCE: articles/x/2026-11-10/article.md, 26 paragraphs.


## 6:04 AM fold-in
- Added one short paragraph on Google DeepMind's AlphaProof Code after the Cloudflare image, sourced to the DeepMind blog (four weeks, over six million lines of Lean, one percent flagged for human review, two reintroduced bugs both proven insecure). Title, caption and lead unchanged; x-article dry run passes (27 paragraphs, ~1549 words).

## 9:30 AM algorithm-review rewrite (Anthony approved the x-algorithm recommendations, 2026-11-10)
- Caption moved off tip-first (the previous post, 2026-11-09, was tip + Meanwhile) to the **number** shape: leads with Harvey's 900 agents in about four hours, then the fix (repeat alerts join the open investigation, t=500s). Ends in `...`, no `$`, no "Mind Blow". Record `"caption_shape": "number"` in state/x_posts.json.
- Close now: one first-person take (limit what one alert or one person can start; grounded in Harvey's talk), the reply question, a share prompt (send to the teammate who owns the alert-to-agent pipeline), and a follow line. Dropped the old "That's the cycle" sign-off.
- Dry run re-run: passes, FORMAT roundup, SOURCE article.md.
