# Brief: Chapter 37 - Distributing the Compute

## Thesis
To process the internet-scale datasets required for modern AI, computation had to be distributed across thousands of machines. Google's MapReduce algorithm, and its open-source clone Hadoop, provided the critical software infrastructure to orchestrate this massive parallelism.

## Scope
- IN SCOPE: Jeffrey Dean, Sanjay Ghemawat, MapReduce, Doug Cutting, Hadoop, the orchestration of commodity clusters.
- OUT OF SCOPE: Kubernetes (belongs to Part 9).

## Scenes Outline
1. **The Coordination Nightmare:** Writing code to run on 1,000 failure-prone PCs is a synchronization nightmare.
2. **Map and Reduce:** Dean and Ghemawat invent an elegant software abstraction that automatically splits tasks (Map) and recombines results (Reduce), hiding the hardware failures from the programmer.
3. **The Yellow Elephant:** Doug Cutting clones the Google paper into Hadoop, democratizing planetary-scale compute infrastructure for the entire industry.
