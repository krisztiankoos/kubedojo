# Brief: Chapter 47 - The Depths of Vision

## Thesis
Following AlexNet, researchers assumed deeper networks would automatically yield better results, but they hit an optimization wall: deeper networks had higher training errors. ResNet solved this by introducing skip connections, allowing gradient information to bypass layers and enabling networks to scale to hundreds of layers deep.

## Scope
- IN SCOPE: Kaiming He, the 2015 ResNet paper, the degradation problem, skip connections/residual learning.
- OUT OF SCOPE: Early CNNs (Part 5), Vision Transformers (Part 8).

## Scenes Outline
1. **The Depth Wall:** Researchers find that stacking 50 layers performs worse than 20 layers, not due to overfitting, but due to optimization failure (vanishing gradients).
2. **The Identity Mapping:** Kaiming He and the Microsoft Research team propose that layers should learn the *residual* mapping rather than the original unreferenced mapping.
3. **The Skip Connection:** The physical infrastructure of a neural network is rewired to allow data to jump past layers, enabling 152-layer networks to win ILSVRC 2015.
