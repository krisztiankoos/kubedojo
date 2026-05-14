# Engineering Craft — Curriculum Gap Brief (#1186)
## Reading Code / Debugging / Code Review / RFCs

Captured 2026-05-14. Stage-1 research brief.

This brief identifies a curriculum gap in "Engineering Craft" — teachable, discipline-oriented
skills that bridge the gap between knowing a language and operating effectively in a professional
engineering organization. KubeDojo covers leadership workflows (postmortems, ADRs, stakeholder
communication) and specific technologies in depth, but has no content that teaches the daily
mechanics of reading an unfamiliar codebase, applying a scientific method to debugging, or
conducting a high-signal code review. These skills are adjacent to — but distinct from — the
existing engineering leadership modules.

---

## §A. Source Summary

### John Ousterhout — "A Philosophy of Software Design" (Yaknyam Press, 2018)

**Core argument.** Complexity is anything that makes a system hard to understand or modify.
Ousterhout's thesis is that complexity is the enemy, and the designer's job is to manage it —
not by writing clever code, but by creating **deep modules** (simple interfaces over complex
logic) and ruthlessly eliminating **shallow modules** (thin wrappers that add indirection
without value).

**Teachable takeaways for a curriculum module:**

1. *Detecting complexity by feel.* Ousterhout names three symptoms: change amplification
   (a single change forces edits in many places), cognitive load (readers must hold too much
   context in mind), and unknown unknowns (you don't know what you need to know). Teaching
   engineers to name these symptoms before reaching for a solution is a concrete, actionable
   skill. A lab exercise can use a real Kubernetes operator codebase and ask: "Where do you
   feel friction? Which of the three symptoms is it?"

2. *Designing it twice.* Ousterhout argues that the first interface you design is almost always
   wrong. The second design, forced through discipline, is usually better. For a module on code
   reading, this principle inverts: when you read unfamiliar code, assume the first mental model
   you build is incomplete. Verifying a mental model by "designing it twice" — drawing the
   architecture, then searching for where it breaks — is a transferable technique.

3. *Documentation as design tool.* Comments that explain *why* something exists (not what it
   does) are a signal of the designer's original intent. This gives code readers a heuristic:
   look for the design comments first; they are the compressed history of the module's purpose.

---

### Diomidis Spinellis — "Code Reading: The Open Source Perspective" (Addison-Wesley, 2003)

**Core argument.** Engineers spend more time reading code than writing it, but reading is
almost never formally taught. Spinellis provides a systematic approach: identify entry points,
trace data flow from input to output, locate the "heart" of the system (the functions that
all paths pass through), and use tests as executable documentation.

**Teachable takeaways for a curriculum module:**

1. *Entry-point-first navigation.* Every codebase has a canonical start: a `main()`, a
   Kubernetes controller's `Reconcile()`, a webhook handler. Spinellis teaches starting there
   and following the execution path forward rather than reading files alphabetically or searching
   for "the interesting bit." This is a skill gap that shows up immediately when junior engineers
   join a team — they grep for keywords; senior engineers trace execution.

2. *Data structure primacy.* Before following control flow, understand what the key data
   structures are. In a Kubernetes controller, the `Reconcile` loop is unreadable without first
   understanding the `CR` spec and the `Status` struct. Spinellis argues the data structures
   *are* the design; control flow is just manipulation of those structures.

3. *Tests as specification.* When you don't understand what a function should do, read its
   tests first. Tests are executable documentation that doesn't lie. This is a practical
   technique junior engineers often skip because they don't value tests as comprehension tools.

4. *The "break things" technique.* Intentionally modify something small and observe what fails.
   The failure pattern reveals the module's dependencies and invariants more reliably than any
   documentation. This is a legitimate, systematic technique — not recklessness.

---

### Andrew Hunt and David Thomas — "The Pragmatic Programmer: Your Journey to Mastery" (Addison-Wesley, 20th Anniversary Edition, 2019)

**Core argument.** Debugging is not guessing. It is the scientific method applied to software:
reproduce the defect, form a hypothesis about the cause, design an experiment to isolate it,
verify or refute the hypothesis, repeat. "Don't Assume, Prove" is their debugging axiom.

**Teachable takeaways for a curriculum module:**

1. *Reproduce first, always.* If you cannot reproduce a bug on demand, you cannot verify a fix.
   Many engineers skip this step and go straight to guessing. Establishing a deterministic
   reproduction is itself a meaningful achievement — it eliminates 80% of the hypothesis space.

2. *Rubber duck debugging.* Explaining the problem aloud to a non-expert (or a rubber duck)
   forces you to articulate assumptions you have been holding implicitly. The act of verbal
   articulation reveals the assumption that is wrong. This is a learnable, practised technique —
   not a joke.

3. *Binary search debugging.* When a bug appeared at an unknown point in history, `git bisect`
   is the tool. Hunt and Thomas would phrase this as: when you don't know *when* the breakage
   happened, binary search the history. Teaching bisection as a debugging technique — including
   the mental model of bisecting a hypothesis space, not just a git log — is directly applicable
   to Kubernetes cluster state changes.

4. *Minimum reproduction.* Isolate the failing case to the smallest possible program or
   configuration that still triggers the defect. This forces precision in the hypothesis.
   In a Kubernetes context, the minimum reproduction might be: a single Pod spec, a single
   NetworkPolicy, a single Helm values file. The skill is knowing how to strip context without
   losing the bug.

5. *Root cause vs symptom discipline.* A bug is a symptom of a deeper failure in the design or
   the process. Fixing the crash is not the same as fixing what caused the crash to be possible.
   This principle mirrors the blameless postmortem philosophy already in KubeDojo (module 1.2),
   but applied to individual debugging sessions rather than post-incident analysis.

---

### Joel Spolsky — "The Joel Test" and Code Review Essays (*Joel on Software*)

**Core argument.** High-quality engineering depends on systematic peer review as both a quality
gate and a knowledge-transfer mechanism. Spolsky distinguishes between style reviews (best
handled by automated linters) and design/correctness/teachability reviews (the human craft).
Code review is the most effective tool for spreading architectural knowledge and standards
across a team. His Joel Test (published 2000) remains a relevant baseline for evaluating
engineering team health.

**URL**: https://www.joelonsoftware.com/2000/08/09/the-joel-test-12-steps-to-better-code/

**Teachable takeaways for a curriculum module:**

1. *Review scope discipline.* A code review that comments on variable names when the
   architecture is wrong has its priorities inverted. Teach engineers to review in layers:
   first correctness and design, then naming and clarity, last style (if not automated).
   Most engineers default to commenting on what they can see immediately — the surface — rather
   than what requires reasoning to evaluate.

2. *Feedback as a teaching act.* Every comment is an opportunity to transfer knowledge.
   "This will cause a nil pointer dereference under concurrent access" teaches the reader to
   think about concurrency. "Use `x` instead of `y`" teaches nothing. Spolsky's implicit
   argument is that reviewers should optimize for the author's long-term growth, not just the
   correctness of this particular PR.

3. *The "approve with nits" threshold.* Blocking a correct, well-designed PR on stylistic
   grounds is engineering culture dysfunction. Teaching when to approve vs. when to block is
   a social and technical skill that is almost never explicitly taught.

4. *Review as onboarding.* New team members should read PRs before writing any code.
   A team's PR history is the most honest representation of how the team actually works —
   more truthful than documentation, more detailed than ADRs.

---

### Written RFC Culture — Engineering Practice

**Source.** The practice of using written RFCs (Requests for Comments) as a pre-decision
consensus mechanism is well-established in major engineering organizations. Rust (github.com/rust-lang/rfcs),
Python (peps.python.org), and IETF (rfc-editor.org) maintain public archives. HashiCorp, Stripe,
and Google's eng culture writings describe internal RFC processes as standard practice for
architectural decisions. This brief treats the RFC as a cross-organization discipline, not
the property of any single codebase.

**Teachable takeaways for a curriculum module:**

1. *RFC vs ADR distinction.* An RFC is a *pre-decision* vehicle: it proposes, solicits
   dissent, explores alternatives, and forces the author to articulate trade-offs before any
   code is written. An ADR is a *post-decision* record. KubeDojo's module 1.4 (ADRs) introduces
   this distinction in Part 5 but does not teach RFC *writing* as a standalone skill. The RFC
   template — Summary, Motivation, Detailed Design, Alternatives Considered, Open Questions —
   is a teachable writing framework.

2. *Writing for disagreement.* The "Alternatives Considered" section of an RFC is not a
   formality. It is the place where the author demonstrates that they understand the trade-off
   space and have engaged with the strongest counterarguments. Engineers who skip this section
   typically receive the harshest review responses, because reviewers will raise the alternatives
   anyway.

3. *Async-first decision-making.* RFCs distribute decision-making across time zones and skill
   levels in ways that synchronous design reviews cannot. A junior engineer can comment on an
   RFC; they often cannot speak up in a real-time design meeting. This is a structural argument
   for written consensus processes in distributed teams.

---

## §B. Curriculum Slot Proposal

### Coverage Map: Existing KubeDojo Modules

The following modules in the platform foundations and prerequisites tracks were audited for
overlap with the engineering-craft gap. Paths are relative to `src/content/docs/`.

| Track / Module | Path | Covers | Engineering-Craft Gap |
|---|---|---|---|
| **Engineering Leadership** | `platform/foundations/engineering-leadership/` | | |
| 1.2 Blameless Postmortems | `module-1.2-postmortems.md` | Post-incident root cause analysis, 5 Whys, Fishbone, blameless culture | Real-time debugging discipline; systematic hypothesis formation during an active investigation |
| 1.4 ADRs & Technical Writing | `module-1.4-adrs.md` | ADR format (context / options / decision / consequences), writing for audiences, RFC-vs-ADR distinction (Part 5, introductory) | RFC *writing* as a full skill; mechanics of high-signal code review; teaching-oriented review feedback |
| 1.6 Mentorship & Multiplying Impact | `module-1.6-mentorship.md` | Code review as a mentorship activity (mentioned), coaching techniques, knowledge sharing culture | Code review mechanics: how to structure feedback, what to review in what order, when to approve vs block |
| **Systems Thinking** | `platform/foundations/systems-thinking/` | | |
| 1.2 Feedback Loops | `module-1.2-feedback-loops.md` | Reinforcing and balancing loops, retry storms, circuit breakers | "The debugging loop" as an applied concept: reproduce → hypothesize → isolate → verify |
| 1.3 Mental Models for Operations | `module-1.3-mental-models-for-operations.md` | Operational mental models (Cynefin, OODA, constraint theory) | Mental models for *source code navigation*: entry-point-first, data-structure-first, tests-as-spec |
| **Prerequisites** | `prerequisites/` | | |
| Git Basics, Git Deep Dive | `git-basics`, `git-deep-dive/` | Git workflows, PRs, remotes | Code review discipline within PRs; `git bisect` as a debugging tool |
| Modern DevOps | `modern-devops/module-1.1-infrastructure-as-code.md` | IaC principles, CI/CD concepts | Reading and navigating complex IaC codebases; debugging IaC-specific failures |

**Summary of the gap.** No module in the curriculum teaches:
- Systematic source code navigation (entry-point-first, data-structure-first reading)
- Debugging as a hypothesis-driven discipline during active investigation
- Code review mechanics — what layers to review in what order, how to frame teaching feedback
- RFC writing as a standalone skill (the ADRs module introduces the concept but does not teach the format or the social dynamics of RFC-based consensus)

---

### Proposed Output Shape: Mini-Arc (3 Modules)

A mini-arc titled **"The Craft of Engineering"** sitting at
`src/content/docs/platform/foundations/engineering-craft/` is the recommended shape.

**Rationale over a single module.** Three reasons:

1. *Different lab environments.* Code reading requires a large, live codebase to navigate.
   Debugging requires a broken system to fix. Code review requires a PR with realistic defects
   to assess. These lab environments cannot be compressed into a single exercise sequence.

2. *Different learner readiness gates.* A reader who cannot yet navigate an unfamiliar
   codebase will not be able to identify design-level issues in a code review. The mini-arc
   enforces a natural prerequisite chain.

3. *Discoverability.* Platform engineers searching for "how do I review code well" should find
   a dedicated module, not a sub-section buried in a mentorship module.

---

#### Module 1: The Art of Code Reading

- **Slug**: `module-1.1-code-reading`
- **Proposed path**: `platform/foundations/engineering-craft/module-1.1-code-reading.md`
- **Prerequisite**: Systems Thinking module 1.3 (Mental Models for Operations)
- **Estimated word count**: 3,500 words

**Section outline:**

1. **Why You Read More Than You Write** — quantitative case: engineering time allocation
   studies; reading-to-writing ratio in mature codebases; what this implies for skill development

2. **Entry-Point Navigation** — finding `main()`, `Reconcile()`, webhook handlers; following
   the execution path forward rather than grepping for keywords; why experienced engineers
   orient before diving

3. **Data Structures First** — in Kubernetes controllers: understand the CR spec and Status
   struct before reading the reconcile loop; Ousterhout's insight that data structures *are*
   the design

4. **Tracing Execution and Data Flow** — IDE cross-referencing vs grep-first vs call-graph
   tools; following a single request from ingress to storage; building a written map

5. **Tests as Executable Specification** — reading tests before reading implementation;
   why tests don't lie about expected behavior; the "break something small" technique for
   validating a mental model

6. **Detecting Complexity** — Ousterhout's three symptoms (change amplification, cognitive
   load, unknown unknowns); how to name what you feel, not just feel it; using this vocabulary
   in code review

