---
revision_pending: true
title: "Notebooks to Production for ML/LLMs"
slug: ai-ml-engineering/mlops/module-1.11-notebooks-to-production-for-ml-llms
sidebar:
  order: 612
---
> **AI/ML Engineering Track** | Complexity: `[MEDIUM]` | Time: 2-3
---
**Reading Time**: 2-3 hours
**Prerequisites**: Notebooks, Scripts, and Project Layouts, Experiment Tracking, ML Pipelines, and Model Serving
---

## What You'll Be Able to Do

By the end of this module, you will:
- recognize when notebook work is still exploration and when it has become production risk
- extract reusable training, evaluation, and inference logic from notebooks into proper code paths
- define a repeatable handoff from experiment artifacts to reviewed production candidates
- separate offline experimentation concerns from online serving concerns
- avoid the common failure mode where "temporary prototype code" quietly becomes the system of record

**Why this matters**: many AI teams do not fail because the model idea was weak. They fail because the project does not fully cross the boundary from exploratory work to reproducible software. The notebook keeps growing, more cells get copied forward, and eventually a business-critical workflow depends on hidden state no one can explain.

---

## The Notebook Is a Lab Bench, Not the Factory Floor

Notebooks are good at:
- exploration
- explanation
- fast plotting
- quick model comparisons
- manual debugging

Production systems need different properties:
- repeatability
- reviewability
- explicit dependencies
- parameterized execution
- stable interfaces

That gives us the central principle of this module:

**A notebook may discover the workflow, but it should not remain the workflow.**

The practical transition is not "delete all notebooks."
The practical transition is:
- keep notebooks for learning and analysis
- move durable logic into code
- move repeatable runs into scripts or pipelines
- move deployment behavior into serving systems

---

## The Four Boundaries You Must Draw

If a team does not draw these boundaries early, production drift becomes inevitable.

### 1. Exploration vs Reproducible Execution

Exploration asks:
- what seems promising?
- what feature helps?
- which prompt pattern behaves better?

Reproducible execution asks:
- can this run again from a clean environment?
- are the inputs explicit?
- can another person get the same artifact?

If the answer is "only if they run the cells in the magic order," the work has not crossed the boundary yet.

### 2. Training vs Evaluation

Training code creates artifacts.
Evaluation code judges whether those artifacts are acceptable.

When both are mixed inside one notebook, teams accidentally:
- tune against their own evaluation set
- overwrite results
- lose baseline comparisons
- confuse anecdotal inspection with actual acceptance criteria

### 3. Offline Inference vs Online Serving

A notebook can call a model and print responses.
That does not mean the model is ready to serve user traffic.

Serving introduces new concerns:
- latency expectations
- failure handling
- request validation
- concurrency
- model versioning
- rollout control

### 4. Artifact Creation vs Artifact Governance

Generating a model once is easy.
Knowing which version is approved, why it exists, and how it was produced is harder.

That is where experiment tracking, model registry practices, and deployment rules matter.

---

## A Healthy Maturity Path

Most teams move through four stages.

### Stage 1: Notebook-Only Experiment

Typical signs:
- everything lives in one notebook
- dataset paths are hardcoded
- output files are manually named
- evaluation is informal

This stage is normal for the first exploration.
It becomes dangerous when it lasts too long.

### Stage 2: Notebook Plus Reusable Code

Typical signs:
- notebooks import code from `src/`
- training and evaluation functions live outside the notebook
- configs start replacing hardcoded values

This is usually the healthiest transition point.

### Stage 3: Scripted Experiment Workflow

Typical signs:
- training runs start from commands
- evaluation runs are reproducible
- artifacts are named and tracked systematically
- notebook usage narrows to analysis and reporting

At this point, the project is becoming operationally trustworthy.

### Stage 4: Production Candidate

Typical signs:
- model lineage is known
- validation criteria are explicit
- inference path is separated from training path
- deployment and rollback expectations exist

This is where MLOps actually begins to matter.

---

## What Should Move Out of the Notebook First

Do not try to industrialize everything at once.
Move the highest-risk logic out first.

### Move These First

- dataset loading and cleaning
- feature generation or prompt construction
- training loops
- evaluation routines
- inference wrappers
- config handling

### Keep These in Notebooks Longer

- exploratory plots
- manual error analysis
- result interpretation
- teaching walkthroughs
- quick sanity checks

