# People: Chapter 15 — The Gradient Descent Concept

Only people who play a load-bearing role in the chapter. Background-only figures from `timeline.md` (Bellman, Crane, Pontryagin, Wiener, von Neumann) are omitted here — they appear in the chapter as citations, not as scene actors.

## Primary scene actors

### Augustin-Louis Cauchy (1789–1857)

- **Role**: presents the 1847 *Comptes Rendus* note that becomes the published-on-paper origin point of the gradient method.
- **Anchored facts** (`Lemarechal12` pp. 251–254): French mathematician; the 1847 note was a marginal contribution within his work ("a paper every week" of more central work on analysis, complex functions, mechanics). The 1847 note's stated motivation was astronomical — computing the orbit of a heavenly body, with the six elements of the orbit as unknowns. Cauchy himself wrote that he was only "outlining the principles" and intended to return to the subject in a follow-up *Mémoire*.
- **Boundary**: do not draft a Cauchy biography. The chapter uses him only at the moment of the 1847 note.
- **Lifespan dates** are background; the only date the chapter cites is October 18, 1847.

### Herbert Robbins (1915–2001)

- **Role**: co-author with Sutton Monro of the 1951 *Annals of Mathematical Statistics* paper that gives the noisy-observation root-finding framework.
- **Anchored facts** (`RobbinsMonro51` Project Euclid landing page): co-authored "A Stochastic Approximation Method," *Annals of Mathematical Statistics* 22(3), September 1951, pp. 400–407. DOI: 10.1214/aoms/1177729586.
- **Boundary**: the chapter does not need Robbins's biography or his other major work (e.g., *empirical Bayes*). The 1951 paper is the only contact point.

### Sutton Monro

- **Role**: co-author with Robbins of the 1951 paper.
- **Anchored facts**: same as Robbins (`RobbinsMonro51`).
- **Boundary**: identified primarily via the joint paper. The chapter does not narrate his career separately.

### Bernard Widrow (b. 1929)

- **Role**: senior author of the 1960 IRE WESCON paper; Stanford EE professor; principal of the Adaline program.
- **Anchored facts** (`WidrowHoff60` p. 96 institutional footnote, p. 100 Acknowledgment): Department of Electrical Engineering, Stanford University. Work supported by the Office of Naval Research under contract with Stanford. Widrow's prior 1959 WESCON paper "Adaptive sampled-data systems — a statistical theory of adaptation" (`WidrowHoff60` ref [7]) and his 1960 IFAC Moscow paper "Adaptive sampled-data systems" (ref [8]) are the statistical foundations the 1960 paper draws on.
- **Boundary**: the chapter does not narrate Widrow's later (post-1960) memistor or MADALINE work. Stay inside what the 1960 WESCON paper documents.

### Marcian E. Hoff Jr. (b. 1937)

- **Role**: co-author of the 1960 IRE WESCON paper; Stanford EE doctoral student at the time.
- **Anchored facts** (`WidrowHoff60` p. 96 institutional footnote: "Doctoral student in the Department of Electrical Engineering, Stanford University"): doctoral student under Widrow at Stanford EE during the work.
- **Boundary**: do not anticipate Hoff's later career (Intel 4004 microprocessor, 1971). For Ch15, he is the doctoral co-author of the 1960 paper. His later fame is *not* the chapter's territory.

### Seppo Linnainmaa (b. 1945)

- **Role**: 1970 master's thesis at the University of Helsinki gives the first explicit, efficient reverse-mode chain-rule machinery on arbitrary computational graphs.
- **Anchored facts** (`Schmidhuber15` p. 91): the 1970 thesis is in Finnish, titled "The representation of the cumulative rounding error of an algorithm as a Taylor expansion of the local rounding errors," and never mentions neural networks. It includes FORTRAN code. The 1976 BIT paper "Taylor expansion of the accumulated rounding error" is the publicly archived restatement.
- **Boundary**: do not anticipate Linnainmaa's later career or claim he "invented backprop." The chapter says "first explicit, efficient reverse-mode chain-rule machinery on arbitrary computational graphs," anchored to Schmidhuber 2015.

## Secondary actors (background mentions only — do not get a scene)

