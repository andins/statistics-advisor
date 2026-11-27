# Analysis triage: the questions to answer before picking a method

Decision guide for [SKILL.md](../SKILL.md) Steps 0-2a: the questions to ask, the signals to look for, and why. SKILL.md holds the procedures and script calls. Reference keys resolve in [core-references.md](./core-references.md).

## Question 0: Has the data already been collected?

If not, and the question is "how many samples do I need", it is a design-phase question. Resolve it before anything else; move to Question 1 once collection is planned or done.

- **Power for a planned hypothesis test** needs alpha, target power (0.8 is a convention, not a law), a test type, and an effect size. **Effect-size sourcing is the hard part.** Small pilots give noisy, often *inflated* estimates (Type M error, GELMAN_CARLIN_2014), so a power calculation built on one can be badly underpowered. Prefer the smallest effect of practical/clinical interest, or a literature/meta-analytic estimate, and report a sensitivity table over plausible effects rather than one number presented as exact.
- **Precision/CI-width planning** fits when there is no single pre-specified test (e.g. "estimate this proportion within ±3 points", survey planning). Plan the margin of error directly instead of forcing a power-analysis shape.
- **Never compute observed/post-hoc power.** It is a deterministic function of the p-value and adds nothing (HOENIG_HEISEY_2001). To assess a result after the fact, look at CI width and run a Type S/M check (GELMAN_CARLIN_2014).

## Question 1: Exploratory or confirmatory?

Classical testing (p-values, pre-specified alpha, reject/fail to reject) is well-calibrated only for **confirmatory** analysis: a specific hypothesis fixed *before* seeing this data, ideally from a designed experiment or pre-registered comparison. Elsewhere it should generally be avoided, not merely used with extra care. Even in the confirmatory case the effect estimate with its interval teaches more than the verdict (GELMAN_CARLIN_2014). Most real requests ("what's going on in this dataset", "what drives X", dashboards, convenience samples) are **exploratory**, even when phrased as "is there a difference/effect/association".

- **Confirmatory signals:** designed experiment/RCT; a single comparison fixed before data collection; pre-registration or analysis plan; replication of a specific known effect.
- **Exploratory signals:** "what's driving/associated with…", "find patterns/segments", reporting/dashboarding, observational or convenience data, many candidate variables with no comparison chosen in advance, the comparison decided after looking at the data.
- **If unclear, ask:** "Was this comparison decided before you saw this data (e.g. a pre-registered experiment), or are we looking for patterns in data you already have?" Don't infer confirmatory from the words "test" or "significant".

**If exploratory:**
- Warn before presenting any classical test as "the answer": implicit multiple comparisons and researcher degrees of freedom inflate false positives even without deliberate p-hacking (GELMAN_LOKEN_2014).
- Start with visualization-first EDA (TUKEY_EDA; GELMAN_EXPLORATORY_CONFIRMATORY); use (G)LMs descriptively. A confirmed answer requires new or held-out data for a true confirmatory test.
- A p-value may accompany a pattern worth taking seriously, labeled hypothesis-generating.
- **Data hygiene is not forking paths.** Checking missingness, impossible values, outliers, and entry errors is always fine. What to avoid is peeking at the *comparison itself* and letting that steer which comparison gets reported.

**If confirmatory:** run the classical workflow (SKILL.md Step 1a), estimate and CI first. If the question concerns a treatment/exposure effect, it is also causal: continue to Question 2.

## Question 1c (evidence synthesis only): is the unit of analysis a study?

Different from the split above: the user is *combining results of several studies* ("what do the trials say overall", "pool these effects", "is there publication bias", "why do studies disagree"). Signals: one row per study (effect, SE, n); terms like meta-analysis, systematic review, pooled estimate, I², forest/funnel plot. Ask whatever isn't already clear:

- **Is it really a meta-analysis?** With raw data from every site/study, use a multilevel model with site as cluster instead of pooling summaries.
- **Common scale?** Same unit, standardized mean difference, or log OR/RR. Each study needs an effect and its *standard error* (not SD, not variance); convert first if needed.
- **How were studies found?** A systematic pre-specified search or whatever the user knew of? A convenience set limits what any pooled number means; say so rather than hiding it behind a tight interval.
- **How many?** Under ~5-10, tau² is poorly estimated (Hartung-Knapp or Bayesian, and state the count). Two or three very different studies may be better shown side by side.
- **Independent estimates?** Multiple estimates from one study (two doses vs one control, several outcomes) are not independent; pick one per study or model the dependence.
- **Mixed designs?** Randomized and observational studies shouldn't be blended without reason; the pool is no more causal than its studies (see Question 2a).

