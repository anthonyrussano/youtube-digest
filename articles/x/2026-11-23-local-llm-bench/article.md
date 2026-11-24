---
title: "Qwen stays my daily local default after a head-to-head with Inkling 2 Mini"
caption: "If your Inkling client uses chat completions, send each earlier turn's reasoning_content back. The tool-call retest stayed at 24 out of 24 and finished about 21% faster..."
caption_shape: tip
edition: "2026-11-23-local-llm-benchmark"
lead_source: "https://cursor.com/canvas/store-3c3759d9-f865-41ac-873b-0630b7e62cc3/94da9ecd-b1d1-4a75-bed7-b4f0be009450"
cover_idea: "A clean split graphic of the 100K prompt-read bars, teal Qwen at 280 s on the left and rust Inkling at 694 s on the right, with the model names and 'iconium, 23 November 2026' underneath. If we keep the usual X Article header, use a fresh NASA Earth still and lead the body with that 100K chart."
---

I ran Qwen3.8 Flash Next and Inkling 2 Mini on the same local box, with the same prompts and seeds. Accuracy was a tie. Speed was not. Qwen stays the default.

## The box, as deployed

The machine is iconium, a Beelink GTR9 Pro. It uses an AMD Ryzen AI MAX+ 395 with a Radeon 8060S, and it has 32 threads. I measured both models on 23 November 2026, Pacific Time, through llama.cpp, a local inference engine. One model sat on the GPU at a time. The two services cannot share it.

Qwen ran at a 128K context window, the amount of text the model can hold at once. It used 91.0 to 91.2 GB of 103 GB of VRAM, with about 12 GB free. Inkling used about 23 GB. Qwen ran with thinking off. Inkling ran with thinking on. This compares the two services as I actually use them, not two models under identical decoding.

[[IMG: /workspace/bench-assets/card-hardware.png | Hardware card for iconium: AMD Ryzen AI MAX+ 395 with Radeon 8060S, 32 threads, measured 23 November 2026, Pacific Time]]

[[IMG: /workspace/bench-assets/table-setup.png | Setup table comparing Qwen3.8 Flash Next and Inkling 2 Mini builds, context, thinking, and sampling]]

## Accuracy was a tie

The homemade tests were 60 core reasoning items, 18 hard items, 24 tool-call scenarios, long-context recall, speed probes, and 7 Codex tasks. Codex here is the local coding-agent profile I use with these models.

At baseline, Qwen scored 59/60 and 18/18. Inkling scored 60/60 and 17/18. Both got 24/24 tool calls. Both got 21/21 on Codex across three reps. Both models sit at or near a perfect score, so a one-item gap is noise.

Qwen was faster on the baseline clock. It wrote at 37.5 and 44.7 tokens per second (tok/s, the rate it reads a prompt or writes a reply). Inkling wrote at 30.1 and 30.2 tok/s. On Codex, Qwen's median was 79 seconds. Inkling's median was 105 seconds.

[[IMG: /workspace/bench-assets/table-baseline-scorecard.png | Baseline and tuned scorecard for reasoning, tools, long context, speed, and Codex]]

## Speed, then a 128K window

The speed probes tell the same story on prompt reading, which is how fast the model ingests the input.

[[IMG: /workspace/bench-assets/chart-prompt-read-8k-16k.png | Grouped bars of prompt-read speed at 8K and 16K for Qwen baseline, Qwen b12651 at 128K, and Inkling]]

[[IMG: /workspace/bench-assets/chart-output-toks.png | Grouped bars of output speed on two generation probes for Qwen baseline, Qwen b12651 at 128K, and Inkling]]

Then I moved Qwen to llama.cpp b12651 and raised its window from 32K to 128K. Prompt reading got 8 to 13% faster: 591 vs 521 tok/s at 16K on the 64K unit, and 590.5 tok/s at 16K with 128K. Accuracy stayed at 59/60 and 24/24.

The long-context edge Inkling used to hold is gone for everyday work. On the new build, Qwen recalled 5/5 items at 48K, 60K, 80K, 100K, and 120K. The scorecard lists a 100K-token prompt read in 281 seconds, versus 694 seconds for Inkling. The context chart displays that pair as 280 s and 694 s, from values of 280.3 and 693.6. Inkling's recall was also perfect through 100K, but its prompt-read rate falls off harder as the input grows.

[[IMG: /workspace/bench-assets/chart-prompt-read-vs-tokens.png | Scatter plot of prompt-read tokens per second versus prompt length for Qwen baseline, Qwen at 128K, and Inkling]]

[[IMG: /workspace/bench-assets/chart-100k-read-time.png | Bar chart of 100K prompt-read time: Qwen 280 s versus Inkling 694 s]]



## Inkling's thinking knob

Inkling's main tradeoff is thinking effort. High was the original default. It scored 60/60 and 17/18, and took 2,352 seconds in all. Medium is now the service default. It scored 60/60 and 18/18, which is 78/78, and finished in 1,343 seconds. The core 60 finished about 40% faster than high: 753 seconds vs 1,261 seconds. Medium is the only setting that got all 78 items right.

Low is what the Codex profile sends on purpose. It scored 59/60 on the core set and 18/18 on the hard set, and finished in 918 seconds. The hard 18 took 405 seconds, versus 1,091 seconds at high.

[[IMG: /workspace/bench-assets/chart-inkling-thinking-time.png | Bar chart of Inkling combined wall time at low 918 s, medium 1,343 s, and high 2,352 s]]

[[IMG: /workspace/bench-assets/table-thinking-effort.png | Inkling thinking effort table for core 60, hard 18, combined score, and wall time]]


## A leaner Codex prompt, and what I did not keep

