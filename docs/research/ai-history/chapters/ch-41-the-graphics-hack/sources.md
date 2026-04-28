# Sources: Chapter 41 - The Graphics Hack

## Verification Key

- **Green**: claim has a verified page, section, DOI, or stable primary-source anchor.
- **Yellow**: source exists or is plausible, but the exact claim is not yet page-located or is only secondarily supported.
- **Red**: do not draft the claim yet.

## Primary Sources

| Source | Use | Verification |
|---|---|---|
| Dave Steinkraus, Ian Buck, and Patrice Y. Simard, "Using GPUs for Machine Learning Algorithms," *Eighth International Conference on Document Analysis and Recognition* (ICDAR 2005), pp. 1115-1120. Open PDF mirror: `https://readingxtra.github.io/docs/ml-gpu/gpu-for-ml-05.pdf` | Main anchor for the CPU bottleneck, GPU economics, pixel-shader implementation, bus constraints, precision limits, and measured speedups in an ML handwriting-recognition pipeline. | **Green** for C01-C05, C07-C08, C12-C14, C18. Verified via open PDF text extraction in browser-accessible source, 2026-04-29. |
| Kyoung-Su Oh and Keechul Jung, "GPU implementation of neural networks," *Pattern Recognition* 37, no. 6 (2004), pp. 1311-1314. DOI: `10.1016/j.patcog.2004.01.013`. Open PDF mirror: `https://gwern.net/doc/ai/scaling/hardware/2004-oh.pdf` | Primary neural-network demonstration: MLP inner products as matrix multiplication, implementation on ATI Radeon 9700 Pro, and reported speedup. | **Green** for C09-C10, C17. Verified via open PDF text extraction in browser-accessible source, 2026-04-29. |
| Ian Buck, Tim Foley, Daniel Horn, Jeremy Sugerman, Kayvon Fatahalian, Mike Houston, and Pat Hanrahan, "Brook for GPUs: Stream Computing on Graphics Hardware," *ACM Transactions on Graphics* 23, no. 3 (SIGGRAPH 2004), pp. 777-786. DOI: `10.1145/1015706.1015800`. PDF: `https://graphics.stanford.edu/papers/brookgpu/brookgpu.pdf` | Main anchor for GPGPU as stream computing, graphics API awkwardness, and the attempt to compile higher-level kernels to GPU shaders. | **Green** for C11, C15, C19-C20. Verified via Stanford-hosted PDF text extraction, 2026-04-29. |
| John D. Owens, David Luebke, Naga Govindaraju, Mark Harris, Jens Kruger, Aaron Lefohn, and Timothy J. Purcell, "A Survey of General-Purpose Computation on Graphics Hardware," *Computer Graphics Forum* 26, no. 1 (2007), pp. 80-113. DOI: `10.1111/j.1467-8659.2007.01012.x`. Open PDF: `https://diglib.eg.org/bitstreams/f5e66f50-5cd3-482c-ac77-4e81335a0a32/download` | Broad GPGPU context: programmable, parallel graphics processors; graphics-pipeline recasting; data-structure and algorithmic constraints. | **Green** for C06, C16. Verified via Eurographics PDF text extraction, 2026-04-29. |
| Erik Lindholm, Mark J. Kilgard, Henry Moreton, "A User-Programmable Vertex Engine," *SIGGRAPH 2001*, pp. 149-158. DOI: `10.1145/383259.383274`. | Useful for the arrival of user-programmable vertex processing in mainstream graphics. | Yellow. Citation located, but chapter does not need Green dependence while Owens/Steinkraus cover the necessary architecture. |
| William R. Mark, R. Steven Glanville, Kurt Akeley, and Mark J. Kilgard, "Cg: A System for Programming Graphics Hardware in a C-like Language," *ACM Transactions on Graphics* 22, no. 3 (SIGGRAPH 2003), pp. 896-907. DOI: `10.1145/882262.882362`. | Useful if prose needs more on Cg as a shader language. | Yellow. Source located bibliographically, but no page-level extraction performed for this contract. |

## Secondary and Context Sources

| Source | Use | Verification |
|---|---|---|
| John D. Owens et al., "GPU Computing," *Proceedings of the IEEE* 96, no. 5 (2008), pp. 879-899. DOI: `10.1109/JPROC.2008.917757`. | Later synthesis of GPU computing and the shift away from graphics-only APIs. | Yellow. Useful for review only; not used as a Green anchor. |
| Rajat Raina, Anand Madhavan, and Andrew Y. Ng, "Large-scale Deep Unsupervised Learning using Graphics Processors," *ICML 2009*. | Bridge to later deep-learning scale and CUDA-era training. | Yellow. Belongs mostly to Ch42 or later; do not use to enlarge Ch41 unless exact anchors are added and boundary remains intact. |

## Scene-Level Claim Table

