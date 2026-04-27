# Infrastructure Log: Chapter 15 — The Gradient Descent Concept

What computing or experimental infrastructure each scene actually depended on. Anchored claims have a citation; unanchored material is flagged "background."

## Scene 1 — Cauchy 1847: paper mathematics

- **Computational infrastructure: none.** Cauchy's note (`Cauchy1847`) is pure paper mathematics — pen, ink, the *Comptes Rendus* of the Académie des Sciences as the publication channel. No computing devices, no tabular calculation aids; the gradient step is stated symbolically and verified by the kind of small hand-calculation a working astronomer of the period would do at a desk.
- **Stated motivation: astronomical orbit computation.** Cauchy says (per `Lemarechal12` p. 251) that astronomical calculations of the period are "normally very voluminous" and that he wants to compute the orbit of a heavenly body using the six elements of the orbit themselves as unknowns rather than reducing the differential equations. The infrastructural pressure that motivates the gradient method is therefore *human-time-on-arithmetic*, not machine-time.
- **Honest scope**: do not project later mechanical-calculator (e.g., Babbage's Difference Engine, the slide rule, Brunsviga calculators) infrastructure backward onto Cauchy's note. The note itself is silent on whether the iteration was meant to be evaluated by hand or with mechanical aid; Lemaréchal does not address this either.

## Scene 2 — Robbins-Monro 1951: pre-electronic statistical computation

- **Computational infrastructure: late-1940s mathematical-statistics computation.** The 1951 paper (`RobbinsMonro51`) does not present an *experimental* implementation — it presents an *abstract* iterative procedure that drives `x_n` toward `x*` in probability via successive observations. The infrastructural setting is the Bell-Labs / academic-statistics environment of late-1940s applied mathematics: punched-card tabulators (IBM 600-series and Mark-I-style electromechanical sequencers were common), early electronic computers had begun to appear (UNIVAC I delivered to the U.S. Census Bureau in 1951, the same year as the paper), and the assumed reader's "experiment" runs on whatever statistical apparatus is appropriate to the problem domain (clinical trials, quality-control sampling, response-curve estimation in chemistry or psychophysics).
- **Honest scope**: the 1951 paper is *infrastructure-agnostic* by design — the procedure is meant to apply to any experimental setup where successive observations are noisy and inexpensive. The chapter should not over-anchor a specific computer; the paper's framing is "you, the experimenter, can choose levels x_1, x_2, ...". This is **background**: the orchestrator's pre-staged note describes this scene as "punched-card-era statistics," which is correct as ambient context but is not asserted in `RobbinsMonro51` itself.

## Scene 3 — Widrow-Hoff 1960: Stanford analog hardware

- **Computational infrastructure: Stanford EE Department / Stanford University, ONR contract.** The Acknowledgment paragraph at `WidrowHoff60` p. 100 reads, in full: "This research was supported by the Office of Naval Research under contract with Stanford University." The institutional footnote at p. 96 places Widrow in the Department of Electrical Engineering, Stanford University; Hoff is a doctoral student in the same department.
- **Hardware: the Adaline as built device.** The 1960 paper says Adaline "is about the size of a lunch pail" (`WidrowHoff60` p. 96). It is described as an *adaptive pattern classification machine*, with:
  - a 4×4 input switch array (toggles set by the operator to feed crude geometric patterns to the machine),
  - a reference switch (sets the desired output ±1 for the current pattern),
  - a meter that displays neuron output and (when the reference switch is flipped) error voltage,
  - 16 input-line gains plus a level-control gain (a₀), each represented by a physical adjustable element.
- **Storage: MAD multi-aperture-device magnetic cores.** The Adaline gains are stored in MAD elements (`WidrowHoff60` p. 100, Section G "Adaptive Microelectronic Systems"; reference [11] H. D. Crane, "A high-speed logic system using magnetic elements and connecting wire only," Proc. IRE, January 1959, pp. 63–73). The paper describes the "special characteristics of these cores" as permitting "multilevel storage with continuous, non-destructive read out … the stored levels are easily changed by small controlled amounts, with the direction of the change being determined by Logic performed by the MAD element." The paper aims toward thin-film successors that would yield "adaptive microelectronic neurons" in the future.
- **What the chapter must NOT say.** The Adaline "memistor" (an electrolytic analog memory device) is a *later* Widrow development — the 1960 WESCON paper does not mention it; the OCR text contains zero occurrences of "memistor." Use only "MAD magnetic cores, with thin-film successors planned" — the language the WESCON paper actually uses.
- **Operating mode: human-in-the-loop training.** The training procedure described at `WidrowHoff60` p. 96 is operator-driven: the operator sets the input pattern via toggle switches, sets the reference switch for the desired ±1 output, reads the error voltage off the meter, and waits while gain adjustments are made. The paper notes that the iterative routine "is purely mechanical, and requires no thought on the part of the operator," with "electronic automation of this procedure" as a stated goal for the next-generation hardware.
- **Time constant**: for n=16 input lines plus a level control, one-pattern-at-a-time adaption gives a time constant of roughly 17 patterns (`WidrowHoff60` p. 98 derivation). Concrete number to anchor the "physical analog hardware with measurable dynamics" framing.

## Scene 4 — Linnainmaa 1970: mainframe FORTRAN

- **Computational infrastructure: University of Helsinki mainframe environment, 1970, FORTRAN.** Per `Schmidhuber15` p. 91: "See early FORTRAN code (Linnainmaa, 1970) and closely related work (Ostrovskii, Volin, & Borisov, 1971)." The FORTRAN-code mention is the only specific infrastructural anchor in the secondary chain; the specific hardware (which mainframe at Helsinki, what FORTRAN dialect, what input/output) is not page-anchored in this pass.
- **Honest scope**: the chapter can say "FORTRAN code, on the kind of late-1960s university mainframe a Helsinki computer-science master's student would have had access to," but should not anchor a specific machine model. The decisive infrastructural property is *that the chain rule was made executable as program code*, not what model of computer the program ran on.
- **What the chapter must NOT say.** No assertion of GPU computation (anachronistic by decades), no assertion of LISP (Linnainmaa wrote FORTRAN per Schmidhuber), no assertion of a connection to the AI labs at MIT/Stanford/CMU (Linnainmaa worked in Helsinki on rounding-error analysis, not on artificial intelligence).

## Scene 5 — The modern reinterpretation: no new infrastructure

- The synthesis scene relies entirely on the four prior scenes' infrastructure. No new computing or experimental apparatus is introduced. The chapter's forward pointer to Ch24 names but does not narrate the post-1970 infrastructure (DEC PDP-10s, Symbolics LISP machines, the Connection Machine, etc.) — those are Ch24 / Ch26 / Ch27 territory.

## Cross-chapter infrastructure consistency

- Ch14 anchors the Cornell Aeronautical Laboratory / IBM 704 / Mark I Perceptron analog hardware as Rosenblatt's program. Ch15 anchors a *parallel* Stanford EE / ONR / Adaline analog hardware program. The two cybernetic-hardware programs of 1958–1960 are coherent siblings, not rivals — the chapter should treat them as evidence that "learning-machine engineering" was a broader 1960 movement, exactly as Ch14 brief.md "cybernetic-hardware contemporary" layer anticipates.
- The Stanford EE / ONR funding line in Ch15 is *not* the same ONR funding line as Cornell Aero / Project PARA in Ch14 — both programs received Office of Naval Research support but through separate contracts (Stanford University contract for Widrow-Hoff per `WidrowHoff60` p. 100; Contract Nonr-2381(00) for Rosenblatt per Ch14's `PsychRev58` p. 386). The chapter can note "both Stanford-EE and Cornell-Aero were funded by ONR in this period" without conflating the contracts.
- Ch16 owns the broader ARPA / Cold-War-funding-of-AI logic. Ch15 does not anticipate it.
