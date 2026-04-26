---
revision_pending: true
title: "Notebooks, Scripts, and Project Layouts"
slug: ai-ml-engineering/prerequisites/module-1.4-notebooks-scripts-project-layouts
sidebar:
  order: 104
---
> **AI/ML Engineering Track** | Complexity: `[MEDIUM]` | Time: 2-3
---
**Reading Time**: 2-3 hours
**Prerequisites**: Modules 1.1 through 1.3 complete
---

## What You'll Be Able to Do

By the end of this module, you will:
- choose when to use notebooks, scripts, packages, and pipelines
- structure AI projects so experiments do not become unmaintainable
- separate exploratory work from reusable code
- keep outputs, datasets, and generated artifacts under control
- move from notebook-first learning to reproducible project habits

**Why this matters**: many promising AI projects fail before the model fails. They fail because the project becomes a pile of copied notebook cells, mystery outputs, and undocumented assumptions.

---

## Notebooks Are Useful, but Dangerous

Notebooks are excellent for:
- exploration
- quick visual inspection
- trying small ideas
- teaching and explanation
- interactive debugging

Notebooks are dangerous when they quietly become:
- your training system
- your evaluation system
- your deployment pipeline
- your only source of truth

That is the core principle of this module:

**Notebooks are a phase. They are not the final architecture.**

---

## The Four Working Modes

Most serious AI projects eventually need four different working modes.

### 1. Notebook Mode

Best for:
- asking questions of the data
- checking model behavior quickly
- plotting and interpretation
- one-off exploration

### 2. Script Mode

Best for:
- repeatable experiments
- preprocessing jobs
- training commands
- evaluation commands

### 3. Package Mode

Best for:
- reusable logic
- shared utilities
- model wrappers
- dataset loaders
- configuration handling

### 4. Pipeline Mode

Best for:
- orchestrated multi-step workflows
- repeatable team execution
- tracked artifacts
- deployment-oriented processes

Learners often start in Notebook Mode and stay there too long. The goal is to graduate deliberately.

---

## A Good Starter Project Layout

Use a layout that makes intent visible:

```text
my-ai-project/
├── .venv/
├── README.md
├── requirements.txt
├── notebooks/
│   ├── 01-exploration.ipynb
│   └── 02-error-analysis.ipynb
├── src/
│   └── my_project/
│       ├── data.py
│       ├── features.py
│       ├── train.py
│       ├── evaluate.py
│       └── inference.py
├── configs/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── outputs/
│   ├── figures/
│   ├── predictions/
│   └── reports/
└── tests/
```

This layout is not sacred. The point is clarity:
- source code in one place
- notebooks in one place
- data in one place
- generated outputs in one place

If those categories mix together, drift usually begins quickly.

---

## What Goes in a Notebook and What Does Not

### Good Notebook Content

- exploratory queries
- charts and plots
- metric comparison tables
- quick prompt tests
- manual error analysis
- explanatory walkthroughs

### Bad Notebook Content

- copy-pasted production logic
- hidden preprocessing state
- final training logic that only exists in cells
- deployment-critical code
- giant outputs committed to Git
- manual cell-order dependencies no one can reproduce

A useful test:

**If the result must be run again exactly and trusted by other people, it probably should not live only in a notebook.**

---

## The Cell-Order Problem

Notebooks allow a dangerous illusion:
- the file looks linear
- the execution history is not linear

This creates the classic problem:

"It works in the notebook, but nobody knows why."

Why it happens:
- cells run out of order
- hidden variables stay alive in memory
- imports change across restarts
- files on disk change between runs

The longer a notebook lives, the more likely it is to contain hidden state.

That is why real project logic should move into scripts or reusable modules quickly.

---

## The Best Practical Workflow

Use this loop:

1. explore in notebook
2. identify reusable logic
3. move reusable logic into `src/`
4. call that logic from notebook or script
5. create a command-line script for repeatable execution

This gives you:
- notebook convenience
- script reproducibility
- code reuse

It is the safest bridge from learning to real work.

---

## Output Hygiene

AI projects generate clutter very quickly:
- notebook checkpoints
- images
- logs
- predictions
- cached model artifacts
- exploratory CSV files

If outputs are not isolated, the repo becomes unreadable.

Use simple rules:
- keep generated outputs in `outputs/`
- keep large raw data out of Git unless intentionally versioned elsewhere
- keep notebook output cells small when possible
- do not store random experiments in the project root

Clean structure is not perfectionism. It is how future-you avoids confusion.

---

## Version Control Rules That Prevent Chaos

Track:
- source code
- configs
- lightweight documentation
- dependency definitions
- small example notebooks that still teach something

Avoid tracking by default:
- large datasets
- generated figures you can recreate
- transient caches
- model checkpoints unless deliberately versioned
- notebook output noise

Version control should describe the project, not mirror every artifact the project ever emitted.

---

