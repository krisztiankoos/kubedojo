# Brief: Chapter 53 - The Dawn of Few-Shot Learning

## Thesis
OpenAI's GPT-2 and GPT-3 proved that if a language model is scaled up massively, it develops emergent abilities. It no longer needs to be explicitly fine-tuned for a specific task; it can learn to perform new tasks simply by reading a few examples in the prompt, shifting AI from specific narrow models to general foundation models.

## Scope
- IN SCOPE: OpenAI, Alec Radford, Ilya Sutskever, GPT-2, GPT-3, unsupervised multi-task learning, few-shot/zero-shot prompting.
- OUT OF SCOPE: ChatGPT/RLHF (Chapter 57/59).

## Scenes Outline
1. **The Unsupervised Bet:** OpenAI hypothesizes that predicting the next word on a massive enough corpus will force the model to learn reasoning.
2. **GPT-2 and the Release Controversy:** The model is so good at generating coherent (and fake) text that OpenAI initially refuses to release the full weights, citing safety concerns.
3. **GPT-3 and Few-Shot Prompting:** The realization that a 175-billion parameter model doesn't need fine-tuning. You just prompt it with examples, and it adapts instantly.
