# Tier 3 reader-aid proposal — Ch01 The Laws of Thought

Issue #564. Drafted by Claude. Adversarial review by Codex required before any element lands.

The hard constraint is bit-identity of the existing prose body. Every proposal here is an *inserted* callout between paragraphs; no proposal modifies an existing prose line. After application, `git diff main -- src/content/docs/ai-history/ch-01-the-laws-of-thought.md | grep -E '^-[^-]'` must remain empty.

---

## 1. Inline parenthetical definition (Starlight tooltip)

**SKIPPED.**

**Reason:** Starlight 0.30 does not ship a tooltip / `:::abbr` / hover-glossary component. Verified by:

- Listing `node_modules/@astrojs/starlight/components/` — no `Tooltip.astro`, `Abbr.astro`, or equivalent.
- Searching the components directory for `tooltip|Tooltip|abbr|Abbr` — no matches.

Plain HTML `<abbr title="…">…</abbr>` would work in markdown, but wrapping any word inside the existing prose body in `<abbr>` tags **modifies the prose line**, which violates the bit-identity rule. The Tier 3 contract explicitly excludes this path: "do NOT add literal parenthetical definitions to the prose body — that violates the bit-identical rule."

A custom `<Tooltip>` Astro component would close the gap, but it sits outside the prototype scope (it adds infrastructure, not just an aid) and the existing collapsible **Plain-words glossary** already serves the same job non-destructively. The skip is documented here and will be repeated in the PR body.

---

## 2. Pull-quote

**PROPOSED.**

**The line.** Boole's own most-quoted sentence, identified in `brief.md` as "the chapter's load-bearing pull-quote" and in `scene-sketches.md` Scene 3 Action 4 as "Boole's most-quotable line":

> It is a consequence of the fact that the fundamental equation of thought is of the second degree, that we perform the operation of analysis and classification, by division into pairs of opposites, or, as it is technically said, by dichotomy.

— Boole 1854, Ch. III §15.

**Insertion anchor.** Immediately after the existing paragraph that ends:

> "…The natural mode of human analysis is binary not because the world has only two kinds of thing, but because the algebra that governs reasoning is a *quadratic* — and a quadratic equation has, in general, two roots."

(In the current file this is the paragraph beginning "He went further. Boole termed the equation $x^2 = x$ the 'law of duality'…", line 99.)

**Proposed rendering.**

```markdown
:::note
> It is a consequence of the fact that the fundamental equation of thought is of the second degree, that we perform the operation of analysis and classification, by division into pairs of opposites, or, as it is technically said, by dichotomy.

— Boole, *Laws of Thought*, Ch. III §15. The sentence in which Boole derives binary thinking *from his algebra* — not from observation of the world.
:::
```

**Rationale.** The whole chapter is built around this sentence. The brief calls it the load-bearing pull-quote; the prose paragraph paraphrases it but does not display it as a typographic event. A pull-quote here lifts the one verbatim line that justifies the entire claim of the chapter. Skipping this would forfeit the single best candidate the chapter has.

---

## 3. Selective dense-paragraph asides (`:::tip[Plain reading]`)

Proposing **two**, both on Chapter II/III/IV mathematical paragraphs where a non-expert reader is likely to lose the thread. Aiming for *under three* deliberately — the chapter has more dense paragraphs than warrant interruption, and the rubric is "1–3 per chapter, refuse on chapters where no paragraph is genuinely dense" — the inverse also applies: refuse to *manufacture* asides past the point where the prose is actually opaque.

### 3a. Plain reading after the `x² = x` derivation

**PROPOSED.**

**Insertion anchor.** Immediately after the long Chapter III paragraph that begins "With the elements defined, Boole proceeded in Chapter III…" and ends "…Subtraction from the universal class produces the negation." (line 95 in the current file).

