# Brief: Chapter 57 - The Alignment Problem

## Thesis
Raw language models trained on internet text are powerful but alien and unsafe; they simply predict the next word, often generating toxic or unhelpful text. Reinforcement Learning from Human Feedback (RLHF) was the critical behavioral infrastructure that aligned these models with human intent, making products like ChatGPT possible.

## Scope
- IN SCOPE: InstructGPT, RLHF, the alignment problem, human labelers ranking outputs, the transition from raw prediction to helpful assistants.
- OUT OF SCOPE: Regulatory legislation (Part 9).

## Scenes Outline
1. **The Alien Shoggoth:** Raw GPT-3 is prompted with a question and, instead of answering, it just generates more questions. It is mimicking internet forums, not acting as an assistant.
2. **The Human Raters:** OpenAI hires contractors to read different model outputs and rank them from best to worst, building a dataset of human preference.
3. **The Reward Model:** Pedagogical explanation of RLHF. A secondary neural network learns to predict human preference, and then trains the primary model to behave safely and helpfully.
