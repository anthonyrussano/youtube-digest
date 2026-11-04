# Check: 2026-11-04-1211 (classic full roundup)

## Rules
- [x] Format: classic full roundup; `format.txt` line 1 `roundup`, line 3 caption identical to `article.md` front matter.
- [x] Title: "Kimi opens 2.8T weights, Siemens ships 400 AI projects in 6 months, and Amp lifts tool picks to 79%" (99 characters): three named brands, each with a number and its own verb, Oxford comma, no `$`.
- [x] Caption (239 characters): tip first ("Amp tip: give agent tool arguments plain names before you swap models..."), then "Meanwhile" + the edition's surprise, ends with `...`, no `$<digit>`, no banned name.
- [x] Body: cold open with two linked hits, the fixed intro line, 19 story paragraphs plus "A few quick ones." paragraph, reply question with three choices, sign-off. ~1,970 words (x-article dry run: 27 paragraphs incl. 3 image markers). No `##`, no bullets, no "Mind Blow", no `$` before a digit (grep clean).
- [x] Ban list and platform-framing greps clean (only hit: "save money", literal).
- [x] No repeats: weight-space programming (2026-11-02-1213) and the Claude Code game-clone rule (2026-11-04) were dropped after grep against `articles/`; earlier Kimi K3.1 Pro mentions (2026-10-23-1213 launch, 2026-10-28 index score) predate the weights release, which is the new story.
- [x] `./run.sh x-article 2026-11-04-1211 --dry-run` prints `FORMAT: roundup` and `SOURCE: articles/x/2026-11-04-1211/article.md`.
- [x] Lead angle real and sourced: the Kimi wins/loss contrast is from Moonshot's own table; the 1.56 TB native-4-bit download and the 20 million dollar license line come from ArtificialWatch's file and license comparison (linked).

## Claims checked against sources
- Kimi: 2.8T/104B, 896 experts/16, 1M context, MXFP4 QAT, 51.7/46.3, 65.7/66.4, 31.5/65.0: Hugging Face model card. ZDR routing behavior: Vercel changelog. 1.56 TB, 96 shards, license threshold: ArtificialWatch.
- Pierre: OpenAI announcement (Trees, Diffs, Code Storage, Highlights, Pando, open source stays open).
- Warp: Zach Lloyd's article text (quote "Terraform for all of the coding agent workflows"; 20+ questions counted from his Sentry list; pre-warm). Flagged as his own product.
- APT: Ubuntu blog (7.7, on-path HTTP, signature bypass, 22.04+ retries, TLS / Retries=0).
- .NET: Stack Overflow blog (42.1 s, 83.6 s, 200 records, ProcessorCount, cancellation-token-only options).
- Lauren Tan, Phone Harness, Atomic, ballots, Revolut/Cohere, Hy4/arena, OpenAI Friday (flagged as a report), Mollick, Teachable Code: their posts.
- Kevin Roose: transcript t=668 (150 people, first 25 hardest), t=931 (big blob of compute, 2017), t=1537-1616 (Claude council, caught errors, quote).
- Siemens: transcript t=88 (39 platforms), t=126-135 (70 in 8 years vs 400 in 6 months), t=145-151 (agent in a day). Flagged as an AWS customer video.
- GitHub: transcript t=113 (no exam), t=145 (five levels), t=284 (Pro badge at proficient), t=338 (usage signals, not code or prompts).
- Amp 53% -> 79%, FlashProve, benchmark audit, AA-Robotics, GSQ, LSA, Qwen4 PR, LongCat, Claude Code October: AINews items, linked to their original sources.
- Deep Insight 95% / 97% / 25K: AWS ML blog. Agent Framework skills quote: Microsoft devblogs.
- Firecrawl: transcript t=24 (HelloFresh 3 years), t=37-39 (60 lines), t=128-151 (harness, Bun, React/Astro/Rust), t=258-267 (one request, four sources). Flagged as a promo.

## Images (each looked at)
1. `/workspace/2026-11-04-1211-0-kimi-vs-opus.png`, original chart (PIL), values copied from the model card table: SWE Marathon 51.7/46.3, DeepSWE 75.5/74.2, Terminal-Bench 4.0 65.7/66.4, ProgramBench 31.5/65.0. Placed after the Kimi paragraph.
2. `/workspace/2026-11-04-1211-1-copilot-proficiency.png`, kind video-frame, https://www.youtube.com/watch?v=aXK0wctLk5U&t=145s : learn.github.com page with Expert/Advanced/Proficient/Intermediate/Beginner levels (UI demo). The paragraph before it links t=145.
3. `/workspace/2026-11-04-1211-2-adfinder.png`, kind video-frame, https://www.youtube.com/watch?v=5uy7anLyT58&t=267s : "One request. One app." slide with Meta ads, Google ads, Podcasts, Creators columns. The paragraph before it links t=267 (changed from the website's t=256 link so the frame matches the cited timestamp).
Frames grabbed with box-local yt-dlp (remote host iphedeiah unreachable this run).

## Header
`/workspace/x-header-2026-11-04-1211.jpg`: NASA iss073e0379986, "Clouds streak across the Indian Ocean beneath the International Space Station" (2025-07-16, 8256x5504 original); id not in any header in state/x_posts.json.

## Changes made in this check
- Added the 1.56 TB / license sentence to the Kimi paragraph (outside fact, linked).
- Firecrawl paragraph: frame-matching t=267 link; "developer advocate" removed (not sourced).
- Added the closing reply question with three choices.