7. **Lab Exercise** — Navigate the `cert-manager` controller source from the `CertificateRequest`
   reconciler entry point. Identify the key data structures, the heart of the system, and one
   example of each of Ousterhout's three complexity symptoms.

---

#### Module 2: The Debugging Discipline

- **Slug**: `module-1.2-debugging-discipline`
- **Proposed path**: `platform/foundations/engineering-craft/module-1.2-debugging-discipline.md`
- **Prerequisite**: Module 1.1 (Code Reading), Engineering Leadership 1.2 (Postmortems)
- **Estimated word count**: 4,000 words

**Section outline:**

1. **Debugging Is Not Guessing** — the scientific method applied to software: the four-step
   loop (reproduce, hypothesize, isolate, verify); why "try things and see" fails at scale

2. **Reproduce First, Always** — establishing a deterministic reproduction as the first
   deliverable; what counts as a minimal reproduction; the failure modes of skipping this step

3. **Forming Useful Hypotheses** — how to constrain the hypothesis space; working backwards
   from the symptom; the "last known good" principle; using git history as evidence

4. **Isolation Techniques** — binary search via `git bisect`; minimal reproduction via
   progressive pruning; log-based tracing vs interactive debuggers; when each is appropriate

5. **The Social Debugger** — rubber duck debugging as a practised technique (not a joke);
   when to escalate vs when to keep digging; pair debugging for genuinely stuck cases

