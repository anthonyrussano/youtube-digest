# Final check: 2026-10-20-1211 (roundup)

- **Research summary:** the lead comes from one primary source (Microsoft for Developers, Waldek Mastykarz, Oct 20, 2026) with full numbers: 340 runs, 111/170 vs 92/170, p = 0.033, per-tool split, the 10/10 prompt trap, the three quoted trajectories, and the authors' caveats (1-22 point range, one model, one repo). Every number in the lead is in that post.
- **Overlooked angle is real:** the post's headline is "mostly, a local remote is fine." The useful part is the direction of the error (agents look *safer*), the prompt trap, and that the quoted trajectories point the opposite way to the counts. Explained in plain language without eval jargon; "bare repo", "reflog" and "force-with-lease" are either explained by context or used only as concrete names.
- **Outline tightened:** dropped a planned paragraph on the eval-awareness papers (kept to one implied line, "when the remote looked like a test") to keep the lead under ~550 words.
- **Rules:** title names the lead idea (not a list). Caption is tip-first, 114 characters, ends in "...", no "$" followed by a number, no banned style name. Roundup shape: in-depth lead, then a short bulleted "Also this cycle" (6 one-liners), then a closing question.
- **Images:** two video frames, both at the timestamp the nearby text links:
  - kind video-frame, `/workspace/2026-10-20-1211-1-monzo.png`, source_url https://www.youtube.com/watch?v=adfw3xJBx1o&t=384s, timestamp 384 s (AI Engineer talk slide: orchestration, sandbox, isolated namespace, Monzo MCP server). Not a talking head; slide is the main content.
  - kind video-frame, `/workspace/2026-10-20-1211-2-privacy.png`, source_url https://www.youtube.com/watch?v=8FEm8mMzeLE&t=494s, timestamp 494 s (Alex Ziskind, Perplexity "Process files locally" view with REDACTED fields). Sample data per the video, not real personal data.
- **Sourcing:** Ziskind's test is labeled as sponsored by Perplexity; Databricks' tripled pass rate is attributed to Databricks and its internal tasks.
- **Changes made:** caption shortened from 133 to 114 characters ("Local remotes hide unasked pushes...") to fit the ~120 limit; format.txt line 3 updated to match.
- `./run.sh x-article 2026-10-20-1211 --dry-run` prints `FORMAT: roundup` and `SOURCE: articles/x/2026-10-20-1211/article.md`.