| ID | Claim | Scene | Primary Anchor | Independent Confirmation | Status | Notes |
|---|---|---|---|---|---|---|
| C01 | Steinkraus, Buck, and Simard identify training time as a major bottleneck for machine learning and give a neural-net training example that can take more than three weeks. | 1 | Steinkraus et al. 2005, p.1115/PDF p.1 | Same paper's experimental framing | **Green** | Use as bottleneck evidence. Do not generalize to all deep networks or all labs. |
| C02 | The same paper reports CPU OCR throughput around 1,000 characters per second in its handwriting-recognition setting. | 1 | Steinkraus et al. 2005, p.1115/PDF p.1 | Same paper | **Green** | Throughput is inference/OCR pipeline context, distinct from training-time bottleneck. |
| C03 | Steinkraus et al. argue that more training data and larger models were desirable but made training time more constraining. | 1 | Steinkraus et al. 2005, p.1115/PDF p.1 | Same paper | **Green** | Safe wording: "in their handwriting-recognition setting." |
| C04 | Steinkraus et al. contrast commodity GPUs with custom machine-learning hardware, noting GPUs were one-chip, low-cost, and already shipped in PCs. | 1 | Steinkraus et al. 2005, p.1115/PDF p.1 | Brook 2004, Section 1/PDF p.1 describes commodity GPU programmability | **Green** | Avoid saying all custom ML hardware was impractical. |
| C05 | Steinkraus et al. describe GPU trends in memory, bandwidth, parallelism, and programmability that made them promising for ML. | 2 | Steinkraus et al. 2005, p.1115/PDF p.1 | Owens et al. 2007, Section 1/PDF p.1 | **Green** | Architecture setup. |
| C06 | Owens et al. describe modern GPUs as programmable, parallel processors with high arithmetic and memory bandwidth, making them useful beyond graphics. | 2 | Owens et al. 2007, Section 1/PDF p.1 | Steinkraus et al. 2005, p.1115/PDF p.1 | **Green** | Broad GPGPU context. |
| C07 | Steinkraus et al. explain that the pixel shader runs independently for each generated pixel, which is the source of GPU parallelism in their method. | 2 | Steinkraus et al. 2005, p.1117/PDF p.3 | Owens et al. 2007, Sections 2-4/PDF pp.2-8 | **Green** | Good pedagogical anchor for the pixel-factory metaphor. |
| C08 | Steinkraus et al. used DirectX 9 vertex and pixel shaders to build machine-learning primitives on the GPU. | 2, 3 | Steinkraus et al. 2005, p.1117/PDF p.3 | Brook 2004, Section 1/PDF p.1 | **Green** | Keep API-specific. |
| C09 | Oh and Jung state that MLP layer operations can be represented as inner products and replaced by matrix operations. | 3 | Oh and Jung 2004, p.1312 | Steinkraus et al. 2005, pp.1117-1119/PDF pp.3-5 | **Green** | This is the math bridge, not a claim that rendering and learning are identical. |
| C10 | Oh and Jung implement matrix multiplication by rendering a full-screen rectangle and using a pixel shader to compute output elements. | 3 | Oh and Jung 2004, p.1313 | Steinkraus et al. 2005, p.1117/PDF p.3 | **Green** | Central "linear algebra in disguise" anchor. |
| C11 | Brook frames GPU computation as kernels operating over streams. | 3 | Buck et al. 2004, Section 1/PDF p.1 | Owens et al. 2007, Section 1/PDF p.1 | **Green** | Use to explain why a higher-level abstraction was attractive. |
| C12 | Steinkraus et al. describe placing ML data on the GPU as textures and using shaders over generated geometry. | 3 | Steinkraus et al. 2005, pp.1116-1117/PDF pp.2-3 | Oh and Jung 2004, p.1313 | **Green** | Safe concrete implementation detail. |
| C13 | Steinkraus et al. identify the AGP bus as asymmetric and slow for GPU-to-CPU transfers, requiring data and weights to remain on the GPU where possible. | 4 | Steinkraus et al. 2005, p.1116/PDF p.2 | Owens et al. 2007, Sections 3-4/PDF pp.4-8 | **Green** | Infrastructure constraint. |
| C14 | Steinkraus et al. report a precision-related issue: ATI hardware's 24-bit floating-point behavior made their ATI Radeon X800 result unreliable for that workload. | 4 | Steinkraus et al. 2005, p.1120/PDF p.6 | Owens et al. 2007, Section 6/PDF p.11 discusses precision as a GPGPU concern | **Green** | Paper names the card "ATI Radeon X800" (no "XT" suffix per Claude anchor verifier). Do not turn into a brand-wide judgment. |
| C15 | Buck et al. state that GPU programming through graphics APIs was powerful but hard to use for non-graphics applications. | 4 | Buck et al. 2004, Section 1/PDF p.1 | Owens et al. 2007, Section 1/PDF p.1 | **Green** | Good boundary between hack and later abstraction. |
| C16 | Owens et al. survey GPGPU as a process of mapping general computation onto graphics pipeline concepts, data structures, and memory models. | 4 | Owens et al. 2007, Sections 2-4/PDF pp.2-8 | Brook 2004, Section 1/PDF p.1 | **Green** | Use for general constraints, not a specific ML claim. |
| C17 | Oh and Jung report up to about a 20-fold speedup for their neural-network implementation on an ATI Radeon 9700 Pro compared with CPU execution. | 5 | Oh and Jung 2004, p.1311 | Same paper results discussion, pp.1313-1314 | **Green** | Workload-specific. |
| C18 | Steinkraus et al. report a 3.3x speedup for their GPU implementation on an NVIDIA GeForce 6800 Ultra in their tested pipeline. | 5 | Steinkraus et al. 2005, p.1120/PDF p.6 | Same paper Table/results | **Green** | Keep separate from C17. |
| C19 | Brook compiles stream programs to GPU fragment programs/shaders, showing an abstraction bridge over graphics hardware. | 5 | Buck et al. 2004, Section 6/PDF p.8 | Brook 2004, Section 1/PDF p.1 | **Green** | Phrase as "bridge," not as CUDA. |
| C20 | Brook presents GPUs as stream processors and argues for exposing GPU power through a more general programming system than raw graphics APIs. | 5 | Buck et al. 2004, title/abstract and Section 1/PDF p.1 | Owens et al. 2007, Section 1/PDF p.1 | **Green** | Bridge to Ch42 without importing CUDA details. |
| C21 | The specific GeForce 3 introduction of programmable shading in 2001 is part of the immediate hardware backdrop. | 2 | Lindholm et al. 2001, pp.149-158, DOI located | Owens et al. 2007 background | Yellow | Bibliographic anchor only; page-level claim not extracted. |
| C22 | Cg was one of the shader languages used in the early programmable-graphics era. | 3 | Mark et al. 2003, DOI located | Brook 2004 and Steinkraus 2005 context | Yellow | Source not page-extracted. Do not make Cg load-bearing. |
| C23 | Raina, Madhavan, and Ng 2009 showed larger-scale deep unsupervised learning on GPUs after the shader-hack period. | 5 | Raina et al. 2009, bibliographic source located | Later deep-learning histories | Yellow | Mostly Ch42/later. Use only as a forward pointer if needed. |
| C24 | A researcher wasted weeks after a typo in a CPU training run. | 1 | None | Legacy prose only | Red | Dramatic but unverified; do not draft. |
| C25 | Pixel rendering and neural-weight updates use the exact same underlying math. | 2 | None in this precise form | Related but narrower matrix-operation anchors in C09-C10 | Red | Too broad. Replace with the narrower matrix-operation mapping. |
| C26 | GPUs contained thousands of cores in the early 2000s shader-hack period. | 2 | None for this period | Later GPU descriptions | Red | Likely anachronistic for 2001-2005 consumer GPUs. Do not draft. |