6. **Root Cause vs Symptom** — the difference between fixing the crash and fixing what made
   the crash possible; connecting to postmortem culture; when to file a follow-up issue vs
   fix it now

7. **Lab Exercise** — A broken `kind` cluster is provided with a deliberate defect in a
   NetworkPolicy configuration causing intermittent pod communication failures. Apply the
   four-step debugging loop to isolate and document the root cause.

*Note on overlap.* Module 1.2 (Postmortems) covers 5 Whys and Fishbone for post-incident
analysis. This module teaches the same hypothesis-formation discipline applied to active,
real-time debugging. The framing is distinct: postmortems start with "what happened";
debugging starts with "why is this happening right now."

---

#### Module 3: Code Review and the RFC Process

- **Slug**: `module-1.3-reviews-and-rfcs`
- **Proposed path**: `platform/foundations/engineering-craft/module-1.3-reviews-and-rfcs.md`
- **Prerequisite**: Module 1.1 (Code Reading), Engineering Leadership 1.4 (ADRs)
- **Estimated word count**: 4,500 words

**Section outline:**

1. **What Code Review Is (and Is Not)** — review is not style-checking (that's what linters
   are for); review is correctness, design, and knowledge transfer; the Joel Test on peer review
   as a team-health baseline

2. **Reviewing in Layers** — correctness first (does it work?), design second (is the
   abstraction right?), clarity third (will future readers understand it?), style last (and
   only if not automated); why the order matters and what happens when it is inverted

