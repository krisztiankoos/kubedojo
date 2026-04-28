# Brief: Chapter 66 - Benchmark Wars

## Thesis

Benchmarks were once mostly scientific instruments; in the frontier-model era they became product claims, market signals, policy evidence, and competitive weapons. This chapter should connect the older common-task tradition to the modern leaderboard economy, then show how MMLU, HELM, Chatbot Arena, contamination disputes, and benchmark gaming turned evaluation into a political economy.

## Boundary Contract

- IN SCOPE: common-task evaluation lineage; MMLU as a generality scorecard;
  BIG-bench and HELM as broad/holistic evaluation attempts; GPT-4's exam and
  benchmark tables as product-release evidence; OpenAI Evals as deployment-time
  evaluation infrastructure; MT-Bench and Chatbot Arena as human-preference /
  LLM-as-judge public comparison; contamination and benchmark-specific
  optimization; SWE-bench as harder real-world benchmark design; Goodhart effects
  when metrics become targets.
- OUT OF SCOPE: detailed leaderboard chronology; timeless model rankings;
  benchmark-by-benchmark score tables; data/copyright fights (Ch68); open-weight
  licensing (Ch65); product launch narrative (Ch59); agentic tool use (Ch60);
  software-agent capability history beyond SWE-bench as an evaluation example.
- Transition from Ch65: open weights created many comparable models; Ch66
  explains how reputation moved to benchmarks, leaderboards, and evaluation
  rituals.
- Transition to Ch67/68: once evaluation becomes a market signal, platforms,
  data provenance, and copyright pressure become harder to separate from
  "capability."

## Required Scenes
1. **From Common Task To Scoreboard:** Connect DARPA/ImageNet-style shared evaluation to modern foundation-model leaderboards.
2. **The Frontier Scorecard:** MMLU, BIG-bench, HELM, and GPT-4's release tables make "general capability" look legible while also showing how much benchmark design shapes the story.
3. **Arena As Courtroom:** MT-Bench and Chatbot Arena turn pairwise preference into public model reputation, while LLM-as-judge turns evaluation into scalable but biased infrastructure.
4. **Contamination And Goodhart:** The more scores matter, the more leakage checks, benchmark-specific optimization, prompt choices, and metric gaming become part of the system.
5. **Harder Tests, Moving Targets:** SWE-bench shows the next stage: benchmarks that try to follow real work rather than short-answer test items, while still becoming targets.
6. **Evaluation As Power:** Close on scores influencing users, investors, regulators, procurement, and open-vs-closed narratives.

## Prose Capacity Plan

Target range: 4,300-5,400 words.

- 550-750 words: bridge from historical evaluation culture to modern scoreboards.
- 900-1,100 words: MMLU, BIG-bench, HELM, and GPT-4 release tables as generality scorecards.
- 800-1,000 words: MT-Bench, Chatbot Arena, LLM-as-judge, and public preference rankings.
- 750-950 words: contamination checks, benchmark-specific optimization, and Goodhart effects.
- 650-850 words: SWE-bench and the move toward harder real-world evaluations.
- 650-750 words: close on evaluation as institutional power and handoff to Ch67/68.

## Guardrails

- Do not rank models unless the claim is source-bound and dated.
- Do not treat leaderboard movement as timeless fact.
- Do not present benchmark scores as direct measures of intelligence.
- Do not make contamination accusations without primary or highly reliable evidence.
- Do not make GPT-4 / Chatbot Arena / Mistral-style performance claims without
  naming the source and date.
- Keep "evaluation as power" institutional; do not invent private investor,
  regulator, or lab reactions.
