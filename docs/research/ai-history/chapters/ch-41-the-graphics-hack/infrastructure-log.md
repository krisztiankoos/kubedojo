# Infrastructure Log: Chapter 41 - The Graphics Hack

## Scene 1 - CPU Ceiling

- **CPU baseline:** Steinkraus et al. report CPU-side handwriting/OCR throughput and frame training time as a machine-learning bottleneck in their setting. Anchors: sources.md C01-C03.
- **Economic constraint:** Custom ML hardware was not the chosen path in the cited paper; commodity GPUs were attractive because they were already one-chip accelerators in PCs. Anchor: C04.

## Scene 2 - Programmable Graphics Hardware

- **Hardware capability:** The relevant GPU properties are high arithmetic throughput, memory bandwidth, parallel execution, and programmability. Anchors: C05-C06.
- **Parallel execution model:** Pixel shaders execute independently across generated pixels, giving the implementation a data-parallel shape. Anchor: C07.
- **API layer:** DirectX 9 vertex and pixel shaders are the specific API/hardware interface in Steinkraus et al. Anchor: C08.

## Scene 3 - Linear Algebra in Disguise

- **Neural-network operation:** Oh and Jung reduce MLP layer operations to matrix operations. Anchor: C09.
- **Rendering trick:** Matrix multiplication is implemented by drawing a full-screen rectangle and using a pixel shader to compute output elements. Anchor: C10.
- **Data representation:** Steinkraus et al. place data on the GPU as textures and use shaders over generated geometry. Anchor: C12.
- **Abstraction attempt:** Brook describes GPU work as kernels over streams rather than as hand-authored graphics plumbing. Anchor: C11.

## Scene 4 - Constraints

- **Host-device transfer:** AGP transfer asymmetry meant CPU-to-GPU movement was much faster than GPU-to-CPU movement, and useful implementations had to keep weights/data resident on the GPU. Anchor: C13.
- **Precision:** Vendor-specific floating-point precision mattered; Steinkraus et al. report the ATI X800 XT's 24-bit floating point as insufficient for that workload. Anchor: C14.
- **Programming friction:** Brook and Owens both frame graphics APIs as powerful but awkward for general-purpose computation. Anchors: C15-C16.

## Scene 5 - Proof and Transition

- **Measured gains:** Oh/Jung report up to about 20x on a Radeon 9700 Pro; Steinkraus/Buck/Simard report 3.3x on a GeForce 6800 Ultra. Anchors: C17-C18.
- **Abstraction bridge:** Brook compiles stream code to GPU shaders, showing the problem that Ch42's programming-model story will pick up. Anchors: C19-C20.

## Do Not Assert Without New Anchors

- Early-2000s GPUs had "thousands" of cores. Status: Red, sources.md C26.
- Pixel rendering and neural-net training are "exactly the same math." Status: Red, sources.md C25.
- Specific lab anecdotes about wasted weeks from a typo. Status: Red, sources.md C24.