3. **High-Signal Feedback** — how to frame a comment as a question vs a directive; citing
   evidence ("this will race under concurrent access because..."); teaching vs nitpicking;
   when "blocking" is appropriate vs blocking the author's time

4. **The Approve Threshold** — when to approve a PR that isn't perfect; the "approve with
   nits" pattern; why blocking on style while design is correct is a culture failure

5. **Review as Onboarding** — reading a team's PR history before writing code; review as
   the most honest representation of team standards; building reading review into onboarding plans

6. **The RFC Process** — RFC template (Summary, Motivation, Detailed Design, Alternatives
   Considered, Open Questions, Timeline); writing "Alternatives Considered" as a signal of
   intellectual honesty; RFC vs ADR lifecycle (pre-decision vs post-decision); the module
   1.4 ADR format handles post-decision records — this section teaches the pre-decision phase

7. **Lab Exercise** — Two exercises: (a) Review a realistic PR containing three deliberate
   defects at different layers (one correctness, one design, one clarity). Write review
   comments in the correct layer order. (b) Draft an RFC for a fictional platform change
   (e.g., introducing a centralized secrets store), including a populated "Alternatives
   Considered" section.

---

### Pedagogical Justification

This mini-arc sits under `platform/foundations/` for two reasons. First, code reading,
debugging, and review are not discipline-specific: they apply equally to SRE, GitOps,
DevSecOps, and platform engineering workflows. They belong in Foundations alongside
Systems Thinking and Engineering Leadership. Second, placing them in Foundations makes them
prerequisites for discipline-specific modules — a platform engineer studying MLOps cannot
effectively read an operator codebase or review infrastructure PRs without these skills.

