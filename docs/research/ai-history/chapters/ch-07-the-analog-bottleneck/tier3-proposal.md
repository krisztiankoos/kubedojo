# Tier 3 proposal — Chapter 7: The Analog Bottleneck

Per `docs/research/ai-history/READER_AIDS.md` Tier 3 workflow. Author: Claude. Reviewer: Codex (cross-family adversarial).

## Element 1 — Pull-quote (`:::note`, ≤1 per chapter)

**Status: SKIPPED**

Rationale: Rule (b). Every quote-worthy sentence in Ch07 is already inside a prose paragraph that introduces and contextualises it. Candidates considered:

- Walter on imitation of life: "is concerned more with performance and behavior" (Walter 1950, p. 42). Already in-prose with framing.
- Walter on the *Machina speculatrix* hardware: "two miniature radio tubes, two sense organs, one for light and the other for touch, and two effectors or motors" (Walter 1950, p. 42). Already in-prose at full length.
- Walter on the 280-years combinatorial argument: "a new pattern every tenth of a second for 280 years — four times the human lifetime of 70 years" (Walter 1950, p. 43). Already in-prose with the surrounding minimalism argument.
- Walter on self-recognition (the mirror passage): "flicker and jig at its reflection in a manner so specific that were it an animal a biologist would be justified in attributing to it a capacity for self-recognition" (Walter 1950, p. 45). Already in-prose with the hedge ("The hedge is doing real work…") that does the additional intellectual work.
- Walter on the dog-in-the-manger scene: "leading to the more needy one expiring from exhaustion within sight of succor" (Walter 1950, p. 45). Vivid but not the chapter's load-bearing claim.
- Walter on his three conditions for a legitimate model: "the absolute minimum of working parts to reproduce the known features" (Walter 1953, p. 280, via Holland 2003 p. 2095). Already in-prose with full three-condition list.
- Walter on the analogue framing: "The model is simply the analogue of one set of familiar mathematical expressions relating to passive networks linked by a nonlinear operator in the form of a discharge tube" (Walter 1953, pp. 284–286, via Holland 2003 pp. 2095–2096). Already in-prose at full length.
- Von Neumann on error: "Error is viewed, therefore, not as an extraneous and misdirected or misdirecting accident, but as an essential part of the process under consideration" (von Neumann 1952, IAS PDF p. 1). Already in-prose with full framing context.
- Von Neumann's §11.1 verdict: "The multiplexing technique is impractical on the level of present technology, but quite practical for a perfectly conceivable more advanced technology and for the natural relay organs (neurons)" (von Neumann 1952, IAS PDF p. 47). Already in-prose with the immediate explanation of what the contrast was.
- Walter's forward-look in May 1950: "More complex models that we are now constructing have memory circuits in which associations are stored as electric oscillations" (Walter 1950, p. 45). Already in-prose at full length, occupying its own paragraph.

Pull-quote: SKIP per (b). No candidate sentence would do *new* work as a callout that the surrounding prose has not already done.

## Element 2 — Plain-reading aside on a dense paragraph (`:::tip[Plain reading]`)

**Status: SKIPPED**

Rationale: `READER_AIDS.md` item 10 reserves plain-reading callouts for *symbolically* dense paragraphs (mathematical formulas, derivations, abstract definitions stacked) — explicitly *not* narratively dense paragraphs (history, biography, who-said-what). Ch07's symbolically densest moments are already plain-read by the very next prose paragraph in each case:

- **Von Neumann's 14,000-multiplexing-factor calculation** (paragraphs containing "1.4 × 10¹³ actuations… approximately 7 × 10⁻¹⁴… N ≈ 14,000"). The next sentence reads "In plain terms, the cure was larger than the disease. A 2,500-tube computer made reliable by this method would not merely add a few safety circuits around vulnerable components; the logical communication of the machine would have to be carried in 14,000-line bundles." That is already a plain reading. Adding a callout would only repeat it. **SKIP per item 10's "refuse the *individual* aside if its commentary would only repeat the surrounding prose."**
- **The four behaviour patterns E / P / N / O** (the Behaviour P / Behaviour N / Behaviour O paragraphs). Descriptive enumeration of relay states, not symbolic density. The prose already names each pattern, says when it triggers, and what the relays and motors do. SKIP.
- **The photocell → first-stage current → second-stage current → relay coil → motor chain** (the "voltage from this photocell controlled the first-stage current of the amplifier" paragraph). This is a circuit walk-through written in plain English, not a stacked abstract definition. SKIP.
- **Walter's three conditions for a legitimate model**: a stacked enumeration of constraints, but Walter's own phrasing is plain English ("the model must contain the absolute minimum of working parts to reproduce the known features"). The subsequent paragraph already plain-reads it ("This was not minimalism for elegance alone. It was a method of biological argument…"). SKIP.
- **The "model is simply the analogue" passage** (Walter 1953 pp. 284–286 via Holland). This is the chapter's most abstract sentence ("simply the analogue of one set of familiar mathematical expressions relating to passive networks linked by a nonlinear operator in the form of a discharge tube"). The next paragraph already plain-reads it: "The staggering combinatorial output of the tortoises… served as his primary defence of minimalism. A low-component-count model could, in principle, explore an almost inexhaustible state space." Plus the paragraph immediately after re-frames the bottleneck. SKIP.
- **The 280-years combinatorial argument** ("a new pattern every tenth of a second for 280 years"). One short numerical claim, immediately given a comparator ("four times the human lifetime of 70 years") in Walter's own quoted prose. Not symbolically dense in the item-10 sense. SKIP.

No paragraph in Ch07 satisfies the symbolic-density criterion in a way that the next paragraph does not already plain-read. SKIP per item 10's explicit permission to refuse.

## Element 3 — Inline parenthetical definition (Starlight tooltip)

**Status: SKIPPED**

Rationale: `READER_AIDS.md` item 8 — universal SKIP across every chapter until a non-destructive tooltip component lands. Ch07's specialist terms (*Machina speculatrix*, photocell, multivibrator, tropism, multiplexing, mean free path, hardware-as-program) are covered by the Plain-words glossary above.

---

## Author's prediction

Calibration so far: Ch01 2/5; Ch02 0/4; Ch03 1/3; Ch04 0/3; Ch05 0/3; Ch06 0/3. Ch07 has the same shape as the 0/3 group — every quote-worthy sentence is already in-prose, and every symbolically dense paragraph is already plain-read by the next paragraph. Predicting **0/3** with all-AGREE from Codex. Open to a counter-proposal, especially if Codex sees a paragraph I've miscategorised as not-symbolically-dense.
