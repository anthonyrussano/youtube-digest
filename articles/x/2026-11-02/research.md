# Research: edition 2026-11-02 (overnight prep)

Window: 2026-11-02T01:17:31Z to 2026-11-02T08:23:21Z (Nov 1, 5:17 PM PT to Nov 2, 12:23 AM PT; about 7.1 hours, Sunday night).

## Videos
1. Thetips4you, "Unlimited Claude Code For Free (Runs On Your Computer)", https://www.youtube.com/watch?v=-Qvf9Y3RT_M (10 min). Transcript from captions (a voice-over translation; some model names are garbled, so the article avoids the specific local model names except the 35B/RTX 3090 speed line).
   - 72 s: Ollama added support for the Anthropic API format; agent thinks it talks to the cloud, requests stay on device; localhost port 11434 (57 s).
   - 119-150 s: VRAM is the number that matters; download size plus 2-6 GB for context (182 s).
   - 206-251 s: Ollama 0.15 or newer; `ollama launch claude`; status bar shows the local model, no API key.
   - 261-274 s: manual route, three env vars (base URL localhost, token any word, API key blank). Matches docs.ollama.com/integrations/claude-code.
   - 289-322 s: "context trap": under 24 GB, default context about 4,000 tokens; exhausted after two files; fix OLLAMA_CONTEXT_LENGTH (frame at 322 s shows 65536), desktop slider; Modelfile num_ctx overrides the variable.
   - 366-374 s: `ollama ps` should show 100% GPU and the new context.
   - 381-399 s: about 40 tok/s feels responsive; 35B on RTX 3090 about 50-65; single digits means trouble.
   - 482-492 s: headless with --model / --yes, args after `--` (docs confirm `--yes` requires `--model`).
   - 502-517 s: three mistakes: model without tool support, skipping permissions, default context.
   - 523-552 s: local wins on cost, privacy, offline; cloud wins on quality and speed for big refactors and long multi-step tasks; use both.
   - Docs: https://docs.ollama.com/integrations/claude-code ("For larger repositories, set the context length to 64k or higher").
2. AI Engineer, "Your AI Pilots Won't Move the P&L. Here's What Will - Adam Nahari, Apollo", https://www.youtube.com/watch?v=vUJDyDnqT4c (16 min). Transcript: local faster-whisper base.en fallback (captions rate-limited, GPU host unreachable).
   - 25-61 s: cargo airline scheduler, 15 minutes to recrew, manual, one legal solution not necessarily cheapest; premium pay as the release valve.
   - 67 s: crew is the second-largest cost after fuel.
   - 82-107 s: 55% of US adults used gen AI within three years (PC 20%, internet 30% at the same point); almost 90% of businesses (slide: 88%) use AI in at least one function; 6% report significant EBIT impact (slide: "6% of companies attribute 5% or more of EBIT to AI"; 39% see any EBIT impact). Sources on slide: St. Louis Fed RPS (Bick, Blandin, Deming) 2025; McKinsey State of AI, Nov 2025.
   - 116-139 s: time savings about 2% of US working hours; Solow 1987.
   - 162-187 s: 5 units change management : 1 unit engineering; engineering share shrinking (slide 5:1 at 176 s).
   - 218-321 s: three layers (general productivity, domain-specific, core operational); high-impact firms 3x as likely to redesign workflows end to end.
   - 339-432 s: move 1, one or two problems not 40; five criteria (CFO-measurable baseline, data ready and owned, named user, CEO top-five priority).
   - 437-542 s: move 2, 10% play vs 10x play; optimization engine ranks all legal solutions by cost in under a minute; engineering still the smaller part, "the bigger job was getting it used".
   - 546-610 s: move 3, CEO commitment or no funding.
   - 612-701 s: move 4, build with the business; schedulers met engineers every other day; hired CIO, VP data and AI, senior director of data science.
   - 703-757 s: move 5, tools in everyone's hands; 3 of 4 executives in a workshop had never used AI before that week (719 s).
   - 758-845 s: move 6, kill metrics: 90-day time gate, metric gate (A/B vs baseline), adoption gate over 50%; CFO unit economics including compute and tokens.
   - 927 s: 15 minutes to under a minute.
3. Machine Learning Street Talk, "Why Leibniz Couldn't Find the Mind Inside the Mill (Joscha Bach)", https://www.youtube.com/watch?v=yW_ngvMFlYs (97 min). NOT transcribed: captions rate-limited, GPU host unreachable, local fallback caps at 45 min. Not used in the draft.

## Articles
- The Register, Simon Sharwood, "India floats AI plan under which 'The model travels to the data...'" (Nov 2, 04:39 UTC): https://www.theregister.com/public-sector/2026/11/02/india-floats-ai-plan-under-which-the-model-travels-to-the-data-rather-than-the-data-travelling-to-the-model/5306872 . MeitY DEPA for AI Training; quote from Prof. Ajay Kumar Sood; TDPs (hospitals, banks, agencies) -> Data Exchange Platforms with hardware-based secure data environments; TDCs train there; differential privacy; immutable audit logs; 400 million underserved individuals and MSMEs (credit); unclear how much work remains.
- Two other feed items in the window were off topic (dropped).
- No AINews issue in the window.

## X items (filter-selected, full visible text read)
- Yonas Beshawred, https://x.com/yonasbe/status/2117129569757245616 : prompt to check against 80+ GitHub Actions optimizations via `npx skills use https://github.com/starslingdev/skills --skill ci-speedup`, "follow the generated skill instructions". Repo had 0 stars at fetch time. Written with a read-the-skill-first caution; not endorsed. Quotes another post (https://x.com/Voxyz_ai/status/2116636332344889391), not read.
- Darryl Ruggles, https://x.com/RDarrylR/status/2117127112637170119 : Dockerfiles, build time and image size; links an article (truncated t.co, not opened). Generic fixes (layer order, .dockerignore, multi-stage) stated as the usual fixes, not attributed to the article.
- Kushal Gangil (Tech Fusionist), https://x.com/techyoutbe/status/2117156770057781529 : 15-visual platform engineering guide (Backstage, golden paths, Crossplane, GitOps). Visible text truncated.
- FHILY (@Oluwaphilemon1), https://x.com/Oluwaphilemon1/status/2117068641082749040 : Xiaomi-OCR-0, 0.8B, built on Qwen3.5-0.8B, receipts/invoices to JSON. Verified on the model card https://huggingface.co/xiaomi-research/Xiaomi-OCR-0 (Apache 2.0, base Qwen3.5-0.8B-Base, about 170M-sample OCR corpus, KIE with a JSON schema prompt). Technical report (third-party PDF host) gives 59.09% on an in-house KIE benchmark, 96.83 on OmniDocBench v1.6.

## Gaps
- X searches stopped after 17 of 33 queries (X reads became temporarily unavailable at query 17); the 3 account-list queries were not run.
