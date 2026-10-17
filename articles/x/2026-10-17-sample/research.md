# Research: 2026-10-17 sample X Article

Edition: `2026-10-17` (website roundup: `reports/2026-10-17.md`). Gathered 2026-10-17 ~4:45 PM PT. Sample only, not posted.

## Lead candidates from the edition
| Candidate | Why it could lead | Coverage elsewhere | Verdict |
|---|---|---|---|
| Hugging Face harness nondeterminism (yb2698 thread) | Practical, actionable fix any agent builder can apply today | Thread head ~380 impressions; AINews one-liner; our roundup one sentence. Nobody explained the fix. | **Lead** |
| Corey Ganim markdown knowledge base | Actionable, popular | 53k impressions, 1.6k bookmarks; already our 2026-10-17 caption | Widely covered: Also |
| Berkeley "forced forgetting" for research agents | Counter-intuitive, practical | 12k impressions on omarsar0; covered by AINews | Also |
| DeepSeek V4.1 Flash, Gemini Minecraft run | Big news | Everyone covered it | Not practical enough to lead |

## Raw facts: the lead (all from the primary thread unless noted)
Source thread by younes (@yb2698, Hugging Face), 2026-10-16 9:45 AM PT:
- Head: https://x.com/yb2698/status/2111136348480708740 "Getting complete different results when running the same task N times? Are some harnesses stochastic?"
- Setup: https://x.com/yb2698/status/2111136364079325443 Re-run the exact same task N times with the same model and harness. First pass: 3 runs per task, measuring pass/fail flips, number of turns, input tokens. Minimal harnesses (ipython, pi) varied a lot; OpenHands was by far the most consistent. Reason found: OpenHands hardcodes `temperature: float = Field(default=0.0)`, while the experiment used default sampling for the others.
- Deeper run: https://x.com/yb2698/status/2111136379308843239 20 trials x 3 tasks, three sampling settings (greedy temperature 0, model-recommended, harness defaults). Task `pandas-etl` had the most disparity. Result: OpenHands still the most consistent, at temperature 0 all harnesses tend to pick the same opening tool, **but overall all harnesses remain very stochastic**: pass rates vary a lot within a task and across tasks (OpenHands goes from near-perfect on one task to 14/20 on another; a 0/20 is an OpenHands+Harbor bug). Author's framing: "pick the best harness for your task x model".
- Harness fixes: https://x.com/yb2698/status/2111136394714522095 Built on the ipython harness (the most stochastic). v0: bare ipython, kernel separate from the task kernel, model got confused and re-ran. v1: fixes that plus empty ipython results. v2: richer system prompt (e.g. `%%writefile`) and asks the model to verify before finishing. v0 to v2 greatly improved performance and average cost per attempt, **but runs stayed stochastic even at temperature 0**. Then "a very simple trick fixed this": normalizing tool outputs.
- The trick: https://x.com/yb2698/status/2111136406882210081 Same task, different tool output: a pip download line shows `150.3 MB/s` once and `129.3 MB/s` the next time. Fix = a "normaliser" (regex filtering on tool outputs) plus a "quiet env" that removes artifacts. "A simple 40-liner python script": https://gist.github.com/younesbelkada/502f2d22cd2768b91fd6d39ad360fa1f
- Scope: https://x.com/yb2698/status/2111136418902974818 Makes sense for **small models**, which are not robust to such artifact changes; author doesn't think large models suffer from it. If you build a harness for a small model, be careful. Harness open-sourced: https://github.com/huggingface/ipython-harness
- Replies (2026-10-17): https://x.com/i/status/2111392259099033879 temperature 0 was a controlled experiment: "even if we force the model to have a deterministic behavior, the end result will be stochastic". https://x.com/i/status/2111391001298497540 tools should return deterministic results; what changes is the output form (timestamp, temp folder name, other artifacts).

The gist (fetched): `QUIET_ENV` sets `PIP_PROGRESS_BAR=off`, `PIP_DISABLE_PIP_VERSION_CHECK=1`, `TQDM_DISABLE=1`, `HF_HUB_DISABLE_PROGRESS_BARS=1`, `UV_NO_PROGRESS=1`, `npm_config_progress=false`, `NO_COLOR=1`. `normalize()` strips ANSI escapes, carriage-return overwritten text, lines of progress-bar glyphs; masks transfer speeds (`MB/s`), memory addresses (`at 0x...`) and random `/tmp` suffixes. Docstring: "Deterministic, idempotent, and only ever removes or masks text."

Context (secondary, linked if used):
- Why temperature 0 itself isn't deterministic on hosted APIs: batch-dependent floating-point kernels (https://thenexttoken.net/posts/why-temperature-zero-is-not-deterministic, Oct 13 2026; cites Thinking Machines Lab's 80 distinct completions from 1,000 runs).
- OpenHands RFC on dropping hardcoded temperature 0: https://github.com/OpenHands/software-agent-sdk/issues/1913

## What others covered vs. missed
- Covered: AINews and our own roundup reduced it to "OpenHands looks stable mainly because it hardcodes temperature 0; normalizing tool outputs fixes much of the variance". X search (harness/openhands + stochastic/deterministic, since Oct 16) found generic "use a deterministic harness" opinion posts, no one explaining this thread.
- **Overlooked / under-explained:**
  1. The headline people repeat (temperature 0) is the *red herring*: the author's own point is that temperature 0 does **not** make the agent repeatable.
  2. The real noise source is the *environment*: progress bars, download speeds, timestamps, temp paths. The model reads them as input, so tiny differences change the next step.
  3. The fix is cheap and copyable (40 lines, env vars + regex), and it only removes text.
  4. Nuance: mainly a small-model problem, per the author; and repeatability is not correctness (pass rates still swing per task: "pick the harness for your task x model").
- Angle: **"Your agent's flaky runs may come from a progress bar, not the model."**