The arc follows KubeDojo's theory-first model: each module establishes the conceptual
framework (why this skill matters, what a systematic approach looks like) before providing
a hands-on exercise that requires applying the framework to a realistic scenario. The
lab exercises use real CNCF project code and realistic Kubernetes configurations rather
than toy examples, matching the practitioner level of the target audience.

The three modules build in a deliberate prerequisite chain. A learner who cannot navigate
a codebase (Module 1) will struggle to isolate a bug to its origin in that codebase
(Module 2), and will not be able to identify design-level issues in a code review (Module 3).
This chain mirrors how the skills compound in professional practice.

---

## §C. References

### Primary Sources

- Ousterhout, John. *A Philosophy of Software Design*. Yaknyam Press, 2018.
- Spinellis, Diomidis. *Code Reading: The Open Source Perspective*. Addison-Wesley, 2003.
- Hunt, Andrew and Thomas, David. *The Pragmatic Programmer: Your Journey to Mastery*, 20th Anniversary Edition. Addison-Wesley, 2019.
- Spolsky, Joel. "The Joel Test: 12 Steps to Better Code." *Joel on Software*, 2000.
  URL verified 2026-05-14: https://www.joelonsoftware.com/2000/08/09/the-joel-test-12-steps-to-better-code/

### RFC Process References (Public Archives)

- Rust Language RFC Process. GitHub: rust-lang/rfcs. Public model of community RFC workflow.
- Python Enhancement Proposals (PEPs). https://peps.python.org — canonical pre-decision
  specification format; one of the oldest public examples of written consensus culture.
- IETF Request for Comments archive. https://www.rfc-editor.org — the original source of
  the RFC format as a technical consensus mechanism.

### Related KubeDojo Modules (Overlap Map)

- `platform/foundations/engineering-leadership/module-1.2-postmortems.md` — post-incident
  root cause analysis; prerequisite for debugging discipline framing
- `platform/foundations/engineering-leadership/module-1.4-adrs.md` — ADR format and
  introductory RFC-vs-ADR distinction (Part 5); prerequisite for Module 3 of this arc
- `platform/foundations/engineering-leadership/module-1.6-mentorship.md` — code review
  mentioned as a mentorship activity; Module 3 of this arc provides the mechanics
- `platform/foundations/systems-thinking/module-1.3-mental-models-for-operations.md` —
  operational mental models; Module 1 of this arc extends this to source-code reading

### URLs Removed (Anchor Verification Failures)

- `github.com/hashicorp/rfcs` — HTTP 404 as of 2026-05-14. Repo does not exist under
  this path. HashiCorp RFC practice referenced as engineering culture, not linked.
- Stripe "The Written Word" article — the specific article URL returns 404. The general
  Stripe engineering blog (stripe.com/blog/engineering, 200) does not index this article.
  Stripe's written-word culture is referenced as established practice, not linked.