The rule is simple:

**If logic must be rerun exactly and trusted by other people, it belongs in code, not only in cells.**

---

## The Minimal Production Handoff

You do not need a giant platform to leave notebook-only mode.
You do need a disciplined handoff.

A minimal handoff looks like this:

1. notebook proves the idea
2. reusable logic moves into `src/`
3. config values move into explicit files or parameters
4. training and evaluation become command-line entry points
5. runs are tracked with metrics and artifact references
6. a candidate model is compared against baseline
7. only approved artifacts move toward serving

That handoff is enough for many small teams.

---

## A Good Project Layout for the Transition

```text
ml-project/
├── README.md
├── pyproject.toml
├── configs/
│   ├── train.yaml
│   ├── eval.yaml
│   └── serve.yaml
├── notebooks/
│   ├── 01-exploration.ipynb
│   └── 02-error-analysis.ipynb
├── src/
│   └── project_name/
│       ├── data.py
│       ├── training.py
│       ├── evaluation.py
│       ├── inference.py
│       └── prompts.py
├── scripts/
│   ├── train.py
│   ├── evaluate.py
│   └── export_model.py
├── tests/
├── reports/
└── outputs/
```

Why this works:
- notebooks remain useful without owning the whole system
- business logic lives in versioned code
- scripts provide repeatable entry points
- configs reduce hidden parameter drift

---

## The Experiment-to-Serving Bridge

The handoff from notebook to production is really a series of decisions:

### Is the Task Stable Enough?

If the task definition keeps changing every day, you are still exploring.
Do not industrialize too early.

### Is the Data Path Stable Enough?

If dataset construction is still ad hoc, the artifact is not trustworthy.

### Is the Evaluation Good Enough?

If the decision is still based on "this output looks nice," do not promote the model.

### Is the Inference Contract Clear?

If the team cannot define:
- the request format
- the output format
- the latency target
- the fallback behavior

then the work is not ready for production serving.

This is where many notebook-first projects fail.
They jump from "interesting demo" to "please ship this" without designing the contract in between.

---

## Common Anti-Patterns

### Notebook as Deployment Artifact

Someone wraps the notebook in a job runner and calls it production.

Problem:
- hidden state
- poor observability
- weak reviewability

### Copy-Paste Pipeline

Notebook logic gets copied into scripts repeatedly instead of being extracted into shared code.

Problem:
- divergence
- bug duplication
- inconsistent fixes

### Baseline Drift

The team keeps improving the current experiment without preserving a clear reference baseline.

Problem:
- no trustworthy comparison
- hard-to-explain regressions

### Serving Before Evaluation Discipline

The team builds an API before it can prove the model deserves traffic.

Problem:
- deployment becomes the experiment
- users become the test set

---

## A Review Checklist Before Promotion

Before notebook-born work becomes a production candidate, ask:

- can the run start from a clean environment?
- are the inputs and configs explicit?
- is the dataset version known?
- is there a baseline comparison?
- are metrics and artifacts tracked?
- can another engineer reproduce the result?
- is the serving contract defined?
- is rollback possible if the promoted model disappoints?

If several of these are still unclear, the right move is usually not deployment. It is one more round of cleanup and hardening.

---

## What Changes for LLM Systems

The notebook-to-production gap is even sharper for LLM work because:
- prompts drift quickly
- evaluation is often weak
- retrieval and model behavior get mixed together
- latency and cost often matter early

For LLM systems, the handoff usually needs three separate code paths:
- prompt or orchestration logic
- evaluation logic
- serving logic

If those stay mixed in one notebook, teams struggle to answer simple questions like:
- did the prompt improve?
- did retrieval improve?
- did the model improve?
- did the deployment just get slower and more expensive?

Separation is how you keep reasoning clear.

---

## The Small-Team Standard

A small team does not need enterprise ceremony.
It does need a minimum engineering bar.

That bar is:
- code outside the notebook for reusable logic
- tracked experiments
- explicit configs
- reviewable model candidates
- clear inference boundaries

If you can do that, you are already moving from hobby workflow to real MLOps.

That is the point of this module.

---

## Key Takeaways

- notebooks are valuable, but they are not a production boundary
- the first goal is not to eliminate notebooks; it is to stop relying on hidden notebook state
- the safest transition is notebook -> reusable code -> scripts/pipelines -> serving
- training, evaluation, and serving must be separated before deployment pressure rises
- a small team can build a credible production handoff without overbuilding platform complexity

