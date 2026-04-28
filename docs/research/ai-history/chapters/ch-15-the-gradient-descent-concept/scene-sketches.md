# Scene Sketches: Chapter 15 — The Gradient Descent Concept

Five scenes mapped 1:1 to the Prose Capacity Plan layers in `brief.md`. Each scene lists the load-bearing claims it can spend words on, with anchor pointers, and the *boundary* — what the scene is forbidden to say.

## Scene 1 — The Note Cauchy Never Followed Up

**Word range**: 800–1,200 (Prose Capacity Plan layer 1).

**Setting**: Académie des Sciences, Paris, October 18, 1847.

**Beats**:

1. The note's title and venue (`Lemarechal12` p. 251 + p. 254 [1] reference): "Méthode générale pour la résolution des systèmes d'équations simultanées," *Comptes Rendus de l'Académie des Sciences*, vol. 25, pp. 536–538.
2. Cauchy's stated motivation, in his own voice via Lemaréchal's translation (`Lemarechal12` p. 251, with original French in footnote 2): astronomical orbit computation, six elements of the orbit as the unknowns, an alternative to reducing the differential equations.
3. The mathematical statement (`Lemarechal12` p. 252, eq. (1)): for a non-negative continuous function `u = f(x, y, z, …)` with derivatives X, Y, Z, ..., let `α = -θX, β = -θY, γ = -θZ, …` for small positive θ. Cauchy's first-order argument shows the function decreases at this step.
4. The two variants in Cauchy's text (`Lemarechal12` p. 253, eqs. (2) and (3)): the Armijo-type line search variant `Θ = f(x - θX, y - θY, z - θZ, …)` and the steepest-descent variant defined by the univariate stationarity condition `Θ′_θ = 0`. This is the scene's most important *deflationary* beat — modern textbooks say "Cauchy proposed steepest descent"; Cauchy actually proposed two variants on the same page.
5. The least-squares extension (`Lemarechal12` p. 253, eq. (4)): for a system `u = 0, v = 0, w = 0, …`, apply the same idea to the single equation `u² + v² + w² + … = 0`. Lemaréchal's footnote 7 cross-references the older Legendre/Gauss least-squares dispute; the chapter can mention it once and move on.
6. The deferred convergence proof (`Lemarechal12` p. 254, with original French in footnote 9): Cauchy writes that he is only "outlining the principles" and intends to return to the subject "in a paper to follow" — `me proposant de revenir avec plus de détails sur le même sujet, dans un prochain Mémoire`. Lemaréchal documents that the follow-up *Mémoire* never appears.
7. The note's marginal status within Cauchy's body of work (`Lemarechal12` p. 251, parenthetical): "a paper every week" of more central work on analysis, complex functions, mechanics. The 1847 note was not, for Cauchy, a major paper.

**Boundary**:

- Do not invent biographical color around the Académie meeting. Lemaréchal does not give a meeting-room scene.
- Do not say "Cauchy invented gradient descent." The honest framing is "Cauchy gave the published-on-paper origin point of what later got called gradient descent."
- Do not project mechanical-calculator infrastructure backward (see `infrastructure-log.md` Scene 1).
- Do not frame the never-published follow-up as a *failure* — Lemaréchal's reading is closer to "he underestimated the difficulty and never came back to it," which is not the same as failure. The chapter can say both.

## Scene 2 — Robbins, Monro, and the Stochastic Bridge

**Word range**: 400–600 (Prose Capacity Plan layer 2). Deliberately compact.

**Setting**: *Annals of Mathematical Statistics* 22(3), September 1951.

**Beats**:

