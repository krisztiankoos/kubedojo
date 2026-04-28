# Sources: Chapter 65 - The Open Weights Rebellion

## Status Legend

- Green: claim has direct primary evidence from a paper, model card, first-party
  release post, or project blog, and the prose should stay within that source's
  wording.
- Yellow: claim is usable only with a caveat: first-party marketing, project-run
  benchmark, license/governance synthesis, or background discovery pointer.
- Red: no claim may be drafted from this row without new verification.

## Primary Source Spine

| Source | Use In Chapter | Anchor Notes |
|---|---|---|
| Stability AI, "Stable Diffusion Public Release," August 22, 2022; Stable Diffusion v1-4 model card. Reused from Ch58 anchored contract. | Open-weights precedent before LLaMA; weights/code/model card/license/consumer GPU framing. | Green/Yellow: Ch58 source review verified Stability's Aug. 22 public release, weights/model card/code availability, OpenRAIL-M license, v1.4 memory footprint, LAION training notes, and limitations. Use only as a transition; Ch58 owns diffusion mechanics. |
| Hugo Touvron et al., "LLaMA: Open and Efficient Foundation Language Models," arXiv:2302.13971. PDF: https://arxiv.org/pdf/2302.13971 | LLaMA 1 scale, public-data framing, research-community release, smaller-model performance claims. | Green: PDF downloaded 2026-04-28 and extracted with pdftotext. Abstract/page 1 says models range 7B-65B; LLaMA-13B outperforms GPT-3 on most benchmarks; LLaMA-65B is competitive with Chinchilla-70B and PaLM-540B; and Meta releases all models to the research community. Intro says the work uses only publicly available data and is compatible with open-sourcing. Conclusion repeats open release and public-data framing. |
| Edward J. Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models," arXiv:2106.09685. PDF: https://arxiv.org/pdf/2106.09685 | Adapter layer that made community fine-tuning cheaper and more modular. | Green: PDF downloaded 2026-04-28. Abstract says LoRA freezes pretrained weights and injects trainable rank-decomposition matrices; reduces trainable parameters by 10,000x and GPU memory by 3x; and releases a PyTorch package. Section 4.2 reports GPT-3 175B VRAM from 1.2TB to 350GB and checkpoint size from 350GB to 35MB for a cited configuration. |
| Stanford CRFM, "Alpaca: A Strong, Replicable Instruction-Following Model," March 13, 2023. URL: https://crfm.stanford.edu/2023/03/13/alpaca.html | Early community instruction-tuning from LLaMA 7B using generated demonstrations; release/caveat scene. | Green/Yellow: page fetched 2026-04-28. Lines around 285-299 say Alpaca is fine-tuned from LLaMA 7B on 52K instruction-following demonstrations generated with text-davinci-003 and that Stanford released training recipe/data. Lines around 307-315 say it is academic-only/non-commercial due to LLaMA and OpenAI terms. Cost/evaluation claims are project-reported and must be caveated. |
| LMSYS, "Vicuna: An Open-Source Chatbot Impressing GPT-4 with 90%* ChatGPT Quality," March 30, 2023. URL: https://lmsys.org/blog/2023-03-30-vicuna/ | Community chat-model fork, ShareGPT data, low training cost, evaluation caveat. | Yellow: project blog fetched 2026-04-28. It says Vicuna-13B was fine-tuned from LLaMA on about 70K user-shared ShareGPT conversations, training cost was around $300, and code/model are available for non-commercial use. The 90% ChatGPT-quality claim is explicitly marked "fun and non-scientific" by the source and must be framed as a historically important but weak evaluation practice. |
| Hugo Touvron et al., "Llama 2: Open Foundation and Fine-Tuned Chat Models," arXiv:2307.09288. PDF: https://arxiv.org/pdf/2307.09288 | Commercially usable open-weight turn and safety/release framing. | Green: PDF downloaded 2026-04-28. Abstract/page 1 says Meta develops and releases Llama 2, pretrained and fine-tuned models 7B-70B. Intro says models are released to the general public for research and commercial use, includes Llama 2 and Llama 2-Chat variants at 7B, 13B, and 70B, and argues open release can be a net benefit. Later release section says models are available with license, acceptable-use policy, code examples, and Responsible Use Guide. |
| Tim Dettmers et al., "QLoRA: Efficient Finetuning of Quantized LLMs," arXiv:2305.14314. PDF: https://arxiv.org/pdf/2305.14314 | Quantization/adaptation layer that lowers the hardware barrier for fine-tuning. | Green: PDF downloaded 2026-04-28. Abstract says QLoRA backpropagates through a frozen 4-bit quantized model into LoRA adapters and enables fine-tuning a 65B model on a single 48GB GPU. Intro reports >780GB to <48GB memory reduction, NF4, double quantization, and paged optimizers. Results report Guanaco memory figures and consumer/professional GPU training examples; benchmark wins require caveats. |
| Mistral AI, "Announcing Mistral 7B," September 27, 2023. URL: https://mistral.ai/en/news/announcing-mistral-7b | Permissive-release climax: Apache 2.0 model, torrent/download culture, strong 7B performance framing. | Green/Yellow: first-party page fetched 2026-04-28. It says Mistral 7B is a 7.3B model, released under Apache 2.0 and usable without restrictions, outperforming Llama 2 13B on Mistral's benchmarks. Treat performance as first-party/product framing unless independently confirmed. |
| Jiang et al., "Mistral 7B," arXiv:2310.06825. PDF: https://arxiv.org/pdf/2310.06825 | Paper-level support for Mistral 7B architecture/performance/license. | Green: PDF downloaded 2026-04-28. Abstract says Mistral 7B outperforms the best open 13B model, uses grouped-query and sliding-window attention, and models are released under Apache 2.0. Body says release includes reference implementation and deployment support; Table 2 compares against Llama models. |
| Wikipedia pages for Stable Diffusion, LLaMA, LoRA, and Mistral AI. | Source-discovery only. | Yellow: useful for checking chronology and finding primary links, not used as evidence for prose claims. |

