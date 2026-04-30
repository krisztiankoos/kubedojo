# Session handoff — 2026-04-30 (night-7) — post-Ch59-72 followups + classical-ml gap surfaced

> Picks up immediately after `2026-04-30-part8-9-ch59-72-shipped.md` (the reader-aid rollout closeout). This session did three small post-rollout follow-ups and surfaced a real curriculum gap that needs a dedicated next-session plan.

## What shipped this session

| Commit | What |
|---|---|
| `f56e87a6` | `scripts/check_reader_aids.py` — Tier 1 cap + structure linter for all 72 AI history chapters. Validates TL;DR ≤80w, Why-still ≤120w, glossary 5–7 terms, cast ≤6 rows, mermaid timeline directive present. Tolerates the optional `<strong>` wrapper in `<summary>` (Ch43 deviation). Surfaces 14 pre-existing cap violations from chapters that shipped before the cap-verification mandate (Ch07/08/09/14/18/21/22/23/27/33/35/37/50/58); user opted to leave them for Codex's dedup pass to trim naturally. |
| `5ba5871e` | `astro.config.mjs` — replaced flat `autogenerate` for AI history with explicit 9-Part hierarchical sidebar (Part 1 Ch01–05 → Part 9 Ch59–72). URLs unchanged → no conflict with Codex's in-flight dedup PRs. Each chapter labeled compactly as `NN: Title`. Build verified: 1955 pages, 0 errors, 38s. |
| `7cd6291f` | `src/content/docs/ai-ml-engineering/history/module-1.1-history-of-ai-machine-learning.md` — seeded 11 Part-level *Go deeper* asides + a top-level pointer that bridge from the 30-min survey module into the canonical 72-chapter book at `/ai-history/`. Module body unchanged; survey-style coverage (exercises, quiz, reflection, Did-You-Know) preserved as the on-ramp. Skipped Part 10 (Personalities) and Part 13 (Timeline Summary) because they're cross-cutting synthesis the book intentionally doesn't replicate. |

## What was decided (the load-bearing parts)

1. **Reader-aid lint is structural, not strict-spec.** The lint accepts both `<summary><strong>X</strong></summary>` and bare `<summary>X</summary>` since both render identically — the goal is regression detection, not specification policing. Cap thresholds being a few words loose is not worth chasing manually; user verified a sample of TL;DRs and called them fine.

2. **The short AI/ML history module is preserved, not replaced.** First instinct (mine) was to replace its body with a stub-bridge into the book. User pushed back: *"keep the short version, and add links inside to the book for more details."* That was clearly the right call — the module has unique, non-overlapping value the book doesn't provide: hands-on exercises, quiz, reflection questions, Did-You-Know facts, a unified flat timeline, and a consolidated personalities table. Different jobs (learning module vs. narrative history). The deep-link bridge is what shipped.

3. **Classical-ml is a real curriculum gap, not just a perception.** User flagged: *"i feel a bit uncomfortable that we only have 3 chapter about ml an without ml there is no ai."* Audit confirmed:
   - **Book** (`/ai-history/`) has ~14 ML-touching chapters (Ch04 Markov, Ch15/24 grad-descent/backprop, Ch25 UAT, Ch26 Bayes, Ch27 CNNs, Ch29 SVMs, Ch30 HMMs, Ch31 RL, Ch44 Word2Vec, Ch45 GANs, Ch46 LSTMs, Ch47 ResNet, Ch55 scaling) — but it's *historical*, not *practitioner*.
   - **`classical-ml/`** has only 3 modules (scikit-learn, XGBoost, time series). Each broad in scope, but no dedicated coverage of: linear/logistic + regularization, unsupervised (k-means/DBSCAN/GMM), dimensionality reduction (PCA/t-SNE/UMAP), feature engineering, model evaluation depth, hyperparameter tuning depth, NB/kNN/SVMs as practitioner content.
   - **Reinforcement learning** has no practitioner home anywhere — book covers history (Ch31, Ch48 AlphaGo) but no PPO/DQN/Stable-Baselines3/RLlib module exists.
   - **Deep-learning** edge gaps: object detection (YOLO/Faster R-CNN), segmentation (U-Net, SAM), classical NLP (NER/POS/spaCy), VAEs/normalizing flows, self-supervised learning.
   - **`bridges/`** subdirectory has *zero* modules — just an `index.md`. Status unclear; may be staged scaffolding for cross-cutting work or stale.

4. **Workflow mismatch found in `context-monitor.sh` hook.** The hook is hard-coded to demand handoffs go to `.pipeline/session-handoff.md` (last touched 2026-04-17, three weeks stale). Actual practice writes to `docs/session-state/YYYY-MM-DD-<topic>.md` (per CLAUDE.md). If the hook ever fires near the 95% emergency tier, it will point the next session at the wrong file. **Not urgent** — this session ended at 28% of the 1M window — but should be fixed before it bites.

## What's queued for next session

**Block A — small mechanical cleanups (~30 min total):**

1. **Git hygiene sweep.** Briefing has been alerting:
   - 50 prunable branches (run `git cleanup-merged` or equivalent)
   - 49 prunable worktrees
   - 2 stashes >24h old (review + drop or keep)
   - 1 detached HEAD worktree at `.worktrees/codex-interactive` (resolve)
   - 5 stale pid files
2. **Fix `context-monitor.sh` handoff target.** Two clean options (user to choose):
   - Option A: edit the hook to point at `docs/session-state/YYYY-MM-DD-<topic>.md` (matches CLAUDE.md and current practice).
   - Option B: keep `.pipeline/session-handoff.md` as a symlink to the latest `docs/session-state/` file (both paths work).