I also trimmed the Codex setup prompt for both local models. The opening prompt fell from about 13.9K tokens to about 7.0K for Qwen and 8.2K for Inkling. Inkling's median input tokens per task fell from 61,489 to 38,494 in the final run.

On one tuned pass each, both models went 7/7. Both had a 66-second median. Qwen's total was 443 seconds. Inkling's total was 493 seconds. Codex wall times vary by about 50% from run to run, so I treat that single-rep final as a check, not a precise ranking. The firmer Codex result is still the baseline: 21/21 for both, with medians of 79 and 105 seconds. Codex already sends Inkling's thinking back, so these Codex numbers stand.

[[IMG: /workspace/bench-assets/table-codex-matchup.png | Final tuned Codex matchup, seven tasks, both models 7/7 with a 66-second median]]

[[IMG: /workspace/bench-assets/table-what-was-tried.png | Tuning table of every change that was tried, with the result and whether it was kept]]

## Send Inkling's thinking back

Inkling's chat template needs each earlier assistant turn's reasoning_content, the hidden thinking from that prior turn, to be sent back. Codex already does that, and llama.cpp renders it, so the Codex numbers stand.

The original tool-call script did not. [@net_termina](https://x.com/net_termina/status/2124952437522149445) raised this after a scoring gap that only made sense once he read the official model card warning. A paired retest at medium thinking still scored 24/24 either way. Keeping reasoning_content finished in 188.6 seconds versus 239.3 seconds, about 21% faster. The original baseline and low tool-call times, 349.1 seconds and 180.9 seconds, used the drop-style harness and were not rerun. Any custom client that talks to Inkling over chat completions should send reasoning_content back.

[[IMG: /workspace/bench-assets/table-thinking-preservation.png | Thinking-preservation table: Codex already sends Inkling thinking back; the tool-call script did not, and keeping it cut 239.3 s to 188.6 s]]

## Qwen thinking stays off

I also probed Qwen with thinking on, on a temporary unit. It used the same flags as the service minus `--reasoning off`, plus Qwen's thinking-mode sampling (temp 0.6, top-p 0.95). The service default is unchanged. Codex kept Qwen's thinking across turns.

On the hard 18, both settings scored 18/18. Thinking off took 319 seconds. Thinking on took 324 seconds. On three Codex tasks, t1, t4, and t7, both went 3/3. Thinking off finished in 210 seconds (80, 76, and 54). Thinking on finished in 390 seconds (83, 128, and 180), about 1.9 times slower, with 2.3 times the output tokens (12.4K versus 5.4K). Thinking adds no accuracy here, because both are already at the ceiling, so I keep `--reasoning off` as the default.

[[IMG: /workspace/bench-assets/table-qwen-thinking.png | Qwen thinking on versus off: hard 18 stayed 18/18, and Codex on three tasks went from 210 s to 390 s]]

## The 680-second first Codex run

An earlier Inkling smoke test spent 680 seconds on the first Codex run. That was not a cold start. Model load is 5 to 8 seconds. The second request of that session was 90,929 tokens, against a normal first request of about 14K. Reading it took 475 seconds at 191 tok/s. The most likely cause is that Codex sent its full app and connector tool list on that first-ever session. That happened after a "failed to initialize model catalog" error. It did not show up again in 40 or more later runs. The lean Codex profile removes app tools entirely.

## A smoke signal from gBench

I also ran [gBench](https://github.com/google-deepmind/gbench) 0.5.0.post1, Google DeepMind's public eval suite, against each live service. The sample counts are tiny, so treat these as a smoke signal, not a leaderboard. CRUXEval caps every reply at 100 tokens, which is unfair to a thinking model. AIME 2026 is the newest, hardest set.

Qwen scored 14/14 on the Golden Set's 14 text checks. On CRUXEval it scored 66.7% on output prediction and 66.7% on input prediction. Twenty of 60 replies in each half hit the 100-token cap. That was six problems times 10 attempts per half. On AIME 2026, one problem times 4 attempts with an 8,192-token cap, Qwen got 1 out of 4 correct, so pass@4 is yes. One of the four attempts hit the cap. Each attempt took about 3 minutes.

Inkling scored 13/14 on the Golden Set. The only miss is safety_boundary, a grader false negative. Inkling did refuse, with "I can’t help...", but a curly apostrophe made the grader's ASCII "can't" match miss, so that is effectively 14/14. Inkling's CRUXEval job was not run. It was dropped for time, and the 100-token cap would truncate its thinking anyway. Inkling has no AIME score. All 4 attempts ran to the 8,192-token cap, about 295 seconds each, and were still thinking. The run was stopped during gBench's last-chance retries. A fair AIME run for Inkling needs a 32K or larger output cap, about 20 minutes per attempt at 28 tok/s.

Once the real tokenizers were installed, both models passed all 4 chat-template checks, so neither template leaks.

[[IMG: /workspace/bench-assets/table-gbench.png | gBench results: Qwen 14/14 Golden, CRUXEval 66.7% on both halves, AIME 1/4; Inkling 13/14 Golden, effectively 14/14, no AIME score because every attempt hit the 8,192-token cap]]

## What I run day to day

I keep Qwen as the default for chat, tools, Codex, and long documents, with thinking off. It is faster at prompt reading and generation in every measured config, and it now has the same 128K window Inkling has. I reach for Inkling when I want a second opinion on tricky reasoning, at medium thinking, where it scored 78/78. I also reach for it when Qwen's memory headroom matters.

My take: Qwen stays the daily default on this box, with thinking off, and Inkling stays the second opinion, with thinking set to medium.

If you run a local pair like this, what is your default today: the faster model with thinking off, the thinking model at medium, or a cloud fallback?

Share this with the teammate who is picking a daily local model for a box like this.

I write up local inference results and the AI and DevOps news that changes how you build. Follow [@russano](https://x.com/russano) for the next one.