## When to Graduate from Notebook to Script

Move work into scripts when:
- you need to rerun it repeatedly
- someone else should be able to run it
- the logic is larger than one exploratory session
- parameters need to be changed systematically
- outputs need to be compared cleanly

Move work into reusable modules when:
- multiple scripts or notebooks need the same logic
- you want tests
- naming and interfaces matter
- the project is becoming long-lived

Move work into pipelines when:
- the workflow has multiple dependent steps
- artifacts need tracking
- execution needs scheduling
- the project is heading toward production

---

## A Healthy Relationship Between Notebooks and Code

The best notebooks do not contain all the logic.

They do this instead:
- import reusable code
- run a focused experiment
- visualize results
- explain what happened

That makes the notebook a scientific record and teaching tool, not a fragile execution engine.

---

## Common Mistakes

| Mistake | What Goes Wrong | Better Move |
|---|---|---|
| Keeping all logic inside notebooks | hidden state and irreproducible runs | move reusable logic into `src/` |
| Mixing data, code, and outputs in one folder | project becomes unreadable | separate directories by purpose |
| Tracking every output in Git | noisy diffs and bloated repos | track source, not every artifact |
| Using notebooks for production-critical steps | difficult handoff and review | create scripts for repeatable execution |
| Copy-pasting code between notebooks | divergence and bug duplication | centralize shared code early |

---

## Check Your Understanding

1. Why are notebooks valuable for exploration but risky as the only source of project logic?
2. What kinds of files belong in `outputs/` rather than beside your source code?
3. What is the practical signal that a notebook experiment should become a script?
4. Why is separating reusable logic from exploratory cells a professional habit, not bureaucracy?

---

<!-- v4:generated type=no_quiz model=codex turn=1 -->
## Quiz


**Q1.** Your team has been training a model from a Jupyter notebook for weeks. A new engineer restarts the kernel, runs the cells top to bottom, and gets different results because some variables had only existed in memory from earlier ad hoc runs. What is the main project problem here, and what should the team move first out of the notebook?

<details>
<summary>Answer</summary>
The problem is hidden notebook state caused by cell-order dependence. The notebook looks linear, but its execution history is not, so other people cannot reliably reproduce what happened.

The first thing to move out is the reusable project logic, especially preprocessing and training steps, into code under `src/` and then into repeatable scripts. The notebook can stay for exploration and visualization, but logic that must run again exactly should not live only in cells.
</details>

**Q2.** Your team has a repository where `train.py`, raw CSV exports, temporary charts, prediction files, and notebook experiments all sit in the project root. New contributors keep opening the wrong files and cannot tell what is source code versus generated output. What restructuring choice best fixes this?

<details>
<summary>Answer</summary>
Separate the project by purpose: keep source code in `src/`, notebooks in `notebooks/`, datasets in `data/`, and generated artifacts in `outputs/`.

The module's main point is clarity of intent. When code, data, and generated results are mixed together, drift usually starts quickly. A clearer layout makes it obvious what should be edited, what should be rerun, and what is just an output artifact.
</details>

**Q3.** You built a useful feature-engineering routine while exploring in a notebook. Two more notebooks now copy-paste the same code, and a teammate wants to reuse it in a training command too. What is the professional next step?

<details>
<summary>Answer</summary>
Move the feature-engineering logic into a reusable module under `src/` and have the notebooks and script import it.

This avoids code duplication and divergence. The module explains that when multiple notebooks or scripts need the same logic, that is the signal to centralize it early so it can be reused, named clearly, and eventually tested.
</details>

**Q4.** Your manager asks for a daily rerun of evaluation with different parameter values so the team can compare outputs cleanly over time. Right now the process only exists as a notebook with manual edits. Which working mode should you adopt next, and why?

<details>
<summary>Answer</summary>
Adopt Script Mode for the evaluation step.

The module says work should move into scripts when it needs repeatable execution, systematic parameter changes, and clean comparison of outputs. A notebook is fine for exploration, but a repeatable evaluation command belongs in a script so other people can run it the same way.
</details>

**Q5.** A repository review shows dozens of committed notebook output cells, generated figures, cached predictions, and a large model artifact that can all be recreated. Pull requests are noisy and hard to review. Based on the module, what should version control track by default, and what should usually stay out?

<details>
<summary>Answer</summary>
Version control should track source code, configs, lightweight documentation, dependency definitions, and small example notebooks that still teach something.

It should usually avoid tracking large datasets, generated figures, transient caches, model checkpoints unless intentionally versioned, and notebook output noise. The explanation is that Git should describe the project, not mirror every artifact the project has emitted.
</details>

**Q6.** You are preparing a handoff to another team. They need to trust a preprocessing step exactly because it feeds a downstream service. The only implementation is in a notebook with several manually run cells and no clear execution contract. What does the module suggest, and why is the current setup risky?