**Block B — proper ML curriculum (the big one):**

User's framing: *"i want proper ml solution, we need dedicated home for ml."*

Plan for next session:
1. Decide ML's home structure. Options:
   - Expand `classical-ml/` to ~10–12 modules + add `reinforcement-learning/` directory.
   - Or restructure into `machine-learning/` with sub-categories: `classical/`, `unsupervised/`, `deep/`, `rl/`, `model-eval/`.
   - User's call which.
2. Draft Tier 1 module specs (titles + 2-line scope each) for the 8 foundational gaps before writing:
   1. Linear/Logistic regression + regularization (L1/L2/Elastic Net, GLMs)
   2. Unsupervised learning (k-means, DBSCAN, hierarchical, GMM)
   3. Dimensionality reduction (PCA, t-SNE, UMAP)
   4. Feature engineering systematic (encoding, scaling, imputation, selection)
   5. Model evaluation deep dive (metrics, CV, calibration, leakage)
   6. Hyperparameter tuning (Optuna/Hyperopt/Ray Tune)
   7. Naive Bayes / k-NN / SVMs as practitioner content
   8. Reinforcement learning practitioner module (PPO/DQN/Stable-Baselines3/RLlib)
3. Tier 2 (curriculum completeness, ~7 more modules): class imbalance, interpretability (SHAP/LIME), recommender systems, probabilistic/Bayesian ML (PyMC), self-supervised learning, GNNs, causal inference.
4. Decide whether `bridges/` directory is alive or should be removed.

**Block C — #388 rubric-critical rewrite work** (after Block B):

Per memory `reference_rubric_heuristic_structural.md`, the 485 "critical rubric" modules are scored by regex (missing Sources sections, etc.), not teaching quality — many are likely false positives. Approach: read actual content before trusting the score. Block B (filling real ML gaps) should land before plowing into #388, since you can't claim AI/ML coverage without solid classical ML and ML home is foundational to the rest.

## Cold-start smoketest (executable)

```bash
# 1. Confirm all reader-aid work landed
git log --oneline -8 | head
# expect: 7cd6291f docs(ai-ml/history): seed deep-links … and earlier
.venv/bin/python scripts/check_reader_aids.py --quiet | tail -5
# expect: 14 fails (all pre-existing cap drift; OK to leave for Codex dedup)

# 2. Confirm primary tree clean
git -C /Users/krisztiankoos/projects/kubedojo status -sb
# expect: ## main...origin/main (no dirty)

# 3. Sidebar grouping renders
grep -oE "Part [1-9]:[^<]{1,60}" dist/ai-history/ch-01-the-laws-of-thought/index.html | sort -u | wc -l
# expect: 9 (after `npm run build`)

# 4. Confirm classical-ml inventory before planning expansion
ls src/content/docs/ai-ml-engineering/classical-ml/
# expect: index.md + 3 modules (1.1 scikit-learn, 1.2 xgboost, 1.3 time-series)

# 5. Check bridges/ status
ls src/content/docs/ai-ml-engineering/bridges/
# expect: only index.md (no modules)

# 6. Git hygiene baseline (run before sweep)
git branch | wc -l                        # local branches
git worktree list | wc -l                 # worktrees
git stash list                             # stashes
ls .worktrees/codex-interactive 2>/dev/null && echo "detached HEAD worktree exists"
```

## Cross-thread updates (for STATUS.md)

- **ADD**:
  - **Reader-aid lint script `scripts/check_reader_aids.py`** — structural validator for all 72 AI history chapters. Manual-run; not yet hooked into pre-commit. Use `--quiet` for CI-style output, `--json` for machine-readable.
  - **AI history sidebar now grouped into 9 Parts.** URLs unchanged; only render hierarchy changed. Implementation: explicit `items[]` array in `astro.config.mjs` instead of flat `autogenerate`. Future chapter additions or renames require a sidebar update (lost the autogenerate convenience for the sake of grouping).
  - **AI/ML history module bridges into the AI history book.** 11 Part-level *Go deeper* asides + a top-level pointer route survey readers into the deep canonical chapters. The module body is unchanged.
  - **Classical-ml is a flagged curriculum gap.** 3 modules where 10–12+ are needed. Reinforcement learning has no practitioner home. Block B in next session covers this.
  - **`context-monitor.sh` hook points at stale handoff target.** `.pipeline/session-handoff.md` is 3 weeks old; actual handoffs land in `docs/session-state/`. Fix queued for next session.

- **DROP** from cross-thread:
  - The "PR #558 / PR #565 stale-prose cleanup" line if those have been resolved by Codex's dedup batch (status unknown to me right now — user to verify next session). Leave for now.

## Files modified this session

```
scripts/check_reader_aids.py                                                    [new, +271]
astro.config.mjs                                                                [+128 -1]
src/content/docs/ai-ml-engineering/history/module-1.1-history-of-ai-machine-learning.md  [+24]
docs/session-state/2026-04-30-night-7-followups.md                              [new]
STATUS.md                                                                       [predecessor + cross-thread updates]
~/.claude/projects/-Users-krisztiankoos-projects-kubedojo/memory/
  feedback_caps_pre_commit_verification.md                                      [new earlier today]
  feedback_worktree_write_discipline.md                                         [new earlier today]
  project_ai_history_post_aid_pipeline.md                                       [new earlier today]
  MEMORY.md                                                                     [pointers added]
```

All on main. No open PRs at session end. No worktrees in flight (Codex's dedup PRs may have re-opened some — verify next session via `gh pr list`).

## Blockers

(none)