---

<!-- v4:generated type=no_quiz model=codex turn=1 -->
## Quiz


**Q1.** Your team has a notebook that trains a classifier, evaluates it, and exports a model file. It only works if people rerun cells in a specific order after manually changing dataset paths at the top. A product manager wants to schedule it as a nightly job and call it "production." What is the main problem, and what should the team do first?

<details>
<summary>Answer</summary>
The main problem is that the workflow is still exploratory, not reproducible. It depends on hidden notebook state, manual path edits, and a specific execution order, which means another engineer may not be able to rerun it from a clean environment and get the same artifact.

The first step is to move the durable logic out of the notebook into proper code paths, especially dataset loading, training, evaluation, and config handling. Then the team should run training and evaluation through explicit scripts or pipeline entry points instead of relying on notebook cells.
</details>

**Q2.** An LLM prototype in a notebook seems to improve after several prompt edits. The same notebook also contains manual spot-checks on a few sample outputs, and the team is ready to expose it behind an API because "the outputs look better now." Based on the module, why is this risky?

<details>
<summary>Answer</summary>
This is risky because the team is mixing experimentation, evaluation, and serving decisions in one place. "The outputs look better" is not a sufficient acceptance criterion, and the notebook does not prove the system deserves production traffic.

The module's guidance is to separate prompt or orchestration logic, evaluation logic, and serving logic. Before deployment, the team should define explicit evaluation criteria, compare against a baseline, and clarify the serving contract such as request format, output format, latency target, and fallback behavior.
</details>

**Q3.** A small ML team has reached the point where notebooks now import reusable functions from `src/`, and hardcoded values are being replaced with YAML configs. Training still starts from a notebook, but evaluation code already lives outside it. Which maturity stage are they in, and why is it a healthy transition point?

<details>
<summary>Answer</summary>
They are in Stage 2: Notebook Plus Reusable Code. That stage is characterized by notebooks importing code from `src/`, training and evaluation functions living outside the notebook, and configs replacing hardcoded values.

It is a healthy transition point because the notebook can still support exploration and analysis, while the logic that needs to be trusted and reused is being moved into versioned, reviewable code. That reduces hidden state without forcing the team to overbuild too early.
</details>

**Q4.** Your team copied prompt-construction logic from a notebook into `scripts/train.py`, `scripts/evaluate.py`, and a serving prototype. Two weeks later, a bug fix is applied in one place but missed in the others, and results no longer line up across environments. Which anti-pattern caused this, and what is the better design?

<details>
<summary>Answer</summary>
This is the Copy-Paste Pipeline anti-pattern. The same logic was duplicated across multiple scripts instead of being extracted into shared reusable code, which caused divergence and inconsistent fixes.

The better design is to put shared prompt-construction or feature-generation logic into code under `src/` and have training, evaluation, and serving entry points call the same implementation. That keeps behavior aligned and makes fixes propagate consistently.
</details>

**Q5.** A notebook-generated recommendation model is about to be promoted because it produced the best metrics so far. During review, nobody can say which dataset version was used, what the baseline score was, or whether rollback is possible if the new model performs worse in production. According to the module, should this be promoted?

<details>
<summary>Answer</summary>
No. The model should not be promoted yet because the handoff and governance are incomplete. The module's review checklist requires clarity on dataset version, baseline comparison, tracked metrics and artifacts, reproducibility, and rollback expectations.

Without that information, the artifact is not a trustworthy production candidate. The correct next step is another round of cleanup and hardening so the model lineage, validation criteria, and rollback path are explicit.
</details>

**Q6.** A data scientist says, "Our notebook already calls the model and prints responses, so building the API is just wrapping the same code in a web framework." What important production concerns are they overlooking?

<details>
<summary>Answer</summary>
They are overlooking the boundary between offline inference and online serving. A notebook calling a model for manual inspection is not the same as a service that handles real traffic.

The missing concerns include request validation, latency expectations, failure handling, concurrency, model versioning, and rollout control. The team also needs a clear inference contract that defines request shape, output shape, performance expectations, and fallback behavior before serving users.
</details>

**Q7.** A team wants to move beyond notebook-only work but does not want to build a large internal platform. They ask for the smallest credible handoff that would still meet a basic MLOps standard. What sequence should they follow?

