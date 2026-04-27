# Scene Sketches: Chapter 12 - Logic Theorist and GPS

## Scene 1: The Paper Machine

- **Setting:** RAND/Carnegie Tech in the moment before a clean machine-run story exists.
- **Beat:** LT is first a program one can barely hand simulate. The drama is not a blinking console. It is the discovery that a stack of symbolic routines can be followed as if a person were executing a machine.
- **Narrative Use:** Opens the chapter by correcting the timeline: hand trace first, computer realization later. This gives the reader a precise boundary for the "first running symbolic-AI program" claim.
- **Evidence Anchors:** `P-868`, p. 1 for specification-not-realization; `P-868`, p. 3 for hand simulation; `CBI91`, pp. 3-9 for Newell's RAND/Shaw/Selfridge path.
- **Pedagogical Demonstration:** Show a theorem-proving program as a recipe over paper memories: read expression, compare expression, choose rule, add result to a list.

## Scene 2: The Theorem-Proving Search

- **Setting:** The sentential calculus of *Principia Mathematica*, represented as symbols, elements, memories, theorem lists, active problem lists, and routines.
- **Beat:** LT does not "understand" mathematics in a human literary sense. It manipulates expressions and searches for proofs using heuristics. The important move is treating proof discovery as structured symbol search.
- **Narrative Use:** This is the chapter's main teaching scene. It should explain why proof search can explode combinatorially and why heuristics mattered.
- **Evidence Anchors:** `P-868`, pp. 7-16 for representation machinery; `P-868`, pp. 2-3 for heuristic-vs.-algorithm framing; `P-868`, p. 8 for the *Principia Mathematica* source domain.
- **Pedagogical Demonstration:** Use one symbolic expression from `P-868` rather than inventing a new one. Avoid exact theorem-count claims until `NSS57` is anchored.

## Scene 3: Dartmouth From the Other Side

- **Setting:** Ch11's Dartmouth summer, viewed briefly from Newell and Simon's arriving research program rather than from McCarthy's naming agenda.
- **Beat:** LT is the concrete symbolic program in a summer otherwise dominated by proposals, conversations, and disciplinary positioning. But the Ch12 prose must say "demonstrated/discussed" unless a source proves live execution.
- **Narrative Use:** Cross-links Ch11 Scene 3 while preventing a duplicate Dartmouth chapter.
- **Evidence Anchors:** Ch11 `sources.md` Yellow LT-at-Dartmouth claim; `CBI91`, pp. 10-12 for Newell's recollection of Dartmouth and the still-unnamed field; `P-868`, p. 1 for post-summer IRE presentation.

## Scene 4: GPS and Means-Ends Analysis

- **Setting:** The post-LT laboratory and conference-paper environment where Newell, Shaw, and Simon try to generalize proof-search lessons.
- **Beat:** GPS turns a problem into objects, operators, differences, goals, and subgoals. The machine asks: what is different between where I am and where I want to be, what operator might reduce that difference, and what subgoal must be solved to apply it?
- **Narrative Use:** This is the conceptual payoff. It explains why GPS mattered even though it was not general intelligence.
- **Evidence Anchors:** `P-1584`, pp. 1, 3-6; `GPS61`, pp. 114-117.
- **Pedagogical Demonstration:** Use the three GPS goal types from `GPS61`: transform object A into object B; reduce difference D; apply operator Q.

## Scene 5: The Generality Ceiling

- **Setting:** The same GPS architecture seen from its limits: task vocabularies, operator tables, feasibility tests, evaluation, memory, and IPL-style implementation.
- **Beat:** GPS is general in the shape of its control structure but dependent on supplied task environments and hand-built methods. The program can be brilliant and limited at the same time.
- **Narrative Use:** Prevents triumphalist AGI framing and sets up later chapters on symbolic AI's successes and bottlenecks.
- **Evidence Anchors:** `P-1584`, p. 6 for special heuristics, programming-language effort, evaluation, and exponential possibility spaces; `GPS61`, pp. 114-117 for goal/subgoal mechanics.

## Anti-Padding Rule

If the final prose needs more length, expand the verified mechanics: memories, lists, routines, goal types, and means-ends analysis. Do not add invented Dartmouth dialogue, unsourced typewriter drama, unverified theorem counts, or claims that GPS was close to general intelligence.
