# Sources: Chapter 69 - The Data Exhaustion Limit

## Verification Key

- Green: direct support from a paper, model card, or official technical report.
- Green/Yellow: usable with source-type caveats or as a synthesis across
  anchored sources.
- Yellow: context, boundary, or source-discovery support only.
- Red: not supported; do not draft.

## Primary / Near-Primary Source Spine

| Source | Use In Chapter | Anchor Notes |
|---|---|---|
| Hoffmann et al., "Training Compute-Optimal Large Language Models," arXiv:2203.15556. PDF: https://arxiv.org/pdf/2203.15556 | Chinchilla data-scaling turn. | Green: local extraction lines 20-28 say model size and training tokens should scale equally, Chinchilla used same compute as Gopher with 70B parameters and 4x more data, and outperformed larger models; lines 98-124 give the 70B/1.4T-token comparison and table; lines 136-138 state high-quality datasets are key to further scaling; lines 962-970 call for larger high-quality datasets and train-test overlap care. |
| Meta, "Llama 3 Model Card," GitHub raw. https://raw.githubusercontent.com/meta-llama/llama3/main/MODEL_CARD.md | Public frontier example of 15T+ pretraining. | Green: lines 35-45 list training data as a new mix of public online data and 15T+ token count; lines 137-141 say Llama 3 was pretrained on over 15T tokens from publicly available sources, with over 10M human-annotated fine-tuning examples and no Meta user data. |
| Penedo et al., "The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale," arXiv:2406.17557 / NeurIPS 2024. PDF: https://arxiv.org/pdf/2406.17557 | Public dataset-cultivation scene; quality/filtering/deduplication infrastructure. | Green: lines 16-30 introduce FineWeb as 15T tokens from 96 Common Crawl snapshots and FineWeb-Edu as 1.3T educational tokens; lines 33-64 explain dataset size, filtering, deduplication, and public knowledge gap; lines 77-97 explain Common Crawl, web text, filtering, and deduplication tradeoffs; lines 139-164 describe ablation models and 80,000 H100 GPU-hour curation experiments. |
| Villalobos et al., "Will we run out of data? Limits of LLM scaling based on human-generated data," arXiv:2211.04325v2 / Epoch AI, June 2024. PDF: https://arxiv.org/pdf/2211.04325 and page https://epoch.ai/blog/will-we-run-out-of-data-limits-of-llm-scaling-based-on-human-generated-data | Main data-stock forecast. | Green: PDF lines 14-46 say public human text could be fully utilized between 2026 and 2032 and name synthetic data, transfer learning, and data efficiency as responses; lines 48-65 estimate around 4e14 indexed-web tokens and state larger datasets are crucial; lines 120-132 distinguish stock estimates from tokens seen during multi-epoch training; lines 136-164 define data-stock/dataset-size and Common Crawl's bounded relation to the indexed web; lines 1425-1441 explain Chinchilla-optimal ratio, overtraining, and Llama 3 as an overtrained example. Epoch page lines 157-160 state an effective stock around 300T quality/repetition-adjusted tokens and utilization between 2026 and 2032. |
| Muennighoff et al., "Scaling Data-Constrained Language Models," arXiv:2305.16264 / NeurIPS 2023, v5 2025. PDF: https://arxiv.org/pdf/2305.16264 | Repetition, filtering, and code augmentation under data constraints. | Green: lines 15-29 state data may soon be limited by internet text, up to 4 repeated epochs have negligible loss changes, and more repetition decays; lines 63-80 explain Chinchilla's implication and ask what to do when data runs out; lines 363-398 show repeated data worsens if excessive and motivate more epochs rather than more parameters; lines 507-549 compare code augmentation, filtering, deduplication, and repetition; lines 592-600 summarize multi-epoch scaling with diminishing returns and code as additional scale. |
| Wang et al., "Self-Instruct: Aligning Language Models with Self-Generated Instructions," arXiv:2212.10560 / ACL 2023. PDF: https://arxiv.org/pdf/2212.10560 | Synthetic instruction-data escape hatch. | Green: lines 35-65 describe bootstrapping instruction/input/output samples from a language model, filtering invalid or similar ones, 33% absolute improvement on Super-NaturalInstructions, and an almost annotation-free method; lines 160-219 detail the generation/filtering pipeline and seed-to-generated task flow. |
| Gunasekar et al., "Textbooks Are All You Need," arXiv:2306.11644. PDF: https://arxiv.org/pdf/2306.11644 | Synthetic textbook-quality data and data quality scene. | Green: lines 14-22 introduce phi-1 as 1.3B parameters trained on 6B web textbook-quality tokens plus 1B GPT-3.5-generated textbook/exercise tokens; lines 33-44 argue data quality can alter scaling and reduce dataset/training compute; lines 50-77 compare phi-1's 7B-token dataset and HumanEval/MBPP results to larger code models; lines 184-194 describe GPT-4-assisted data-quality annotation and GPT-3.5 synthetic content generation. |
| Shumailov et al., "The Curse of Recursion: Training on Generated Data Makes Models Forget," arXiv:2305.17493 / Nature 2024. PDF: https://arxiv.org/pdf/2305.17493 | Model-collapse warning. | Green: lines 60-74 define model collapse as forgetting the true distribution when learning from model-produced data and argue human-produced data remains crucial; lines 92-97 state the paper's contributions and need for genuine human-generated content; lines 164-173 define model collapse as generated data polluting future training sets and losing tail information. |
| OpenAI, "GPT-4 Technical Report," arXiv:2303.08774. PDF: https://arxiv.org/pdf/2303.08774 | Evaluation contamination and synthetic-data use inside an industrial report. | Green: lines 391-404 say OpenAI ran contamination checks, excluded BIG-bench portions mixed into training, and treated GSM-8K specially; lines 1737-1771 describe substring-based cross-contamination checks, limitations, and interpretation of GSM-8K as between transfer and benchmark-specific tuning; lines 1948-1954 describe Table 11 contamination reporting; lines 3550-3560 say GPT-4 was used to generate synthetic comparison data for closed-domain hallucination mitigation. |
| White et al., "LiveBench: A Challenging, Contamination-Limited LLM Benchmark," arXiv:2406.19314 / ICLR 2025. PDF: https://arxiv.org/pdf/2406.19314 | Dynamic benchmark response to public-test contamination. | Green: lines 22-42 state test-set contamination is well documented, LiveBench uses frequently updated recent questions, objective scoring, and monthly updates; lines 47-58 explain why public internet benchmarks become unreliable when benchmark questions enter training data; lines 123-130 state LiveBench's three desiderata and no model above 70% at publication. |
| Wikipedia pages on model collapse, Llama 3, Chinchilla, synthetic data, and data contamination. | Source discovery only. | Yellow: use only to discover paper names, chronology, and terminology. Do not cite as evidence in prose. |

