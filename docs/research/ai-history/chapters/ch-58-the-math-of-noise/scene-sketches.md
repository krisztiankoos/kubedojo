# Scene Sketches: Chapter 58

## Scene 1: The Thermodynamic Metaphor
- **Action:** Begin with the intuition of a drop of ink spreading through water, then immediately qualify it: the chapter is not claiming physical entropy is reversed. Sohl-Dickstein's move is to build a controlled mathematical corruption process whose reverse transitions can be learned.
- **Evidence Anchor:** Sohl-Dickstein et al. 2015 PDF pp.1-5.
- **Prose Caution:** Use the metaphor to open the door, then switch to Markov chains/noise schedules before the metaphor becomes misleading.

## Scene 2: The Dog Becomes Static
- **Action:** A familiar image is repeatedly noised until the original signal disappears. Each step is small enough that the reverse conditional can be approximated as a Gaussian denoising move.
- **Evidence Anchor:** Ho et al. 2020 PDF p.2 for forward Gaussian diffusion; Sohl-Dickstein Figure 1 for the trajectory idea.
- **Prose Caution:** The dog/cat image is a teaching prop, not a specific experiment unless the prose uses source images from CIFAR/LSUN/CelebA.

## Scene 3: The Network Learns the Noise
- **Action:** The network is not asked to imagine the final picture in one leap. It is trained to predict the noise component at a timestep, then sampling begins from random noise and applies the learned denoising step again and again.
- **Evidence Anchor:** Ho et al. 2020 PDF p.4 Algorithms 1-2 and epsilon-prediction discussion.
- **Prose Caution:** Avoid "magic" as explanation. The wonder comes from iteration and scale, not from a hidden symbolic artist inside the model.

## Scene 4: The Benchmark Break
- **Action:** Move from mechanism to historical validation. Dhariwal and Nichol tune architecture and guidance, then show diffusion beating strong GAN baselines on ImageNet metrics while preserving a real cost: many denoising passes.
- **Evidence Anchor:** Dhariwal/Nichol 2021 PDF p.1, pp.2-3, pp.11-12.
- **Prose Caution:** Benchmark victory is not the same as universal image quality or cultural legitimacy.

## Scene 5: Stable Diffusion Shrinks the Machine
- **Action:** Rombach et al. stop denoising every pixel directly and work in a compressed latent space. Stable Diffusion combines that latent machinery with text conditioning and releases a model that can run on comparatively accessible hardware.
- **Evidence Anchor:** Rombach 2022 PDF pp.1-3 and 7-9; Stable Diffusion model card; Stability AI Aug 10/Aug 22 posts.
- **Prose Caution:** Copyright, open-weights governance, and data-labor politics are transitions only; Ch65 and Ch68 carry the full burden.
