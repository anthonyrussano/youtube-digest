# Check: edition 2026-10-30 (classic full roundup)

## Winning formula rules
- [x] Body = full edition: cold open with hard numbers (40%, 14%, 14 seconds), fixed intro line, 17 story paragraphs (16 items plus "A few quick ones"), about 1,350 words in the dry run. No `##` sections, no bullets.
- [x] Title names three items with numbers and verbs, Oxford comma: "Opus 5.5 costs 14% more per task, AWS adds an AI chip every 14 seconds, and Intel sinks 23.7%" (93 characters).
- [x] Caption tip-first, "Coding agent tip:" + action + "Meanwhile" surprise, 191 characters, ends with "...", no dollar sign + digit, never blank. Same text on format.txt line 3.
- [x] Images: 2 cited-video still frames (slides, no talking-head-only shots), each on its own line right after the paragraph that cites its timestamp. NASA header prepared.
- [x] Closing question with three concrete choices, then sign-off.
- [x] No "Mind Blow" anywhere; no platform framing (grep hits for "like"/"looks like" are literal comparisons).
- [x] Craft ban-list grep clean (one "very" replaced with "wildly").
- [x] `./run.sh x-article 2026-10-30 --dry-run` prints FORMAT roundup and SOURCE articles/x/2026-10-30/article.md, no warnings.

## Image numbers checked (against the frames themselves and the transcript)
1. /workspace/2026-10-30-1-token-vs-task-price.png, https://www.youtube.com/watch?v=rWtbOgl5FTU&t=240s (slide shown 230-260 s; text links 230 s and 242 s). Slide: 40% cheaper on paper, Opus 5.5 at $4/$20 vs Fable 5.1 at $10/$50; 14% more expensive in practice, $15.09 vs $13.18; 3.62% lower score, 45.60% vs 49.22%; "from Tax Agent Bench". Arithmetic: 15.09/13.18 = 1.145 (14%); 49.22 - 45.60 = 3.62 points; 4/10 and 20/50 = 0.4 of the price (the slide's "40% cheaper" is the slide's own wording, quoted as is). Alt text matches.
2. /workspace/2026-10-30-2-vals-smith-comparison.png, https://www.youtube.com/watch?v=rWtbOgl5FTU&t=757s (text links 750 s). Slide "Vals Smith": accuracy 74.32% (GPT-5.6 Sol) vs 72.97% (Kimi K3); cost per test $2.51 vs $11.73; latency 8m28s vs 16m44s ("about half the time" holds: 508 s vs 1,004 s). Alt text matches.
Model names follow the slides (the Whisper transcript mishears them as "fable", "gbt 5.6 soul").

## Facts spot-checked against sources
- 1.5 million dollars in a month, team of "10 or 12", about 10x salary: transcript 673-679 s. Slide at 675 s reads "What do you do when your engineers spend $1.5M in a month?"
- 90% less spend: transcript 794 s ("I think we're spending 90% less"), attributed to Krishnan.
- AWS and Intel figures: The Register articles as linked (see research.md).
- KubeCon items: CNCF End User TAB post as linked; the Anthropic incident is described by a TAB member's talk pick, attributed to that post.
- X items: full post text read (long-form text included); dubious/promotional token-price claim flagged in copy; one off-topic filter pick (power grid) dropped.

## Shortfalls
- Window was about 7.2 hours: one relevant video. The 6:04 run may fold in items from after the window end.
