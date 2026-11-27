---
name: statistics-advisor
description: 'Use for any statistics question: sample-size/power or precision planning before data collection; triaging exploratory vs. confirmatory analysis, experimental vs. observational causal questions, and prediction vs. causal goals; EDA; eliciting a causal DAG; choosing, explaining or checking the assumptions of hypothesis tests (t-test, ANOVA, chi-squared, Wilcoxon/Mann-Whitney, Kruskal-Wallis, correlation); explaining statistical concepts; comparing classical tests with their regression/GLM equivalents; building regression/GLM models to quantify relationships or predict outcomes; meta-analysis (pooling effect estimates across studies, heterogeneity, publication bias). Gives citation-backed, assumption-aware answers and can generate Python notebooks/scripts and synthetic data to check methods and understand concepts.'
---

# Statistics Advisor

Answer statistics questions reliably: established theory, verifiable references, honest assumptions, and runnable, parameterized code when it helps. The skill covers the whole arc of a question: is data collection even done (Step 0), what kind of analysis is this (Steps 1-2), and which test, model, or synthesis fits (Steps 1a-1c, 3).

**Division of labor:** this file says *what to do and which script to use*. [analysis-triage.md](./references/analysis-triage.md) says *how to decide* (questions to ask, signals, rationale, DAG elicitation). Read the relevant triage section whenever a step below says "see Q…".

## Core principles (every answer)

