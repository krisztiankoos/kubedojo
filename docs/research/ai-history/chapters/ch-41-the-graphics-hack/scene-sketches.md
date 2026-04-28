# Scene Sketches: Chapter 41 - The Graphics Hack

## Scene 1: The CPU Ceiling

Open with a paper, not a fictional lab night. Steinkraus, Buck, and Simard describe a handwriting-recognition workload where better accuracy wanted more data and bigger models, but training time was already a major bottleneck. Their example of neural-network training taking more than three weeks gives the writer a concrete clock without inventing a person who discovers a typo. The scene should show why a commodity accelerator looked tempting: GPUs were cheap relative to dedicated ML hardware, already in PCs, and improving quickly.

Anchors: sources.md C01-C04.

## Scene 2: The Pixel Factory Becomes Programmable

Shift from waiting to hardware shape. The GPU is not introduced as a magical AI chip. It is introduced as a programmable graphics pipeline whose strengths happened to line up with data-parallel arithmetic: high bandwidth, many independent pixel operations, and shader programmability. The prose can use a "pixel factory" explanation as long as it stays anchored to Steinkraus's pixel-shader description and Owens's broader GPGPU survey.

Anchors: C05-C08.

## Scene 3: Linear Algebra in Disguise

This is the chapter's central scene. Oh and Jung show that the operations inside a multilayer perceptron can be represented as matrix operations. The implementation does not ask the GPU to "train a network" in ordinary programming language terms. It draws a rectangle, treats data as textures, and lets a pixel shader compute output elements. Brook gives the broader abstraction: kernels over streams. The prose should make the strangeness visible without overstating the math.

Anchors: C09-C12.

## Scene 4: The Cost of the Hack

Now complicate the victory. The GPU was powerful, but the programmer paid in transfers, formats, precision, and API contortions. Steinkraus's AGP-bus warning and ATI precision issue are useful because they are concrete, page-anchored constraints. Brook and Owens supply the broader reason: this was general computing forced through a graphics interface. The scene prevents the chapter from reading like a deterministic march from graphics cards to deep learning.

Anchors: C13-C16.

## Scene 5: Useful Proof, Insufficient Abstraction

Close on what the hack proved and what it did not. Oh/Jung's 20-fold result and Steinkraus/Buck/Simard's 3.3x result should be presented as workload-specific evidence, not a universal speed law. Brook's abstraction work shows the next pressure point: once researchers knew GPUs could help, the graphics pipeline itself became the bottleneck. End with a sparse pointer to Ch42: the next chapter is the programming model, not a replay of the hardware proof.

Anchors: C17-C20.
