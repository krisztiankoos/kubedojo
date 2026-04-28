# Infrastructure Log: Chapter 58

## Technical Metrics & Constraints
- **Pixel-space diffusion cost:**
  - Rombach et al. state that powerful pixel-space diffusion can require hundreds of GPU days and expensive repeated inference evaluations in RGB image space.
  - Use as the problem statement for why latent diffusion mattered.
- **Iterative inference:**
  - Dhariwal/Nichol note diffusion models are still slower than GANs at sampling time because they require multiple denoising steps/forward passes.
  - Stable Diffusion's model card examples still assume dozens of sampling steps for common pipelines.
- **Guidance as compute/control:**
  - Classifier guidance and classifier-free guidance improve controllability/fidelity but introduce an explicit diversity/fidelity trade-off.
  - Do not present guidance as free quality. It is a lever with costs and failure modes.
- **Latent-space compression:**
  - LDMs use an autoencoder to move from image space into a lower-dimensional latent representation. Stable Diffusion v1-4 uses a relative downsampling factor of 8 and trains the denoising objective in latent space.
  - This is the infrastructure hinge: less pixel-space work made broader experimentation and deployment more practical.
- **Stable Diffusion hardware anchors:**
  - Stability's Aug 10 post claims under 10 GB VRAM consumer-GPU feasibility and 512x512 generation in seconds.
  - Stability's Aug 22 public release says the v1.4 release memory usage should be 6.9 GB VRAM and recommends NVIDIA chips at release.
  - The v1-4 model card records training hardware as 32 x 8 A100 GPUs and estimated emissions from 150,000 A100 PCIe 40GB hours. Use carefully and cite as model-card self-report.

## Prose Guardrails

- Do not collapse training economics and inference economics. Pixel-space training cost, sequential sampling latency, and consumer-GPU runtime are separate layers.
- Do not move the full open-source/open-weights argument here; Chapter 65 owns that after Stable Diffusion/LLaMA.
- Do not move the full LAION/copyright/labor conflict here; Chapter 68 owns that.