<details>
<summary>Answer</summary>
They should follow the module's minimal production handoff:

1. The notebook proves the idea.
2. Reusable logic moves into `src/`.
3. Config values move into explicit files or parameters.
4. Training and evaluation become command-line entry points.
5. Runs are tracked with metrics and artifact references.
6. A candidate model is compared against a baseline.
7. Only approved artifacts move toward serving.

This works for small teams because it creates repeatability, reviewability, and clear boundaries without requiring heavyweight platform engineering.
</details>

<!-- /v4:generated -->
<!-- v4:generated type=no_exercise model=codex turn=1 -->
## Hands-On Exercise


Goal: turn a notebook-based ML/LLM prototype into a reproducible, reviewable workflow with separated training, evaluation, and serving paths.

- [ ] Create a clean project structure for the handoff from exploration to production. Add `notebooks/`, `src/project/`, `scripts/`, `configs/`, `outputs/`, and `reports/`, then move the original notebook into `notebooks/01-exploration.ipynb`.
- [ ] Identify the logic that should leave the notebook first: data loading, preprocessing, prompt construction or feature generation, training, evaluation, and inference helpers. Write down which notebook cells map to which reusable modules.
- [ ] Extract reusable code into Python modules such as `src/project/data.py`, `src/project/training.py`, `src/project/evaluation.py`, and `src/project/inference.py`. Keep only analysis, plotting, and error inspection inside the notebook.
- [ ] Move hardcoded paths, model names, hyperparameters, and prompt settings into explicit config files such as `configs/train.yaml`, `configs/eval.yaml`, and `configs/serve.yaml`.
- [ ] Create repeatable command-line entry points like `scripts/train.py` and `scripts/evaluate.py` so training and evaluation can run without opening the notebook.
- [ ] Save outputs in a predictable way. Store model artifacts, metrics, and evaluation summaries under timestamped or versioned directories in `outputs/` and `reports/`.
- [ ] Define a simple production handoff rule: only artifacts that beat a named baseline and have recorded config, metrics, and dataset reference are allowed to become production candidates.
- [ ] Separate offline experimentation from online serving. Write down the serving contract: expected request format, response format, timeout or latency target, and fallback behavior for invalid input or model failure.
- [ ] Re-run the notebook using the extracted modules instead of notebook-only logic. Confirm the notebook still works for analysis, but no longer owns the critical workflow.
- [ ] Document the transition in `README.md`: how to train, how to evaluate, where artifacts are stored, and how a candidate model is promoted.

Verification commands:

```bash
find notebooks src scripts configs outputs reports -maxdepth 2 -type f | sort
```

```bash
python scripts/train.py --config configs/train.yaml
python scripts/evaluate.py --config configs/eval.yaml
```

```bash
ls -R outputs
ls -R reports
```

```bash
python -c "from src.project.training import train; from src.project.evaluation import evaluate; print('imports ok')"
```

```bash
grep -R "TODO\|FIXME" src scripts configs
```

Success criteria:
- The notebook is no longer the only place where training, evaluation, or inference logic exists.
- Training and evaluation can run from command-line scripts with explicit configs.
- Artifacts and metrics are saved in predictable locations.
- A baseline comparison is recorded before promotion decisions.
- The serving contract is defined separately from notebook experimentation.
- Another engineer can reproduce the workflow from the project structure and commands alone.

<!-- /v4:generated -->
## Next Modules

- [Small-Team Private AI Platform](./module-1.12-small-team-private-ai-platform/)
- [ML Monitoring](./module-1.10-ml-monitoring/)
- [Local Inference Stack for Learners](../ai-infrastructure/module-1.4-local-inference-stack-for-learners/)

## Sources

- [MLOps: Continuous delivery and automation pipelines in machine learning](https://cloud.google.com/solutions/machine-learning/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) — Explains the transition from notebook-driven experimentation to modularized, automated ML pipelines and production delivery.
- [MLOps machine learning model management](https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment?view=azureml-api-2) — Covers model registration, versioning, metadata, and deployment concerns that map directly to artifact governance and production handoff.
- [Model Cards](https://huggingface.co/docs/hub/en/model-cards) — Useful for making model candidates reviewable by documenting datasets, evaluation results, intended use, and limitations.
