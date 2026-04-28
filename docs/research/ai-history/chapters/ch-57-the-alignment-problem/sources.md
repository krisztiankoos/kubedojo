# Sources: Chapter 57 - The Alignment Problem

## Verification Key

- Green: claim has direct primary evidence from a paper/blog section or abstract.
- Yellow: claim is interpretive, source-limited, or requires careful caveated wording.
- Red: claim should not be drafted unless new evidence is added.

## Primary Sources

| Source | Use | Verification |
|---|---|---|
| Long Ouyang et al., "Training language models to follow instructions with human feedback," arXiv:2203.02155, 2022. URL: https://arxiv.org/pdf/2203.02155 | Core source for InstructGPT, RLHF pipeline, labeler workflow, preference comparisons, reward model, PPO, results, and limitations. | Green: Abstract says bigger language models do not inherently follow user intent and can be untruthful, toxic, or unhelpful; the method collects labeler demonstrations and rankings, trains a reward model, and fine-tunes with RLHF. Section 3 gives the three-step method, dataset sizes, about 40 contractors, K=4 to K=9 ranked outputs, and PPO. Sections 3.6/4 and Discussion give preference, truthfulness, toxicity, alignment-tax, and limitation claims. |
| Ryan Lowe and Jan Leike, "Aligning language models to follow instructions," OpenAI, January 27, 2022. URL: https://openai.com/index/instruction-following/ | Public OpenAI framing of InstructGPT deployment and method. | Green: blog says InstructGPT models were much better at following user intentions than GPT-3, were trained with humans in the loop, and became default API models. It describes GPT-3's next-word internet-text objective as misaligned with safely performing the desired task, and summarizes demonstrations, rankings, reward model, and PPO. It also lists limitations and refusal as future work. |
| Paul F. Christiano et al., "Deep reinforcement learning from human preferences," arXiv:1706.03741, 2017. URL: https://arxiv.org/pdf/1706.03741 | Prehistory of learning reward functions from human comparisons. | Green: Abstract and Introduction say the method learns from non-expert human preferences between pairs of trajectory segments, solves Atari and simulated robotics tasks without access to the reward function, uses feedback on less than 1% of interactions, and fits a reward function while training a policy to optimize predicted reward. |
| Nisan Stiennon et al., "Learning to summarize from human feedback," arXiv:2009.01325, 2020. URL: https://arxiv.org/pdf/2009.01325 | Bridge from general preference RL to language-model outputs before InstructGPT. | Green: Abstract and Method say the authors collect human comparisons between summaries, train a reward model to predict human-preferred summaries, and use it as a reward function for PPO. Main results say human-feedback summaries outperform much larger supervised summarization models on TL;DR. |

## Scene-Level Claim Table

