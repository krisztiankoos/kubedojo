# Brief: Chapter 46 - The Recurrent Bottleneck

## Thesis
While CNNs conquered computer vision, sequence data (text and audio) was dominated by Long Short-Term Memory (LSTM) networks. However, the fundamental mathematics of recurrent networks required processing data sequentially, creating a hard physical bottleneck that GPUs could not accelerate through massive parallelism.

## Scope
- IN SCOPE: Sepp Hochreiter, Jürgen Schmidhuber, the 1997 LSTM paper, the vanishing gradient problem in RNNs, the sequential processing constraint.
- OUT OF SCOPE: Transformers (Part 8).

## Scenes Outline
1. **The Vanishing Gradient:** Why standard RNNs forget early information in a sequence.
2. **The Constant Error Carousel:** Hochreiter and Schmidhuber invent the LSTM to preserve error gradients across long time steps.
3. **The O(N) Ceiling:** Despite their mathematical brilliance, LSTMs must read a sentence one word at a time, severely limiting GPU utilization and training scale.
