---
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

**Why this matters**: many AI teams do not fail because the model idea was weak. They fail because the project never crosses the boundary from exploratory work to reproducible software. The notebook keeps growing, more cells get copied forward, and eventually a business-critical workflow depends on hidden state no one can explain.

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
- latency and cost matter immediately

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

## Next Modules

- [Small-Team Private AI Platform](./module-1.12-small-team-private-ai-platform/)
- [ML Monitoring](./module-1.10-ml-monitoring/)
- [Local Inference Stack for Learners](../ai-infrastructure/module-1.4-local-inference-stack-for-learners/)
