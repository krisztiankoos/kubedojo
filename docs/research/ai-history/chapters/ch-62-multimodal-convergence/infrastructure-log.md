# Infrastructure Log: Chapter 62 - Multimodal Convergence

## Systems To Track In Prose

- **Language-image contrastive pretraining:** CLIP trains image and text encoders
  on web-scale image-text pairs. This is the clean bridge from language as
  output to language as supervision for visual categories.
- **Interleaved multimodal prompt sequences:** Flamingo and GPT-4 Section 4.1
  make the key interface shift concrete: prompts can combine text with images,
  screenshots, diagrams, documents, photos, and videos depending on the system.
- **Vision assistant deployment layer:** GPT-4V shows image analysis inside an
  assistant product, with risk controls for hallucination, jailbreaks, medical
  claims, and sensitive visual inferences.
- **Joint-training multimodal product claim:** Gemini is the safe anchor for the
  "natively multimodal" phrase, defined narrowly as joint training across image,
  audio, video, and text plus support for interleaved multimodal inputs.
- **End-to-end speech interface:** GPT-4o replaces a prior three-model voice
  pipeline with a single end-to-end model across text, vision, and audio. The
  key infrastructure signal is not only accuracy; it is audio latency,
  turn-taking, tone, multiple speakers, and background sound.
- **Video patch infrastructure:** Sora represents videos and images as latent
  patches across space and time and trains diffusion transformers over those
  patches. This is the video-era analogue to tokenization, but the prose must
  avoid implying solved physical reasoning.
- **Multimodal safety stack:** Image-borne jailbreaks, unsafe visual advice,
  voice cloning/speaker identification, video red teaming, multimodal
  moderation, provenance, and watermarking all become part of product
  infrastructure.

## Metrics And Claims To Keep Source-Bound

- CLIP: 400M image-text pairs, zero-shot transfer framing.
- GPT-4/GPT-4V: image/text inputs and text outputs; vision deployment risks.
- Gemini: joint training across text/image/audio/video; interleaved inputs; text
  and image outputs in the cited report.
- GPT-4o: accepts text/audio/image/video inputs; generates text/audio/image
  outputs; 232 ms minimum and 320 ms average audio response latency.
- Sora: up-to-one-minute high-fidelity video claim; visual/spacetime patches;
  explicit simulator limitations.
- Veo: 1080p videos longer than a minute is an official product claim, not an
  independently tested capability in this contract.

## Boundary

- Copyright, scraping, creator compensation, book/image/video licensing, and
  data labor belong primarily in Chapter 68.
- Benchmark politics and public ranking contests belong primarily in Chapter 66.
- Inference cost, serving latency economics, and datacenter load belong in
  Chapter 63, except where GPT-4o latency is needed to explain the interface.
- Image diffusion history belongs in Chapter 58. This chapter may mention
  diffusion only to explain Sora's video architecture.
