# Check: 2026-10-28 X Article

## Rules (docs/X_ARTICLE_STYLE.md, STYLE checklist, WRITING_GUIDE section 6)
- [x] format.txt line 1 "roundup", line 2 reason, line 3 caption (matches article.md front matter)
- [x] Classic full roundup: 16 linked story paragraphs, ~1,612 words in the dry run (23 paragraphs), no headings, bullets or tables (grep '^(#|[-*] |\|)' empty on article and draft)
- [x] Title names three brands with numbers in "A, B, and C" form, 95 characters. Headline compression: "Anthropic drops code tests" refers to one Anthropic hiring manager's loops (the body says so)
- [x] Caption "Chainguard tip: ..." + "Meanwhile" surprise, 225 characters, ends with "..."
- [x] No "$<digit>" and no sibling-bot name anywhere in the folder
- [x] Platform-word grep (on x / bookmark / saves / saved / likes / posted / tweet / viral / followers / trend): no hits after rewording two literal "like"s
- [x] WRITING_GUIDE ban-list grep clean (Dabit's "essentially obsolete" paraphrased as "now obsolete")
- [x] Cold open, intro line, items, reply question, sign-off
- [x] Every transcribed video (8) cited with timestamped links
- [x] 3 images, all slide frames from cited videos, each right after the paragraph that cites it; alt names channel/event, speaker and video
- [x] `./run.sh x-article 2026-10-28 --dry-run` prints SOURCE: articles/x/2026-10-28/article.md

## Images (each viewed)
- /workspace/2026-10-28-1-chainguard-exploit-gap.png: xZX3pmaB8Hk at 218s (3:38), slide "Exploit arrives before the patch". Verified labels: 2025 -7 days, 2023 +5, 2021-22 +32, 2020-21 +44, 2018-19 +63, "30-day patch window", source Mandiant (Google) Time-to-Exploit Trends (Oct 2024) and M-Trends 2026. Speaker inset only; slide fills most of the frame.
- /workspace/2026-10-28-2-geedge-seed.png: MaKRLgXzWp0 at 830s (13:50), slide "TCP RST Injector Fingerprints". Verified: TSG RST+ACK, count 1-3, stable k = 13; GFW II k = 13; GFW III k = 13; GFW I, Henan, Myanmar, Pakistan no stable k.
- /workspace/2026-10-28-3-ctf-scoreboard.png: xPxlzzMB9O8 at 622s (10:22), slide "RQ3 - Agents vs. Human Teams". Verified: agent peak 4900, human peak 5400, "About 1/5 human solving-time", "Model capability ultimately sets the ceiling". Speaker label on slide reads Tingxuan Tang.

## Numbers and sources
- Chainguard: -7/+63 from slide (transcript's "negative 70" is a mis-hearing); 30 days "a million years" 254-265s; Axios 2 hours / 600,000 382-390s; cool-down, CVE, Sigstore/SLSA 555-576s; SLA 1/7/14 997-1006s; skills 5% / 30-40% 1188-1204s
- Rieseberg: "This month", "Claude is now better at both", two new engineers, one weekend, ~eight days later: blog 27 Oct
- Dabit: 13 years, means to an end
- Razenshteyn: ~two dozen interviews, stock Claude Code/Codex, no swarms, three no-read cases, slop infestation, overbuilding, human one-pager: substack
- Amazon: no tools named, tokenmaxxing line, 10th/90th percentile, "finding, not a failing": aboutamazon.com memo
- Levie: <1% of economy, computer use / long-running agents / swarms, finance / life sciences / healthcare
- Artificial Analysis v5: Kimi K3.1 Pro 46, 12 behind, 3-point gap in v4.3, DeepSeek V4.1 Flash and GLM-5.3 at 32, Haiku 5.5 above them
- CTF: 24 hours, 17 challenges; trust drop 283s; answer shopping 514s; 12 agent teams 569-595s; 5,400 / 4,900 / 4 hours 614-628s; under 100 dollars, prizes 1,000/500 643-659s; Haiku 300-1,100 707-736s; expert + agent 760-787s. Event name unclear in transcript, so not named
- Geedge: 100,000+ docs, ~572 GB, 100+ repos 66-98s; Fang Binxing 129-136s; 29 tools / 21 risk 5 452-461s; Signal urgent 535-540s; Docker 578-590s; k = 13 816-849s and slide; quote 862-868s
- Revelio: 71 countries / 19 censor / 5 apps 952-962s; mazebook 524-528s; Myanmar 4,600 vs 336 643-676s; UAE 1.5M ICMP 743s; China >90% 1053-1058s
- Localhost: 198-222s; 5.8M / ~3M 317-324s; Feb 2017 363-374s; >75% on page load 516-522s; stopped 565-577s; browser prompt (all but Safari) 623-638s
- Tile: anti-theft hides tags 144-160s; 6 scans / 3 blocks 655-662s; unencrypted, millions of users 234-243s; 30-day repeat, static MAC 526-546s; drop anti-theft 825s
- ReDoS: 2PMFA 393s; 48 regexes Snort 2.9 1020-1032s; 15 missed 1067-1070s; PCRE match limit passes packet 1159-1171s
- WBC: 10M+ diffs, 20,000 docs 190-196s; windows 2-40 1034-1037s; AUC 0.839 vs 0.754, 11 datasets 1097-1105s; 2.8x TPR at 1% FPR 1110-1114s; quote 1188s
- ub-mode: stages, CRAP < 10, duplication < 0.8, mutation testing, skills folders, /ub-mode: README
- Coolify: repo description and API metadata

## Skipped
- A quote of a hype post about agent-driven hiring offers: unverifiable, skipped.
