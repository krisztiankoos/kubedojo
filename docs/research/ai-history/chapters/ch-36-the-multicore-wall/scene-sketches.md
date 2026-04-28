# Scene Sketches: Chapter 36 — The Multicore Wall

Five scenes, mapped 1:1 to the Prose Capacity Plan layers in `brief.md`. Each scene cites the specific anchored claims from `sources.md` it depends on.

## Scene 1 — The Gigahertz Religion (600–900 words)

**Anchored to Plan layer 1.**

**Action.** Open with the marketing reality of the late-1990s and early-2000s consumer PC market: clock speed was *the* number on the box. CPUs were sold to non-technical buyers as a single-axis product, and Intel's NetBurst architecture, introduced in 2000, was deliberately designed to keep climbing the GHz axis. The GHz number was the contract between Intel's silicon roadmap and the sales floor.

Then, with that frame established, pull on the contrary thread. In 1999, an Intel engineer named Shekhar Borkar published a paper at *IEEE Micro* — Intel's own technical-society outlet — warning that the technology-scaling recipe driving the GHz race would push power density past manageable limits. Three years earlier, in 1996, Kunle Olukotun's Stanford group had argued at ASPLOS that the architectural alternative — many smaller cores rather than one bigger one — was already on the table. The early-warning record was not ambiguous; it was on record from inside Intel itself and from inside the field's most prestigious architecture conference. The industry kept climbing the GHz axis anyway.

Sutter would mark the visible inflection point in early 2003 — the year the trend line stopped rising at the rate it had risen for thirty years before. But nobody bought a 2003 PC because of an inflection point; consumers bought 2 GHz Pentium 4s in August 2001 and 3.4 GHz Pentium 4s in 2004, and the GHz number kept advertising a future that physics was already reluctant to deliver.

**Anchored claims (from `sources.md` Scene-Level Claim Table):**
- "For roughly thirty years before the mid-2000s, mainstream CPUs delivered exponential single-thread performance growth driven by Moore's Law and proportional clock-speed increases." (Green; Sutter 2005 §"The Free Performance Lunch"; Borkar & Chien 2011 p.67.)
- "Intel's NetBurst architecture, introduced in 2000, was deliberately designed around a deep pipeline so that operating frequency could keep climbing." (Green; Sutter 2005; Borkar & Chien 2011 p.68 figure annotation.)
- "In 1999 Intel engineer Shekhar Borkar warned in an *IEEE Micro* paper that continued technology scaling would push CPU power density past manageable limits." (Green for the existence-and-warning chain; Asanovic et al. 2006 §4.1 + references list.)
- "In 1996 a Stanford architecture group led by Kunle Olukotun argued at ASPLOS ..." (Yellow for content; Green for existence; Olukotun et al. 1996 DOI.)
- The 2 GHz / 3.4 GHz / "early 2003 inflection" timeline. (Green; Sutter 2005 §"Obstacles ...".)

**Density target:** 600–900 words. Use 6–8 verified factual claims; do not pad with generic Moore's-Law explanation that the 1980s/90s CPUs chapter would already have delivered.

## Scene 2 — The Quiet Cancellation (800–1,100 words)

**Anchored to Plan layer 2.**

**Action.** Reconstruct May 7, 2004 from *The Register*'s same-evening dispatch, in chronological prose. The cancellation was confirmed late on a Friday: Intel told Ashlee Vance that both Tejas and Jayhawk were being killed. The reason given on the record was not thermal — it was strategic: "single core chips just don't do it for the company anymore." The line that the chapter must pull verbatim is the spokesman's: "We are accelerating our dual-core schedule for 2005."

Add the structural facts from the same article: both cancelled chips were 90 nm parts, originally due Q2 2005; the dual-core desktop schedule had just been pulled "12 to 18 months ahead of previous schedules." Then introduce the contrary thermal evidence — but as a separate fact stream, not a collapsed cause-and-effect. Four months earlier, *AnandTech* had published leaked engineering-sample data showing Tejas at 2.8 GHz consuming roughly 150 W (about 50% more than Prescott). This is the fact that lets the chapter explain *why* a cancellation framed as "strategic" was actually a thermal surrender — without overclaiming Intel's own internal reasoning.

The scene's sharp turn: contrast the on-record framing (single-core economics) with the off-record reality (the 4 GHz Pentium 4 line target, separately abandoned in fall 2004 per Sutter 2005). The cancellation was not about a 4 GHz chip; it was about the realization that the entire Pentium 4 line was no longer going to keep climbing. Tejas was the last credible push, and it died because the only way to ship it was at thermal numbers nobody could put in a desktop chassis.

