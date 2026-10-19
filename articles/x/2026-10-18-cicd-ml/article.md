---
title: "Catching CI failures 14 minutes early works for about half of them. Start with 3 cheap signals"
caption: "CI tip: flag any running job that is far slower than its usual time, or whose early logs fill up with error keywords. In a 194,400-run study those were the top 2 failure signals..."
edition: "2026-10-18-cicd-ml"
lead_source: "https://doi.org/10.57041/86apby39"
---
A new paper says it can warn you about a failing CI/CD pipeline **14.1 minutes before it fails**.

That number is real. It's in [the paper](https://doi.org/10.57041/86apby39). But read the number next to it: at that point the model catches **54.2% of failures**. About half.

For most teams, the useful part isn't the model. It's **which signals did the work**. You can collect those this week.

## What the study did

Sana Fatima, Muazzam Khan and Shayan Faiz of NED University in Karachi published it on Oct 15 in the *International Journal of Emerging Engineering and Technology*.

They used **194,400 pipeline runs** from Jenkins, GitHub Actions, GitLab CI/CD, Azure DevOps and CircleCI, logged from 2021 to 2024. About **21.9% of them failed**.

The model mixes three parts. XGBoost, a fast tree model, reads the metrics. A Bi-LSTM, a sequence model, and BERT, a language model, add log text. A small network decides how much to trust each part.

It scored an **AUC-ROC of 0.974 and an F1 of 0.940**. BERT alone got 0.961 and 0.924. The authors say they did not test whether that gap is significant.

## What 14 minutes actually buys

The model checks in at 10%, 25% and 50% of a run's expected duration.

- At **10%**: 54.2% of failures caught, **14.1 minutes** of warning on average.
- At **25%**: 78.6% caught, 8.7 minutes.
- At **50%**: 91.3% caught, 4.3 minutes.

[[IMG: img/early-detection-tradeoff.png | Chart from the paper (Fig. 3): early detection rate rises from 54.2% at the 10% checkpoint to 78.6% at 25% and 91.3% at 50%, while mean lead time falls from 14.1 to 8.7 to 4.3 minutes. Fatima, Khan and Faiz 2026, CC BY-SA 4.0.]]

That's the trade-off: **earlier warnings, fewer catches**.

Fourteen minutes is enough time to cancel a doomed run, free the runner and ping the author. The paper mentions a survey of 48 DevOps engineers that used **two minutes** as the bar for an actionable warning.

But there's a gap. The detection rate only counts runs that failed. The paper **does not report false alarms** on healthy runs. If you auto-cancel on this signal, you don't know how many good builds you'd kill.

## The cheap signals did the most work

The top-ranked features are not exotic:

1. **Build-duration deviation** (0.187): this run is slower than usual.
2. **Error-keyword frequency** (0.163): how often error words show up in the logs.
3. **CPU spike ratio** (0.141).
4. Test failure rate (0.129).
5. Code complexity change (0.112).

[[IMG: img/feature-importance-table.png | Table IV from the paper: feature importance scores. Build duration deviation 0.187, error keyword frequency 0.163, CPU spike ratio 0.141, test failure rate 0.129, cyclomatic complexity delta 0.112, dependency resolution time 0.098, artifact download failure 0.087, container resource OOM 0.083. Fatima, Khan and Faiz 2026, CC BY-SA 4.0.]]

The authors say these scores show **association, not cause**. Still, the top three come from **CI timing data, raw logs and runner metrics**. No GPU needed.

A [separate 2026 study](https://www.mdpi.com/2078-2489/17/2/178) on TravisTorrent data also ranked build duration among its top features.

## The limits

- **One pooled dataset.** There's no test on a platform the model never saw.
- **Unequal inputs.** Classic models got 98 features, deep models got 167. So the comparison doesn't prove the architecture is better.
- **No old-versus-new split.** Results use five-fold cross-validation. The authors call for chronological holdouts next.
- **Cost is open.** BERT took 891.4 seconds to train, XGBoost 63.5. The authors say these numbers don't settle the real end-to-end cost.
- **Data you can't check.** The paper describes real logs from company and open-source projects, not synthetic ones. But the data is only "available on reasonable request," and no code is linked.

## What to try on Monday

These steps are my suggestions, not the paper's:

- Pull a few months of runs from your CI API. Store each job's **usual duration**.
- At 10%, 25% and 50% of that time, compute **elapsed versus usual**, **error keywords so far** and **runner CPU spikes**.
- **Use only what's known at that moment.** The paper warns that final run time or final test results leak the answer.
- Start **alert-only**. Log every alert and whether the run really failed. That gives you the false-alarm rate the paper didn't publish.
- Test on **runs newer than the ones you tuned on**.

[[IMG: img/monday-plan.png | Diagram: the paper's top 3 signals (run slower than usual, error keywords in the logs so far, CPU spikes on the runner) feed a score at 10, 25 and 50% of usual run time, then a suggested rollout that is not from the paper: alert only, log every alert as real failure or false alarm, then decide on auto-cancel or ML.]]

**Takeaway:** an early warning is only as good as its false-alarm rate. Measure yours with cheap signals before you reach for a big model.

What's the earliest sign that one of your builds is going to fail?

## Sources

- Fatima, Khan and Faiz, ["An Intelligent Machine Learning Framework for Early Detection of CI/CD Pipeline Failures"](https://doi.org/10.57041/86apby39), IJEET 5(1-1): 45-50, Oct 15, 2026 ([journal page](https://grsh.org/journal1/index.php/ijeet/article/view/218), [PDF](https://grsh.org/journal1/index.php/ijeet/article/download/218/120), CC BY-SA 4.0)
- Figure and table above: Fig. 3 and Table IV of that paper, CC BY-SA 4.0
- [Multi-class XGBoost CI/CD failure prediction on TravisTorrent](https://www.mdpi.com/2078-2489/17/2/178), Information, Feb 2026
