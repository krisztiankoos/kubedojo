# Brief: Chapter 69 - The Data Exhaustion Limit

## Thesis

The post-ChatGPT scaling race did not only run into GPUs, energy, and product
distribution. It also ran into a less photogenic resource: high-quality human
data. Chinchilla made data quantity part of the compute-optimal scaling law;
Llama 3 and FineWeb made trillion-token data budgets ordinary public facts;
Epoch AI then put a date range on the constraint, estimating that continued
scaling would fully use the stock of public human text between 2026 and 2032.
The industry response was not one tactic but a portfolio: filter better, repeat
data carefully, add code or other domains, synthesize textbooks and
instructions, protect evaluations against contamination, and hope synthetic
data would not poison future corpora. The chapter should make the limit feel
technical rather than apocalyptic: data does not "run out" like oil, but the
easy frontier of fresh, public, high-signal human text stops scaling smoothly.

## Scope

- IN SCOPE: Chinchilla's data-scaling result; public trillion-token examples
  such as Llama 3 and FineWeb; Epoch's public-human-text stock estimate and
  2026-2032 utilization forecast; data repetition and multi-epoch training;
  filtering/deduplication tradeoffs; code and domain-transfer as data
  substitutes; synthetic instruction data and synthetic textbook data; model
  collapse as a recursive synthetic-data risk; benchmark/test-set contamination
  as another symptom of exhausted public evaluation data; live/dynamic
  benchmarks as a response.
- OUT OF SCOPE: copyright/labor/legal enclosure, which Ch68 owns; datacenter
  power and grid limits, which Ch70 and Ch72 own; chip export controls, which
  Ch71 owns; comprehensive benchmark politics, which Ch66 owns; claiming that
  synthetic data is useless or sufficient; private proprietary corpus
  speculation not anchored in papers or model cards.

## Required Scenes

1. **The Scaling Law Turns Toward Data:** Open with the conceptual shift from
   bigger models to compute-optimal smaller models trained on more tokens.
   Chinchilla's 70B/1.4T-token comparison with Gopher is the bridge from Part 8
   scaling to Part 9 scarcity.
2. **The Trillion-Token Horizon:** Use Llama 3's model card and FineWeb to show
   that 15T-token language datasets were no longer abstract. The point is not
   that all models disclose data, but that the public frontier now talked in
   token stocks large enough to make the web feel finite.
3. **Epoch's Data-Stock Clock:** Present the 2026-2032 forecast carefully as a
   model, not prophecy. Include the 300T/400T effective-stock language and the
   key caveat that overtraining accelerates consumption.
4. **Squeezing The Dataset:** Explain multi-epoch repetition, filtering,
   deduplication, and code augmentation through the data-constrained scaling
   paper. The scene should show engineers turning one finite corpus into more
   effective training signal.
5. **The Synthetic Escape Hatch:** Self-Instruct and phi-1 show productive uses
   of model-generated instructions and textbook-like code data. This is the
   optimistic half of the chapter: models begin manufacturing training
   problems for other models.
6. **The Recursion Warning:** Model-collapse work supplies the caution. The
   prose must not say all synthetic data causes collapse; the supported claim is
   narrower: indiscriminate recursive training on model output can erase tails
   and make genuine human data more valuable.
7. **Evaluation Starts Spoiling Too:** GPT-4's contamination checks and
   LiveBench's monthly/recent-question design show that the exhaustion problem
   extends to test sets. Public benchmarks become part of the data soup unless
   they stay fresh, private, or carefully filtered.

## Prose Capacity Plan

Target range: 4,500-5,500 words after source verification.

- 500-650 words: bridge from Ch68's enclosed data market to the technical
  scarcity question: rights and labor make data costly; scaling laws make it
  necessary.
- 700-900 words: Chinchilla and the data turn. Explain why "more data" became
  a scaling requirement, not a dataset-engineering footnote.
- 750-900 words: public trillion-token horizon. Llama 3, FineWeb, Common Crawl,
  and dataset curation as industrial infrastructure.
- 700-850 words: Epoch's stock forecast and caveats. Keep the dates and token
  estimates precise, but avoid deterministic exhaustion rhetoric.
- 750-900 words: squeezing finite corpora through repetition, filtering,
  deduplication, and code/domain transfer.
- 700-850 words: synthetic data as escape hatch and trap: Self-Instruct,
  phi-1, GPT-4 synthetic comparison data, and model collapse.
- 400-550 words: benchmark contamination and handoff to Ch70: when data can no
  longer be assumed fresh, evaluation and training become infrastructure
  problems, not just research methodology.

## Guardrails

- Do not say humanity "ran out of data." Say the public, high-quality,
  human-generated text stock became a scaling constraint under specific trend
  assumptions.
- Do not conflate dataset size, tokens seen during training, and unique tokens.
- Do not imply all LLM developers used FineWeb, Llama 3 data, or any named
  corpus unless the cited model card or paper says so.
- Do not treat Epoch's 2026-2032 range as a settled prediction. It is a model
  based on continuation of then-current scaling trends.
- Do not claim synthetic data is either a universal solution or a universal
  poison. Separate curated synthetic data from indiscriminate recursive
  self-training.
- Do not reuse Ch68's copyright/labor claims except as one-paragraph context.
- Do not let benchmark contamination become a repeat of Ch66's benchmark-politics
  chapter. Here it serves the data-scarcity argument: public tests become
  trainable data unless evaluation moves faster than training corpora.