End the scene with what the cancellation immediately accomplished: the dual-core x86 future, which had been a 2006–2007 problem on the previous roadmap, was now a 2005 problem. Intel had given itself one year to ship a part that would not need 4 GHz to compete.

**Anchored claims:**
- "On May 7, 2004 Intel confirmed the cancellation of Tejas (Pentium 4 successor) and Jayhawk (Xeon successor) ..." (Green; Vance, *Register*, 2004-05-07.)
- "Intel's on-record framing: 'We are accelerating our dual-core schedule for 2005.'" (Green for the journalistic record.)
- "The cancelled Tejas and Jayhawk were 90nm parts originally slated for Q2 2005; the cancellation pulled Intel's mainstream dual-core schedule '12 to 18 months ahead of previous schedules.'" (Green; Vance 2004-05-07.)
- "Pre-cancellation Tejas engineering samples were running at 2.8 GHz at approximately 150 W ..." (Green; Shimpi, *AnandTech*, 2004-01-09; Sutter 2005 §"Obstacles ..." for the parallel 4 GHz line-target abandonment.)

**Density target:** 800–1,100 words. This is the chapter's load-bearing event scene; the four Green primary anchors here will carry the chapter even if other layers stay tight.

## Scene 3 — The Free Lunch Is Over (800–1,100 words)

**Anchored to Plan layer 3.**

**Action.** Walk through Sutter's article in the order it builds its argument. Begin with Sutter's three-axis framing of *historical* CPU performance gains — clock speed, execution optimization, cache — because that framing is the load-bearing structural device of his essay. Then state the explicit physical-issue list: heat, power consumption, current leakage. Then state the sentence that did the most work in 2005 to convince software developers this was real: "CPU performance growth as we have known it hit a wall two years ago. Most people have only recently started to notice."

Pivot to Sutter's three-axis future: hyperthreading, multicore, cache. Important: Sutter named this future without yet seeing the dual-core x86 parts that would ship later in 2005; his contemporaneous knowledge was that PowerPC and Sparc IV had multicore already and that Intel and AMD were committing to it. The chapter should preserve that contemporaneous framing.

Then the chapter's load-bearing direct-quote sentence — the one that the software industry actually read in 2005 and acted on: "single-threaded programs are likely not to get much faster any more for now except for benefits from further cache size growth." That single sentence reframed every C++ codebase on Earth as legacy.

Close the scene with Sutter's structural metaphor — the buffet — and his explicit framing of concurrency as the next OOP-scale revolution. Be careful not to overstate what Sutter claimed. He did not claim concurrency would be *bigger* than OOP; he claimed it would be of the same order of magnitude in scope and learning-curve cost.

**Anchored claims:**
- "Sutter identified three physical issues that had ended the GHz race ..." (Green; Sutter 2005 §"Obstacles ...".)
- "Sutter explicitly told software readers that single-threaded code would no longer get faster ..." (Green; Sutter 2005 §"What This Means For Software".)
- "In December 2004 Herb Sutter published 'The Free Lunch Is Over' ... naming the multicore pivot as a software-industry inflection comparable in magnitude to the OO revolution." (Green; Sutter 2005 §"What This Means For Software".)

**Density target:** 800–1,100 words. The article is its own anchor; the chapter should quote three to five short verbatim passages.

## Scene 4 — The Mainstream Pivot (500–800 words)

**Anchored to Plan layer 4.**

**Action.** A compact, declarative scene. In 2005 Intel shipped Pentium D and AMD shipped Athlon 64 X2, and the mainstream x86 desktop was a dual-core machine for the first time. Sutter's contemporaneous design read — that Pentium D was essentially two Xeon dies on a package, while Athlon 64 X2 was more architecturally integrated — should be quoted because it is the rare contemporary judgment that aged well.

Add the server precedents that Sutter and Berkeley View both name (IBM POWER4 from 2001, Sun Niagara coming later in 2005), then immediately stop expanding the cast. The scene's job is to mark the transition, not to catalog every multicore part of the year.

End the scene by acknowledging what the chapter does *not* fully anchor: the exact ship dates, the SKU lineup, the Intel/AMD primary press-release voices. The chapter's evidence base supports a clear year-level statement about the 2005 mainstream-x86 dual-core arrival; it does not yet support a date-level statement.

