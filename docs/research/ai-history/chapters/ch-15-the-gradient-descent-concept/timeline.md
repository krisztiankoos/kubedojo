# Timeline: Chapter 15 — The Gradient Descent Concept

A chronology of the events the chapter draws from. Anchored events have a Green/Yellow tag matching `sources.md`; unanchored items are background context only.

## 1847

- **October 18, 1847 — Cauchy presents "Méthode générale pour la résolution des systèmes d'équations simultanées" to the Académie des Sciences.** Three-page note in *Comptes Rendus de l'Académie des Sciences*, vol. 25, pp. 536–538. Two variants of the iteration (Armijo-type line search and steepest descent) and a least-squares extension to systems. No rigorous convergence proof; the announced follow-up *Mémoire* is never published. **Green** via `Lemarechal12` pp. 251–254.

## 1908

- **Hadamard publishes "Mémoire sur le problème d'analyse relatif à l'équilibre des plaques élastiques encastrées."** Schmidhuber's Section 5.5 cites Hadamard 1908 once parenthetically as an early-20th-century continuation of "minimization of errors through gradient descent." The connection is metaphorical at best — the paper is on equilibrium of clamped elastic plates. **Yellow** via `Schmidhuber15` p. 90 bibliography only; no Hadamard scene in this chapter.

## 1949

- **Wiener publishes *Extrapolation, Interpolation, and Smoothing of Stationary Time Series with Engineering Applications.*** Cited in `WidrowHoff60` reference [10] as the continuous-filter optimization framework that Widrow's discrete adaptive predictor is the analogue of. Background only.

## 1951

- **September 1951 — Robbins and Monro publish "A Stochastic Approximation Method"** in *The Annals of Mathematical Statistics* 22(3), pp. 400–407. DOI: 10.1214/aoms/1177729586. Defines the noisy-observation root-finding framework that the gradient-descent concept later inherits. **Green** for citation, DOI, page range, and high-level problem statement (via Project Euclid landing page). Specific theorem-page anchors stay **Yellow**.

## 1956

- **John von Neumann publishes "Probabilistic Logic and Synthesis of Reliable Organisms from Unreliable Components"** in *Automata Studies* (Princeton University Press). Cited in `WidrowHoff60` reference [3] as the source of the "neuron model" that Adaline resembles. Background only — von Neumann's neuron model and the McCulloch-Pitts lineage are owned by Ch5.

## 1957

- **Bellman publishes *Dynamic Programming.*** Cited in `Schmidhuber15` p. 90 as the framework "à la Dynamic Programming" within which Kelley/Bryson/Dreyfus iterate the chain rule. Background only.

## 1958

- **Rosenblatt publishes the *Psychological Review* perceptron paper.** Owned by Ch14. Mentioned here only because Ch14 forward-references Ch15 for the gradient-descent reinterpretation of the perceptron rule.

## 1959

- **Crane publishes "A high-speed logic system using magnetic elements and connecting wire only,"** *Proc. IRE*, January 1959, pp. 63–73. The MAD (multi-aperture device) magnetic-core element that `WidrowHoff60` p. 100 cites (reference [11]) as the storage technology for Adaline's gains. **Green** via the WESCON paper's reference list.
- **Widrow publishes "Adaptive sampled-data systems — a statistical theory of adaptation,"** 1959 WESCON Convention Record, Part 4. Cited in `WidrowHoff60` reference [7] as the statistical foundation Widrow's 1960 paper draws on. Background only.

## 1960

- **Kelley publishes "Gradient theory of optimal flight paths,"** *ARS Journal*, 30(10), pp. 947–954. The optimal-control / Euler–Lagrange precursor that Schmidhuber places at the head of his Section 5.5 attribution chain. **Green** for citation via `Schmidhuber15` p. 110 bibliography; specific in-paper anchor **Yellow**.
- **Widrow publishes "Adaptive sampled-data systems,"** IFAC Moscow Congress Record, Butterworth, London, 1960. Cited in `WidrowHoff60` reference [8] as a parallel companion paper to the WESCON. Background only.
- **August 1960 — Widrow and Hoff present "Adaptive Switching Circuits"** at the IRE WESCON convention. Published in the *1960 IRE WESCON Convention Record*, Part 4, pp. 96–104. Stanford EE / ONR. Introduces Adaline; explicit gradient-of-MSE framing on p. 97; explicit "method of steepest descent" framing on p. 98; MAD magnetic-core storage and thin-film successor plans on p. 100. **Green** for the eight specific page-anchored claims in `sources.md`.

## 1961

- **Bryson publishes "A gradient method for optimizing multi-stage allocation processes,"** *Proc. Harvard Univ. Symposium on Digital Computers and Their Applications*. **Green** for citation via `Schmidhuber15` p. 109 bibliography.
- **Bryson and Denham publish "A steepest-ascent method for solving optimum programming problems"** (Raytheon technical report BR-1303). **Green** for citation via `Schmidhuber15` p. 109 bibliography.
- **Pontryagin et al.** publish on optimal-control theory. Cited in the `Schmidhuber15` p. 90 attribution cluster. Background only.

## 1962

- **Dreyfus publishes "The numerical solution of variational problems,"** *Journal of Mathematical Analysis and Applications*, 5(1), pp. 30–45. Schmidhuber's Section 5.5 (`Schmidhuber15` p. 90) cites Dreyfus as the simplification that "uses the chain rule only." **Green** for citation; specific in-paper anchor **Yellow**.

## 1969

- **Bryson and Ho publish *Applied Optimal Control: Optimization, Estimation, and Control*** (Blaisdell). Cited in `Schmidhuber15` p. 90 as the textbook codification of the optimal-control gradient line. Background only.

## 1970

- **Linnainmaa submits his master's thesis at the University of Helsinki:** "The representation of the cumulative rounding error of an algorithm as a Taylor expansion of the local rounding errors." In Finnish. Per `Schmidhuber15` p. 91, this is the first explicit, efficient reverse-mode chain-rule machinery on arbitrary, discrete, possibly sparsely connected computational graphs, with FORTRAN code, *without* mentioning neural networks. **Yellow** via `Schmidhuber15` (the only English-language anchor in this pass).

## 1976

- **Linnainmaa publishes "Taylor expansion of the accumulated rounding error,"** *BIT Numerical Mathematics*, 16(2), pp. 146–160. Publicly archived restatement of the 1970 thesis machinery. Listed here as the practical citation chain most history-of-ML papers use; not page-extracted in this pass.

## After 1970 — owned by other chapters

- **1974 — Werbos's Harvard PhD thesis** *Beyond Regression: New Tools for Prediction and Analysis in the Behavioral Sciences.* Owned by Ch24.
- **1981 — Werbos publishes the first NN-specific application of efficient BP** (per `Schmidhuber15` p. 91). Owned by Ch24.
- **1986 — Rumelhart, Hinton, Williams publish "Learning representations by back-propagating errors,"** *Nature* 323, 533–536. Owned by Ch24.

## Cross-chapter anchor reuse

- `WidrowHoff60` is the same anchor key used in Ch14 (`docs/research/ai-history/chapters/ch-14-the-perceptron/sources.md` row for the Stanford analog-hardware contemporary). Ch14 had it Green for bibliographic metadata only; Ch15 upgrades several specific in-paper claims to Green.
- `POND61` is the Ch14 anchor for Rosenblatt's *Principles of Neurodynamics* and is used by Ch15 only at Scene 5 for the modern-reinterpretation cross-link.