Reporting requirements and limits: SKILL.md Step 1c (INTHOUT_2016; STERNE_2011; PAGE_PRISMA_2021; BORENSTEIN_2009; COCHRANE_HANDBOOK).

## Question 2: Prediction or causal interpretation?

Matters whenever variables are being related, including a confirmatory treatment-effect test. If unclear, ask: "Do you need to predict/forecast this outcome for new cases, or to know whether changing X would actually change Y (would an intervention on X work)?" (SHMUELI_EXPLAIN_PREDICT).

- **Predictive:** accurate estimates for new data; no coefficient needs a causal reading. Any available predictor is fair game, flexible/regularized models are fine, and success is out-of-sample performance (train/test, CV, proper scoring rules), not p-values or in-sample fit.
- **Causal:** a "what if we intervened" question (price, policy, treatment). It needs an identification strategy, not just a good fit. **Go to Question 2a before modeling.**

### Question 2a (causal only): was the exposure assigned by a well-designed experiment?

The most important fork in the causal branch, and easy to skip straight to "build a DAG"; don't. Ask: "Was [exposure] assigned by you/the researcher (or another mechanism outside anyone's control) independently of the units' other characteristics, e.g. randomized assignment?"

- **Yes (randomized or as-good-as-randomized):** assignment is independent of every pre-treatment variable, measured or not, so it blocks every backdoor path. This is stronger than any observational adjustment (IMBENS_RUBIN).
  - The unadjusted difference between arms is already a valid estimate of the average treatment effect; no confounding DAG is needed.
  - A lightweight covariate list is still useful for **baseline (pre-treatment) covariates that reduce residual variance** (ANCOVA). This improves precision, not validity.
  - **Never adjust for anything measured after assignment** (mediators, post-treatment variables); that reintroduces bias even in an RCT.
- **No (observed/self-selected exposure):** no design guarantees balanced confounders. Build the full DAG (below), and report the result as an adjustment-based ("selection on observables") estimate, the weakest common identification strategy, valid only if the adjustment set captures *all* confounding and nothing else (HERNAN_ROBINS). If the setup resembles a natural experiment, instrument, assignment-rule discontinuity, or pre/post with a control group, flag that IV/DID/RDD might identify the effect more credibly. They are out of scope here; note as a direction only.

### DAG elicitation questions

Run through [causal_dag_builder.py](../scripts/causal_dag_builder.py) (tool order in SKILL.md Step 2a). Required for the observational branch; precision-covariates only for the experimental one. The schema starts with one node per *recorded* column, so nothing in hand is forgotten, and invites nodes for variables *never recorded*, making that assumption explicit (PEARL_CAUSALITY; PEARL_BOOK_OF_WHY). Ask, in order:

1. **Outcome:** "What outcome do you ultimately care about?"
2. **Exposure:** "Whose causal effect do you want: what would you imagine 'intervening on'?"
3. **Role of each remaining variable:** plausibly (a) a cause of the exposure, (b) a cause of the outcome, (c) both, a **confounder** (adjust), (d) a consequence of the exposure, a **mediator** (don't adjust if you want the *total* effect), or (e) a consequence of both exposure and outcome, a **collider** (never condition on it; it creates spurious association).
4. **Direction via timing:** "What happened first?" Causes weakly precede effects. (In experiments, anything after assignment is off-limits for adjustment regardless of role.)
5. **Mechanism:** "How would A affect B?" With no plausible mechanism, be skeptical of the edge even if the variables correlate.
6. **Unmeasured variables:** "Does anything affect [exposure] and/or [outcome] that wasn't recorded?" Add as `recorded: false` nodes.
7. **Doubts:** log unsure edges in `open_questions`; an approximate DAG the team can revisit beats a silent assumption.

## Missing data: a default, not a full treatment

After EDA shows how much is missing and where (`plot_missingness()`):

- **Default:** listwise deletion on the columns the model uses, stating the rows dropped and their fraction. Unbiased under MCAR.
- **Get more careful** if many rows are dropped or missingness plausibly depends on the outcome or an unobserved variable (MAR/MNAR): flag it rather than silently dropping, and point to LITTLE_RUBIN_MISSING (multiple imputation, model-based methods) rather than improvising.
