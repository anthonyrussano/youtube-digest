# Outline: one core idea at a time

Core idea: an agent's run-to-run randomness often comes from noisy tool output, not the model; clean the output and runs get repeatable.

1. **Hook (overlooked angle).** Same task, same model, different result. The usual answer is temperature 0. Hugging Face found a pip progress bar matters more.
2. **The experiment, plainly.** Re-run the same task 20 times. Count pass/fail flips, turns, tokens. Define "harness" = the code wrapped around the model (tools, prompt, loop).
3. **Why OpenHands looked stable.** It hardcodes temperature 0. Define temperature: how much randomness the model uses when it picks the next word.
4. **The twist.** At temperature 0 every harness was still stochastic. Pass rates swung (14/20 on one task). Even the improved ipython harness stayed random.
5. **The real culprit.** Tool output differs each run: 150.3 MB/s vs 129.3 MB/s. The model reads every character, so a different number can send it down a different path.
6. **The fix.** Quiet the environment (env vars) + a normaliser (regex that strips bars, colors, speeds, temp paths). 40 lines, only removes text. Show the env vars.
7. **What people miss / nuance.** Mostly small models; repeatable is not correct; still pick harness per task and model.
8. **Takeaway + CTA.** Before blaming the model, diff two tool outputs. Question: what's the noisiest tool output your agent reads?
9. **Also this cycle** (5 one-liners with links): Berkeley forced forgetting; markdown brain; Claude writes 90% of Claude Code; Cursor Environments API; vibe-code security checklist.
