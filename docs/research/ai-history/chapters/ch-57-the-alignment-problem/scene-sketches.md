# Scene Sketches: Chapter 57 - The Alignment Problem

## Scene 1: The Objective Mismatch
- **Action:** Explain the clean technical mismatch: GPT-3 was trained to predict the next token in internet text, while users wanted a system that followed instructions helpfully and safely.
- **Texture:** The model is not evil or magical. It is optimizing the wrong training objective for the assistant role.
- **Guardrail:** Do not invent a harmful prompt example. Use the paper's categories: untruthful, toxic, biased, harmful, or not following instructions.

## Scene 2: Learning From Preferences
- **Action:** Step back to Christiano 2017 and Stiennon 2020. Humans compare short behavior clips or pairs of summaries; a reward model learns which output humans prefer; RL optimizes against that learned reward.
- **Texture:** This is the conceptual invention: when a goal is hard to write as code, ask humans for comparisons and train a model to approximate the preference signal.
- **Guardrail:** Keep the prehistory short enough that it supports InstructGPT rather than becoming a robotics/summarization chapter.

## Scene 3: The Labeler Pipeline
- **Action:** Ouyang et al. build a production-like pipeline: prompts from the API Playground and labeler-written prompts, demonstrations, 33k reward-model prompts, 31k PPO prompts, about 40 contractors, screening, instructions, onboarding, and chat support.
- **Texture:** The assistant is partly made of human labor. The "alignment layer" is a data-production system as much as an algorithm.
- **Guardrail:** Do not romanticize or vilify the labelers. Stick to the published workflow and limits.

## Scene 4: Reward Model And PPO
- **Action:** Labelers rank four to nine responses for a prompt. Those rankings become pairwise comparisons. A reward model predicts preferred outputs; PPO fine-tunes the policy to get higher reward.
- **Texture:** Make the math readable: the reward model is a learned judge, not a moral oracle.
- **Guardrail:** Do not imply the reward model knows truth or safety directly. It predicts labeler preference under instructions.

## Scene 5: A Smaller Model Wins The Preference Test
- **Action:** Show the headline result: 1.3B InstructGPT preferred over 175B GPT-3, and 175B InstructGPT strongly preferred over 175B GPT-3 and few-shot GPT-3 on the tested prompt distribution.
- **Texture:** The story is not that size stopped mattering. It is that behavior tuning could unlock usefulness that raw scale alone did not deliver.
- **Guardrail:** Do not claim global superiority across all tasks.

## Scene 6: The Unfinished Problem
- **Action:** Close with the caveats: alignment to a particular labeler/researcher/customer pipeline, not all people; residual toxic/biased/false outputs; refusal of harmful instructions as future work; misuse risk.
- **Texture:** This ending sets up the product era honestly: RLHF made assistants viable, but it also created the next layer of governance and safety questions.
- **Guardrail:** No triumphalist "alignment solved" ending.
