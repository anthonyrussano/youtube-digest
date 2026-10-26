# Check: 2026-10-26 X Article

## Rules (docs/X_ARTICLE_STYLE.md)
- [x] format.txt line 1 "roundup", line 2 reason, line 3 caption
- [x] Classic full roundup: whole edition, 12 linked story paragraphs, ~1,290 words (dry run), no headings or bullets
- [x] Led by the broadest story (Tesco/Proxmox, The Register)
- [x] Title names three brands with numbers, "A, B, and C" form, 96 chars
- [x] Caption tip-first ("Voice agent tip: ..."), 172 chars, ends with "..."
- [x] No "$<digit>" in title or caption; no "Mind Blow" anywhere
- [x] No platform framing (grep for on X / bookmarks / likes / saves / posted: only "like" as a preposition)
- [x] 3 images, all still frames from cited videos, each on its own line right after the paragraph citing that timestamp; alt names channel and video
- [x] Closing reply question, then sign-off
- [x] `./run.sh x-article 2026-10-26 --dry-run` prints SOURCE: articles/x/2026-10-26/article.md

## Numbers and sources
- Tesco 5,000+ stores; VMware offer = 175 percent price increase (Tesco's claim in its lawsuit); hearings likely 2027; job based in Bengaluru; Proxmox 24/7 support added in September: The Register, 26 Oct 2026 (lead_source)
- LiveKit false cutoffs 4.5% vs 9.9% best alternative, harness open source: OmyqelTwpOo t=773-800s, frame at 795s (13:15) shows both numbers
- 210 ms TTFB vs up to 0.75 s silence: OmyqelTwpOo t=425-452s
- ~1.5 s holds, 500-600 ms feels human: OmyqelTwpOo t=881-902s
- Time to first sentence 381 ms (Gemma 4 31B, LiveKit), 844 ms (Gemma 4 31B, OpenRouter), 932 ms (Gemini 2.5 Flash), 1097 ms (GPT-4.1), 1645 ms (GPT-5.5): slide at OmyqelTwpOo t=1125s (18:45), read from an upscaled crop
- ChatGPT advanced voice on LiveKit: OmyqelTwpOo t=212s
- Arize: 20 traces, one dimension, one judge: gv4w23xYj-0 t=2066s; one quality per eval: t=1192-1215s; concrete criteria slide: t=1160s (19:20); metric vs eval: t=2038s; vibes/CI gates: t=126-158s; traces vs evals: t=236s
- DNS: "three years or five, but it's probably not ten" (John Crain, ICANN CTO); UDP to TCP a few years; Category 1 gTLDs 45 percent higher abuse chance: The Register, 26 Oct
- China: 23 technologies added to export catalogue, open source exempt; DeepSeek, MiniMax authorised; Firmus IPO (~5 billion, 40+ billion valuation) cancelled; NEXTDC down almost 40 percent: The Register Asia in brief, 26 Oct
- X posts cited by link only (Curran, Tan/Pocock, CI runners); no counts used
