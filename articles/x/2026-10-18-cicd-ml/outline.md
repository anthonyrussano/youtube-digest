# Outline: 2026-10-18-cicd-ml

1. Hook: "14.1 minutes early" is real, but at that point it catches 54.2% of failures. The useful part is which signals did the work.
2. What the study did (one idea): who/where/when; 194,400 runs, five platforms, 2021-2024, ~21.9% failed; three-part model explained in plain words (tree model, sequence model, language model, a small network that weighs them); 0.974 / 0.940 vs BERT 0.961 / 0.924, gap not tested for significance.
3. What 14 minutes buys (one idea): three checkpoints as bullets; Fig. 3 inline; trade-off; what you can do with 14 minutes; 2-minute survey bar; gap: no false-alarm rate, so auto-cancel is risky.
4. The cheap signals (one idea): Table IV top 5 with plain definitions; Table IV inline; association not cause; top 3 need only timing, logs, runner metrics; independent TravisTorrent study also ranks build duration high.
5. Limits (one idea each bullet): pooled data / no unseen platform; unequal inputs 98 vs 167; no chronological split; cost unsettled; data and code not public (not synthetic per the paper).
6. Monday plan (labelled as my suggestions): usual duration per job; compute three signals at 10/25/50%; no leakage; alert-only and log outcomes; test on newer runs. Diagram inline.
7. Takeaway + question.
8. Sources (short list) instead of "Also this cycle" (single-source request; same as 2026-10-18-opencode).

Jargon to define on first use: AUC-ROC/F1 (kept as scores, compared with BERT), XGBoost, Bi-LSTM, BERT, checkpoint, false alarm, leakage.
