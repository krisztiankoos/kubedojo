# People: Chapter 41 - The Graphics Hack

## Primary Actors

- **Dave Steinkraus** - Co-author of the 2005 ICDAR paper using GPUs for machine-learning algorithms. Verified facts: the paper frames ML training time as a bottleneck, implements primitives with DirectX 9 shaders, and reports a 3.3x speedup on a GeForce 6800 Ultra for the tested workload. Anchors: sources.md C01, C08, C18.
- **Ian Buck** - Co-author of both Steinkraus et al. 2005 and Brook for GPUs (2004). Verified facts: appears in the primary-source chain both as a machine-learning GPU implementer and as part of the Brook abstraction effort. Anchors: C08, C11, C15, C19-C20.
- **Patrice Y. Simard** - Co-author of Steinkraus et al. 2005. Verified facts: the paper's handwriting-recognition setting supplies the chapter's CPU-bottleneck and measured-speedup anchors. Anchors: C01-C04, C18.
- **Kyoung-Su Oh** - Co-author of the 2004 *Pattern Recognition* neural-network GPU implementation. Verified facts: the paper maps MLP inner products to matrix operations and reports up to about 20-fold speedup on an ATI Radeon 9700 Pro. Anchors: C09-C10, C17.
- **Keechul Jung** - Co-author of Oh and Jung 2004. Verified facts: same neural-network implementation and speedup evidence. Anchors: C09-C10, C17.

## Infrastructure and Abstraction Actors

- **Tim Foley, Daniel Horn, Jeremy Sugerman, Kayvon Fatahalian, Mike Houston, and Pat Hanrahan** - Co-authors with Ian Buck on Brook for GPUs. Verified facts: the paper frames GPU computation as kernels over streams and presents compilation to GPU shaders as an abstraction over graphics APIs. Anchors: C11, C15, C19-C20.
- **John D. Owens, David Luebke, Naga Govindaraju, Mark Harris, Jens Kruger, Aaron Lefohn, and Timothy J. Purcell** - Authors of the GPGPU survey used for architectural context. Verified facts: the survey describes GPUs as programmable parallel processors and explains the general pattern of recasting non-graphics computation for graphics hardware. Anchors: C06, C16.

## People to Keep Out of the Center

- **NVIDIA executives, CUDA product leads, and later deep-learning figures** - important for adjacent chapters, but Ch41's contract is about the shader-era hack and early ML/GPGPU papers. Mention only as forward pointers if a prose reviewer requests continuity.
- **Unnamed "researcher with a typo"** - appears only in legacy prose as drama. No anchor. Status: Red via sources.md C24.