**Anchored claims:**
- "In 2005 the mainstream x86 desktop line shipped its first dual-core parts: Intel's Pentium D and AMD's Athlon 64 X2." (Green at year-level; Sutter 2005 §"TANSTAAFL"; Asanovic et al. 2006 p.4. Yellow at exact-date-level.)
- "Sutter's contemporaneous read of the two designs ..." (Green; Sutter 2005 §"TANSTAAFL".)
- "Multicore CPUs existed in the server market before mainstream x86 ..." (Green; Sutter 2005 + Asanovic et al. 2006 p.4.)

**Density target:** 500–800 words. Compact by design; the chapter should not pad this scene because the Yellow ship-date claims would force overreach.

## Scene 5 — Naming the Wall (900–1,200 words)

**Anchored to Plan layer 5.**

**Action.** The intellectual close. December 2006: a UC Berkeley group published a 56-page technical report that did three things the chapter has been building up to.

First, it named the inflection in plain language: "The recent switch to parallel microprocessors is a milestone in the history of computing." (Asanovic et al. 2006 p.1.) Second, it formalized the underlying constraints — Power Wall, Memory Wall, ILP Wall — and combined them into "Brick Wall," explicitly arguing that uniprocessor doubling no longer ran on an 18-month clock. Third, it cited Tejas's cancellation and Borkar 1999 as the *industrial* evidence for the academic claim, closing the loop between the two streams the chapter has been narrating.

The chapter should walk readers through the Old-CW / New-CW pairs that matter most: pair #11 (clock frequency → parallelism), pair #9 (Power Wall + Memory Wall + ILP Wall = Brick Wall), pair #1 (transistors are now free, power is expensive). These are the headlines; do not list all 12 pairs.

Then bring in Borkar's own 2011 retrospective — the same author who in 1999 had warned this was coming, now writing seven years after the cancellation he helped justify. The CACM 2011 abstract names the new normal directly: "the frequency of operations will increase slowly, with energy the key limiter of performance, forcing designs to use large-scale parallelism, heterogeneous cores, and accelerators." (Borkar & Chien 2011 p.67.) And the body of the paper documents the specific compromise: "single-thread performance has already leveled off, with only modest increases expected in the coming decades." (p.72.) This is Borkar saying, with seven years of evidence, that the regime that ended in May 2004 has not come back.

Close on the through-line — but tightly. By 2006, mainstream software developers had spent eighteen months learning that "single-threaded code will not get faster" was now an architectural fact, not a temporary inconvenience. The next decade of compute scaling would be built on top of that fact, not against it. The chapter should explicitly *not* anticipate Part 7's GPU story or Ch49's custom silicon. The forward link is one sentence: a world that has just learned to write parallel software for two and four cores is, ten years later, prepared to write parallel software for thousands. The Multicore Wall did not cause that — it cleared the cultural ground for it.

End with the honesty close. Some of what came after is anchored elsewhere in the book; some will need to be anchored on its own evidence. The Multicore Wall chapter does only its own job.

**Anchored claims:**
- "The December 2006 *View from Berkeley* technical report named the post-2004 regime as 'Power Wall + Memory Wall + ILP Wall = Brick Wall' ..." (Green; Asanovic et al. 2006 pp.5–6.)
- "The *View from Berkeley* explicitly cited Tejas's cancellation and Borkar 1999 ..." (Green; Asanovic et al. 2006 §4.1 p.~21.)
- "Borkar & Chien wrote in 2011 that 'the frequency of operations will increase slowly ...'" (Green; Borkar & Chien 2011 p.67.)
- "Borkar & Chien 2011 ... 'single-thread performance has already leveled off ...'" (Green; Borkar & Chien 2011 p.72.)
- "The multicore pivot was not driven by AI demand." (Green-by-absence; Sutter 2005 silence on ML; Asanovic et al. 2006 application list omits ML as a motivating workload.)

**Density target:** 900–1,200 words. The longest scene by design — it is the chapter's intellectual close and earns more space than the others, with three Green primary anchors.

## Scene Density Summary

| Scene | Plan Layer | Words | Green Anchors | Yellow Anchors |
|---|---|---|---|---|
| 1 | 1 | 600–900 | 4 | 1 (Olukotun 1996 content) |
| 2 | 2 | 800–1,100 | 4 | 0 |
| 3 | 3 | 800–1,100 | 3 | 0 |
| 4 | 4 | 500–800 | 3 | 1 (exact ship dates) |
| 5 | 5 | 900–1,200 | 5 | 0 |
| **Total** | — | **3,600–5,100** | **19** | **2** |

The chapter is built so that no scene depends on a Yellow anchor for its load-bearing claim.