**Why it qualifies as dense.** The paragraph runs from "$x \cdot x = x$" through the observation that the equation is satisfied numerically only by 0 and 1, to the assignment of $0 = $ Nothing and $1 = $ Universe, to the definition of the complement as $1 - x$. Three formal moves are stacked. A non-mathematician who reads the paragraph linearly may track the words but lose the *direction of inference*: that Boole noticed an algebraic peculiarity in his own calculus, asked which numbers obey it, found there are only two, and identified those two with the boundary classes of his system.

**Proposed text.**

```markdown
:::tip[Plain reading]
The argument runs in one direction: Boole notices that, in his calculus, $x \cdot x$ is always just $x$. He then asks which **numbers** could play the role of these symbols. Only $0$ and $1$ satisfy $x^2 = x$ in ordinary arithmetic. Boole reads this as a clue: if his logical symbols are to be interpreted as numbers at all, they must be these two. He assigns them to the empty class and to the universe of discourse — the only two classes whose extension is fixed in advance.
:::
```

### 3b. Plain reading after Boole's `x + y(1 − x)` workaround

**PROPOSED.**

**Insertion anchor.** Immediately after the paragraph that begins "The strict-disjoint addition was a limitation, and Boole himself knew it…" and ends "…over a calculus in which $+$ silently absorbed the disjointness assumption and the algebra acquired the slightly strange identity $x + x = x$." (line 105 in the current file).

**Why it qualifies as dense.** The paragraph's centerpiece — the formula $x + y(1 - x)$ — is the modern reader's inclusive-OR in unfamiliar dress. The prose tells the reader to "read it slowly" and supplies the gloss in the same sentence, but the formula's structure (adding to $x$ "the part of $y$ that does not already lie inside $x$") is precisely the Venn-diagram operation a present-day reader learns first and Boole's notation last. A 2-sentence plain-reading caption that maps the formula to the now-standard mental picture is the exact use case for this aid.

**Proposed text.**

```markdown
:::tip[Plain reading]
Modern notation writes the union of two sets as $x \cup y$. Boole, working only with multiplication, addition, and subtraction, had to construct the same idea by hand: take all of $x$, then add the slice of $y$ that does *not* already lie inside $x$. The formula $x + y(1 - x)$ is the modern $x \cup y$ assembled from Boole's three operations — same set, different machinery.
:::
```

### 3c. Plain reading after the Jevons-redefinition paragraph

**SKIPPED.**

The Jevons paragraph (line 109 in the current file) is historically dense but not *mathematically* dense — its load is narrative (who said what to whom in 1864), not symbolic. The prose itself glosses the technical move ("flattened Boole's careful partial operation into a total one") and quotes Boole's reply directly. A plain-reading caption here would paraphrase prose that is already plain. Refusing this third aside on the rubric's own criterion: no genuinely dense paragraph, no aide.

---

## Summary for Codex

| # | Element | Status | Rationale to test |
|---|---|---|---|
| 1 | Inline tooltip | SKIPPED | Starlight has no tooltip component; HTML `<abbr>` violates bit-identity. Glossary already covers terms non-destructively. |
| 2 | Pull-quote (Boole, "second degree → dichotomy") | PROPOSED | Brief identifies as load-bearing; chapter would forfeit its best candidate by skipping. |
| 3a | Plain reading after $x^2 = x$ derivation | PROPOSED | Three formal moves stacked; non-mathematician loses the *direction* of inference. |
| 3b | Plain reading after $x + y(1 - x)$ workaround | PROPOSED | Boole's notation for what modern readers know as $x \cup y$; mapping the formula to the union picture is the exact use case. |
| 3c | Plain reading after Jevons paragraph | SKIPPED | Narratively dense, not symbolically dense; gloss would paraphrase already-plain prose. |

For each PROPOSED element, please return APPROVE / REJECT (with reason) / REVISE (with suggestion). Be willing to reject. Forced Tier 3 elements produce filler — the goal is to keep only what genuinely helps a reader.
