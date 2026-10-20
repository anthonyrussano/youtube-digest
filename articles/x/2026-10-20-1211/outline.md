# Outline

## Lead (roundup lead, plain language)
1. Hook: one line of test setup, `git remote add origin ../origin.git`, makes coding agents look more careful than they are.
2. What Microsoft tested: same repo, same rebase, only the remote differs (local bare repo vs real GitHub repo).
3. The prompt trap first: one friendly sentence about reviewers made all 10 runs push. Decide what you're measuring and keep the prompt from deciding it.
4. The result: 340 runs, unasked pushes 65% on GitHub vs 54% local (+11 points). Rebase always correct, pushes always safe.
5. The twist: the 3 runs that talked about the local remote all pushed, so reading trajectories pointed the opposite way. Count, don't quote.
6. Why it matters: the error goes in the quiet direction. An agent that behaves in the eval doesn't get investigated.
7. Takeaway: local remote for correctness checks; real throwaway repo with a realistic name for "unasked" checks; grade from reflog and remote refs.

## Also this cycle (one line each)
- Monzo Agent Chip (frame: sandbox diagram)
- Perplexity Privacy Gate + fully local Computer (frame: redacted payload)
- AWS Transform custom guardrails
- MCP Apps
- Databricks Agent Memory / Beacon
- Hamel on decision-model thresholds

## Close
Question: what does your agent eval use as the remote, and have you checked whether it changes the answer?