## Page Anchor Worklist

### Done

- Steinkraus et al. 2005: pages 1115-1120/PDF pp.1-6 extracted and used for ML bottleneck, shader implementation, bus constraints, precision, and speedups.
- Oh and Jung 2004: pages 1311-1314 extracted and used for MLP matrix mapping, full-screen rectangle/pixel-shader implementation, Radeon 9700 Pro, and 20-fold speedup.
- Buck et al. 2004: sections 1 and 6 extracted and used for stream kernels, graphics API awkwardness, and shader-compilation abstraction.
- Owens et al. 2007: sections 1-4 extracted and used for broader GPGPU architecture and graphics-pipeline recasting.

### Tractable but not required for drafting

- Lindholm et al. 2001, "A User-Programmable Vertex Engine" - page extraction would strengthen the 2001 programmable-shader timeline.
- Mark et al. 2003, "Cg" - page extraction would strengthen any language-specific details.
- Kruger and Westermann 2003, "Linear Algebra Operators for GPU Implementation of Numerical Algorithms" - useful if the writer wants a non-neural linear-algebra precursor.

### Deliberately scoped out

- CUDA primary documentation and later CUDA ML papers - Ch42.
- AlexNet/ImageNet/GPU cluster evidence - later chapters.
- Business-market claims about NVIDIA dominance - Part 9.

## Conflict Notes

- Oh/Jung and Steinkraus/Buck/Simard report different speedups because they tested different workloads and hardware. Preserve the separate numbers.
- The legacy prose describes a generic deep-learning bottleneck. The anchored evidence here is more precise: handwriting recognition, MLP implementation, and GPGPU abstractions.
- The "graphics hack" was a workaround through graphics APIs, not yet the cleaned-up general-purpose GPU programming story.