1. The citation (`RobbinsMonro51`): "A Stochastic Approximation Method," *Annals of Mathematical Statistics* 22(3), pp. 400–407, DOI 10.1214/aoms/1177729586.
2. The problem statement, in the paper's own framing (`RobbinsMonro51` Project Euclid landing-page abstract): there is a monotone unknown regression function `M(x)`; the experimenter wants to find the level `x*` where `M(x*)` equals a given constant `α`; only successive noisy observations of `M` at chosen levels `x_1, x_2, …` are available; the procedure drives `x_n` toward `x*` *in probability*.
3. The careful gradient-descent bridge (the chapter's own synthesis, *not* a Robbins-Monro claim): Cauchy's iteration assumes the gradient is known exactly at the current point. Many learning-from-data settings give only a noisy estimate. Robbins-Monro shows there is a recursive procedure with a vanishing step-size sequence that still converges — later expositions write the conditions as `Σ c_n = ∞`, `Σ c_n² < ∞`. Modern hindsight calls the combined idea "stochastic gradient descent"; the 1951 paper does not use the phrase.
4. A short closing paragraph that names the two things the 1951 paper is *not*: it is not a paper about neural networks (which did not exist as a research program in 1951), and it is not a paper that uses the word "gradient." It is a noisy-observation root-finding paper that the gradient-descent concept later inherits.

**Boundary**:

- Do not state Theorem 2 (the convergence-in-probability result) with anchored page numbers in this pass. The Project Euclid PDF is Imperva-blocked; the specific theorem statement stays Yellow until a non-Imperva mirror is located.
- Do not assert "Σ" notation as Robbins-Monro's own — frame as "the conditions Robbins-Monro imposed on their step-size schedule, later usually written as `Σ c_n = ∞`, `Σ c_n² < ∞`."
- Do not draft Robbins's later empirical Bayes work or Monro's career trajectory. The 1951 paper is the only contact point.

## Scene 3 — Widrow, Hoff, and the Lunch-Pail Adaline

**Word range**: 1,100–1,500 (Prose Capacity Plan layer 3). The chapter's evidence-richest scene.

**Setting**: IRE WESCON convention, August 1960. Stanford EE Department.

**Beats**:

1. The citation and venue (`WidrowHoff60` p. 96 institutional footnote, p. 104 reprint stamp): "Adaptive Switching Circuits," *1960 IRE WESCON Convention Record*, Part 4: Computers, pp. 96–104. Widrow at Stanford EE; Hoff a Stanford EE doctoral student. ONR contract with Stanford (`WidrowHoff60` p. 100 Acknowledgment).
2. The Adaline as built device (`WidrowHoff60` p. 96, Section C "An Adaptive Pattern Classifier"): "An adaptive pattern classification machine (called 'Adaline,' for adaptive linear) has been constructed for the purpose of illustrating adaptive behavior and artificial learning." It is "about the size of a lunch pail." Photograph caption (Fig. 2 reference).
3. The neuron architecture (`WidrowHoff60` p. 96, Section B "A Neuron Element"): ±1-valued binary inputs; a linear combination through adjustable gains a₀, a₁, ..., aₙ (a₀ is the level/threshold control, fed +1 permanently); a thresholding output of +1 if the weighted sum exceeds threshold, -1 otherwise. The neuron's resemblance to a "neuron model introduced by von Neuman" is acknowledged (reference [3]).
4. The training procedure (`WidrowHoff60` p. 96, Section C, lines describing Adaline's operation): toggle switches set the input pattern in the 4×4 array; the reference switch sets desired output ±1; the operator reads the error voltage on the meter; gain adjustments are made; the per-pattern step shrinks the error magnitude by a factor 1/17 in this 4×4-input case. The procedure "is purely mechanical, and requires no thought on the part of the operator."
5. **The two load-bearing quotes — the chapter's central anchor.** First, `WidrowHoff60` p. 97 paragraph following the boss/worker block-diagram (Fig. 7 area): "The 'error' signal in the feedback control sense is the gradient of mean square error with respect to adjustment." Then, `WidrowHoff60` p. 97 paragraph immediately after: "Many of the commonly used gradient methods search surfaces for stationary points by making changes in the independent variables (starting with an initial guess) in proportion to measured partial derivatives to obtain the next guess … These methods give rise to geometric (exponential) decays in the independent variables as they approach a stationary point for second-degree or quadratic surfaces." Then, `WidrowHoff60` p. 98 paragraph following the squared-error derivation: "The method of searching that has proven most useful is the method of steepest descent. Vector adjustment changes are made in the direction of the gradient." This is a 1960 paper *naming* gradient descent on its own — and using Cauchy's vocabulary explicitly.
6. The mean-square-error surface as parabolic in the gain settings (`WidrowHoff60` p. 97 text accompanying Eq. (1); p. 98 text following Eq. (11)): a quadratic function of the adjustments. This makes the steepest-descent terminus calculable in closed form for the analyzed conditions.
7. The time-constant calculation (`WidrowHoff60` p. 98 derivation following Eq. (15)): for one-pattern-at-a-time adaption with k = 1/(2(n+1)), the time constant is τ = (n+1) patterns. For Adaline's n=16 input lines plus a level control, this is roughly 17 patterns; verified empirically against Fig. 5's learning curve.
8. The analog memory technology (`WidrowHoff60` p. 100, Section G "Adaptive Microelectronic Systems"): the Adaline gains are stored in MAD (multi-aperture-device) magnetic-core elements per Crane 1959 (reference [11]). The paper aims toward thin-film successors that would yield "adaptive microelectronic neurons" eventually. **No mention of the memistor — the chapter must respect this.**
9. The closing positioning beat: this is the *parallel* cybernetic-hardware program to Rosenblatt's perceptron (Ch14 cross-link). Both Stanford-EE and Cornell-Aero received ONR support; both built electromechanical learning devices in 1958–1960. The decisive difference is that Widrow-Hoff *wrote down explicitly* what the learning rule was doing in gradient/steepest-descent vocabulary, in print, in 1960.

**Boundary**:

- Do not assert "memistor." The 1960 paper documents MAD magnetic cores.
- Do not assert "TR 1553-1." The 1960 paper does not cite that number.
- Do not anticipate Hoff's later Intel 4004 work.
- Do not lapse into a numerical-analysis tutorial on the misadjustment formulas. The chapter is a history; quote the paper's own vocabulary ("misadjustment," "time constant"), do not derive modern equivalents.
- Do not say Widrow-Hoff "invented gradient descent" or "invented SGD." They explicitly cite "the method of steepest descent" by name as a known numerical-analysis technique.

## Scene 4 — Linnainmaa and the Chain Rule on Arbitrary Graphs

**Word range**: 500–700 (Prose Capacity Plan layer 4). Deliberately compact because the underlying primary source is in Finnish.

**Setting**: University of Helsinki, 1970.

**Beats**:

1. The thesis citation (`Schmidhuber15` p. 91; bibliography p. 111): Linnainmaa, S. (1970), "The representation of the cumulative rounding error of an algorithm as a Taylor expansion of the local rounding errors," Master's thesis, University of Helsinki (in Finnish). The 1976 BIT paper "Taylor expansion of the accumulated rounding error" is the publicly archived restatement.
2. What the thesis gives, per Schmidhuber (`Schmidhuber15` p. 91 paragraph beginning "Explicit, efficient error backpropagation …"): the first explicit, efficient reverse-mode chain-rule machinery on arbitrary, discrete, possibly sparsely connected computational graphs, *including FORTRAN code*, *without reference to NNs*.
3. The conceptually decisive property (`Schmidhuber15` p. 91, same paragraph; cites Griewank 2012): this is what is now called the *reverse mode* of automatic differentiation — "the costs of forward activation spreading essentially equal the costs of backward derivative calculation." Linear-cost chain-rule propagation is what makes deep computational graphs feasible.
4. The optimal-control precursor cluster (`Schmidhuber15` p. 90, Section 5.5 paragraphs 1–2): Schmidhuber places Linnainmaa as the abstraction step downstream of Kelley 1960, Bryson 1961, Bryson & Denham 1961, Bryson & Ho 1969, Dreyfus 1962, Pontryagin 1961 — "initially within the framework of Euler–Lagrange equations in the Calculus of Variations." Dreyfus 1962 is singled out as "a simplified derivation … using the chain rule only." The chapter mentions these as a citation cluster, not individual scenes.
5. The closing "what Linnainmaa did *not* do" beat: the thesis never mentions neural networks. Backpropagation as a learning algorithm for NNs comes later — Werbos 1981 NN-specific application, Rumelhart-Hinton-Williams 1986. Both are Ch24's territory.

**Boundary**:

- Do not say "Linnainmaa invented backprop." The honest claim is "first explicit, efficient reverse-mode chain-rule machinery on arbitrary computational graphs."
- Do not anchor specific Helsinki mainframe hardware (which model, what FORTRAN dialect) — Schmidhuber's chain does not give it.
- Do not adopt Schmidhuber's Ivakhnenko priority claims (Section 5.3) or any other contested attribution — the Linnainmaa attribution is the only one Ch15 needs.
- Do not draft a Werbos / Rumelhart / Hinton scene. Forward-reference Ch24 once at Scene 5.

## Scene 5 — The Modern Reinterpretation, and Where Ch15 Stops

**Word range**: 600–900 (Prose Capacity Plan layer 5).

**Setting**: synthesis. No new historical event.

**Beats**:

1. The thesis sentence (anchored to the entire Scene-Level Claim Table): the perceptron rule (Ch14, `POND61`) and the LMS rule (Ch15, `WidrowHoff60`) can be read, in modern terms, as stochastic gradient descent on different loss surfaces — a piecewise-linear loss for the perceptron, a squared-error loss for Adaline. **But only Widrow-Hoff actually wrote that down in 1960** (`WidrowHoff60` p. 97 gradient-of-MSE quote, p. 98 steepest-descent quote). Rosenblatt did not write "gradient descent on a piecewise-linear loss" anywhere in `POND61`; the modern reading attributes the framing in retrospect.
2. The four-node summary, in the order the chapter narrated them:
   - Cauchy gave the *iteration* on paper (Scene 1, anchored to `Lemarechal12`).
   - Robbins-Monro gave a way to drive parameters under *noisy observations* (Scene 2, anchored to `RobbinsMonro51`).
   - Widrow-Hoff gave the *first explicit gradient-method framing* on physical analog hardware (Scene 3, anchored to `WidrowHoff60`).
   - Linnainmaa gave the *machinery* to compute the gradient through any computational graph (Scene 4, anchored to `Schmidhuber15`).
3. None of the four claimed to have invented "neural network training." The chapter must say this explicitly; it is the chapter's central honest-history move.
4. A single thin forward pointer to Ch24 (anchored to `Schmidhuber15` p. 91 paragraph beginning "To my knowledge, the first NN-specific application …"): the Linnainmaa → Werbos 1981 → Rumelhart-Hinton-Williams 1986 chain is what makes backpropagation-as-NN-learning-algorithm. That is not Ch15's territory.
5. The honest close: this chapter is the conceptual hinge of the book's algorithmic narrative, not the climax. The climax is Ch24 (the math that waited for the machine).

**Boundary**:

- Do not draft any beat that is not anchored above.
- Do not say "the perceptron is gradient descent" without the modifier "in modern reading" or equivalent.
- Do not anticipate Ch24. The forward pointer is a single sentence.
- Do not introduce new primary sources at Scene 5. The synthesis must rest on what the prior scenes already anchored.
