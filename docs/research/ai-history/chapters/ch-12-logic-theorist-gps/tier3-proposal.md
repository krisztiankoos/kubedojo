# Tier 3 Proposal — Chapter 12: The Logic Theorist and GPS

Per `docs/research/ai-history/READER_AIDS.md` Tier 3 workflow. Author: Claude. Reviewer: Codex (cross-family).

## Element 8 — Inline parenthetical definition (Starlight tooltip)

**SKIPPED on every chapter** per `READER_AIDS.md` until a non-destructive tooltip component lands. The collapsible *Plain-words glossary* (Tier 1) covers the same job non-destructively.

## Element 9 — Pull-quote (at most 1)

The chapter has zero verbatim quotes from primary sources. It paraphrases throughout. Possible candidates:

### Candidate A — GPS-I framing sentence (1959 paper)

The chapter at the "GPS Architecture" section paraphrases Newell, Shaw, and Simon's 1959 description: "a digital-computer program for investigating intelligent, adaptive, and creative behavior by synthesis." Source: P-1584, p. 1.

This is paraphrased in the chapter (line 84) but the verbatim wording is iconic and the surrounding paragraph does not duplicate it word-for-word. Possible insertion anchor: immediately before the "GPS represented a problem in terms of objects, operators, and differences" paragraph.

**Status: PROPOSED**, with a short annotation that names the methodological wager (build the program, then study what the construction reveals).

### Candidate B — 1961 simulation framing

The chapter (line 84) paraphrases the 1961 reframing of GPS as "a program that simulates human thought, developed in relation to protocol data from people solving problems." Source: GPS61, p. 109.

**Status: SKIPPED.** Element 9 cap is one per chapter. Candidate A serves the chapter's "performance vs. simulation" thesis better because it captures the build-and-investigate methodology that the surrounding prose unpacks; B is downstream of A in the same scene.

## Element 10 — Plain-reading asides (1–3 per chapter)

Ch12 has more genuinely symbolic-dense paragraphs than Ch11 because it walks through GPS's architectural primitives. Survey:

### Candidate C — the means-ends analysis recursion paragraph (line 88)

> "Suppose the current state and the goal state differ in some respect. Rather than search blindly through every possible operator, the system asks which operator is associated with reducing that kind of difference. If the operator cannot yet be applied, the system does not simply give up. It sets a subgoal: change the situation so the operator becomes feasible. That subgoal may generate another subgoal, creating a recursive structure of problem solving."

**Status: SKIPPED.** Although the recursion is structurally dense, the paragraph IS already a plain-reading. The author put the plain-reading work in the prose itself; an aside would only echo it.

### Candidate D — the three GPS goal types (line 90)

> "Newell and Simon's 1961 description gave GPS three broad types of goals. One goal type was to transform object A into object B. Another was to reduce a difference D between objects. A third was to apply an operator Q to an object."

**Status: PROPOSED** as a plain-reading aside candidate. The three goal types are an abstract definition stacked, but the prose does not unpack the *interaction* between them — that they are mutually generating, so a "transform" goal can call a "reduce difference" goal which calls an "apply operator" goal which calls another "transform." That cycle is the architectural punchline; an aside could state it crisply. The next paragraph (line 92) hints at this with "stack of mutually generating intentions" but does not lay it out as a worked example.

Proposed aside text:

```markdown
:::tip[Plain reading]
The three goal types are mutually generating. Transforming object A into object B can require *reducing* a particular difference; reducing that difference can require *applying* an operator; applying that operator can require another *transformation*. GPS does not run three separate procedures — it recurses through one stack of goals, each of which can summon any of the three.
:::
```

### Candidate E — the IPL chronology paragraph (line 114)

> "This is also where the IPL chronology matters. Later IPL-V documentation belongs to 1960 and should not be projected backward as if it were the language environment of the first LT implementation..."

**Status: SKIPPED.** Narrative-historical, not symbolic. The chapter already self-explains the chronology distinction.

## Summary verdict

- Element 8: SKIP (universal default).
- Element 9: 1 PROPOSED (Candidate A — GPS-I framing sentence).
- Element 10: 1 PROPOSED (Candidate D — three goal types recursion), 2 SKIPPED (C, E).

**Total: 2 PROPOSED, 3 SKIPPED.**

Author asks Codex to:
1. Verify Candidate A's verbatim wording against P-1584 p. 1 and propose a corrected text if mine is off.
2. Adjudicate Candidate D — is the three-goal-types recursion *symbolically* dense in a way the surrounding prose does not already unpack, or is it narrative density I'm misclassifying?
3. Confirm or reject the SKIPs on B, C, E.
4. Identify any paragraph I missed.
