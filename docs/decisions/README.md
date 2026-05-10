# Decision Records

This directory holds durable records for high-leverage project decisions: architecture choices, threshold freezes, contested review outcomes, and strategic bets that affect many modules.

Use `scripts/ab discuss <channel> --with claude,codex,gemini --max-rounds 3` when the decision benefits from multiple model-family perspectives. Treat the discussion as distributed deliberation, not quorum. LLM agents have correlated priors, so the goal is to expose disagreement and option space, not to manufacture a vote.

## Decision Card Convention

Decision Cards are emitted only when `ab discuss` surfaces disagreement or multiple viable options. If all agents converge with `[AGREE]`, no card is needed; the orchestrator records or proceeds with the converged decision.

Use [`_template.md`](./_template.md) for cards that need user input. Use [`pending/`](./pending/) when the user is AFK and the decision must survive the session boundary.

Surface protocol:

- User online: emit the card inline in chat for immediate visibility.
- User AFK: write the card to `docs/decisions/pending/{date}-{slug}.md`.
- Multi-week or architecture-level decision: open a GitHub issue with the card body.
- User decides: move the pending file to `docs/decisions/{date}-{slug}.md` and record the chosen option plus decision date.

## Scope

Use `ab discuss` for:

- architecture choices
- threshold freezes
- contested NEEDS CHANGES outcomes
- strategic bets affecting 100+ modules
- major curriculum scope decisions

Do not use it for per-PR review, one-line fixes, single-module choices, or decisions where the agents will obviously converge.

## References

- Canonical agent rule: [`.claude/rules/decision-card.md`](../../.claude/rules/decision-card.md)
- Project memory: `~/.claude/projects/-Users-krisztiankoos-projects-kubedojo/memory/feedback_ab_discuss_for_decisions.md`
- Adoption issue: [kube-dojo/kube-dojo.github.io#740](https://github.com/kube-dojo/kube-dojo.github.io/issues/740)
