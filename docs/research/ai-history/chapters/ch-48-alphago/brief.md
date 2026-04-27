# Brief: Chapter 48 - AlphaGo

## Thesis
Go was considered the holy grail of AI because its search space (10^170) is vastly larger than the number of atoms in the universe, making Deep Blue's brute-force approach mathematically impossible. AlphaGo conquered it by combining deep neural networks (to evaluate board states and select moves) with reinforcement learning and Monte Carlo Tree Search.

## Scope
- IN SCOPE: DeepMind, Demis Hassabis, David Silver, Lee Sedol, the 2016 match, the architecture of AlphaGo (Policy and Value networks).
- OUT OF SCOPE: AlphaFold (later developments).

## Scenes Outline
1. **The Uncomputable Board:** Why Go cannot be solved by a VLSI chip evaluating 200 million moves a second (the branching factor is too high).
2. **The Two Brains:** DeepMind trains a "Policy Network" to suggest good moves (intuition) and a "Value Network" to evaluate who is winning (calculation).
3. **Move 37:** The legendary 2016 match against Lee Sedol. AlphaGo plays a move no human would play, proving the machine has developed a novel, superhuman intuition.
