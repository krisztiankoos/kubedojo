# KubeDojo Quality Rubric

**Purpose**: Measurable scoring system for rating module and lab quality. Used during audits and reviews.

---

## Module Rubric (7 Dimensions, 1-5 Scale)

### Dimension 1: Learning Outcomes

| Score | Description |
|-------|-------------|
| **1** | No learning outcomes stated. Reader has no idea what they'll learn. |
| **2** | Vague outcomes ("understand Kubernetes networking"). Not measurable. |
| **3** | Outcomes stated but only at Bloom's Level 1-2 (remember/understand). |
| **4** | Clear, measurable outcomes at Level 3+ (apply/analyze). Aligned with content. |
| **5** | Outcomes explicitly use action verbs, are testable, and the module delivers on every one. Includes Level 4-6 outcomes. |

### Dimension 2: Scaffolding & Structure

| Score | Description |
|-------|-------------|
| **1** | No logical order. Sections could be rearranged randomly. Dump of disconnected facts. |
| **2** | Some ordering but no narrative bridges. Reader must infer connections. |
| **3** | Logical progression from simple to complex. Prerequisites mentioned. |
| **4** | Clear scaffolding: each section builds on the last. Explicit bridges between sections. References prior modules when building on concepts. |
| **5** | Expert scaffolding: worked examples before practice, complexity gradually increases, expertise reversal considered (different depth for different audiences). |

### Dimension 3: Active Learning

| Score | Description |
|-------|-------------|
| **1** | Pure reading. No exercises, no questions, no interactivity. The learner is passive. |
| **2** | Exercise at the end only. Module body is entirely passive reading. |
| **3** | Exercise + quiz present. Some scenario-based questions. |
| **4** | Multiple active learning touchpoints: prediction prompts in the body, "what would happen if" scenarios, decision-making exercises. Quiz tests understanding not recall. |
| **5** | Active learning woven throughout: embedded questions, try-it-yourself moments before solutions are shown, comparison exercises, design challenges. Learner constructs knowledge, not just reads it. |

### Dimension 4: Real-World Connection

| Score | Description |
|-------|-------------|
| **1** | No real-world context. Pure theory or command reference. |
| **2** | Mentions "in production" but no specific examples or stories. |
| **3** | Has "Did You Know?" or equivalent. Some real numbers/dates. Generic examples. |
| **4** | Has war stories with specific (anonymized) companies, financial impact, timeline. "Why This Matters" section opens with a real incident. Common Mistakes table with production-relevant pitfalls. |
| **5** | Real-world context is integrated throughout, not just in designated sections. Examples use realistic scenarios. Trade-offs are discussed honestly. Reader feels why this matters viscerally. |

### Dimension 5: Assessment Alignment

