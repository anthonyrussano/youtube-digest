# Research: 2026-10-18-cicd-ml

## Primary source (ground truth)
Sana Fatima, Muazzam Khan, Shayan Faiz (Department of Software Engineering, NED University of Engineering and Technology, Karachi). "An Intelligent Machine Learning Framework for Early Detection of CI/CD Pipeline Failures." *International Journal of Emerging Engineering and Technology* (IJEET), ISSN 2958-3764, vol. 5, no. 1-1, pp. 45-50, 2026. Received 17/08/2026, revised 09/10/2026, accepted 12/10/2026, published 2026-10-15.
- DOI: https://doi.org/10.57041/86apby39 (resolves to the journal page)
- Journal page: https://grsh.org/journal1/index.php/ijeet/article/view/218
- PDF: https://grsh.org/journal1/index.php/ijeet/article/download/218/120
- License: CC BY-SA 4.0 (PDF footer and journal page). Figures may be reused with attribution; derivatives share-alike.

## Facts from the paper (page numbers are the journal's)
- Data: 194,400 executions, Jan 2021-Dec 2024, via APIs and webhooks: enterprise Jenkins clusters, open-source GitHub Actions repos, organizational GitLab CI/CD namespaces, commercial Azure DevOps projects, containerized CircleCI projects (p. 47). Not described as synthetic. Data "available on reasonable request"; no code link.
- Table II: Jenkins 48,500 / 23.4% / 142 features; GitHub Actions 62,300 / 18.7% / 167; GitLab 35,200 / 27.1% / 153; Azure DevOps 29,800 / 21.3% / 138; CircleCI 18,600 / 19.8% / 124. Implied overall failure rate ~21.9% (recomputed: 42,568.5 / 194,400 = 21.90%). GitHub Actions share ~32.0% (recomputed 32.05%).
- Cleaning: dedupe by run id + content hash; drop records >15% missing; kNN imputation; UTC timestamps; SMOTE for imbalance.
- Features: 167 candidates in six groups: build metrics 31, log semantics 42 (TF-IDF, 5,000-token vocab, first 500 log messages, 87 error keywords), resource 28, test 24, code changes 22, dependencies/environment 20 (sum = 167). Mutual information >= 0.01 -> 143, RFECV -> 98. Classical models use 98; deep models use 167.
- Models: LR, DT, RF, XGBoost (200 Bayesian-opt iterations), SVM-RBF, LSTM (2x256, dropout 0.3), Bi-LSTM, BERT-base-uncased (12 layers, 768), ensemble (XGBoost probs + pooled Bi-LSTM state + BERT CLS; MLP 512->128->2, GELU, layer norm; softmax gating on a 16-dim platform/project context vector). Log tokens max length 512.
- Early-detection protocol: checkpoints at 10/25/50% of *estimated* duration; only features available at prediction time; final duration/future test outcomes would leak. Isotonic calibration + alert threshold. Lead time = alert timestamp to recorded failure timestamp. Survey of 48 DevOps engineers "provides practitioner feedback on warning lead times, including a two-minute actionability criterion" (no survey results reported).
- Setup: 2x A100 40GB, 256 GB RAM, 64 EPYC cores; Python 3.11, PyTorch 2.2, sklearn 1.4, Transformers 4.39. Stratified five-fold CV. Differences "not treated as statistically significant".
- Table III (P / R / F1 / AUC / train s): LR .781/.764/.772/.831/12.4; DT .803/.791/.797/.854/8.7; RF .876/.869/.872/.921/47.2; XGBoost .891/.883/.887/.934/63.5; SVM .858/.841/.849/.907/124.8; LSTM .903/.896/.899/.947/312.6; Bi-LSTM .914/.908/.911/.953/478.3; BERT .927/.921/.924/.961/891.4; Ensemble .943/.937/.940/.974/512.7. Ensemble-BERT gaps 0.016 F1, 0.013 AUC; BERT/XGBoost train time 14.0x (recomputed 14.04).
- Fig. 3: detection 54.2% / 78.6% / 91.3% at 10/25/50%; mean lead 14.1 / 8.7 / 4.3 min. Lead-time SD 2.4 min (25%) and 1.8 min (50%); no SD given for 10%. Detection rate counts failing runs only; does not quantify false alarms.
- Table IV: build duration deviation .187, error keyword frequency .163, CPU spike ratio .141, test failure rate .129, cyclomatic complexity delta .112, dependency resolution time .098, artifact download failure .087, container resource OOM .083. Association, not cause.
- Limitations (Sec. V): no leave-one-platform-out; repository-grouped and chronological holdouts needed; unequal feature sets; leakage risks; calibration/threshold need separate data; false-positive rates, alerts per run and operational costs not quantified; concept drift; end-to-end compute cost unresolved; replication needs data access.
- Internal inconsistency: Fig. 1 labels "Numeric Features (167 dimensions)" feeding XGBoost and Bi-LSTM, while the text says classical models (incl. XGBoost) use 98 selected features. Also not explained: the ensemble's 512.7 s training entry is lower than its BERT component's 891.4 s (paper only says accounting boundaries differ).

## NotebookLM materials (not trusted; checked in check.md)
- 15-slide deck PDF (image-only, "Predicting the Break") and the infographic PNG. Several numbers and claims do not match the paper (see check.md). The infographic's model-performance bar chart has wrong values, so it is not used.

## Coverage scan (Oct 18, 2026)
- Web: only the journal page and DOI landing page carry the paper. No news or blog coverage found.
- X: searches for the paper's topic and numbers returned no posts.
- Related, not coverage: Information (MDPI) Feb 2026, multi-class XGBoost on TravisTorrent, SHAP ranks build log status and build duration among top features: https://www.mdpi.com/2078-2489/17/2/178
- What summaries (incl. NotebookLM) lead with: 0.974 AUC, 94% F1, "14-minute warning". What they under-explain: 14.1 min comes with only 54.2% coverage, no false-alarm/precision numbers per checkpoint, the top signals are cheap to compute, and generalization/cost are explicitly unestablished.

## Candidates
| Angle | Why lead | Coverage | Verdict |
|---|---|---|---|
| "AI predicts CI failures with 97% AUC" | headline number | what NotebookLM leads with | no: overstated, gap vs BERT not significant |
| What 14 minutes buys + missing false-alarm rate | practical, honest | not covered | yes (part 1) |
| Cheap top signals you can compute today | actionable | not covered | yes (part 2) |
| Ensemble architecture deep-dive | technical | NotebookLM slides | no: not actionable for most teams |

## Chosen angle
The 14-minute warning only catches about half of failures and the paper publishes no false-alarm rate, but its top signals (run slower than usual, error keywords, CPU spikes) are cheap, so a team can test an alert-only version on its own CI logs before any big model.