### Henry J. Kelley (1926–1988)

- **Role**: 1960 *ARS Journal* paper "Gradient theory of optimal flight paths" is, per `Schmidhuber15` p. 90, one of the optimal-control precursors to the chain-rule-on-multistage-systems lineage Linnainmaa later abstracted.
- **Anchored facts**: paper citation — *ARS Journal*, 30(10), pp. 947–954 — Green via `Schmidhuber15` p. 110 bibliography.
- **Boundary**: appears in Scene 4 as a bullet of the precursor cluster. No scene.

### Arthur E. Bryson (b. 1925)

- **Role**: 1961 Harvard Symposium paper "A gradient method for optimizing multi-stage allocation processes" is, per `Schmidhuber15` p. 90, the multi-stage gradient/optimal-control work alongside Kelley.
- **Anchored facts**: paper citation Green via `Schmidhuber15` p. 109 bibliography. Co-authored 1969 textbook *Applied Optimal Control* with Y. C. Ho (Blaisdell).
- **Boundary**: precursor cluster bullet only. No scene.

### Stuart E. Dreyfus (b. 1931)

- **Role**: 1962 *J. Math. Analysis and Applications* paper "The numerical solution of variational problems" is, per `Schmidhuber15` p. 90, the simplification that "uses the chain rule only."
- **Anchored facts**: paper citation Green via `Schmidhuber15` p. 109 bibliography.
- **Boundary**: precursor cluster bullet only. No scene.

### Claude Lemaréchal (b. 1944)

- **Role**: not an actor in any scene; he is the *anchor bridge*. His 2012 Documenta Math. ISMP note "Cauchy and the Gradient Method" is the source through which every Cauchy-1847 Green claim in this chapter is verified.
- **Anchored facts**: senior INRIA optimization researcher; the 2012 note is part of the 2012 International Symposium on Mathematical Programming "Optimization Stories" volume.
- **Boundary**: he is cited in the chapter as "Lemaréchal documents …" or "per Lemaréchal," not narrated as a person.

### Jürgen Schmidhuber (b. 1963)

- **Role**: not an actor in any scene; he is the *anchor bridge* for Linnainmaa, Kelley, Bryson, Dreyfus, and the broader Cauchy → optimal-control → reverse-mode chain. His 2015 *Neural Networks* survey "Deep learning in neural networks: An overview" Section 5.5 is the single secondary chain that anchors the Linnainmaa attribution in English.
- **Boundary**: cited as "Schmidhuber's history attributes … " or "per Schmidhuber's Section 5.5," not narrated. The chapter's Conflict Notes flag that Schmidhuber's history is itself contested in places (e.g., Ivakhnenko priority claims in Section 5.3, which Ch15 does not adopt).

## Out-of-scope figures (named for boundary reasons only)

- **Frank Rosenblatt** — Ch14. Cross-link only; Ch15 does not narrate him.
- **John von Neumann** — Ch5 (McCulloch-Pitts lineage). The 1960 WESCON paper acknowledges his neuron model (`WidrowHoff60` p. 96, ref [3]); the chapter cites it once and moves on.
- **Norbert Wiener** — Ch6 (cybernetics). Wiener's 1949 *Extrapolation* book is cited in `WidrowHoff60` ref [10] as the continuous-filter analogue framework; Ch15 mentions only as a citation, not a scene.
- **Paul Werbos, David Rumelhart, Geoffrey Hinton, Ronald Williams** — Ch24. The Linnainmaa → Werbos → 1986 Nature chain is forward-referenced once at Scene 5 and not narrated here.
- **Henri Poincaré, Joseph-Louis Lagrange, Leonhard Euler** — Schmidhuber's parenthetical "Euler-Lagrange equations in the Calculus of Variations (e.g., Euler, 1744)" appears in the precursor cluster but the chapter does not draft scenes for these figures.
- **Pierre-Louis Lions** — the orchestrator's pre-staged note suggested him as a possible historiographic source on Cauchy. Lemaréchal 2012 is the cleaner anchor; Lions does not appear in this chapter.
- **Hadjisavvas 1986** — historical note on Cauchy mentioned in the orchestrator's pre-staged note. Not verified in this pass; not used.
