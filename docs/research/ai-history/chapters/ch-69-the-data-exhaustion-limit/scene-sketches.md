# Scene Sketches: Chapter 69 - The Data Exhaustion Limit

## Scene 1 - The Law Changes What Counts As Fuel

Start with Chinchilla as a methodological surprise rather than a mascot. The
field had been trained to look at parameter count; Hoffmann et al. showed that a
smaller 70B model trained on much more data could beat larger models at the same
compute budget. The prose should make the reader feel the pivot: data becomes a
planning variable like GPUs.

## Scene 2 - Fifteen Trillion Becomes A Public Number

Move from the paper result to public infrastructure. Llama 3's model card says
15T+ pretraining tokens from public sources. FineWeb says 15T tokens from 96
Common Crawl snapshots and then describes extraction, filters, deduplication,
ablation models, and 80,000 H100 GPU-hours of curation work. The scene is a data
refinery, not a warehouse.

## Scene 3 - The Stock Estimate

Epoch/Villalobos gives the chapter its clock: if trends continue, models reach
the effective stock of public human text between 2026 and 2032. Treat the date
range as a model result. Show the definitions: data stock, dataset size, tokens
seen during training, repeated epochs. The tension is that the web looks huge
until scaling laws convert it into a finite input budget.

## Scene 4 - Squeezing More Signal Out Of The Same Corpus

The data-constrained scaling paper should feel like a shop-floor response:
repeat data for a few epochs, avoid too much repetition, allocate compute toward
more epochs rather than more parameters in constrained regimes, add code where it
helps, and change filters carefully. This is the engineering middle of the
chapter.

## Scene 5 - Machines Write Lessons For Machines

Synthetic data enters as a practical workaround. Self-Instruct bootstraps
instructions from model generations and filters them. Phi-1 uses a small amount
of high-quality synthetic textbook/exercise data to compete surprisingly well in
code. The prose can be optimistic here, but the optimism must be specific:
curated synthetic data can target gaps; it does not create unlimited fresh human
experience.

## Scene 6 - The Mirror Gets Noisy

Model collapse supplies the warning image. If generated data feeds future
models indiscriminately, tails disappear and the model starts learning a
flattened version of reality. Use the "tails" concept, not melodrama. Human data
becomes valuable because it anchors the distribution.

## Scene 7 - The Tests Spoil Too

Close with evaluation. GPT-4's report discusses contamination checks, excluded
BIG-bench material, and special handling of GSM-8K. LiveBench answers by using
recent, monthly updated, objectively scored questions. The last paragraph should
turn toward Ch70: if data has to be mined, filtered, synthesized, refreshed, and
protected, the next bottleneck is the physical machinery doing that work.
