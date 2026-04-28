# Infrastructure Log: Chapter 65 - The Open Weights Rebellion

## Systems To Track In Prose

- **Weights as artifacts:** downloadable checkpoints become the central object,
  separate from papers, APIs, demos, model cards, licenses, and datasets.
- **Model hubs and distribution:** releases live through Hugging Face-style
  repositories, GitHub code, torrents/download links, and community mirrors.
- **Adapters:** LoRA turns customization into small trainable modules layered on
  a frozen base model.
- **Quantization:** QLoRA makes the storage precision of the base model part of
  the access story; a 4-bit frozen model plus adapters changes who can tune.
- **Instruction data:** Alpaca's generated demonstrations and Vicuna's ShareGPT
  conversations show that open weights immediately depend on data pipelines with
  legal and ethical pressure.
- **Licenses and AUPs:** OpenRAIL-M, LLaMA/Llama 2 terms, non-commercial
  restrictions, and Apache 2.0 are plot devices, not footnotes.
- **Evaluation rituals:** project blogs, GPT-4-as-judge, MT-Bench-style scores,
  and leaderboards become reputation infrastructure; Ch66 owns the full story.

## Metrics And Claims To Keep Source-Bound

- LLaMA 1: 7B-65B; LLaMA-13B outperforms GPT-3 on most benchmarks; LLaMA-65B
  competitive with Chinchilla-70B and PaLM-540B; released to research community.
- LoRA: up to 10,000x fewer trainable parameters and 3x lower GPU memory in the
  abstract; GPT-3 175B example from 1.2TB to 350GB VRAM and 350GB to 35MB
  checkpoint in a specific Section 4.2 setup.
- Alpaca: 52K instruction-following demonstrations generated with
  text-davinci-003; reported <$500 data generation and <$100 fine-tuning cost;
  academic/non-commercial restrictions.
- Vicuna: about 70K ShareGPT conversations; around $300 13B training cost; 90%
  ChatGPT-quality claim explicitly non-scientific.
- Llama 2: 7B/13B/70B pretrained and chat models released for research and
  commercial use with license/AUP/responsible-use materials.
- QLoRA: 65B fine-tuning on one 48GB GPU; >780GB to <48GB memory reduction;
  NF4, double quantization, paged optimizers; benchmark claims caveated.
- Mistral 7B: 7.3B parameter model; Apache 2.0; first-party/paper claims of
  outperforming Llama 2 13B.

## Boundary

- Ch65 owns access, modification, and licensing infrastructure.
- Ch66 owns the leaderboard and benchmark weaponization that grows out of this.
- Ch68 owns the data/copyright reckoning around LAION, ShareGPT, generated
  demonstrations, scraped web/books, and training provenance.
