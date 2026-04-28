# Infrastructure Log: Chapter 5 — The Neural Abstraction

The 1943 paper has a thin infrastructure story by design. There was no machine. There was no simulation. There was no compute budget. The paper is a *formal* proof-of-principle, written in pencil-on-paper symbolic logic and published in a print journal. The chapter's infrastructure thread must therefore be honest about the absence of running hardware and concentrate on the *intellectual* infrastructure — symbolic notation, journal venue, and downstream uptake into actual machine architecture.

## Computational Infrastructure of the 1943 Paper Itself

| Item | Description | Anchor |
|---|---|---|
| Computing hardware | None. The paper is a paper-and-pencil mathematical argument. There is no simulation of any net, no implementation of any threshold-logic gate. | Implicit; M-P 1943 has no implementation section. The paper's "Various applications of the calculus are discussed" (p.115 abstract) refers to applications-on-paper. |
| Symbolic notation | "Language II of Carnap (1938), augmented with various notations drawn from Russell and Whitehead (1927)." Includes the Carnap syntactical notations (printed in boldface), the Principia conventions for dots, an upright `E` for the existential operator (typographical convenience), an arrow `→` for implication, and the temporal-shift functor $S$ defined so that $S(P)(t) \equiv P(t-1)$. | M-P 1943 p.118 (Section 2 opening). Verified by `pdftotext` 2026-04-28. |
| Idealised neuron | Binary threshold unit. Five physical assumptions: all-or-none firing; fixed-number-of-synapses threshold; synaptic delay as the only significant delay (~0.5 ms in the introduction's quantitative gloss, p.116); absolute inhibition by an inhibitory synapse; structure of the net invariant in time. | M-P 1943 p.118 (Section 2 numbered list); pp.116-117 (introduction's biophysical context for the assumptions). |
| Quantitative biological glosses | Synaptic delay > 0.5 ms; period of latent addition ~0.25 ms; axonal conduction velocity < 1 m/s in thin axons, > 150 m/s in thick axons. The chapter may use these to ground the all-or-none assumption in 1940s neurophysiology, but should not over-quote — they are background, not the calculus. | M-P 1943 p.116 (introduction). Verified by `pdftotext` 2026-04-28. |
| Threshold-logic gate constructions | AND realised at threshold $\theta = 2$ with two inputs; OR at $\theta = 1$; NOT via inhibitory connection. The constructions are pencil-and-paper diagrams (paper Figure 1). | M-P 1943 pp.118-124 (theorems and figures for nets without circles). The chapter may reproduce one or two as line-art if the prose layer permits. |
| Nets with circles | The Section 3 extension allows recursive predicates and bounded memory by feeding outputs back as inputs through circular pathways. This is what gives the calculus its full reach (anything Turing-computable using bounded memory). | M-P 1943 pp.124-130 (Section 3). |
| Theorem 7 (alterable synapses) | Formal absorption of synaptic plasticity into nets-with-circles: a net whose connections change over time can be re-expressed as a fixed net with extra circular pathways set into activity by the right peripheral afferents. | M-P 1943 p.124 (verbatim Theorem 7). The chapter must keep this as the chapter's primary defence against the "no learning treatment" framing. |

## Publication Infrastructure

| Item | Description | Anchor |
|---|---|---|
| Journal | *Bulletin of Mathematical Biophysics*, vol. 5 (1943), pp. 115-133. Founded and edited at Chicago by Nicolas Rashevsky, who also led the mathematical-biophysics community Hebb later catalogued at p.xv of the 1949 *Organization of Behavior*. The venue mattered: it placed the paper inside the same print and intellectual circuit as Rashevsky's continuous-biophysics work, even as M-P were quietly switching to symbolic logic. | M-P 1943 reprint header (1990 reprint, p.99 footer); Hebb 1949 p.xv. |
| Author affiliation | "University of Illinois, College of Medicine, Department of Psychiatry at the Illinois Neuropsychiatric Institute, University of Chicago, Chicago, U.S.A." | M-P 1943 p.115 (author block). Verified by `pdftotext` 2026-04-28. The dual-affiliation phrasing is unusual and reflects McCulloch's joint posts; Pitts had no formal affiliation at the time of writing. |
| Reprint route | The paper was reprinted in 1990 in *Bulletin of Mathematical Biology* vol. 52, pp. 99-115 — the digital copy widely circulated today. The reprint is reliable for direct quotation and pagination conversion (reprint page = original page minus 16). | Reprint header. Verified 2026-04-28. |

