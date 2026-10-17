---
title: "Your flaky AI agent might be reading a progress bar"
caption: "Agent tip: if the same task passes one run and fails the next, strip progress bars, timestamps and temp paths from tool output before the model reads it..."
edition: "2026-10-17"
lead_source: "https://x.com/yb2698/status/2111136348480708740"
---
Run the same AI agent on the same task twice. One run passes. The next one fails.

Most people blame the model, and reach for **temperature 0**.

A Hugging Face engineer found something smaller to blame: **a download progress bar**.

Here is the experiment, and the 40-line fix anyone building agents can copy.

## The test

Younes Belkada at Hugging Face asked a simple question: [what happens if you re-run the exact same task N times](https://x.com/yb2698/status/2111136364079325443), with the same model and the same harness?

A **harness** is the code around the model. It holds the tools, the prompt and the loop that runs the agent step by step.

He counted three things: how often pass flips to fail, how many turns each run takes, and how many tokens go in.

The small, minimal harnesses swung the most. **OpenHands was by far the most consistent.**

## Why OpenHands looked calm

The reason was one line. OpenHands [hardcodes temperature to 0.0](https://x.com/yb2698/status/2111136364079325443).

**Temperature** controls how much randomness the model uses when it picks its next word. At 0, it always takes the top choice.

That is where most summaries of this work stopped. It is also the least interesting part.

## The twist

He pushed further: [20 trials on 3 tasks](https://x.com/yb2698/status/2111136379308843239), under three sampling settings, including temperature 0.

At temperature 0, the harnesses tended to open with the same tool. **But every harness stayed very stochastic.** Even OpenHands went from near-perfect on one task to 14 out of 20 on another.

He then [improved the ipython harness three times](https://x.com/yb2698/status/2111136394714522095). Better prompts and fixes made it more accurate and cheaper per attempt.

It was still random at temperature 0. In his words, [even if you force the model to be deterministic, the end result is stochastic](https://x.com/i/status/2111392259099033879).

## The real culprit

The noise was coming from the **environment**, not the model.

When the agent installs a Python package, [one run sees a download at 150.3 MB/s. The next sees 129.3 MB/s](https://x.com/yb2698/status/2111136406882210081).

The model reads every character of tool output. A different number is a different input. Different input can mean a different next step, and that step compounds.

Timestamps and random temp folder names [do the same thing](https://x.com/i/status/2111391001298497540). The tool did the same work. Only the text around it changed.

## The fix

Two parts, and both are boring on purpose.

**1. Quiet the environment.** His [40-line script](https://gist.github.com/younesbelkada/502f2d22cd2768b91fd6d39ad360fa1f) sets variables like `PIP_PROGRESS_BAR=off`, `TQDM_DISABLE=1`, `UV_NO_PROGRESS=1`, `HF_HUB_DISABLE_PROGRESS_BARS=1` and `NO_COLOR=1`.

**2. Normalize tool output.** A few regexes strip terminal colors, progress-bar lines and overwritten lines, and mask transfer speeds, memory addresses and random `/tmp` names.

It only ever **removes or masks** text. It never rewrites what a tool reported.

The [ipython harness is open source](https://github.com/huggingface/ipython-harness) if you want to test it yourself.

## What most people missed

**Temperature 0 is not the fix.** It hid noise in one harness and did not remove it in the others. Hosted models [are not fully deterministic at temperature 0 anyway](https://thenexttoken.net/posts/why-temperature-zero-is-not-deterministic).

**It matters most for small models.** The author says [small models are not robust to these artifacts](https://x.com/yb2698/status/2111136418902974818), and he doubts large models suffer as much. If you run a local model in an agent loop, this is for you.

**Repeatable is not the same as correct.** Clean output makes runs comparable. It does not make a weak harness good. His own conclusion: [pick the best harness for your task and model](https://x.com/yb2698/status/2111136379308843239).

## Takeaway

Before you blame the model for a flaky agent, **diff the tool output from two runs.** If the only differences are speeds, times and temp paths, quiet them and strip them.

What is the noisiest tool output your agent reads every day?

## Also this cycle

- Berkeley found that [periodically resetting research agents to their best result so far](https://x.com/omarsar0/status/2110911109964386460) beats parallel agents by up to 15% on the same budget.
- Corey Ganim keeps [one company brain in plain markdown in private GitHub repos](https://x.com/coreyganim/status/2111490096402677760), so every agent reads the same context.
- Anthropic says [Claude now writes about 90% of Claude Code's own code](https://x.com/ClaudeDevs/status/2111168901723906176), with reverted changes down more than 40%.
- Cursor launched [an Environments API](https://x.com/cursor_ai/status/2111193980981665837) for agents working across up to 500 repos.
- Rohit Ghumare's [15-item security checklist for vibe-coded apps](https://x.com/ghumare64/status/2111332908657148356) runs from SQL injection to row-level security.
