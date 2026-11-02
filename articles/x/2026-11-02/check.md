# Check: edition 2026-11-02 (classic full roundup, overnight draft)

## Winning formula rules
- [x] Body = full edition: cold open with hard numbers (15 minutes -> under a minute, 0.8 billion parameters), fixed intro line, 13 story paragraphs (7 stories), about 1,173 words in the dry run. No `##` sections, no bullets.
- [ ] 10+ distinct stories: only 7 in a thin Sunday-night window. The 6:04 run should fold in morning delta items (and the Joscha Bach video if it gets transcribed).
- [x] Title names three tools with numbers, Oxford comma: "Ollama needs 64K context, Xiaomi-OCR-0 reads receipts at 0.8B, and Claude Code runs for 0 dollars" (97 characters).
- [x] Caption tip-first ("Ollama tip:"), action + "Meanwhile" surprise, 205 characters, ends with "...", no dollar sign + digit. Same text on format.txt line 3.
- [x] Images: 2 cited-video still frames, each right after the paragraph citing its timestamp. NASA Earth header prepared (STS-66 Himalayas, id not used before).
- [x] Closing question with three concrete choices, then sign-off.
- [x] No banned brand name anywhere; platform-framing and ban-list grep clean (0 hits).
- [x] `./run.sh x-article 2026-11-02 --dry-run` prints FORMAT roundup and SOURCE articles/x/2026-11-02/article.md, no warnings (17 paragraphs, ~1173 words).

## Image numbers checked
1. /workspace/2026-11-02-1-ollama-context.png, https://www.youtube.com/watch?v=-Qvf9Y3RT_M&t=322s. Frame: chapter "04/06 THE CONTEXT TRAP", terminal "the fix": `OLLAMA_CONTEXT_LENGTH=65536 ollama serve`. Text says 65536 and 64K (65536 = 64 x 1024). Narration says "64,000"; the article uses the on-screen value. Alt matches.
2. /workspace/2026-11-02-2-apollo-ebit.png, https://www.youtube.com/watch?v=vUJDyDnqT4c&t=110s. Slide: 55% of US adults used gen AI within three years of launch; PC 20%, internet 30%; 6% of companies attribute 5% or more of EBIT to AI; 88% use AI in at least one function; 39% see any EBIT impact. Text uses 55%, "almost 90%" (speaker's words; slide 88%), and 6% with the slide's 5%-of-EBIT definition. Alt matches.

## Facts spot-checked
- Ollama commands and the 64K advice: docs.ollama.com/integrations/claude-code.
- 4,000-token default under 24 GB and 50-65 tok/s on an RTX 3090: the video's claims, attributed to it.
- Apollo numbers and quotes: transcript timestamps in research.md (Whisper base.en; spot-read for sense).
- DEPA: The Register article as linked; "unlock" in the ministry quote deliberately not quoted (ban list).
- Xiaomi-OCR-0: model card (base model, ~170M samples, Apache 2.0, JSON schema prompt); 59.09% from its technical report.
- X items: visible post text only; the CI skill item is framed as a caution because it tells an agent to run and obey a remote skill from a 0-star repo.

## Shortfalls
- 7 stories, below the 10+ target.
- X collection incomplete: 17 of 33 search queries and 0 of 3 account queries (X reads became temporarily unavailable).
- The Bach video (97 min) is untranscribed.


## Morning update 2026-11-02
Folded in 9 brief items from the morning delta; reran ban-list grep (clean), no headings/bullets, no platform framing, no 'Mind Blow'. Claims from X summaries (NVIDIA/MIT harness, RTX 3090 throughput) are framed as reported. Word count ~1,990.
