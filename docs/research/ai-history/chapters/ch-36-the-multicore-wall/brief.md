# Brief: Chapter 36 - The Multicore Wall

## Thesis
The free ride of Moore's Law ended when CPU clock speeds hit a thermodynamic wall in the mid-2000s. To keep scaling compute, the hardware industry was forced to pivot to multicore architectures, forcing software engineering (and eventually AI) into massive parallelism.

## Scope
- IN SCOPE: The end of Dennard scaling, the heat wall (Borkar 1999), the cancellation of Intel's Tejas, the shift from single-core GHz races to multicore CPUs (Pentium D/Athlon X2).
- OUT OF SCOPE: GPUs (covered in Part 7).

## Scenes Outline
1. **The Gigahertz Race:** Intel and AMD blindly chasing higher clock speeds with architectures like NetBurst.
2. **The Melting Point:** Dennard scaling breaks down; chips get too hot. Intel famously cancels the 4GHz Tejas processor in 2004 due to thermal constraints.
3. **The Parallel Pivot:** The industry introduces dual-core chips (Pentium D, Athlon X2). Software engineers realize they must learn parallel programming.
