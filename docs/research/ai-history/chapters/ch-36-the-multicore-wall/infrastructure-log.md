# Infrastructure Log: Chapter 36 — The Multicore Wall

What the computing infrastructure of each scene actually looked like — process node, transistor count, clock, power envelope, cache size — anchored to verified primary sources. Each entry references at least one Green claim in `sources.md`.

## Scene 1 — The Gigahertz Religion (1999–2003)

**Reference architecture: Intel Pentium 4 (NetBurst).**

- **Manufacturing process:** 180 nm at introduction (2000), 130 nm by 2002, 90 nm by 2004 (Prescott). Borkar & Chien 2011 p.68 figure 2 maps the Pentium-family generation transitions through this period.
- **Clock speed trajectory:** Intel chips reached 2 GHz in August 2001; the trend visibly flattened "around the beginning of 2003" (Sutter 2005 §"Obstacles, and Why You Don't Have 10GHz Today"). By the time of Sutter's writing in late 2004, mainstream parts had reached 3.4 GHz.
- **Architectural intent:** the NetBurst architecture was deliberately designed around a deep pipeline so that operating frequency could keep climbing. Borkar & Chien 2011 p.68 figure 2 explicitly annotates the Pentium-4-to-Core transition as "Deep pipeline → Back to non-deep pipeline" — the post-pivot architectural retreat.
- **Power and thermal envelope:** the contemporaneous understanding (per Borkar 1999 in *IEEE Micro* 19(4), cited via Berkeley View 2006 §4.1) was that further frequency scaling at this trajectory would push power density past manageable limits. The specific physical mechanisms named by Sutter 2005 in retrospect: "heat (too much of it and too hard to dissipate), power consumption (too high), and current leakage problems."

**Reference architecture: server multicore precedents.**

- **IBM POWER4 (2001).** First commercial dual-core chip in mass production. Cited by Sutter 2005 ("multicore is available on current PowerPC and Sparc IV processors") and Asanovic et al. 2006 p.4. The chapter does not narrate its development; it appears as the existing-server-multicore baseline.
- **Sun UltraSPARC IV (2004) and the in-development Niagara / UltraSPARC T1.** Cited by the same two sources. Niagara would ship later in 2005 with 8 cores per die.

## Scene 2 — The Cancellation (May 7, 2004)

**Reference architecture: Tejas (cancelled Pentium 4 successor) and Jayhawk (cancelled Xeon successor).**

- **Process node:** 90 nm. (Vance, *The Register*, 2004-05-07: both processors "were once slated to arrive in the second quarter of next year and be built on a 90nm manufacturing process.")
- **Originally scheduled launch:** Q2 2005.
- **Sample clock and power:** ten engineering samples, all running at 2.8 GHz, drawing approximately 150 W — about 50% more power than the contemporaneous Prescott Pentium 4 at the same clock (Shimpi, *AnandTech*, 2004-01-09). The chapter must distinguish this *sample-level* fact from the Pentium 4 *line target* of 4 GHz that Intel separately abandoned in fall 2004.
- **Replacement schedule:** Intel's confirmed dual-core desktop was now scheduled for 2005, "12 to 18 months ahead of previous schedules" (Vance, *Register*, 2004-05-07).
- **Replacement parts (announced May 2004, shipped 2005):**
  - **Pentium D** — the mainstream desktop dual-core part. Sutter 2005 §"TANSTAAFL" describes its design honestly: "Intel's initial entry basically just glues together two Xeons on a single die." Specific ship date Yellow.
  - **Server replacement plan:** Vance reports the Nocona Xeon would arrive shortly, then a dual-core server part would replace it (instead of Jayhawk); Potomac (single-core multiprocessor) remained on schedule for first-half 2005, followed by dual-core Tulsa "in late 2005 or early 2006."

## Scene 3 — Sutter's Diagnosis (December 2004 / March 2005)

No new hardware infrastructure introduced in this scene. The infrastructure being described is the same as Scene 2 plus the cross-vendor multicore landscape Sutter named:

