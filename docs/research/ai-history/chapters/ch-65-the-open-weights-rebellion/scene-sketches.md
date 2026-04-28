# Scene Sketches: Chapter 65 - The Open Weights Rebellion

## Scene 1: The Image Model Leaves The API

Open with the contrast between an API account and a file on disk. Stable
Diffusion's release package matters because it made multiple artifacts visible at
once: weights, code, model card, license, memory footprint, data notes, and
limitations. Keep this short and explicitly send diffusion mechanics back to
Ch58. The point is social: once weights are downloadable, the boundary between
user, developer, artist, platform, and regulator shifts.

Guardrail: do not make Stability's public-release claims independent adoption
metrics. Say what the release made possible and visible.

## Scene 2: LLaMA Makes Portability Concrete

Move from image generation to language models. LLaMA's paper can carry the whole
scene: 7B-65B scale, 13B versus GPT-3 claims, 65B versus Chinchilla/PaLM claims,
publicly available data, and research-community release. The scene should explain
why the 13B claim mattered: it made "small enough to move" compatible with "good
enough to care about."

Guardrail: do not narrate leak mechanics without a verified source. The chapter
can explain rapid derivatives after LLaMA without asserting how every actor got
the weights.

## Scene 3: Adapters Turn Access Into Modification

This is the technical center. LoRA changes the unit of sharing: not just a base
model, but a small adapter. QLoRA adds 4-bit quantization, NF4, double
quantization, and paged optimizers so large-model fine-tuning becomes a hardware
story, not only a lab-access story. Make this accessible: the base model becomes
the heavy instrument; adapters become swappable sheet music.

Guardrail: use the LoRA/QLoRA numbers exactly and source-bound. Do not imply any
single hobbyist can reproduce frontier training.

## Scene 4: The Weekend Clone Moment

Alpaca and Vicuna should feel fast, exciting, and uncomfortable. Stanford's
Alpaca shows 52K generated demonstrations and a cheap fine-tune claim; Vicuna
adds ShareGPT conversations, mult-turn chat, and the historically telling
GPT-4-as-judge evaluation. The prose should let the reader feel why this shocked
closed labs while also making the caveats explicit: non-commercial licenses,
upstream terms, user-shared data, content-filter limits, and weak evaluation.

Guardrail: do not celebrate the "90%" claim. It is a scene about evaluation
pressure and community speed, not settled model quality.

## Scene 5: Commercial Open Weights Arrive

Llama 2 makes the commercial-use pivot. Mistral 7B makes the permissive-license
pivot. Put them in contrast: Meta couples release with license, AUP, safety
framing, and responsible-use guidance; Mistral foregrounds Apache 2.0 and
frictionless reuse. This is where "open" fractures into terms of use,
governance, data opacity, benchmarks, and distribution.

Guardrail: do not turn the scene into brand advocacy. Use each release to explain
ecosystem strategy.

## Scene 6: The Rebellion Becomes Infrastructure

Close with the new stack: base weights, adapters, quantized variants, local
runtimes, leaderboards, model hubs, cloud endpoints, and enterprise policies.
The rebellion did not end closed labs. It forced everyone to answer a harder
question: if model weights can travel, what still concentrates power?

Handoff: Ch66 answers reputation/evaluation, Ch67 answers platform power, Ch68
answers data and copyright.
