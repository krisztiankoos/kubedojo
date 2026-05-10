# Pending Decisions

This directory holds Decision Cards that need user input and were created while the user was AFK.

Cold-start agents must scan this directory before starting unrelated work. If any pending card exists, surface it to the user first with the question, options, disagreement, and orchestrator recommendation.

## When to Write Here

Write `docs/decisions/pending/{date}-{slug}.md` only when all of these are true:

- a high-leverage `ab discuss` produced disagreement or multiple viable options
- the decision needs user input before proceeding
- the user is not available in chat

Do not write a pending card when the agents converge with `[AGREE]`. In that case, record the outcome in the relevant handoff, issue, PR, or decision record and proceed.

## Promotion

When the user decides:

1. Move the file to `docs/decisions/{date}-{slug}.md`.
2. Fill in the `## Decision` section with the chosen option, decision date, and who decided.
3. Link the final record from the related issue, PR, or handoff.

For multi-week or architecture-level decisions, use a GitHub issue instead of relying only on a pending file.
