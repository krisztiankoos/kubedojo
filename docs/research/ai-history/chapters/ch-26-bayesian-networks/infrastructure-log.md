# Infrastructure Log: Chapter 26
# Infrastructure Log: Chapter 26 - Bayesian Networks

## Knowledge Representation

- Bayesian networks are knowledge infrastructure: the graph records conditional-dependence assumptions, and probability tables record uncertainty.
- The graph makes maintenance partly visible. If a dependency changes, the model has a place to update; this is different from scattered certainty factors in rule chains.
- This does not remove expert elicitation. Conditional probability tables can become large and hard to fill.

## Computation

- Pearl 1986 emphasizes local propagation in singly connected networks. That is computationally attractive because evidence can move through the graph rather than requiring a monolithic recalculation.
- General networks reintroduce computational difficulty. Cooper 1990 belongs in the chapter as the limit-setting source.
- The chapter should avoid a fake binary between "rules are brittle" and "Bayesian networks solve uncertainty." The honest claim is that Bayesian networks structure the problem.

## Data

- Early Bayesian networks were often knowledge-engineered rather than learned from massive datasets.
- Later work on learning Bayesian networks can be a forward pointer, but the main 1980s infrastructure story is representation plus inference, not big-data training.

## Interfaces and Operations

- The graph is explainable compared with opaque numeric tables alone: domain experts can inspect nodes and arrows.
- Operational cost remains: choosing variables, deciding dependencies, filling probabilities, and revising the graph as the domain changes.

## Claims Not Yet Safe

- "Bayesian networks replaced expert systems" is too broad without deployment evidence.
- "Bayesian networks made AI Bayesian" is rhetorically tempting but historically sloppy.
- "Pearl invented all graphical models" is false/misleading; keep Lauritzen/Spiegelhalter and broader statistical context in view.