| Claim | Scene | Primary Anchor | Independent Confirmation | Status | Notes |
|---|---|---|---|---|---|
| GPT-style language-model pretraining optimizes next-token prediction, which differs from safely and helpfully following user instructions. | Objective Mismatch | Ouyang Abstract and Introduction | OpenAI InstructGPT blog opening/method | Green | Core thesis; do not anthropomorphize. |
| Larger language models do not inherently become better at following user intent and can be untruthful, toxic, biased, or unhelpful. | Objective Mismatch | Ouyang Abstract and Introduction | OpenAI blog | Green | Say "can," not "always." |
| Christiano et al. learned reward functions from human preferences over short behavior clips and optimized policies against those learned rewards. | Preference Prehistory | Christiano Abstract, Introduction, method overview | Ouyang cites Christiano as RLHF lineage | Green | Keep robotics/Atari examples brief. |
| Stiennon et al. applied human-feedback reward modeling to summarization by collecting comparisons, training a reward model, and optimizing with PPO. | Preference Prehistory | Stiennon Abstract and Method | Ouyang Section 3.1 cites Stiennon method | Green | Useful bridge into language. |
| InstructGPT used three stages: supervised fine-tuning on demonstrations, reward-model training from comparisons/rankings, and PPO optimization against the reward model. | Reward Model And PPO | Ouyang Figure 2 and Section 3.1 | OpenAI blog Methods | Green | This is the technical spine of the chapter. |
| Ouyang et al. used prompts from an earlier InstructGPT Playground plus labeler-written prompts, filtered PII, deduplicated prompts, and split by user ID. | Labeler Pipeline | Ouyang Section 3.2 | N/A | Green | Shows data governance and product coupling. |
| The SFT dataset contained about 13k training prompts, the reward-model dataset 33k training prompts, and the PPO dataset 31k training prompts. | Labeler Pipeline | Ouyang Section 3.2 | N/A | Green | Use approximate wording. |
| OpenAI hired about 40 contractors through Upwork and ScaleAI, screened them, trained them, and used detailed instructions/shared chat for the labeling work. | Labeler Pipeline | Ouyang Section 3.4 | OpenAI blog acknowledgments note labelers | Green | Important labor scene. |
| Labelers ranked K=4 to K=9 responses per prompt, producing pairwise comparisons used to train the reward model. | Reward Model And PPO | Ouyang Section 3.5 Reward modeling | N/A | Green | Good pedagogical anchor. |
| Ouyang et al. report that 1.3B InstructGPT outputs were preferred over 175B GPT-3 outputs despite 100x fewer parameters. | Smaller, More Useful | Ouyang Abstract and results | OpenAI blog Results | Green | Avoid implying capability dominance on every task. |
| Ouyang et al. report 175B InstructGPT was preferred over 175B GPT-3 85 +/- 3% of the time and over few-shot 175B GPT-3 71 +/- 4% of the time. | Smaller, More Useful | Ouyang results summary | N/A | Green | Strong but distribution-specific result. |
| InstructGPT improved truthfulness and reduced toxic output generation in measured settings, but did not significantly improve some bias/toxicity-related metrics. | Smaller, More Useful | Ouyang results and limitations | OpenAI blog Results/Limitations | Green | Keep nuance. |
| RLHF cost was modest relative to GPT-3 pretraining: Ouyang reports 175B SFT at 4.9 petaflops/s-days and 175B PPO-ptx at 60 versus GPT-3 at 3,640. | Reward Model And PPO | Ouyang Discussion 5.1 | N/A | Green | Good infrastructure/economics detail. |
| Ouyang et al. explicitly say their procedure aligned to labelers/researchers/API-customer influences, not to all human values. | Not Full Alignment | Ouyang Section 5.2 | OpenAI blog Generalizing/Limitations | Green | Must appear in close. |
| InstructGPT remained not fully aligned or safe, could generate toxic/biased/false/sexual/violent content, and refusing harmful instructions was future work. | Not Full Alignment | Ouyang Limitations/Open Questions; OpenAI blog Limitations | N/A | Green | Prevents triumphalist ending. |
| RLHF made assistant-style products plausible by converting behavior into a trainable layer around large pretrained models. | Thesis/Close | Synthesis from Ouyang/OpenAI | Ch56 infrastructure context | Yellow | Interpretive; keep grounded in source claims. |

## Conflict Notes

- Do not claim RLHF solved alignment or made models safe.
- Do not claim InstructGPT is ChatGPT; keep ChatGPT as downstream context only if needed.
- Do not invent scary prompt examples. Source-supported categories are enough.
- Do not say "human preferences" without specifying the preference sources and representativeness limits.
- Do not imply smaller InstructGPT was better than GPT-3 on all capabilities; the key result is labeler preference on the prompt distribution.
- Do not omit the alignment-tax caveat or the fact that PPO/pretraining mix was used to reduce regressions.

## Anchor Worklist

- Ouyang 2022: Done for Abstract, Introduction, Figure 2/Section 3.1 method, Section 3.2 datasets, Section 3.4 labelers, Section 3.5 reward modeling, results summary, Discussion 5.1, Section 5.2 "Who are we aligning to?", and Limitations/Open Questions.
- OpenAI 2022 blog: Done for public product framing, default API deployment, method summary, limitations, and refusal as future work.
- Christiano 2017: Done for human comparisons over trajectory segments and learned reward functions.
- Stiennon 2020: Done for language-model summarization bridge, human comparisons, reward model, PPO, and preference results.
