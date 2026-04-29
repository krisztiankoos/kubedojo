# Tier 3 proposal — Chapter 2: The Universal Machine

Per `docs/research/ai-history/READER_AIDS.md` Tier 3 workflow. Author: Claude. Reviewer requested: Codex (cross-family adversarial). The reviewer should be willing to REJECT.

## Element 1 — Pull-quote (`:::note`, ≤1 per chapter)

**Status: SKIPPED**

Rationale: Rule (b) of READER_AIDS.md item 9 — refuse if "the prose paragraph already quotes the sentence verbatim." Every quote-worthy sentence in Ch02 is already in-prose:

- Turing's "the Hilbert Entscheidungsproblem can have no solution" — quoted verbatim in the §11 reduction paragraph (line ≈124 post-T1).
- Turing's "It is possible to invent a single machine which can be used to compute any computable sequence" — quoted verbatim in the §6 paragraph (line ≈132).
- Turing's "It should perhaps be remarked that what I shall prove is quite different from the well-known results of Gödel" — quoted verbatim in the Gödel-distinction paragraph (line ≈92).
- Church's "has the advantage of making the identification with effectiveness... evident immediately" — quoted verbatim in the Princeton-connection paragraph (line ≈162).
- De Morgan and Boole quotations are Ch01 material, not Ch02.

There is no candidate sentence that is both genuinely quote-worthy *and* not already in-prose. SKIP per (b), consistent with the Ch01 prototype's pull-quote skip.

## Element 2 — Plain-reading aside after Gödel arithmetisation paragraph

**Status: PROPOSED**

Anchor: end of the paragraph beginning "The proof rested on a coding device of remarkable economy" (the second Gödel paragraph). This paragraph is symbolically dense — it stacks the numbering scheme, the self-referential predicate, the if/then/else case analysis, and the consistency assumption in one breath.

Insertion: immediately after the paragraph ending "…lay beyond the reach of every consistent formal axiomatisation strong enough to express it."

Draft:
```
:::tip[Plain reading]
The trick is the second move. By assigning a number to every symbol, formula, and proof, Gödel turned questions about provability into questions about ordinary arithmetic — questions the system itself can already state. He then constructed a sentence that, decoded, says "this sentence has no proof in the system." If the system proved it, the system would be lying. If the system proved its negation, the system would be asserting that an unprovable formula was provable. Provided the system never contradicts itself, neither move is open — and the sentence is therefore unprovable, and therefore true.
:::
```

Rationale: The aside makes the *self-reference closure* visible — why both branches are blocked, and how truth follows from unprovability. The surrounding prose states the conclusion ("Some arithmetical truth … lay beyond the reach…") but does not walk the reader through the symmetric breakage that produces it. The aside does new work in 4 sentences.

The candidate paragraph is symbolically dense (the chapter's only Gödel-numbering paragraph), not narratively dense. It satisfies READER_AIDS.md item 10's "symbolically dense" criterion.

## Element 3 — Plain-reading aside after §11 reduction paragraph

**Status: PROPOSED**

Anchor: end of the paragraph beginning "The final step was to bring this mechanical impossibility back to Hilbert" (the §11 reduction paragraph that introduces the formula `Un(M)`). Symbolically dense — the paragraph encodes a logical reduction in compressed form: a formula `Un(M)` that is provable iff M ever prints 0, plus the §8 result that no machine decides M's print behaviour, plus the conclusion that no decision procedure for provability exists.

Insertion: immediately after the paragraph ending "…'the Hilbert Entscheidungsproblem can have no solution.'"

Draft:
```
:::tip[Plain reading]
Turing did not attack Hilbert's problem head-on. He built a translation. The formula $\text{Un}(M)$ is provable in the functional calculus *if and only if* the machine $M$ ever prints the symbol 0. So a general procedure that decided provability for every formula would, in particular, decide $\text{Un}(M)$ — i.e., decide whether $M$ prints 0. But §8 had just proved that no machine can decide that. The decision procedure Hilbert asked for would solve a problem Turing had just shown was unsolvable. It cannot exist.
:::
```

Rationale: The aside names the *strategy* (reduction by translation, not by direct attack) that the surrounding prose performs but does not label. It uses inline math notation (`$\text{Un}(M)$`) consistent with the math sidebar pattern from Ch01 and the chapter's own use of backticked `Un(M)`. It does new work — the surrounding prose moves through the reduction; the aside extracts the move-shape.

## Element 4 — Inline parenthetical definition (Starlight tooltip)

**Status: SKIPPED**

Rationale: READER_AIDS.md item 8 — universal SKIP across every chapter until a non-destructive tooltip component lands. HTML `<abbr title="…">` would violate the bit-identity rule. The Plain-words glossary (Tier 1, item 4) covers the same job non-destructively for Ch02's specialist vocabulary (Entscheidungsproblem, λ-calculus, a-machine, S.D, recursive function, Church-Turing thesis).

## Selective dense-paragraph asides — additional candidates considered and rejected

Three further paragraphs were evaluated and rejected from PROPOSED status:

- **§6 universal-machine definition paragraph** (line ≈148, "It is possible to invent a single machine…"). Architecturally dense rather than symbolically dense. The paragraph already does the plain-reading work itself ("the table of instructions governing any specific computing machine M could itself be encoded as a string…"). REJECT — would duplicate.
- **§8 diagonal-argument paragraph** (line ≈122, "He posed a question: could one invent a general-purpose machine, called D…"). The prose already contains the plain-reading summary in its own body: "Through a rigorous logical contradiction, Turing showed that if machine D existed, it could be used to construct a paradoxical machine that defied its own operational rules." REJECT — would duplicate.
- **Lemmas 1+2 paragraph** (line ≈126, "The reduction unfolded in two short lemmas…"). Same shape as Element 3's §11 reduction paragraph; including both would create adjacent repetition. REJECT — Element 3 covers it.

## Summary table (for the reviewer)

| # | Element | Status | Approve? Reject? Revise? |
|---|---|---|---|
| 1 | Pull-quote | SKIPPED (rule b) | reviewer: agree / disagree |
| 2 | Plain-reading after Gödel arithmetisation | PROPOSED | reviewer: APPROVE / REJECT / REVISE |
| 3 | Plain-reading after §11 reduction | PROPOSED | reviewer: APPROVE / REJECT / REVISE |
| 4 | Inline parenthetical | SKIPPED (universal) | reviewer: agree / disagree |

The Ch01 prototype's calibration was 2-of-5 candidates landing. Ch02 proposes 2 candidates outright (pull-quote and inline-parenthetical pre-skipped per rules); the reviewer is invited to reject either or both of the plain-reading asides.