## Intellectual Infrastructure: What the 1943 Paper Borrowed

| Source | Borrowing | Anchor |
|---|---|---|
| Carnap, *Logical Syntax of Language* (1938) | Language II symbolic notation; the Carnap syntactical conventions printed in boldface; the framing of formal sentences as syntactic objects. | M-P 1943 p.118 (verbatim citation); M-P 1943 p.131 (literature list). |
| Russell-Whitehead, *Principia Mathematica* (2nd ed. 1925) | The dots-as-grouping convention; the inverted-E existential operator (replaced by upright `E` for typographical convenience in the 1943 paper); the propositional-logic apparatus generally. | M-P 1943 p.118 (in-text "Russell and Whitehead (1927)"; the literature list at p.131 says "1925"); M-P 1943 p.131. |
| Hilbert and Ackermann, *Grundzüge der Theoretischen Logik* (1927) | Hilbert disjunctive normal form, used in the Section 3 derivation for nets with circles. | M-P 1943 p.131 (literature list); used implicitly in the body of Section 3. |
| Rashevsky-school mathematical biophysics | The biophysical assumptions about neuron behaviour (all-or-none, threshold, synaptic delay) circulated in Rashevsky's *Bulletin of Mathematical Biophysics* throughout the 1930s. The novelty of M-P 1943 is the *symbolic-logic* superstructure on top of this biophysics, not the biophysics itself. | Piccinini 2004 abstract; Hebb 1949 p.xv; M-P 1943 itself published in this journal. |

## Downstream Computing Infrastructure: What the 1943 Paper Set Up

| Item | Description | Anchor |
|---|---|---|
| Finite automata theory | Kleene's 1956 paper "Representation of Events in Nerve Nets and Finite Automata" (in the Shannon-McCarthy *Automata Studies* volume) reads M-P 1943 as the founding text of finite-automata theory. | Out-of-scope for primary anchoring in this chapter; bibliographic forward-pointer only. Piccinini 2004 abstract identifies this as the first of M-P's four contributions. |
| Logic design | The use of threshold-logic gates as building blocks for digital design flowed forward into computer engineering. Piccinini 2004 abstract identifies this as the second M-P contribution. | Piccinini 2004 abstract. |
| The von Neumann *First Draft of a Report on the EDVAC* (June 1945) | Section 4.2, p.12 cites the 1943 paper verbatim: "Following W. Pitts and W. S. McCulloch ('A logical calculus of the ideas immanent in nervous activity', Bull. Math. Bio-physics, Vol. 5 (1943), pp 115-133) we ignore the more complicated aspects of neuron functioning…" A full-document scan confirms it is the only journal citation in the report — von Neumann ignores all other neural-modelling sources and works directly from M-P 1943's idealised threshold neuron when designing the EDVAC's logical units. | **Green**. Verified by Claude `curl` + `pdftotext` on the Internet Archive scan 2026-04-28. The chapter's honest close uses this as the most concrete downstream-uptake anchor. |
| Hebb's 1949 biological postulate | Hebb 1949 p.62 — the postulate that synapses strengthen with repeated co-activation — is a biological hypothesis adjacent to (not algorithmic for) M-P 1943's calculus. The chapter must keep this distinction. | **Green** via direct `pdftotext` 2026-04-28. |
| Rosenblatt's perceptron (1957-1958) | The first *algorithmic* learning rule for a McCulloch-Pitts-style network. Out-of-scope for this chapter; reserved for Ch14. | Forward-pointer only. |

## What the Chapter Should Not Claim

- That the 1943 paper "ran" or "simulated" anything. It is paper mathematics.
- That there was a 1940s machine implementation of a McCulloch-Pitts network. There was not.
- That M-P-style threshold logic was novel as a *biophysical* model. The Rashevsky community had been doing biophysics of neurons for over a decade. What was novel was the symbolic-logic superstructure.
- That Hebb 1949 p.62 is a learning algorithm. It is a biological postulate. The first algorithmic learning rule for these networks is Rosenblatt's perceptron, treated in Ch14.
- That the von Neumann *First Draft* citation footprint is a "discovery" of this chapter. It is a Yellow secondary claim from Gefter; it can be upgraded but the chapter must not present it more confidently than the verification permits.
