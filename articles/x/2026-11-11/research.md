# Research: 2026-11-11 (overnight prep, classic full roundup)

Window: 2026-11-11 01:15 UTC to 08:33 UTC (about 7.3 hours, overnight). Sources: 27 transcribed videos (7 new OpenAI DevDay 2026 talks plus 20 carried over from the retry queue), 2 feed articles, 0 X posts used, 0 AINews stories (no issues in the window). One retry video (OpenAI "Introducing Businesses in ChatGPT in beta", 49 s) has no speech and stays queued.

Note: the DevDay event itself was in late September. The talk videos are new in this window, so items describe what the talks say and avoid "launched today" framing.

## Lead: OpenAI, "Codex Security: From Vulnerability to Verified Fix" (DevDay 2026)
Primary: https://www.youtube.com/watch?v=gUQN7juxvVI (transcript read in full)
- 162s: security sprint with a quarter of all OpenAI product engineers. Start of the internal "defense factory": a continuous loop that scans, validates, assigns owners and verifies fixes. Ian quotes a 0.81% false-positive rate.
- 207s: Codex fixes had a rollback rate under 1%. Ships as an open-source plugin, CLI and SDK, plus a cloud version.
- 298s: CLI is open source under Apache 2.0.
- 343-433s: per-scan custom instructions, a cross-scan knowledge base (architecture docs, firewall config), and security.md files committed across components so product owners define their own threat models.
- 524s: a fleet of hundreds of agents across many hosts scanned parts of the code base. 570s: tens of thousands of findings.
- 615s: 36% of findings were duplicates. Dedup workflow now in the CLI.
- 846s: rollback under 1% on auto-generated patches. Kyle ties it to "the 0.81% that Ian mentioned", which conflicts with Ian's false-positive wording, so the Article uses only "under 1%" and drops 0.81%. verify-fix command = "an adversarial agent of sorts against the fix".
- 984s: patch benchmark slide (frame checked). GPT-6 Astra at medium beats GPT-5.6 Sol at x-high at less than half the cost per case. Slide: Astra medium about 62.7% at about 2.4 dollars, Sol xhigh about 61.4% at about 4.9 dollars. OpenAI humans about 50%.
- 1121-1166s: Codex Security Cloud runs Daybreak-class security models, installs from the plugin marketplace, can scan on every commit.
- Supporting: Greg Brockman https://www.youtube.com/watch?v=vdEGZYIvFiI (0s): pointed Astra at OpenAI's own code base and infrastructure, found and fixed a number of very important vulnerabilities. "Always take the latest frontier model and put it into your defensive loop."
- Supporting: CodeRabbit, Harjot Gil https://www.youtube.com/watch?v=ZTxzWJeGFAA (0s): about 2,500 to 3,000 PRs in the last 30 days with Codex. Uses the cyber models internally to pen-test its own platform.

What coverage did (web search): StartupHub, OpenTools, note.com (Duke) and a DevDay live blog cover the cloud product, Daybreak Blue access, the 0.81% / under 1% figures and draft PRs. Mostly missed: the 36% duplicate rate, the security.md ownership files, and the patch benchmark result (medium Astra beats x-high Sol at under half the cost). That is the angle.

