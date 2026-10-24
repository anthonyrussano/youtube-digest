# Research: 2026-10-24

Lead: Jeffrey Morgan (Ollama), YC Paper Club "inference stack" night, https://www.youtube.com/watch?v=mHNKuH-9OxU
- [2783–2861] causes of provider differences: over-quantized weights, faulty hardware, different weight versions, tool-call parsing at tokenizer level, schema enforcement, sampling, custom kernels / KV cache precision (shows up at long context), models served under the wrong name.
- [2886–2906] "the gap between the worst provider for a model and the best provider is actually bigger than the gap between closed and open models."
- Slide at ~2900: Artificial Analysis Intelligence Index v4.3 (Oct 2026): best open = 79% of best closed; Endpoint Accuracy Index, gpt-oss-120b across 14 endpoints: worst endpoint = 72% of best.
- [2954–2972] 2024 paper tested 31 Llama endpoints; some behaved closer to GPT-3.5 than the same weights elsewhere.
- [2979–3024] agents compound it: 10% deviation over a 15-step coding task -> up to 79% wrong.
- [3048–3092] full evals (Artificial Analysis runs them) catch bad quantization but are expensive and slow.
- [3152–3187] reference distribution test: ~a dollar per test; doesn't explain why; needs a reference model running.
- [3192–3272] log-prob drift: single next-token request vs baseline, catches redeploys/engine upgrades; slide: Chauvin et al., ICLR 2026, ~1/1,000th the cost of an eval, 37 suspected silent changes across 189 endpoints from 10 providers, 34 on open-weight models; cons: needs log-probs from the API, detects drift only (useless if the baseline was already wrong).
- [3276–3318] routers watch tool-call pass/error rates and output-length shape without retaining data; catches infinite-loop run-ons.

Also-this-cycle sources: OpenCode/Dax via ThePrimeTime (9OahTki4cPA 131, 198, 531, 562); Arize (v5tm5EAzsAs 214, 680); LangChain Deep Agents blog; Bridgewater Vault (CLve4Nx_RwI 538); SGLang (mHNKuH-9OxU 5982); Luminal (mHNKuH-9OxU 3980); Claude Code desktop creator leaving (x.com/amorriscode/status/2113972174524674247).
