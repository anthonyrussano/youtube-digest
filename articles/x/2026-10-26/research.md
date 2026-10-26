# Research: 2026-10-26 (overnight)

Window: 2026-10-26T00:13:31Z to 2026-10-26T07:18:56Z (Sunday 5:13 PM to Monday 12:18 AM PT).

## Videos (both transcribed with Whisper large-v3-turbo on the home GPU host)
- gv4w23xYj-0, AI Engineer, "How to Write Your First AI Eval - SallyAnn DeLucia, Arize AI" (workshop, Oct 12). Head of product at Arize (0s). Vibes problem (126s); without evals no regression detection, no model comparison, no CI quality gates (158s); eval vs unit test (191s); traces are the logs for AI, evals are tests (236s); types of evals incl. LLM-as-judge, decision models, code, annotations, agent-as-judge (316-420s); vague vs concrete criteria slide (1152-1180s, frame at 1160s); judge one quality per eval, research says LLM judges do best with one criterion (1192-1215s); metric vs eval (2038s); start small: 20 traces, one dimension, one judge (2066s).
- OmyqelTwpOo, AI Engineer, "How to Build Voice Agents That Don't Fall Apart When You Interrupt - Jesse Hall, LiveKit" (expo session, Oct 13). OpenAI chose LiveKit for ChatGPT advanced voice mode (212s); cascaded STT-LLM-TTS vs speech-to-speech (259s); "3rd" heard as "30th" (331s); 210 ms TTFB vs up to 0.75 s silence from popular providers, measure time to first audio (425-452s); time to first sentence not first token (479-507s); async tool call one-liner (568-608s); hotel demo (618s); turn detector listens to rhythm/pitch/intonation, 9.9% vs 4.5% false cutoffs on their hotel use case, harness open source (773-800s, frame at 795s); "$555.23" example (818s); ~1.5 s holds, 500-600 ms feels human (881-902s); simulated callers, swap stacks (940-1076s); Gemma 4 31B on LiveKit inference fastest, slower elsewhere (1112-1135s; slide at 1125s: time to first sentence 381 ms LiveKit, 844 ms OpenRouter, Gemini 2.5 Flash 932 ms, GPT-4.1 1097 ms, GPT-5.5 1645 ms); checklist (1175s).

## Feeds (The Register, tier 2)
- Tesco VMware to Proxmox (Simon Sharwood, 26 Oct 05:24 UTC): job ad for Head of Software Engineering, Edge Platform, based in Bengaluru; quote "own the engineering strategy and execution of Tesco's migration from VMware to Proxmox across the edge estate"; 5,000+ stores; lawsuit over perpetual licences, VMware offer = 175 percent price increase (Tesco's claim); hearings likely 2027; scuttlebutt: Hyper-V for core; Proxmox added 24/7 enterprise support in September; Warrilow quotes.
- DNS quantum (ICANN 87, Bali): CTO John Crain, "I don't know if it's three years or five, but it's probably not ten"; larger keys mean larger responses, UDP to TCP "going to take a few years"; Category 1 gTLDs 45 percent higher chance of abuse (Siôn Lloyd); ICP-2 RIR reform.
- Asia in brief: China's export catalogue adds 23 technologies (large models, agents, computing clusters, information processing), open source exempt; DeepSeek and MiniMax (named elsewhere) authorised to keep exporting; Firmus IPO cancelled (aimed ~5 billion dollars, valuation over 40 billion); NEXTDC shares down almost 40 percent after power supplier halted work amid opposition.

## X (from the edition's selected posts)
- Andrew Curran on Claude "nerf" rumors and cyber guardrails; quotes an OpenAI reply that Codex reverse-engineering blocks are accidental decision-boundary issues and being fixed.
- Lauren Tan (poteto) quoting Matt Pocock: next language for agents = Rust speed, Go's small design space, strictest type/verification system; Bend as a first effort.
- Yash: CI runner alternatives (Blacksmith, WarpBuild, Depot, Namespace, StarSling); link-card claims "2x faster", "50% cheaper", "2x-10x faster".
- Dropped: ARTEX follow-up (already covered in an earlier edition), Hallmark (covered), Karpathy/Obsidian hype post, poteto's "no moat" meme, listicles, crypto post.

## AINews
No new issue in the window.

## What others missed
The LiveKit talk's numbers are about what the caller hears, not what dashboards report; the Arize workshop's most useful point is small: one criterion per judge, 20 traces to start.
