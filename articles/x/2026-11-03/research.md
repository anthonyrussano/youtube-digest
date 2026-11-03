# Research: edition 2026-11-03 (overnight prep, classic full roundup)

Window: 2026-11-02T20:33:01Z (12:33 PM PT Nov 2, the previous edition's publish time) to 2026-11-03T08:38:28Z (12:38 AM PT Nov 3).

## Lead: OpenAI's Pando Git backend (primary: https://openai.com/index/scaling-git-at-openai/)
Authors Aaron Friel, Taylor Blau, Ted Nyman (OpenAI MTS), Nov 2, 2026. Supporting posts: OpenAI Developers https://x.com/OpenAIDevs/status/2117408792346509663, Greg Brockman https://x.com/gdb/status/2117435285021810921, Tibo https://x.com/thsottiaux/status/2117412956950638872.

Raw facts (all from the OpenAI post unless noted):
- Why: Codex made parallel work normal; more branches, pushes, merges, fetches from dev environments, research jobs and CI. "Reliability at times falling below 90%" on the old system.
- Pando now powers all development in OpenAI's monorepo. Kept the Git protocol and client, so no devex change.
- Results: "cut median push latency by nearly 5x" (intro) and "reduced the latency of the median push by nearly 80%" (deploy section); the two are the same claim (5x = 80% reduction). OpenAI Developers: "~80%". Nearly a petabyte of Git data per day; served more than 57 TB of packs in one hour, over 99% of bytes from local disk cache; "a handful of CPU cores".
- Design: causal consistency. Each ref is serialized on its own; unrelated branches never contend; a reader of several branches can see them at different points in time. Only contended key is the ref pointer (compare-and-swap-like).
- Push path: pack validated in a single-pass decode while streamed to blob storage, never unpacked; ref version written to a metadata store in a multi-key transaction; O(1) metadata reads/writes per push. Only the trunk is advertised for new feature-branch pushes (ref advertisement with millions of branches can exceed 100 MiB). Median pack this way under 20 KiB, p99 under 3 MiB.
- Fetch path: haves/wants mapped to ref versions, O(log delta) metadata reads; packfile-uri used exclusively (empty inline pack); Express pack cache, consistent hashing, cache hit rates over 99%; clones saturate 10 Gbps links on standard VMs.
- Compaction: LSM-like covers L0..L4; packs kept at every level, never garbage collected.
- Building it (the under-covered angle): kick-off to production in 10 weeks with Codex; core designed by a single engineer, implemented by teams of agents, deployed by a handful of engineers; Rust, no legacy deps; a conformance test suite "so agents could test their changes against standard Git behavior"; deterministic simulation testing harnesses; with GPT-6 Astra, agents wrote Lean and TLA+ to formalize a "theory of Pando" used to find and fix bugs; continuous sessions ran hundreds of hours on edge cases; production traffic since April.
- Migration: read/write-through proxy to the old system first; Codex skills to migrate checkouts.
- Brockman: "Considering providing this to others".

What coverage said (quick web search, Nov 3): The New Stack, MarkTechPost and iFeeling Daily all centered on architecture (causal consistency, packfile-uri, Express caches, ~80% latency). None of the three highlighted, in their summaries, the build process: one designer, agent teams, a conformance suite and deterministic simulation as the agents' ground truth, plus Lean/TLA+ proofs. That is the angle we lead with, paired with Lauren (poteto, https://x.com/poteto/status/2117437607940681849): "adversarial reviews mostly a waste of tokens ... far better to use those tokens on empirical combined with formal verification", agents "get lost in the nitpicks and yagnis"; she is using the pstack interrogate skill less.

Chosen angle (one sentence): OpenAI's agents could build a new Git backend in 10 weeks because they were checked against things they could not argue with (a conformance suite, a simulator, formal proofs), which is the same conclusion an independent agent-tooling developer reached the same day.

## Other items (facts used)
- GhostAction video (Thetips4you, https://www.youtube.com/watch?v=emX1F-0vKs4): 1,900 accounts, 30,000+ repos [0-7s]; workflow "security audit dot yaml" dumps Actions secrets, scans full history incl. keys deleted years ago [61-94s]; plain HTTP to a bare IP [94s]; GitGuardian: October wave 30,000 repos, 3,000+ secrets, campaign GhostAction, first seen Sept 2025 [106-119s]; GitHub blocking since Oct 9 [127s]; OIDC creds expire in about an hour [422-458s]. Note: the video calls the file "security audit dot yaml" (spoken), we do not print a file name.
- Mixedbread talk (AI Engineer, https://www.youtube.com/watch?v=3Ad73Onx3Aw): grep-style search can cost 10 or 20 dollars a query [176s]; Nvidia 1996 vs 2026 reports embed to similar points [425s]; late-interaction model [595s]; hedge fund 36% -> 98% answer accuracy [904-912s], slide: "55 questions on their own documents. They only swapped the search backend."; LLM spend down 3x [936s]. Vendor claims, attributed.
- Pieter Levels, BF1942 port (https://x.com/levelsio/status/2117374984192512391; site https://bf1942.pieter.com): tried 6 months ago, gave up; Opus 5.5 in Claude Code; 57,000 x86 functions disassembled; each translated to C; 100,000 lines of C; Emscripten to WebAssembly; "300x" Windows and Direct3D functions rewritten to WebGL 2/OpenGL; own WebSocket network stack; shareware demo with multiplayer.
- WorkOS (Michael Grinich https://x.com/grinich/status/2117400083151138954; bulletin https://workos.com/security/bulletins/october-30th-2026-data-security-incident): found Oct 30; ARTEX, autonomous AI agent framework for offensive security; production and customer platform data not accessed; CRM/support data incl. business contact details, summaries of sales calls, support discussions, customer Slack conversations; advice to verify unexpected requests.
- Gartner via The Register (https://www.theregister.com/ai-and-ml/2026/11/03/open-models-can-do-90-percent-of-agentic-work-at-a-twentieth-of-the-cost-of-a-frontier-llm-gartner/5307132): Mark Petty, Raymond Paquet; 9 in 10 steps routine; quarter the price of the cheapest closed model at the same score; as little as a twentieth vs frontier on every step; real saving 5-6x; by 2030 90% of enterprise operational agent workflow steps on open weights; harnesses as the source of value.
- Yingjun Wu (https://x.com/YingjunWu/status/2117387909183816165): DeepSeek V4.1 Flash; H200 cannot cover rent at 100% utilization; B300 breaks even at ~35%. His linked long-form article was not readable from here; only the post text is used.
- Hugging Face MIC (https://huggingface.co/blog/transformers-mic): SDPA for T5 enabled July 30, 2026 let UMT5's decoder attend to future tokens; in main almost two months (fixed Sept 28); fixture 66 MB vs 1,227 MB; T5 contract runner step 13.4 s on CPU; 750+ model types; 88,000+ CPU tests, 200,000+ GPU tests daily; eager-only run missed the bug.
- Q Labs (Samip, https://x.com/industriaalist/status/2117370524330594698; https://qlabs.sh/research/parameters/; paper https://arxiv.org/abs/2610.37842): humans ~1,000,000x more sample efficient; brain 100T synapses, ~200M tokens; Chinchilla 1T params on 20T tokens; 7 OOMs apart; quadrillion-parameter extrapolation; paper: hyperparameter transfer (weight decay) + ensembling, 0.15 nats / 14% perplexity better on 100M FineWeb tokens.
- Runway, Cristóbal Valenzuela (https://www.youtube.com/watch?v=q4ITwvlFplQ): first AI film 2019 [61s], 128x128 pixels [76s]; car demo with no 3D representation [527-548s], "world interface model" [557-560s]; Continuum, OS streamed from a video model [649-671s]; connected to a coding agent, "visual thinking" [836-857s]; release in the next 8-12 months [996-999s]. Claim "Turing test we've already passed" [277s] not used.
- Node-RED (The Register, https://www.theregister.com/security/2026/11/02/max-severity-bug-in-widely-used-ot-programming-tool-exploited-to-deliver-linux-malware/5307086): CVE-2026-58115, CVSS 10; Siemens SIMATIC IoT2050; VulnCheck canary Oct 30; inject + exec nodes; single POST /flows; 16 attempts Oct 30-Nov 1, 125 hits on 8 CVEs; bot-linux-amd64; not yet in CISA KEV.
- LangChain Managed Deep Agents (https://www.langchain.com/blog/introducing-managed-deep-agents): public beta Nov 2; mda dev / mda deploy; memory.py, schedules/, channels/slack.py, sandbox/; MCP endpoint at /mcp; Content Studio code shrank ~80%.
- AWS AgentCore CLI research agent (https://www.youtube.com/watch?v=ZEfmlXJOpME): "as few as maybe two command line commands" [88-94s]; agentcore dev [336s]; deploy without IAM roles or S3 buckets [431-446s].
- AWS cost module (https://www.youtube.com/watch?v=eflczOYnqxQ): max iterations default ~75 [347-355s]; max tokens the direct cost cap [364-372s]; cached reads "tens of its input rates" (spoken; read as a tenth), writes ~1.25x for 5-minute cache, double for longer [391-405s]; cache point below the minimum silently ignored [449-454s]; output tokens / latency trick [668-686s].
- AWS Module 1 (https://www.youtube.com/watch?v=WD0caEH76og): support cases H1 2026, service configuration issues about a third [185-190s], slide shows 30%, 21%, 13%; triage agent log with customer email, session token, developer name [639-644s]. Module 6 (https://www.youtube.com/watch?v=hGTZlh1LJI8): topology from IaC templates [203-209s]; model routing takeaway [308-332s].
- MCP (Pieter Levels quoting Steve Lacey, https://x.com/levelsio/status/2117361943938031845): agents almost never use MCPs; Levels adds them because people expect them; MCP and API endpoints will merge, API keys and OAuth. Steve Lacey's own post (2117359574181163199) explains why: the connector step needs a human.
- Ethan Mollick (https://x.com/emollick/status/2117445039211086096): mass replication of old LLM findings; no invented citations; hallucination and stereotyping down; still sycophantic and lean left.
- AWS humanoids (https://www.youtube.com/watch?v=ljUjsyPhVOE): GR00T N1.6 3B [365s]; 16-step action chunk [388s]; 100 episodes [433s]; ~30% success [525-532s].
- Amjad Masad (https://x.com/amasad/status/2117504072416890937): agents on employee endpoints a systemic risk; Goldman Sachs reportedly restricting Claude Code; Replit advisory by Luis Héctor Chávez (X article, not readable from here).
- Vercel (https://vercel.com/changelog/projects-can-now-be-configured-with-vercel-toml): vercel.toml, comments, flatter structure; only one config file.

## Dropped / not used
- Weight-space programming (Garry Tan, Andrew Curran "Reproduced", Alex Krentsel, The Register): already covered in edition 2026-11-02-1213.
- Anthropic Q3 revenue / compute: already covered in 2026-11-02-1213.
- poteto "hire grok bot" and a "20 repositories" listicle: promotional.
- AINews: mail bridge unavailable this run.

## Candidates table
| Story | Why lead | Coverage | Verdict |
|---|---|---|---|
| OpenAI Pando | big brand, hard numbers, agent-built | architecture widely covered; build process under-covered | Lead |
| GhostAction | actionable security fix | one video | Item 3 |
| Mixedbread | 36% -> 98% | vendor talk | Item 4 |
| BF1942 port | strongest surprise | creator post | Cold open + item |
| Gartner open weights | enterprise cost | one article | Item |
