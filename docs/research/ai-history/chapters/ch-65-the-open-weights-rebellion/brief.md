# Brief: Chapter 65 - The Open Weights Rebellion

## Thesis

Open weights changed the politics of frontier AI without cleanly solving the
politics of AI. Stable Diffusion proved that a capable generative model could
leave the API and run in public hands. LLaMA then made language models feel
portable: released weights, cheap instruction tuning, LoRA adapters,
QLoRA quantization, and permissive releases like Mistral 7B turned the lab moat
from "only we can run it" into "who controls the best base model, data, license,
distribution channel, evaluation story, and deployment stack?" This chapter
should not romanticize "open" as a single category. It should explain the messy
ladder from research-only access to non-commercial derivatives to commercially
usable weights, and why that ladder forced closed labs, cloud vendors, regulators,
and hobbyist communities to react.

## Boundary Contract

- IN SCOPE: Stable Diffusion as the public open-weights precedent; LLaMA 1's
  research-community release and public-data/open-sourcing claim; LoRA/QLoRA as
  the adaptation and hardware-barrier reducers; Alpaca/Vicuna as early
  instruction-tuned community descendants with non-commercial and evaluation
  caveats; Llama 2's research/commercial release; Mistral 7B's Apache 2.0
  permissive release; the difference between open weights, open source, open
  data, and open governance.
- OUT OF SCOPE: diffusion mathematics and image-generation mechanics (Ch58);
  inference serving economics (Ch63); edge deployment constraints (Ch64);
  benchmark politics as a standalone product weapon (Ch66); monopoly/platform
  power (Ch67); data labor/copyright fights (Ch68); data exhaustion (Ch69);
  datacenter power/grid constraints (Ch70/72); export controls (Ch71).
- Transition from Ch64: Ch64 explains why local devices need smaller, quantized,
  specialized models; Ch65 explains why downloadable weights and cheap adapters
  made those constraints politically and commercially salient.
- Transition to Ch66/67/68: once weights circulate, reputation moves to
  leaderboards, platforms, licenses, and data provenance.

## Required Scenes

1. **The Image Model Leaves The API:** Stable Diffusion is the precedent: weights,
   code, model card, license, consumer-GPU memory claims, LAION data, and safety
   caveats all arrive in public view.
2. **LLaMA Makes Portability Concrete:** Meta's paper frames LLaMA as 7B-65B
   models trained on public data and released to the research community, with
   13B/65B performance claims that make smaller downloadable models feel serious.
3. **Adapters Turn Access Into Modification:** LoRA changes "fine-tune a giant
   model" into "freeze the base, train small low-rank modules"; QLoRA later pushes
   large-model tuning onto a single 48GB GPU.
4. **The Weekend Clone Moment:** Alpaca and Vicuna show how quickly instruction
   tuning, ShareGPT-style data, and community evaluation can wrap a base model,
   but their non-commercial licenses, self-reported costs, and evaluation caveats
   prevent easy triumphalism.
5. **Commercial Open Weights Arrive:** Llama 2 and Mistral 7B move from research
   access toward commercially usable and permissively licensed weights; the story
   becomes not "open versus closed" but "which terms, which data, which safety
   process, and which ecosystem?"
6. **The Rebellion Becomes Infrastructure:** close on open weights as a durable
   ecosystem layer: base models, adapters, quantized forks, leaderboards, hosting,
   local inference, and legal/governance arguments.

## Prose Capacity Plan

Target range: 4,200-5,300 words.

- 450-600 words: define open weights vs open source vs open data vs open
  governance; bridge from Ch64's local constraints to Ch65's access politics.
- 650-800 words: Stable Diffusion as the public precedent, using Ch58's anchored
  release facts without re-explaining diffusion math.
- 650-800 words: LLaMA 1 as the language-model portability shock: 7B-65B scale,
  public-data/open-sourcing framing, and performance claims.
- 800-950 words: LoRA and QLoRA as the technical reason weights became
  modifiable by small teams: trainable-parameter, memory, and hardware anchors.
- 750-900 words: Alpaca and Vicuna as community instruction-tuning case studies,
  with explicit non-commercial, data, cost, and evaluation caveats.
- 650-800 words: Llama 2 and Mistral 7B as the commercial/permissive turn,
  contrasting limited open release with Apache 2.0.
- 250-450 words: close and handoff to Ch66/67/68.

## Guardrails

- Do not call LLaMA, Llama 2, Stable Diffusion, or Mistral "open source" unless
  the source/license actually supports that wording. Prefer "open weights" or
  "released weights" when code/data/governance are not fully open.
- Do not treat leaked LLaMA access as a verified episode unless a primary or
  reliable archived source is added later; the current contract can describe
  rapid community derivatives without asserting leak mechanics.
- Treat Alpaca/Vicuna cost and benchmark claims as project-reported and caveated,
  not independent proof of model quality.
- Do not import Ch66's benchmark-politics chapter except to hand off the
  evaluation problem.
- Do not import Ch68's copyright/data-labor chapter except to flag LAION,
  ShareGPT, and text-davinci data provenance as unresolved governance pressure.