| Score | Description |
|-------|-------------|
| **1** | No quiz or exercise. No way to test learning. |
| **2** | Quiz present but questions test recall only ("What command does X?"). |
| **3** | Quiz has mix of recall and understanding questions. Exercise is "follow these steps." |
| **4** | Quiz tests analysis/evaluation (Bloom's 4-5). Exercise requires problem-solving, not just command execution. Solutions explain WHY, not just WHAT. |
| **5** | Assessment perfectly aligned with outcomes: every stated learning outcome is tested. Exercise has progressive difficulty. Quiz answers are thorough explanations. Learner can self-assess genuine understanding. |

### Dimension 6: Cognitive Load Management

| Score | Description |
|-------|-------------|
| **1** | Information dump. Too many concepts introduced at once. No chunking. |
| **2** | Some organization but concepts pile up without breaks. No worked examples. |
| **3** | Reasonable chunking. Concepts introduced one at a time. Some diagrams help. |
| **4** | Good cognitive load management: prerequisites taught before combining, diagrams integrated with text, worked examples before practice, clear section boundaries. |
| **5** | Expert load management: split-attention eliminated (labels on diagrams, not separate), complexity gradient appropriate for target audience, dual coding (visual + verbal), completion problems before full problems. |

### Dimension 7: Engagement & Motivation

| Score | Description |
|-------|-------------|
| **1** | Dry, robotic tone. No hook. Reader would close the tab. |
| **2** | Functional but boring. Gets the job done but nothing memorable. |
| **3** | Some personality. "Why This Matters" section present. Analogies used occasionally. |
| **4** | Conversational, authoritative tone. Strong opening hook. Good analogies. "Did You Know?" facts are genuinely interesting. Reader feels mentored by a senior engineer. |
| **5** | Memorable. Reader would recommend this module to a colleague. Stories stick. Analogies are vivid and accurate. Humor used sparingly but effectively. Reader feels they understand the topic at a level they couldn't get from official docs. |

### Dimension 8: Practitioner Depth

| Score | Description |
|-------|-------------|
| **1** | Command reference only. "Run X, then Y." No explanation of why, when, or what could go wrong. |
| **2** | Some context around commands but no decision frameworks. Reader knows HOW but not WHEN or WHY NOT. |
| **3** | Includes tradeoff mentions and comparison tables. Some "when to use X vs Y" guidance. Patterns mentioned but not explained in depth. |
| **4** | Dedicated sections for: patterns (proven approaches with rationale), anti-patterns (what fails and why), decision frameworks (flowcharts or matrices for choosing approaches), and architectural reasoning (how components interact, what breaks at scale). Theory explains the WHY before showing the HOW. Prose explains concepts between code blocks — not just "here's the YAML." |
| **5** | Practitioner-grade throughout: every technique comes with tradeoffs discussed honestly, failure modes documented, scaling considerations addressed. Reader could defend their architecture choices in a design review. Content balances theory and practice — neither a textbook nor a cookbook. Anti-patterns include real consequences. Decision frameworks are actionable, not theoretical. An experienced engineer would learn something new. |

---

## Lab Rubric (5 Dimensions, 1-5 Scale)

### Dimension L1: Scenario-Based Design

| Score | Description |
|-------|-------------|
| **1** | "Run these commands in order." No context or motivation. |
| **2** | Brief context paragraph then "run these commands." |
| **3** | Scenario sets up a problem but steps are prescriptive (copy-paste). |
| **4** | Scenario presents a real problem. Learner must figure out approach with guidance. Steps describe WHAT to achieve, not exactly HOW. |
| **5** | Immersive scenario. Learner makes real decisions. Multiple valid approaches. Environment starts in a "broken" or "incomplete" state that reflects production reality. |

### Dimension L2: Progressive Difficulty

| Score | Description |
|-------|-------------|
| **1** | All steps same difficulty. No progression. |
| **2** | Roughly easy→hard but jumps in difficulty between steps. |
| **3** | Clear easy→medium→hard progression. Each step builds on the last. |
| **4** | Smooth difficulty curve. Early steps build confidence. Later steps require combining multiple concepts. Optional "stretch" challenge for advanced learners. |
| **5** | Expert progression: warm-up → core challenge → integration → "what if" extension. Difficulty matches the module's Bloom's level targets. |

### Dimension L3: Understanding Over Memorization

| Score | Description |
|-------|-------------|
| **1** | Validates only output format ("did the pod start?"). Tests command memorization. |
| **2** | Validates correct behavior but doesn't test understanding of WHY. |
| **3** | Some "why" questions. Validation checks behavior, not just existence. |
| **4** | Requires the learner to explain or predict behavior. Validation tests correct configuration AND understanding. Includes "what would break if you changed X?" |
| **5** | Lab IS the reasoning exercise. Learner must diagnose, decide, implement, and verify. Tests transfer — could the learner apply this to a different but related scenario? |

### Dimension L4: Hint & Feedback Quality

| Score | Description |
|-------|-------------|
| **1** | No hints. Learner is stuck or looks up the answer externally. |
| **2** | Hints are just the answer in a `<details>` tag. |
| **3** | Tiered hints: concept hint → component hint → command hint. |
| **4** | Hints teach, not just tell. First hint explains the concept, second narrows the approach, third gives specific guidance. Error messages are helpful. |
| **5** | Feedback loop: hints adapt to common mistakes. "If you see error X, it means Y — try Z." Hints reference the module's teaching for reinforcement. |

### Dimension L5: Transfer Potential

| Score | Description |
|-------|-------------|
| **1** | Learner can complete the lab but couldn't apply the skill elsewhere. |
| **2** | Some transferable skills but tightly coupled to the specific scenario. |
| **3** | Core skill is transferable. Learner understands the general approach. |
| **4** | Lab explicitly discusses generalization: "This same pattern applies when..." Reflection question at the end. |
| **5** | Lab ends with an open-ended challenge: "Now apply this approach to [different but related problem]." Learner practices transfer, not just repetition. |

---

## Scoring Template

Copy this template when auditing a module:

```markdown
## Module: [Title]
**File**: [path]
**Lines**: [count]
**Track**: [track]

### Module Scores (1-5)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Learning Outcomes | /5 | |
| Scaffolding | /5 | |
| Active Learning | /5 | |
| Real-World Connection | /5 | |
| Assessment Alignment | /5 | |
| Cognitive Load | /5 | |
| Engagement | /5 | |
| **Average** | **/5** | |

### Key Strengths
- 

### Key Weaknesses
- 

### Action Required
- [ ] None / Low / Medium / High / Critical
- [ ] Specific fixes needed:
```

```markdown
## Lab: [Title]
**File**: [path]
**Track**: [track]

### Lab Scores (1-5)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Scenario-Based Design | /5 | |
| Progressive Difficulty | /5 | |
| Understanding Over Memorization | /5 | |
| Hint & Feedback Quality | /5 | |
| Transfer Potential | /5 | |
| **Average** | **/5** | |

### Action Required
- [ ] None / Low / Medium / High / Critical
```

---

## Score Interpretation

Scoring uses **sum of all 7 dimensions** (max 35) with a **per-dimension floor**.

| Sum | Rating | Action |
|-----|--------|--------|
| **29-35** | Pass | Ship it. Must excel in at least one dimension. |
| **22-28** | Needs polish | Close — fix the weakest dimensions. |
| **15-21** | Needs work | Significant gaps across multiple dimensions. |
| **7-14** | Rewrite | Fundamentally broken. Start over. |

### Scoring Tool

```bash
python scripts/score_module.py 4 5 4 4 5 4 4          # interactive
python scripts/score_module.py 4 5 4 4 5 4 4 --json   # machine-readable
echo "4 5 4 4 5 4 4" | python scripts/score_module.py -  # stdin
```

Dimension order: D1 Outcomes, D2 Scaffolding, D3 Active Learning, D4 Real-World, D5 Assessment, D6 Cognitive Load, D7 Engagement.

---

## Line Count Policy

Visual aids (ASCII diagrams, Mermaid charts, illustrative code blocks) do NOT count toward content line minimums. They supplement teaching but don't substitute for it. A 600-line module with 400 lines of diagrams and 200 lines of text is a 200-line module — it fails.

---

## Threshold for "Passing"

A module passes the quality bar when **both** conditions are met:

1. **Every dimension >= 4** — a score of 3 or below in ANY dimension is an automatic fail, regardless of sum. Every dimension matters equally. You cannot compensate for weak real-world connection with strong quizzes.

2. **Sum >= 29 out of 35** — all 4s (sum=28) is not enough. At least one dimension must be at 5, meaning the module excels somewhere, not just meets the bar everywhere.

A module that scores 3-5-5-5-5-5-5 (sum=33) **fails** — the floor is violated.
A module that scores 4-4-4-4-4-4-4 (sum=28) **fails** — it needs to excel somewhere.