- **PowerPC and Sparc IV** — already shipping multicore as of late 2004.
- **Intel and AMD x86** — multicore "coming in 2005" per Sutter's contemporaneous text.

## Scene 4 — The Mainstream Pivot (2005)

**Reference architectures: first mainstream x86 dual-core desktop parts.**

- **Intel Pentium D** — manufactured on 90 nm (the same Prescott-derived process Tejas would have used). Two physical dies on a single package per Sutter's "glues together two Xeons" characterization. Specific ship date and SKU details remain Yellow pending primary press-release verification.
- **AMD Athlon 64 X2** — manufactured on 90 nm SOI. More architecturally integrated than Pentium D per Sutter's contemporaneous design judgment. Specific ship date Yellow.
- **Sun UltraSPARC T1 (Niagara)** — released later in 2005, 8 cores per die, primarily a server/throughput part. Named by Asanovic et al. 2006 p.4 alongside POWER4 as the precedents Intel "followed."

## Scene 5 — The Berkeley View and Borkar's Retrospective (2006–2011)

No new hardware in scene; the infrastructure is the diagnosis of the regime.

**The "Brick Wall" decomposition** (Asanovic et al. 2006 pp.5–6):

- **Power Wall (CW pair #1):** "Power is expensive, but transistors are 'free'. That is, we can put more transistors on a chip than we have the power to turn on."
- **Memory Wall (CW pair #7):** "Modern microprocessors can take 200 clocks to access Dynamic Random Access Memory (DRAM), but even floating-point multiplies may take only four clock cycles." (After Wulf & McKee 1995.)
- **ILP Wall (CW pair #8):** "There are diminishing returns on finding more ILP." (After Hennessy & Patterson 2007.)
- **Sum (CW pair #9):** "Old CW: Uniprocessor performance doubles every 18 months. New CW is Power Wall + Memory Wall + ILP Wall = Brick Wall."

**Quantitative anchor for the regime change** (Asanovic et al. 2006 pp.5–6, CW pair #9 commentary):
> "In 2006, performance is a factor of three below the traditional doubling every 18 months that we enjoyed between 1986 and 2002. The doubling of uniprocessor performance may now take 5 years."

**Borkar's 2011 retrospective infrastructure projection** (Borkar & Chien 2011 p.71):
- Desktop power envelope: ~65 W in a ~100 mm² die.
- 45 nm node (2008) example: 50 million logic transistors + 6 MB cache fit in the 65 W envelope; this matched the dual-core Core 2 Duo on 45 nm.
- Beyond that point: "If chip architects simply add more cores ... and operate the chips at the highest frequency the transistors and designs can achieve, then the power consumption of the chips would be prohibitive."

**The single-thread floor** (Borkar & Chien 2011 p.72):
> "single-thread performance has already leveled off, with only modest increases expected in the coming decades. Multiple cores and customization will be the major drivers for future microprocessor performance."

## Cross-Scene Constants

- **The Dennard-scaling regime** (the framework whose breakdown the chapter narrates) is summarized at Borkar & Chien 2011 p.68: "the transistor dimensions are scaled by 30% (0.7x), their area shrinks 50%, doubling the transistor density every technology generation ... performance increases by about 40% (0.7x delay reduction, or 1.4x frequency increase) ... supply voltage is reduced by 30%, reducing energy by 65%, or power (at 1.4x frequency) by 50%." This is the recipe that, by the mid-2000s, stopped delivering its full set of three benefits simultaneously.
- **The leakage-current floor** (Borkar & Chien 2011 p.71): "the transistor is not a perfect switch, leaking some small amount of current when turned off, increasing exponentially with reduction in the threshold voltage. ... a substantial portion of power consumption is due to leakage. To keep leakage under control, the threshold voltage cannot be lowered further."

## Out of Scope (do not narrate as infrastructure here)

- GPU architectures (Part 7).
- Custom AI silicon: TPU, Trainium, Cerebras, etc. (Ch49).
- Specific cache-coherence protocols, NUMA topologies, or multi-socket server design beyond what Sutter 2005 names.
- Mobile multicore (Apple A4 etc., post-2010); the chapter narrates the desktop/server pivot and stops there.