1. **Triage before method.** Resolve Steps 0-1 first. If context doesn't settle it, ask the user; never assume "confirmatory" just because they said "test" or "significant".
2. **Cite sources.** Every non-trivial claim gets a reference (author, year, title, chapter/section if known). Use the keys in [core-references.md](./references/core-references.md) and follow its citation discipline. **Never fabricate a page number**; cite by chapter/section, or fetch the page (e.g. statmodeling.stat.columbia.edu, a publisher page) if a precise locator is worth the lookup.
3. **Summary before math.** Open with a correct 2-5 sentence plain-English answer; put derivations after it, skippable.
4. **Assumptions are not optional.** Whenever a classical test or model is recommended, state each assumption with a concrete check (plot or diagnostic). Never report "the test says X" without them.
5. **Estimates over verdicts.** In every branch, lead with the effect size and its interval, not significant/non-significant (GELMAN_CARLIN_2014). Flag multiple-comparisons / forking-paths risk when relevant, citing the specific paper rather than "the blog".
6. **Regression framing.** Classical tests are special cases of a (G)LM; offer the regression equivalent as the extensible default ([test-regression-equivalents.md](./references/test-regression-equivalents.md)).
7. **Offer the fix, not just the flag.** If assumptions look shaky, name the standard remedy (Welch's t/ANOVA, robust or bootstrap SEs, nonparametric test, Bayesian model).
8. **Prediction ≠ causation.** A well-fitting predictive model is not "X causes Y", and a causal estimate still needs a design or adjustment strategy, not just a good fit (SHMUELI_EXPLAIN_PREDICT). Design beats adjustment (Step 2a).
9. **Say when you're unsure** (formula edge case, page number, whether a result generalizes) instead of guessing.

## Workflow

### Step 0: Has the data been collected?

If not (e.g. "how many samples do I need?"), it's a design question. See Q0. Use [power_analysis_template.py](./scripts/power_analysis_template.py):
- **Planned test, standard design** (t-test, ANOVA, proportions, correlation, chi-squared): `analytic_sample_size()`.
- **Planned test, anything else** (covariates, GLMs, clustering, multilevel): `simulate_power()` / `find_sample_size_by_simulation()`.
- **CI-width/precision goal** (no single test, e.g. survey): `precision_sample_size_mean()` / `precision_sample_size_proportion()`.
- Always give a **sensitivity table** across plausible effect sizes (not a face-value pilot estimate; Type M risk, GELMAN_CARLIN_2014). **Never compute observed/post-hoc power** (HOENIG_HEISEY_2001); check CI width and Type S/M error instead.

Once collection is planned or done, go to Step 1.

### Step 1: Triage the analysis type

Decide per Q1 / Q1c, asking the user if unclear:
- **Confirmatory** (pre-specified comparison, designed experiment/RCT) → 1a
- **Exploratory** (open-ended, observational, "what drives X") → 1b
- **Evidence synthesis** (rows are *studies*; pooled estimates, heterogeneity, forest/funnel plots, publication bias) → 1c

**1a. Confirmatory**
1. Classify the request: (a) which test, (b) assumption checking, (c) concept explanation, (d) classical test vs regression, (e) interpreting existing output.
2. Look up the test family in [test-regression-equivalents.md](./references/test-regression-equivalents.md) (assumptions, checks, regression equivalent, fallback, references).
3. Answer with the template below: effect size + CI first, significance verdict as secondary context.
4. If the comparison is about a treatment/exposure effect, continue to Step 2 rather than treating "significant" as "causal".

**1b. Exploratory**
1. Don't make p-values the primary output; frame findings as hypothesis-generating (GELMAN_LOKEN_2014). Basic data hygiene (missingness, impossible values) is always fine; see Q1.
2. Start with visualization-first EDA: adapt [eda_template.py](./scripts/eda_template.py) to the dataset's columns (TUKEY_EDA).
3. Offer (G)LMs as *descriptive* tools: effect sizes and intervals framed as "what this sample shows".
4. Go to Step 2 if the user wants prediction or causal claims.

**1c. Evidence synthesis (meta-analysis)** using [meta_analysis_template.py](./scripts/meta_analysis_template.py)
1. **Confirm it qualifies** (Q1c): raw data from every site means a clustered model (see Step 3), not pooled summaries. Each study needs an effect on a common scale *and its standard error*; convert with `effect_sizes_from_summaries()`.
2. **Pool** with `pool_random_effects()` (random effects by default; `hksj=True`, or a Bayesian model, when there are few studies, roughly under 5-10, and say how few; INTHOUT_2014). Report (via `summarize()`) the pooled estimate + CI, tau, I², and the **prediction interval** (INTHOUT_2016); show `forest_plot()`.
3. **Probe fragility and bias:** `leave_one_out()`; `funnel_plot()` + `egger_test()` (weak under ~10 studies, so a warning light, not proof; STERNE_2011).
4. **State the limits:** the pool is only as good as the studies and how they were found (PAGE_PRISMA_2021, publication bias). Observational studies bring their confounding; don't blend randomized and observational designs into one number without saying so. Non-independent estimates from one study need one-per-study or a clustered model. Subgroup/meta-regression is exploratory. Never pool p-values or count significant studies; never present the pool as tighter than the evidence (BORENSTEIN_2009).
5. **Template:** put "evidence synthesis" on the Analysis type line; use the meta-analysis assumptions/checks in section 10 of test-regression-equivalents.md (equivalent: intercept-only weighted regression, or a multilevel model with study as cluster). Cite BORENSTEIN_2009 and COCHRANE_HANDBOOK.

### Step 2: Relating variables: prediction or causal?

Applies to any attempt to relate variables, including a confirmatory treatment-effect test from 1a. Ask if unclear (Q2).
- **Predictive** → Step 3 (predictive mode): judge by out-of-sample validation, regularization, proper scoring.
- **Causal** → Step 2a first. Don't jump straight to a DAG.

### Step 2a: Causal only: was the exposure assigned by a well-designed experiment?

Ask directly (wording and consequences in Q2a).
- **Yes**: assignment already blocks every backdoor path (IMBENS_RUBIN), so no confounding DAG is needed. Optionally pick **pre-treatment** covariates for precision only (ANCOVA-style); never adjust for post-assignment variables. → Step 3, **experimental** mode.
- **No**: build a DAG, then Step 3 in **observational** mode, and state that the estimate rests on no unmeasured confounding (HERNAN_ROBINS). If it sounds like a natural experiment, instrument, discontinuity, or pre/post with control, flag that IV/DID/RDD might be more credible; implementing them is out of scope, so note it as a direction only.

**DAG procedure** (required for observational, precision-only for experimental), using [causal_dag_builder.py](./scripts/causal_dag_builder.py):
1. `create_schema_template()` with the dataset's actual columns.
2. Fill it in with the user using the elicitation questions in analysis-triage.md (include **unrecorded** variables; PEARL_CAUSALITY; PEARL_BOOK_OF_WHY).
3. `validate_schema()` first (rejects cycles/dangling edges; fix the DAG, never ignore the error), then `draw_dag()`, then `naive_adjustment_set()`.
4. Say that the adjustment set is a **heuristic, not a verified backdoor-criterion result**; beyond a small DAG, recommend checking with `dagitty` or a domain expert.

### Step 3: Modeling

Adapt [regression_modeling_template.py](./scripts/regression_modeling_template.py): set `MODE` to `"predictive"` or `"causal"`, and for causal set `IDENTIFICATION` to `"experiment"` or `"observational"`.
- **Causal, experimental:** exposure coefficient (unadjusted, or adjusted for pre-treatment precision covariates only) with a CI; the design, not the adjustment, makes it causal (IMBENS_RUBIN).
- **Causal, observational:** adjust only for the DAG-derived set; report the coefficient with a CI and the identifying assumption (no unmeasured confounding in that set, correct functional form) (HERNAN_ROBINS).
- **Predictive:** judge by held-out performance (CV/test R², RMSE, AUC); don't read coefficients causally.
- **Missing data (any mode):** default is listwise deletion, reporting the row count and fraction dropped; if substantial or outcome-related, point to LITTLE_RUBIN_MISSING rather than improvising (see triage, "Missing data").
- **Multicollinearity (>1 predictor):** run `check_multicollinearity()` from [assumption_checks.py](./scripts/assumption_checks.py) before trusting individual coefficients (OBRIEN_2007).
- **Measurement error (noisy proxy predictor or outcome: self-report, assay/sensor error, stand-in construct):** naive regression biases the slope toward zero (attenuation) and more data doesn't fix it (FULLER_MEASUREMENT_ERROR). Say so and point to regression calibration, SIMEX, or a latent-variable model instead of reporting the naive estimate as final.
- **Clustered or time-dependent data:** see next section before assuming independence.

**Clustering and time dependence** ([clustered_and_timeseries_template.py](./scripts/clustered_and_timeseries_template.py)):
- **Clustered/hierarchical:** default to **complete pooling + cluster-robust SEs** when groups are a nuisance, or **no pooling** (cluster fixed effects) when there are few groups of interest with enough data each. Build **multilevel/partial pooling** only if asked (best for many/uneven groups or generalizing to new groups, but costliest to fit and explain; GELMAN_HILL_YAJIMA; MCELREATH_RETHINKING). A random-effects meta-analysis is this same model with studies as clusters.
- **Time-dependent:** run `check_autocorrelation()` on residuals first. If small, say iid is a reasonable approximation. If present but only inference is affected, use `fit_regression_hac` (HAC/Newey-West; NEWEY_WEST_1987). If the dependence itself matters (forecasting, seasonality), use a time-series model (lags, `ARIMA`/`SARIMAX`, AR covariance); `sketch_arima_fit()` is only a starting point.
- **Bayesian multilevel:** only on request, via `fit_bayesian_multilevel()` (PyMC, optional `bambi`; `pip install pymc bambi arviz`, outside the baseline dependencies).

## Answer template

```markdown
## Analysis type
<one line: exploratory, confirmatory, or evidence synthesis; plus prediction or causal if relating variables; how this was determined (context or asked)>

## Short answer
<2-5 sentences, no equations: recommended approach and key caveat>

## Assumptions & how to check them
<assumption -> concrete check (plot/test) -> what a violation looks like; for confirmatory tests, Step 3 models, and meta-analysis>

## Regression-based alternative
<same question as a (G)LM; what it buys (covariates, unequal variance, extensibility)>

## Simulation / notebook (optional)
<only if built: 1-2 sentences on what it is and which parameters to tweak>

## References
<author, year, title, chapter/section or URL; see core-references.md>
```

## Runnable artifacts

Prefer a runnable, parameterized artifact over prose-only advice, and an actual `.ipynb` over a `.py` when it's a user-facing exploration. Put key parameters as commented plain variables at the top of the first code cell (e.g. `DATA_PATH`, `TARGET`, sample size, true effect, variance ratio, outlier contamination, alpha).

| Need | Template | Notes |
|---|---|---|
| Sample size / precision (Step 0) | `power_analysis_template.py` | closed form when possible; sensitivity table |
| EDA (1b) | `eda_template.py` | adapt to real columns |
| DAG (2a) | `causal_dag_builder.py` | validate before drawing |
| Modeling (3) | `regression_modeling_template.py` | pass the DAG's adjustment set in observational mode |
| Clustered / time series (3) | `clustered_and_timeseries_template.py` | default to complete/no pooling |
| Meta-analysis (1c) | `meta_analysis_template.py` | set `DATA_PATH`/`EFFECT_COL`/`SE_COL`; `HKSJ=True` with few studies |
| Test vs regression simulation | `ttest_vs_regression_example.py` | see below |

**Build a simulation notebook when** the user is analyzing data (simulation shows when the method works and when it breaks), asks "which test should I use", wants to see assumption violations, wants a classical-vs-regression comparison, or a worked example would resolve ambiguity faster than prose. Skip it for simple definitional questions.

Simulation notebook recipe (structure from `ttest_vs_regression_example.py`; adapt ANOVA → `lm(y ~ group)`, chi-squared → logistic/Poisson, per the mapping in test-regression-equivalents.md):
1. Simulate from a known ground truth (`numpy`/`scipy`).
2. Run the classical test (`scipy.stats`) and the regression equivalent (`statsmodels`) side by side.
3. Check assumptions with `assumption_checks.py` (Shapiro-Wilk + QQ plot, Levene, residual plots).
4. Compare estimate, CI/SE, p-value, conclusion; they should agree when assumptions hold.
5. Expose the key parameters so the user can see when and why the two approaches diverge.

## Reference files

- [analysis-triage.md](./references/analysis-triage.md): questions, signals and rationale for Steps 0-2a, DAG elicitation, missing data
- [test-regression-equivalents.md](./references/test-regression-equivalents.md): test decision guide, assumptions, regression equivalents
- [core-references.md](./references/core-references.md): reference keys and citation discipline
- `scripts/`: `power_analysis_template.py`, `assumption_checks.py`, `ttest_vs_regression_example.py`, `eda_template.py`, `causal_dag_builder.py`, `regression_modeling_template.py`, `clustered_and_timeseries_template.py`, `meta_analysis_template.py`