## Scene-Level Claim Table

| Claim | Scene | Primary Anchor | Confirmation | Status | Notes |
|---|---|---|---|---|---|
| Stable Diffusion made weights, code, model card, license, and consumer-GPU feasibility public enough to become the open-weights precedent. | Image Model Leaves API | Ch58 verified Stability release + model card | Ch58 source review | Yellow | Transition only; Ch58 owns diffusion details. |
| LLaMA 1 was presented as 7B-65B models released to the research community. | LLaMA Portability | LLaMA p.1 abstract | LLaMA conclusion | Green | Do not claim fully public/commercial release. |
| LLaMA 13B/65B performance claims made smaller models look strategically serious. | LLaMA Portability | LLaMA p.1 + benchmark tables | LLaMA conclusion | Green | Paper claims only. |
| LLaMA was framed as trained on publicly available data and compatible with open-sourcing. | LLaMA Portability | LLaMA intro/public-data paragraph | LLaMA conclusion | Green | Avoid proving data cleanliness. |
| LoRA freezes base weights and trains low-rank matrices, reducing trainable parameters and memory. | Adapters | LoRA abstract | LoRA Section 4.2 | Green | Core technical explanation. |
| LoRA's GPT-3 example reduces fine-tuning VRAM/checkpoint size enough to make adapters a distribution object. | Adapters | LoRA Section 4.2 | LoRA abstract | Green | Keep configuration-specific. |
| Alpaca fine-tuned LLaMA 7B on 52K text-davinci-003 generated demonstrations and released recipe/data. | Weekend Clone | Stanford Alpaca blog | LLaMA base-model paper | Green | Academic/research release framing. |
| Alpaca was explicitly non-commercial/academic-only because of upstream terms. | Weekend Clone | Stanford Alpaca blog license section | N/A | Green | Important no-overclaim guardrail. |
| Alpaca's cheap-cost and text-davinci similarity claims were project-reported and evaluation-limited. | Weekend Clone | Stanford Alpaca blog cost/evaluation sections | Blog limitations section | Yellow | Must not become independent benchmark proof. |
| Vicuna used about 70K ShareGPT conversations and reported roughly $300 training cost for Vicuna-13B. | Weekend Clone | LMSYS Vicuna blog | LMSYS cost table | Yellow | Project-reported; data provenance goes to Ch68. |
| Vicuna's 90% ChatGPT-quality claim was explicitly non-scientific and illustrates the coming evaluation problem. | Weekend Clone / Handoff | LMSYS caveat line | LMSYS evaluation limitations | Yellow | Handoff to Ch66. |
| Llama 2 moved the release frame to general public research and commercial use at 7B/13B/70B. | Commercial Open Weights | Llama 2 intro | Llama 2 release section | Green | License/AUP still matter. |
| Llama 2's paper ties openness to reproducibility, safety research, license, AUP, and responsible-use guidance. | Commercial Open Weights | Llama 2 intro + release section | Llama 2 Section 5.3 | Green | Good governance nuance. |
| QLoRA enables 65B fine-tuning on a single 48GB GPU through frozen 4-bit quantized models plus LoRA adapters. | Adapters | QLoRA abstract | QLoRA intro | Green | Strong accessibility anchor. |
| QLoRA's Guanaco benchmark claims need caveats despite the memory/access breakthrough. | Adapters / Weekend Clone | QLoRA abstract/results | QLoRA qualitative failure notes | Yellow | Avoid leaderboard triumphalism. |
| Mistral 7B was released under Apache 2.0 and framed as usable without restrictions. | Commercial Open Weights | Mistral announcement | Mistral paper abstract | Green | Permissive-release climax. |
| Mistral 7B performance claims rely on Mistral's evaluation pipeline and should be source-bound. | Commercial Open Weights | Mistral announcement + paper | Mistral Table 2 | Yellow | Say "Mistral reported." |
| Open weights are not the same as open source, open data, or open governance. | Rebellion Infrastructure | License/source rows above | Alpaca/Llama 2/Mistral contrasts | Green | Synthesis from contract. |

## Conflict Notes

- "Open-source chatbot" appears in some project titles, but prose should prefer
  "open weights" or "released weights" unless source code, license, data, and
  governance are actually open.
- Cost numbers for Alpaca and Vicuna are useful historically because they shaped
  community perception, but they are not audited total-cost accounting.
- GPT-4-as-judge/Vicuna quality claims belong mainly to Ch66. Ch65 may use them
  only to show how open-weight communities immediately needed evaluation rituals.
- LAION, ShareGPT, generated instruction data, and web/book provenance are
  handoffs to Ch68, not a full legal analysis here.
