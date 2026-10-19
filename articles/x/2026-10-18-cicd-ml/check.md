# Final check: 2026-10-18-cicd-ml

## Ground truth
Fatima, Khan and Faiz, IJEET 5(1-1): 45-50, published 2026-10-15, DOI 10.57041/86apby39, CC BY-SA 4.0. Every number in article.md was checked against the paper's text, Tables II-IV and Fig. 3 (see research.md). Recomputed: overall failure rate 21.90%, GitHub Actions share 32.05%, BERT/XGBoost training time 14.04x, ensemble-BERT gaps 0.016 F1 / 0.013 AUC, feature groups sum to 167.

## NotebookLM vs paper
Infographic PNG ("Machine Learning Framework for Early CI/CD Pipeline Failure Detection"):
- Matches: 194,400 runs; per-platform failure rates and feature counts; feature-group counts 31/42/28/24/22/20; MLP 512->128->2 and 16-dim context vector; ensemble 0.940 F1 / 0.974 AUC; checkpoint numbers 14.1/8.7/4.3 min and 54.2/78.6/91.3%; Table IV signals and scores.
- **Mismatches in the model bar chart:** BERT F1 0.954 (paper 0.924); LSTM F1 0.839 (paper 0.899); XGBoost F1 0.994 (paper 0.887) and AUC 0.973 (paper 0.934); Decision Tree AUC 0.864 (paper 0.854). XGBoost is also drawn above Random Forest and SVM, implying it is the 5th-best model with near-perfect F1.
- **Verdict: not included inline** (numbers do not all match), not copied to /workspace/cicd-infographic.png.

Slide deck PDF ("Predicting the Break", 15 image-only slides):
- Slide 1: "94.0% F1-Score" is F1 0.940 shown as a percent; acceptable but not how the paper reports it.
- Slide 3: "five major enterprise platforms": the paper says GitHub Actions data came from open-source repositories.
- Slide 5: sample telemetry table and log lines are invented illustrations; "deep learning models are required" and "a single architecture cannot optimally handle both" are not claims the paper makes.
- Slide 6: "XGBoost processes the 167-dimensional structured telemetry" follows the paper's own Fig. 1 label, but the paper's text says classical models (incl. XGBoost) use the 98 selected features. Internal inconsistency in the paper; article uses the text (98 vs 167).
- Slide 7: "If GitLab logs are sparse but GitHub Actions metrics are rich..." is an invented example; the paper reports no gating weights.
- Slide 8: "near-perfect discrimination" overstates; the paper treats differences as descriptive, not significant.
- Slide 9: "requires ~8x the training time of XGBoost" (512.7/63.5 = 8.07) is arithmetic the paper explicitly declines to draw: training-time entries "do not establish" end-to-end cost. XGBoost point is plotted near 75 s, not 63.5 s.
- Slide 10: "the model first estimates the total pipeline duration", the "50.1%" lock and "up to that exact millisecond" are not in the paper (it only requires a duration estimate available at prediction time).
- Slide 11: chart lines extend beyond the three measured checkpoints (to 0% and past 50%), implying data that doesn't exist.
- Slide 13: survey "mandates a minimum two-minute lead time": the paper only says the survey "provides practitioner feedback... including a two-minute actionability criterion"; no survey results are reported.
- Slide 14: "isolate architectural gains from data volume": the paper says representation vs architecture (different feature sets), not data volume.
- Slide 15: "XGBoost, LSTM, and BERT" (ensemble uses Bi-LSTM); "state-of-the-art", "proves a mathematical trade-off" and "the Gating MLP proves" overstate a descriptive study.
- Correct in the deck: Table II values, 21.9%, Jan 2021-Dec 2024, feature groups, AUC values on slide 8, Table IV top 5, limitations on slide 14 (except the data-volume wording).
No NotebookLM-only number is used in the article.

## Images
- img/early-detection-tradeoff.png: Fig. 3, extracted losslessly from the PDF (671x413, original embedded image). CC BY-SA 4.0, credited in alt text and Sources.
- img/feature-importance-table.png: Table IV, cropped from a 300 dpi render of p. 49 (1300x550). CC BY-SA 4.0, credited.
- img/monday-plan.png: diagram-generator spec-batch (spec in img/specs/monday-plan.yaml), rendered with a locally built diagram-gen:local image on the home host; repo tracked files untouched (output/ is gitignored). The rollout half is labelled "not from the paper".
- Attachment PDFs not committed (open license allows it, but the article links the DOI and journal PDF instead).

## Rules
- [x] Angle real, sourced and simple: 14.1 min goes with 54.2% coverage (Fig. 3); no false-alarm rates (Sec. IV-D, V-B); top 3 signals cheap (Table IV); limits from Sec. V.
- [x] "Synthetic data?" answered honestly: the paper describes real enterprise/open-source logs; data only on request, no code, so not independently checkable.
- [x] Monday steps are labelled as suggestions, not paper findings; the leakage warning is the paper's.
- [x] Title names the idea, 94 chars (<=100), no "$<digit>", no "Mind Blow".
- [x] Caption tip-first (from Table IV ranks 1-2), 180 chars (<250), ends "...", no "$<digit>".
- [x] Lead ~658 words (script counts ~878 incl. alt text and Sources); takeaway and closing question present.
- [x] "Also this cycle" replaced by a short "## Sources" list (single-source deep-dive, per request; same as 2026-10-18-opencode).
- Changes in check: none needed in article.md. While drafting, a "the 14-minute warning clears the 2-minute bar" line was left out (survey results are not reported), and the Monday step uses "usual duration" so it reads as our estimate, not the paper's method.
- `./run.sh x-article 2026-10-18-cicd-ml --format deep-dive` printed FORMAT: deep-dive, SOURCE: articles/x/2026-10-18-cicd-ml/article.md. Served at http://127.0.0.1:8765/2026-10-18-cicd-ml.html.

## Header
NASA PIA14415, "A New View of the Tarantula Nebula" (Chandra/Hubble/Spitzer composite), original 3600x2880, not in any `header` field of state/x_posts.json. Saved to /workspace/x-header-2026-10-18-cicd-ml.jpg (not committed).