## Scene-Level Claim Table

| Claim | Scene | Primary Anchor | Confirmation | Status | Notes |
|---|---|---|---|---|---|
| Chinchilla shifted scaling logic by showing compute-optimal training required scaling model size and training tokens together. | Scaling Law | Hoffmann lines 20-28 | Hoffmann lines 98-124 | Green | Avoid over-explaining formulas; focus on historical effect. |
| Chinchilla used the same compute budget as Gopher but 70B parameters and 1.4T tokens, outperforming larger models. | Scaling Law | Hoffmann lines 98-124 | Hoffmann lines 936-948 | Green | Useful opening scene. |
| The Chinchilla authors explicitly linked further scaling to high-quality larger datasets and train-test overlap concerns. | Scaling Law | Hoffmann lines 962-970 | FineWeb lines 33-64 | Green | Bridge to data quality. |
| Llama 3's model card says it used over 15T public-source pretraining tokens and over 10M human-annotated fine-tuning examples. | Trillion Horizon | Llama 3 lines 137-141 | Llama 3 lines 35-45 | Green | Do not infer exact source composition. |
| FineWeb is a 15T-token dataset from 96 Common Crawl snapshots, with a 1.3T-token educational subset. | Trillion Horizon | FineWeb lines 16-30 | FineWeb lines 46-64 | Green | Open public dataset scene. |
| FineWeb frames dataset curation as filtering, deduplication, extraction, ablation, and benchmark measurement, not just scraping more pages. | Trillion Horizon | FineWeb lines 33-64, 77-97, 139-164 | Muennighoff lines 507-549 | Green | Good "data refinery" metaphor if kept factual. |
| Villalobos et al. forecast that public human text could be fully utilized between 2026 and 2032 if trends continued. | Epoch Clock | Villalobos lines 14-46 | Epoch page lines 157-160 | Green | Must say "if trends continue." |
| Epoch/Villalobos estimate the effective text stock around 300T quality/repetition-adjusted tokens on the blog page and around 4e14 indexed-web tokens in the paper figure. | Epoch Clock | Epoch page lines 157-160; Villalobos lines 41-49 | Villalobos lines 120-132 | Green/Yellow | Explain the different estimate phrasings without pretending they are identical. |
| Villalobos distinguishes dataset size from tokens seen during training, which may be larger under multi-epoch training. | Epoch Clock | Villalobos lines 120-132 | Muennighoff lines 15-29 | Green | Important guardrail. |
| Villalobos names synthetic data, transfer learning, non-public data, and data efficiency as ways to continue progress. | Epoch Clock | Villalobos lines 39-46, 59-65 | Muennighoff lines 507-549 | Green | Keep as options, not guarantees. |
| Data-constrained scaling finds up to four epochs of repeated data can have negligible loss change, but more repetition has diminishing/decaying value. | Squeezing Dataset | Muennighoff lines 15-29 | Muennighoff lines 529-549 | Green | Avoid saying repetition is free indefinitely. |
| In data-constrained settings, smaller models trained for more epochs can be preferable to adding parameters under a naive Chinchilla extrapolation. | Squeezing Dataset | Muennighoff lines 363-398 | Muennighoff lines 592-600 | Green | Good technical middle. |
| Code augmentation and filtering choices can extend useful training signal, but carry task/domain limits. | Squeezing Dataset | Muennighoff lines 507-549 | FineWeb lines 77-97 | Green | Do not generalize code to all domains. |
| Self-Instruct showed a pipeline for generating and filtering synthetic instruction data with large instruction-following gains. | Synthetic Escape | Wang lines 35-65 | Wang lines 160-219 | Green | Avoid implying today's systems use same pipeline. |
| Phi-1 showed a 1.3B code model trained on 6B web textbook-quality tokens and 1B GPT-3.5 synthetic tokens could be competitive on coding benchmarks. | Synthetic Escape | Gunasekar lines 14-22 | Gunasekar lines 50-77 | Green | Keep code-domain boundary. |
| The phi-1 paper argues high-quality data can alter the apparent shape of scaling and reduce compute/dataset needs. | Synthetic Escape | Gunasekar lines 33-44 | FineWeb-Edu lines 57-64 | Green | Do not overclaim beyond code/education-style data. |
| Model-collapse work warns that indiscriminately learning from model-produced data can make models forget tails of the true distribution. | Recursion Warning | Shumailov lines 60-74 | Shumailov lines 164-173 | Green | "Indiscriminately" and "recursive" are essential. |
| Shumailov et al. explicitly argue access to genuine human-generated content is essential to avoid collapse. | Recursion Warning | Shumailov lines 92-97 | Shumailov lines 68-74 | Green | Good closing tension. |
| GPT-4's technical report treated benchmark contamination as a live measurement problem and excluded mixed-in BIG-bench material. | Evaluation Spoils | GPT-4 lines 391-404 | GPT-4 lines 1737-1771 | Green | Do not use this to attack GPT-4; use as evidence of serious handling. |
| LiveBench was designed around recent, monthly updated, objectively scored questions to limit contamination. | Evaluation Spoils | LiveBench lines 22-42 | LiveBench lines 123-130 | Green | Connect to "fresh tests become scarce too." |

## Conflict Notes

- Epoch's paper and blog use related but not identical stock phrasings. Preserve
  the wording: "around 300 trillion quality/repetition-adjusted tokens" for the
  blog page and "around 4e14 indexed-web tokens" for the paper figure.
- "Data exhaustion" is shorthand. The safe claim is that public, high-quality,
  human-generated text stops scaling along the old trend.
- FineWeb and Llama 3 are examples of public token-scale discourse, not proof of
  what closed labs used.
- Model collapse is not a general anti-synthetic-data proof. It is a warning
  against recursive or indiscriminate use of generated data without enough real
  distributional grounding.
- Benchmark contamination belongs here only as a data-freshness problem; Ch66
  owns the broader political economy of leaderboard use.