## Other items (facts used)
- OpenAI, "What Will You Build With Coding Agents That Don't Quit?" https://www.youtube.com/watch?v=U1IVZy9FhVQ : over 1,000 hours (340s); CI flaky-test agent ran six weeks, 200-word starting prompt (386s); more than 100 PRs per week, more than 1,000 commits, more than 600 Slack messages (479-525s, slide checked); merged more than 213 of its own fixes; most productive in a five-day stretch with no messages from its owner; just under half a million tool calls; more than 5,800 subagent sessions (525s); over 67,000 calls were waiting (572s); about 32 dollars an hour, 16 dollars with GPT-6 Sol (1441s).
- Zenity, Roey Ben Chaim https://www.youtube.com/watch?v=_7P580m4kPY : one tool call becomes a process tree (386s, slide); about 100 malicious skills out of thousands, shut off on skills.sh (433-483s, slide says "~100 skills removed after review"); fake Paperclip org with a credential harvester for SSH, AWS, Azure (674-719s); skills on the same command-and-control server had 1.7 million total downloads (719s); Vercel and Microsoft took it down within 12 hours (772s); treat skills as package dependencies (817s).
- OpenAI Control Room https://openai.com/index/control-room (primary) and The Register https://www.theregister.com/ai-and-ml/2026/11/11/openai-builds-a-kill-switch-for-its-research-models/5309006 : every research workload doing agentic inference must be tied to an approved safety case and gets a job_id; engines ask Control Room before each request; halts output within 35 seconds of a stop decision (cache for inference authorization), aiming for zero; fails closed if Control Room goes down; deployed across research infrastructure.
- OpenAI, "What Comes After Loops?" https://www.youtube.com/watch?v=nAubbmlhPfI : start with one agent, add more only when the work gives a reason (694s); "middle management tax" (1059s); Navier-Stokes solution with 10,000 agents, 2.7 million messages, about 130 billion output tokens (1195s, OpenAI's claim).
- Microsoft, Girish Konda https://www.youtube.com/watch?v=DxP5aW4VknQ : subagent failures are classic distributed-system failures; partial failure returns text that looks like success (98s); 10/1,000 vs 6/600 both 1% (1166s).
- OpenAI Agents API https://www.youtube.com/watch?v=b7l_Dhe1h8M : computer use over the API (430s); three nines of reliability (612s); airline demo, results advisory, hold needs human confirmation, max two concurrent subagents (838s).
- GitHub Copilot SDK https://www.youtube.com/watch?v=STVHfSaSw7o : used in non-coding scenarios much more than coding (45s); inference gateway, agent has no access to credentials (518s).
- ServeTheHome, AMD EPYC Venice https://www.youtube.com/watch?v=hLHDiRi_E2U : up to 256 cores, 512 threads, 5.3 GHz, 16 channels DDR5 MRDIMM, 1.6 TB/s per socket, PCIe Gen 6 (0s); SP7 TDP up to 600 W (424s); MEXT moves cold pages to NVMe (679s); 256 two-vCPU agents per chip, AMD's framing (1863s).
- Alex Ziskind, GMKtec mini PC https://www.youtube.com/watch?v=k7_K34eY9TM : 7,000 dollars with 192 GB (4 TB); two Sparks almost 14,000 dollars (0s); GLM 5.3 157 GB at 14.2 tok/s with 160 GB to the GPU (826s); containers about 4 GB per agent; GMK tops out at two clean agents (7.6 tok/s), Spark runs eight cleanly (17.4 tok/s) (1148-1196s).
- Meta on-call teammate https://www.youtube.com/watch?v=_NBx2NNOuA4 : three-quarters of new code written with AI (0s); level 3 example, 23 items in, 3 need you (430s); fixes only land through normal review and CI, most drafts don't land, no load number yet (851s).
- Tessl, Patrick Debois https://www.youtube.com/watch?v=fTUinMqA1XQ : about 10x more PRs (103s); intent conflict, dollars vs cents (435s); speculative merge trains (483s).
- Vorflux, Prasanna Sankar https://www.youtube.com/watch?v=TlOAhw9t5DA : Rippling founder, raised about 15 million dollars (96s); 3-5 parallel tasks on desktop to 20-30 with cloud agents; bottleneck moved to landing work (528s).
- Allos AI, Ayush Bhardwaj https://www.youtube.com/watch?v=rS36lYuvXQ8 : about 20,000 agent calls, a quarter piped into filters (90s); without pipefail, cargo test piped into head can report success (135s).
- Stephen and Cassandra Chin https://www.youtube.com/watch?v=gbeuC0ud1p4 : PR claimed tests passed while Bun and bunx tsc ran at once (557s); evidence graph cut cost almost in half (1106s). Quality score numbers at 1015s are garbled in the transcript, not used.
- Paper Compute, Brian Douglas https://www.youtube.com/watch?v=vg3JdjGuJwM : about 80,000 sessions, fine-tuned a Qwen 4B model (616s).
- OpenAI plugins https://www.youtube.com/watch?v=pIW_8VyvCuQ : 4,000 plugins (206s); Supabase three times weekly installs after Sign in with ChatGPT (981s); first major MCP client to ship the upcoming MCP events spec (1391s).
- OpenAI Sites https://www.youtube.com/watch?v=QRm7VNMnurA : 8 million Sites hosted, over 70% of OpenAI employees make Sites (65s); built-in SQLite database (297s); WebMCP (933s).
- Tether BotPsy https://huggingface.co/blog/qvac/botpsy : 0.8B model on Qwen3.5-0.8B; BFCL v4 23.4 to 44.0 (Tether's numbers); Apache 2.0 open weights planned.
- OpenProse, Raymond Weitekamp https://www.youtube.com/watch?v=hFNbPmzzcEs : Factorio played by recursive decision models with no generative model (1309s).
- Standard Agents, Justin Schroeder https://www.youtube.com/watch?v=3Krz7Rdd4JI : open spec at standardagentspec.org (803s), agents coupled to a given model; Claude Code built a battery warranty agent in 5 min 21 s (1815s).
- Python Simplified https://www.youtube.com/watch?v=rYElE9GZudA : Qwen + Flux chained with if statements and while loops.
- Careem / dbt https://www.youtube.com/watch?v=uwI2ZnlVAyY : almost 95% of data pipelines AI generated (94s).
- AWS Developers https://www.youtube.com/watch?v=UU2CM7e2MsE : commit or branch first (194s), keep changes small (239s).
- Cline, Ara Khan https://www.youtube.com/watch?v=iK9gmxXyBR0 : GPT-5.6 Sol led a 17-hour harness hill climb with Kimi K3 running evals; found loop detection and background-process issues (747-794s).
- OpenAI GPT-Live https://www.youtube.com/watch?v=jDxKzlGLCas : client delegation to an existing harness; how Codex Voice is built (838-884s).
- GitHub pixel dog https://www.youtube.com/watch?v=w2NrzcVzpC4 : MCP server with shared state, composes tunes (186-371s).

Not used: X posts in the window (roadmap and list threads, hype, a Fermi Paradox prompt test, a Yang-Mills validation link with no readable detail, a CyberOffense benchmark update), the Latent Space Codex workshop write-up (overlaps the DevDay talks), the Australia unsafe-AI story (feed text did not load).
