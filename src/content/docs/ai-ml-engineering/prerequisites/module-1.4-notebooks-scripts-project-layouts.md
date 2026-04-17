---
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

If those categories mix together, drift begins immediately.

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
| Using notebooks for production-critical steps | impossible handoff and review | create scripts for repeatable execution |
| Copy-pasting code between notebooks | divergence and bug duplication | centralize shared code early |

---

## Check Your Understanding

1. Why are notebooks valuable for exploration but risky as the only source of project logic?
2. What kinds of files belong in `outputs/` rather than beside your source code?
3. What is the practical signal that a notebook experiment should become a script?
4. Why is separating reusable logic from exploratory cells a professional habit, not bureaucracy?

---

## Next Modules

- [Home-Scale RAG Systems](../vector-rag/module-1.6-home-scale-rag-systems/)
- [Notebooks to Production for ML/LLMs](../mlops/module-1.11-notebooks-to-production-for-ml-llms/)
- [Experiment Tracking](../mlops/module-1.6-experiment-tracking/)
