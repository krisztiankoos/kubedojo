# Brief: Chapter 41 - The Graphics Hack

## Thesis
The Deep Learning revolution was bottlenecked by the sheer time required to train models on standard CPUs. It took creative researchers hacking into consumer Graphics Processing Units (GPUs)—hardware originally designed for video games—to unlock the massive, parallel matrix multiplication required for modern AI.

## Scope
- IN SCOPE: Early GPGPU computing, the architectural difference between CPUs and GPUs, the use of graphics APIs (OpenGL/DirectX) for general computing before CUDA.
- OUT OF SCOPE: NVIDIA's later monopoly (covered in Part 9).

## Scenes Outline
1. **The CPU Ceiling:** Training early neural networks takes weeks or months on standard CPUs.
2. **The Graphics Architecture:** Explaining why GPUs (built to render millions of pixels simultaneously) are perfectly suited for matrix math.
3. **The Shader Hack:** Early researchers painstakingly translating neural network math into pixel shading languages just to run it on the GPU.
