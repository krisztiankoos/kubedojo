# Infrastructure Log: Chapter 57 - The Alignment Problem

## Behavioral Training Infrastructure

- **Base model:** GPT-3 pretrained language models, adaptable to tasks but poorly characterized for deployed assistant behavior.
- **Objective mismatch:** next-token prediction on internet text versus following instructions helpfully and safely.
- **Supervised fine-tuning (SFT):** labeler-written demonstrations of desired behavior on prompts from API/labeler distributions.
- **Reward model (RM):** model trained to take a prompt and response and output a scalar reward predicting labeler preference.
- **Policy optimization:** PPO fine-tunes the supervised policy against the reward model.
- **Pretraining mix:** PPO-ptx mixes PPO updates with pretraining-gradient updates to reduce regressions on public NLP datasets.

## Human Data Infrastructure

- **Prompt sources:** earlier InstructGPT Playground prompts plus labeler-written prompts; production API data excluded according to Ouyang Section 3.2.
- **Data handling:** PII filtered, prompts deduplicated, user IDs limited, train/validation/test split by user ID.
- **Dataset sizes:** about 13k SFT training prompts, 33k reward-model training prompts, and 31k PPO training prompts.
- **Labeler team:** about 40 contractors hired through Upwork and ScaleAI, screened for performance on sensitive prompts, onboarded with instructions and shared chat support.
- **Ranking interface:** labelers ranked K=4 to K=9 outputs for a prompt, producing pairwise comparisons for reward-model training.

## Results / Metrics Infrastructure

- **Preference results:** 1.3B InstructGPT preferred over 175B GPT-3 on the prompt distribution; 175B InstructGPT preferred over 175B GPT-3 85 +/- 3% of the time and over few-shot 175B GPT-3 71 +/- 4% of the time.
- **Truthfulness:** InstructGPT generated truthful and informative answers on TruthfulQA about twice as often as GPT-3, according to Ouyang's summary.
- **Hallucination:** On closed-domain API tasks, InstructGPT made up information not present in the input about half as often as GPT-3 in the reported summary.
- **Toxicity:** InstructGPT generated about 25% fewer toxic outputs than GPT-3 when prompted to be respectful, but did not significantly improve over GPT-3 on some bias datasets.
- **Alignment cost:** Ouyang reports 175B SFT at 4.9 petaflops/s-days and 175B PPO-ptx at 60 petaflops/s-days, compared with GPT-3 pretraining at 3,640 petaflops/s-days.

## Limits / Constraints

- **Preference source:** labelers, researchers, and API-customer prompt distribution, not a representative sample of humanity.
- **Language/culture limit:** data mostly English; labelers mostly English-speaking and located in the United States or Southeast Asia, per Ouyang's caveat.
- **Safety limit:** models still generated toxic, biased, false, sexual, or violent content in some cases.
- **Refusal limit:** Ouyang says training models to be harmless despite harmful user instructions remained important future work.
- **Misuse limit:** better instruction following can also make misuse easier.
