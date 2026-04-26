# Sources: Chapter 26 - Bayesian Networks

## Verification Legend

- Green: source is strong enough for drafting the stated claim once page/section anchors are recorded.
- Yellow: source is relevant but needs exact passage extraction, access verification, or corroboration.
- Red: claim should not be drafted except as an open question.

## Primary Sources

| Source | Use | Verification |
|---|---|---|
| Judea Pearl, "Fusion, propagation, and structuring in belief networks," *Artificial Intelligence* 29(3), 241-288, 1986. DOI: `10.1016/0004-3702(86)90072-X`. URL: https://www.sciencedirect.com/science/article/pii/000437028690072X | Core primary source for belief-network definition, local propagation, and the idea that network links can direct data flow as well as store knowledge. | Green for bibliographic/abstract-level claims; exact pages still needed. |
| Judea Pearl, *Probabilistic Reasoning in Intelligent Systems: Networks of Plausible Inference*, Morgan Kaufmann, 1988. URL: https://www.sciencedirect.com/book/9780080514895/probabilistic-reasoning-in-intelligent-systems | Core book source for mature presentation of probabilistic reasoning, Markov/Bayesian networks, and propagation methods. | Green for source authority; page anchors needed before prose lock. |
| Steffen L. Lauritzen and David J. Spiegelhalter, "Local computations with probabilities on graphical structures and their application to expert systems," *Journal of the Royal Statistical Society: Series B* 50(2), 157-224, 1988. DOI: `10.1111/j.2517-6161.1988.tb01721.x`. | Independent statistical-graphical-model anchor; useful for showing that local computation with probabilities had a broader expert-system context. | Yellow until full text and exact passages are verified. |
| Gregory F. Cooper, "The computational complexity of probabilistic inference using Bayesian belief networks," *Artificial Intelligence* 42(2-3), 393-405, 1990. DOI: `10.1016/0004-3702(90)90060-D`. | Complexity limit: exact probabilistic inference in Bayesian belief networks can be computationally hard. | Yellow until exact theorem/passages are extracted. |

## Secondary and Context Sources

| Source | Use | Verification |
|---|---|---|
| Eugene Charniak, "Bayesian Networks without Tears," *AI Magazine* 12(4), 50-63, 1991. URL: https://www.cse.unr.edu/~bebis/CS479/Readings/BayesianNetworksWithoutTears.pdf | Accessible tutorial for explaining networks without drowning the chapter in notation. | Yellow; PDF access found, page anchors needed. |
| Richard E. Neapolitan, *Probabilistic Reasoning in Expert Systems: Theory and Algorithms*, Wiley, 1990. | Context source for expert-system framing and early algorithms. | Yellow until bibliographic/access details are verified. |
| David Heckerman, "A Tutorial on Learning with Bayesian Networks," Microsoft Research technical report, 1995/1996. | Later tutorial for separating manual knowledge engineering from learning network structure/parameters. | Yellow; later than chapter period, use only for legacy/clarity. |
| Judea Pearl, "Bayesian Networks," UCLA Cognitive Systems Laboratory technical report / encyclopedia entry, 1995. | Later definitional source if primary book page anchors are hard to access. | Yellow; use only as backup definition, not as event source. |

## Scene-Level Claim Table

| Claim | Scene | Primary Anchor | Secondary Anchor | Status | Notes |
|---|---|---|---|---|---|
| Belief/Bayesian networks represent variables/propositions as nodes in a directed acyclic graph, with arcs encoding direct dependencies and conditional probabilities quantifying them. | The Graph as a Memory Aid | Pearl 1986; Pearl 1988 | Charniak 1991 | Green | Use Pearl wording once page anchors are extracted. |
| Pearl's propagation work showed how evidence could be updated locally in singly connected networks, with computation tied to graph structure. | Propagation Instead of Global Recalculation | Pearl 1986 | Pearl 1988 | Green | Must preserve the "singly connected" qualifier unless discussing later/general methods. |
| Bayesian networks helped AI move away from brittle certainty factors toward probabilistically coherent uncertainty handling. | Rules Meet Uncertainty | Pearl 1988 | Charniak 1991; Neapolitan 1990 | Yellow | Need a source that directly contrasts certainty factors/ad hoc expert-system uncertainty. |
| Exact inference in general Bayesian networks can be computationally hard. | The Cost Returns | Cooper 1990 | Later tutorials | Yellow | Do not overgeneralize from singly connected networks to all networks. |
| Bayesian networks later became a bridge to causal reasoning, but causal calculus is not the main 1980s story. | Legacy Bridge | Pearl 1988; later Pearl sources if used | Later survey/source to find | Yellow | Keep this as forward pointer unless Chapter 26 scope expands. |

## Conflict Notes

- Do not conflate Bayesian networks with neural networks. The shared word "network" is graph structure, not weighted differentiable layers.
- Do not imply inference is always efficient. Pearl 1986's local propagation result has structural assumptions.
- Do not make causal do-calculus the center of this chapter unless the book plan explicitly moves causal reasoning into Part 5.
- Do not treat probability tables as magically easier than rules; expert elicitation and model maintenance remain infrastructure costs.

## Page Anchor Worklist

- Pearl 1986: extract definition of belief networks and the passage about links storing knowledge/directing data flow.
- Pearl 1986: extract local propagation/singly connected network claim.
- Pearl 1988: extract chapter/page anchors for Markov and Bayesian networks and network-propagation techniques.
- Lauritzen/Spiegelhalter 1988: extract expert-system application and local computation passages.
- Cooper 1990: extract complexity theorem/summary passage.
- Charniak 1991: extract a concise tutorial explanation suitable for narrative exposition.
