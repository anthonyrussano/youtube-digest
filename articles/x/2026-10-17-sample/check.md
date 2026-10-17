# Final check: 2026-10-17 sample

Run 2026-10-17 ~4:55 PM PT. **Sample only: not posted to X**, no entry in `state/x_posts.json`.

## 1. Research summary
- [x] Lead facts come from the primary source (the 6-post Hugging Face thread plus 2 author replies, the gist, the repo), not from the AINews one-liner.
- [x] Coverage check done (X search + web search): others repeated "OpenHands = temperature 0"; nobody explained the tool-output fix or the small-model caveat.
- [x] The one outside claim (temperature 0 not deterministic on hosted APIs) is linked to its source.

## 2. Outline
- [x] One core idea (noisy tool output, not the model, causes run-to-run flips), one step per section.
- [x] Tightened: dropped the v0/v1/v2 harness details to one sentence; dropped the OpenHands RFC (true but a side road).
- [x] Jargon defined on first use: harness, temperature. "Stochastic" appears only after the idea is explained, inside a quote.

## 3. Clarity (technically curious non-expert)
- [x] Short sentences, one idea per line, every line its own paragraph in the HTML.
- [x] Hook uses the overlooked angle (progress bar vs. temperature 0).
- [x] Concrete example a reader can picture (150.3 vs 129.3 MB/s).
- [x] Ends with a takeaway (diff two tool outputs) and a reply-inviting question.
- [x] Lead story ~600 words (target 400-800); "Also this cycle" has 5 linked one-liners.
- [x] Redundancy pass: the 14/20 figure appears once; no line repeats another.

## 4. Overlooked angle: real, sourced, simple
- [x] Real: the author says it directly ("even if we force the model to have a deterministic behavior, the end result will be stochastic"; "a very simple trick fixed this issue which consists of normalizing tool outputs").
- [x] Sourced: every claim links the specific thread post, reply, gist or repo.
- [x] Nuance kept: mostly small models; repeatable is not correct.

## 5. Rules
- [x] Title names the lead idea, not three stories.
- [x] Caption leads with one actionable tip, ends with "...".
- [x] No "$" followed by a number in title, caption or body (`./run.sh x-article` enforces this for article.md).
- [x] No "Mind Blow". No platform framing or engagement counts in the article.
- [x] `./run.sh x-article 2026-10-17-sample` -> SOURCE articles/x/2026-10-17-sample/article.md, 42 paragraphs.

Result: PASS. No fixes to article.md were needed after this check.
