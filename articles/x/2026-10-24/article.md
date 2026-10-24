---
title: "The provider serving your open model matters more than open vs closed. Ollama's CEO showed the numbers and three cheap ways to check."
caption: "Running a coding agent on an open model through a third-party API? Ping it with a one-token log-prob probe every day, because the worst endpoint for the same weights scored 72% of the best one..."
edition: "2026-10-24"
lead_source: "https://www.youtube.com/watch?v=mHNKuH-9OxU&t=2886s"
---
Everyone argues about how far open models trail closed ones. At YC's inference night, Ollama founder and CEO Jeffrey Morgan argued that's the wrong gap to worry about. For open models, [the gap between the worst and best provider serving the same model is bigger than the gap between open and closed](https://www.youtube.com/watch?v=mHNKuH-9OxU&t=2886s).

[[IMG: /workspace/2026-10-24-1-provider-gap.png | Slide from Jeffrey Morgan's talk at YC Paper Club (YouTube): best open model at 79% of the best closed model, while the worst of 14 gpt-oss-120b endpoints scores 72% of the best]]

## Same weights, different model

His slide puts numbers on it. On the Artificial Analysis Intelligence Index, the best open model sits at **79%** of the best closed model. Across **14 endpoints serving gpt-oss-120b**, the worst endpoint scores **72%** of the best one. A 2024 study of 31 Llama endpoints found some behaving closer to GPT-3.5 than to the same weights served elsewhere.

The causes he listed are [mostly boring](https://www.youtube.com/watch?v=mHNKuH-9OxU&t=2793s):

- Over-quantized weights, faulty hardware, or a different version of the weights
- Tool-call parsing that breaks at the tokenizer level, or loose schema enforcement
- Different sampling, custom kernels, or KV cache precision that only bites at long context
- Models [served under the wrong name](https://www.youtube.com/watch?v=mHNKuH-9OxU&t=2850s), which is hard to spot because every model is "a friendly assistant trying to help you"

## Why agents feel it most

Chat users might never notice. Agents will. Morgan's math: a 10% deviation per call compounds to [as much as 79% wrong over a 15-step coding task](https://www.youtube.com/watch?v=mHNKuH-9OxU&t=2995s).

## Three cheap checks

Full benchmark runs catch bad quantization, but they're [expensive and slow](https://www.youtube.com/watch?v=mHNKuH-9OxU&t=3080s), so nobody runs them every day. His cheaper options:

- **Reference distribution test.** Send the same prompts to a reference model and the endpoint and compare outputs. About [a dollar per test](https://www.youtube.com/watch?v=mHNKuH-9OxU&t=3158s), but it won't tell you why things differ.
- **Log-prob drift.** A [one-token request on a schedule](https://www.youtube.com/watch?v=mHNKuH-9OxU&t=3192s), compared with yesterday's log-probs, flags redeploys and engine upgrades.
- **Shape monitoring.** Track tool-call pass and error rates and output lengths, which [catches infinite-loop run-ons](https://www.youtube.com/watch?v=mHNKuH-9OxU&t=3276s) without storing any request data.

[[IMG: /workspace/2026-10-24-2-logprob-drift.png | Slide from Jeffrey Morgan's talk at YC Paper Club (YouTube) on log-prob tracking (Chauvin et al., ICLR 2026): one-token probes cost about 1/1,000th of an eval and found 37 suspected silent changes across 189 endpoints]]

The log-prob paper he cited (Chauvin et al., ICLR 2026) found **37 suspected silent changes across 189 endpoints from 10 providers, 34 of them on open-weight models**, at about a thousandth of the cost of an eval. The catches: plenty of APIs no longer return log-probs, and drift only tells you something changed. If the endpoint was wrong on day one, your baseline is wrong too.

## What to do with this

- Pick your provider with an eval, then keep that run as your baseline.
- Add a daily one-token log-prob probe if the API supports it.
- Alert on tool-call error rate and output length, per provider.
- Re-run the eval when the probe moves.

## Also this cycle

- OpenCode's breach hit [1.4% of console users](https://www.youtube.com/watch?v=9OahTki4cPA&t=131s), and the keys fed a distillation ring. Dax says the always-on agent defense costs [at least several thousand dollars a day](https://www.youtube.com/watch?v=9OahTki4cPA&t=562s).
- Arize showed a one-line "confirm before any action" prompt change that gave [+17 on safety and −17 on task completion](https://www.youtube.com/watch?v=v5tm5EAzsAs&t=214s). Gate prompt PRs on evals in CI.
- LangChain's Deep Agents [offloads tool results over about 20,000 tokens to files](https://www.langchain.com/blog/context-engineering-deep-agents-remember) and summarizes at 85% of the window.
- Bridgewater hand-built about 200 search test questions in under a week and took [precision at 10 from about 60% to 90–95%](https://www.youtube.com/watch?v=CLve4Nx_RwI&t=538s).
- SGLang's three-tier KV cache across GPU, host memory and storage [cut time to first token by 56%](https://www.youtube.com/watch?v=mHNKuH-9OxU&t=5982s).
- The creator of Claude Code on desktop [has left Anthropic](https://x.com/amorriscode/status/2113972174524674247).

Have you ever caught a provider silently changing the model behind your endpoint, and how did you notice?