<details>
<summary>Answer</summary>
The preprocessing step should be moved into scripts or reusable modules, not left only in the notebook.

The current setup is risky because deployment-critical or trust-critical logic should not live only in exploratory cells. Notebooks are useful for investigation and explanation, but if a result must be rerun exactly and trusted by others, it should exist in repeatable code with a clearer interface.
</details>

**Q7.** An AI project has grown from one exploration notebook into a multi-step workflow: ingest data, preprocess it, train a model, evaluate it, and store artifacts for later review. Different teammates run different pieces at different times, and nobody can track outputs cleanly. What is the next architectural step?

<details>
<summary>Answer</summary>
Move toward Pipeline Mode.

The module recommends pipelines when workflows have multiple dependent steps, need tracked artifacts, require repeatable team execution, or are heading toward production. At this point, a notebook or a single script is no longer enough because the problem is orchestration across stages, not just running one command.
</details>

<!-- /v4:generated -->
<!-- v4:generated type=no_exercise model=codex turn=1 -->
## Hands-On Exercise


**Goal:** create a small AI project workspace that separates exploratory notebook work from reusable code, repeatable scripts, and generated outputs.

- [ ] Create a starter project layout with clearly separated folders for notebooks, source code, data, and outputs.
  ```bash
  mkdir -p my-ai-project/{notebooks,configs,data/raw,data/processed,outputs/figures,outputs/reports,src/my_project}
  touch my-ai-project/README.md my-ai-project/requirements.txt
  find my-ai-project -maxdepth 3 -type d | sort
  ```

- [ ] Add reusable Python code under `src/` instead of placing all logic in a notebook.
  Create `my-ai-project/src/my_project/features.py` with a small function such as `normalize_text(text)` that lowercases and trims text.
  ```bash
  cat my-ai-project/src/my_project/features.py
  ```

- [ ] Add a repeatable script that imports the reusable code and writes an output artifact.
  Create `my-ai-project/src/my_project/run_features.py` so it reads a few hardcoded sample strings, applies `normalize_text()`, and writes results to `outputs/reports/features_preview.txt`.
  ```bash
  PYTHONPATH=my-ai-project/src python3 my-ai-project/src/my_project/run_features.py
  cat my-ai-project/outputs/reports/features_preview.txt
  ```

- [ ] Create a notebook placeholder for exploration only.
  Add `my-ai-project/notebooks/01-exploration.ipynb` or a plain text placeholder file describing what should stay in the notebook: quick inspection, charts, and experiment notes, not production logic.
  ```bash
  ls -R my-ai-project/notebooks
  ```

- [ ] Separate input data from generated outputs.
  Put a small sample file such as `sample.txt` in `data/raw/`, and keep script-generated files only in `outputs/`.
  ```bash
  printf "  Hello AI Project  \nNotebook To Script\n" > my-ai-project/data/raw/sample.txt
  find my-ai-project/data my-ai-project/outputs -type f | sort
  ```

- [ ] Confirm that the project can be rerun from the command line without relying on notebook cell order.
  Run the script twice and verify the same output file is produced both times.
  ```bash
  PYTHONPATH=my-ai-project/src python3 my-ai-project/src/my_project/run_features.py
  PYTHONPATH=my-ai-project/src python3 my-ai-project/src/my_project/run_features.py
  diff -u my-ai-project/outputs/reports/features_preview.txt my-ai-project/outputs/reports/features_preview.txt
  ```

- [ ] Review the layout and identify what belongs in each area before expanding the project.
  Check that notebooks contain exploration, `src/` contains reusable logic, `data/` holds datasets, and `outputs/` holds generated artifacts.
  ```bash
  find my-ai-project -maxdepth 3 -type f | sort
  ```

Success criteria:
- the project has separate `notebooks/`, `src/`, `data/`, and `outputs/` directories
- reusable logic lives under `src/my_project/` and is imported by a script
- a command-line run produces a file under `outputs/` without manual notebook steps
- raw inputs are stored under `data/` rather than mixed with source code
- the structure makes it obvious which files are exploratory, reusable, and generated

<!-- /v4:generated -->
## Next Modules

- [Home-Scale RAG Systems](../vector-rag/module-1.6-home-scale-rag-systems/)
- [Notebooks to Production for ML/LLMs](../mlops/module-1.11-notebooks-to-production-for-ml-llms/)
- [Experiment Tracking](../mlops/module-1.6-experiment-tracking/)

## Sources

- [Cookiecutter Data Science](https://github.com/drivendataorg/cookiecutter-data-science) — Provides a widely used reference project layout for separating code, data, notebooks, and outputs.
- [nbdime](https://github.com/jupyter/nbdime) — Shows practical tooling for diffing and merging notebooks without treating them like ordinary text files.
- [nbstripout](https://github.com/kynan/nbstripout) — Directly supports the module's version-control hygiene advice by stripping notebook outputs and noisy metadata.
