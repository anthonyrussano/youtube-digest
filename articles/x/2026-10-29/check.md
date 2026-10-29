# Check: 2026-10-29 X Article

## Rules (docs/X_ARTICLE_STYLE.md, STYLE checklist, WRITING_GUIDE section 6)
- [x] format.txt line 1 "roundup", line 2 reason, line 3 caption (matches article.md front matter)
- [x] Classic full roundup: 18 linked story paragraphs, ~1,708 words in the dry run (25 paragraphs), no headings, bullets or tables (grep '^(#|[-*] |\|)' empty on article and draft)
- [x] Title names three brands with numbers in "A, B, and C" form, 95 characters. "Sonar finds 46 bugs" = 46 open issues from one Hunter Agent demo scan (the body says so)
- [x] Caption "Claude Code tip: ..." + "Meanwhile" surprise, 209 characters, ends with "..."
- [x] No "$<digit>" and no sibling-bot name anywhere in the folder (money written as "billion dollars")
- [x] Platform-word grep (on x / bookmark / saves / saved / likes / posted / tweet / viral / followers / trend): no hits after rewording two literal "like"s
- [x] WRITING_GUIDE ban-list grep: only hit is Graver's literal quote "very unpleasant"
- [x] Cold open, intro line, items, reply question, sign-off
- [x] Every transcribed video (10) cited with timestamped links
- [x] Repeat check against published editions: uzu benchmark (2026-10-27) dropped; GitHub Copilot app/projects/Fusion benchmark, 4 million cores, 7.4B commits, Enterprise seat change (2026-10-28) not repeated
- [x] 3 images, all slide/demo frames from cited videos, each right after the paragraph that cites it; alt names channel/event, speaker and video
- [x] `./run.sh x-article 2026-10-29 --dry-run` prints SOURCE: articles/x/2026-10-29/article.md

## Images (each viewed)
- /workspace/2026-10-29-1-github-git-writes.png: AArI948SDz8 at 2255s (37:35). Verified: "7,200 WRITES PER SECOND, SUSTAINED", "5,000 CONCURRENT AGENT SESSIONS", "180x THROUGHPUT"; matches transcript 2251-2261s.
- /workspace/2026-10-29-2-circleci-merges.png: AnsXWH2_EBU at 125s (2:05). Verified: "Writing code is no longer the constraint. Checking it is."; "+59% CI throughput, the largest increase CircleCI has ever recorded"; "~3 in 10 attempts to merge into production now fail"; source "CircleCI 2026 State of Software Delivery, 28 million CI workflows".
- /workspace/2026-10-29-3-hunter-46.png: UW8Qkk7MG8A at 520s (8:40), SonarQube Cloud Hunter Agent results. Verified: 46 open issues, most severe High 27; broken access control 14 (High 13); business logic 5 (High 5); authentication & session 27 (High 9); confirmed 0, accepted 0.

## Numbers and sources
- Claude Code: 16.4% vs 15.7%, 19.7% of requests, 96% Opus, ~9,000:1, 18-26%, 2.1.232, 2.1.257-2.1.312, ~80 lines, ~7 ms: gist
- Qwenputer: 11 + 32 layers, 18M instructions, 230,000 positions, 97.5/95/72.5%, 6e-4 vs 5e-4, 1,024 slots, 90 vs 30%, 18.8 GB / 24 GB: blog
- Anthropic/Sonar: 30,000 vs ~2,500 343-373s; +59%, 3 in 10, 28M 122s + frame; 2027 forecast 902s
- Qodo: Bitwarden 142s; web/mobile/CLI/MCP 222s; separate grader 450s; 25/50/75% 787s
- GitHub: 3-4x 2180s; 7,200 / 5,000 / 180x 2251s + frame; Dreaming "about three weeks" 763s; 200M findings + Max 1621s; Agent Merge 1726s; 30% off 1174s
- Hunter: 46 / 27 high 518s + frame; role field 635s
- Alphabet: ~10%, +12% to 63.25B, 51.4B capex, 26.17B vs 35B, 195-205B guidance: The Register
- Fujifilm: 5x, 10 billion yen, 30-40 TB, 400 MB/s, 70 TB ~2029, 160.3 vs 176.5 EB: The Register
- Dwarf planet: 2026 ED138, ~46 au, 600-1,500 km, Holman thought it was a bug: The Register
- TPU suite 35/54/176/206s; memory 151/268/576s; Graver 812/1635/1998/2727/2907s; SageMaker 41/91/617s; Oracle 51/138/242s
