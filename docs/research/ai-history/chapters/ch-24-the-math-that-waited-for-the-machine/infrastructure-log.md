# Infrastructure Log: Chapter 24 - The Math That Waited for the Machine

## Technical Constraint

Multi-layer neural networks had many adjustable weights, but hidden units had no direct target label. The infrastructure problem was therefore not just "more math"; it was a scalable bookkeeping procedure for assigning credit and blame through layers.

## Algorithmic Infrastructure

- **Forward pass:** Store each unit's activation so later derivative calculations can reuse it.
- **Backward pass:** Move error sensitivities from output units back through hidden units using the chain rule.
- **Weight update:** Adjust each connection in proportion to its contribution to output error.
- **Hidden representation:** The useful feature is not hand-coded. It emerges as the network adjusts internal weights.

## Compute and Hardware Constraints

- 1986 demonstrations ran on small networks by modern standards. The chapter should not imply ImageNet-era scale.
- Backpropagation converted learning into repeated numerical operations over weights and activations. That shape later mapped naturally to vector processors, CPUs, GPUs, and accelerators, but the 1986 systems were still constrained by memory, processor speed, and experiment turnaround.
- The bottleneck shifted: once hidden-layer training became executable, the limiting factors became data volume, initialization, local minima/plateaus, conditioning, and available compute.

## Metrics to Verify Before Prose

- Exact network sizes and tasks in the Nature paper and PDP chapter.
- Hardware or computing environment used for the reported experiments.
- Runtime or training-iteration counts, if reported.
- Whether any 1985 technical report contains details omitted from the Nature letter.
