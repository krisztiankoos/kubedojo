# Scene Sketches: Chapter 26
# Scene Sketches: Chapter 26 - Bayesian Networks

## Scene 1: Rules Meet Uncertainty

Open from the maintenance problem of rule-based systems: expert rules often sounded crisp, but real evidence arrived incomplete, noisy, and sometimes contradictory. The scene should not mock expert systems. It should show why uncertainty demanded a first-class representation.

Evidence needed:
- Ch19-Ch23 source anchor on certainty factors or expert-system uncertainty.
- Pearl/Charniak passage contrasting probabilistic reasoning with earlier approaches.

## Scene 2: The Graph as a Memory Aid

Introduce a small medical or diagnostic-style network only as an explanatory device: symptoms, disease, test result. The point is not the example itself, but how the graph encodes direct dependence and conditional independence assumptions.

Evidence needed:
- Pearl 1988 or Charniak 1991 definition.
- Avoid invented historical deployment unless sourced.

## Scene 3: Propagation Instead of Global Recalculation

Show how evidence at one node changes beliefs elsewhere through local message passing in appropriate network structures. This is the infrastructure moment: the graph is not only a diagram but a route for computation.

Evidence needed:
- Pearl 1986 local propagation passage.
- Keep "singly connected" visible.

## Scene 4: The Cost Returns

End with the caveat: once networks become dense or multiply connected, exact inference can become expensive. Bayesian networks survive because they organize uncertainty, not because they make uncertainty free.

Evidence needed:
- Cooper 1990 complexity result.
- Optional later tutorial for approximation/learning afterlife.
