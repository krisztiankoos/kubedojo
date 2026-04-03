---
name: module-quality-reviewer
description: Review KubeDojo modules for quality against the pedagogical rubric. Use when reviewing, scoring, or checking modules. Triggers on "review module", "check quality", "score module".
---

# Module Quality Reviewer Skill

Review KubeDojo modules against the quality rubric at `docs/quality-rubric.md`.

## How to Review

1. Read the module fully
2. Score against ALL 7 rubric dimensions (1-5 each)
3. Be STRICT — a 4 means genuinely good, a 5 is exceptional
4. Flag specific issues with line numbers

## Rubric Dimensions (1-5 each)

| Dimension | What to Check |
|-----------|--------------|
| **Learning Outcomes** | Are they stated? Measurable? Bloom's L3+? |
| **Scaffolding** | Does content build simple→complex? Narrative bridges between sections? |
| **Active Learning** | Are there inline prompts? Or is all practice back-loaded to the end? |
| **Real-World Connection** | War stories with specific details? Or generic "in production" handwaving? |
| **Assessment Alignment** | Do quiz questions test understanding (scenarios) or recall (what is X?)? |
| **Cognitive Load** | Well-chunked? Diagrams integrated? Or information dump? |
| **Engagement** | Memorable tone? Would you recommend this to a colleague? Or dry/robotic? |

## Structure Checklist

- [ ] Learning Outcomes (Bloom's L3+ verbs: debug, design, evaluate)
- [ ] Why This Module Matters (war story with real impact)
- [ ] Core content (3-6 sections with code, diagrams, tables)
- [ ] Inline active learning (at least 2 prediction/try-it prompts in the body)
- [ ] Did You Know? (4 facts with real numbers)
- [ ] Common Mistakes table (6-8 rows: Mistake | Why | Fix)
- [ ] Quiz (6-8 scenario-based questions with `<details>` answers)
- [ ] Hands-On Exercise (multi-step with success criteria)
- [ ] Next Module link

## Passing Criteria

- Average score >= 3.5/5
- No single dimension scores 1
- Active Learning >= 3
- Assessment Alignment >= 3

## Output Format

```markdown
## Module Review: [Name]
**File**: [path]
**Lines**: [count]

### Scores

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

### Structure Checklist
- [x] or [ ] for each required element

### Key Strengths
1. ...

### Must Fix
1. ...

### Verdict: PASS / NEEDS WORK / FAIL
```

## Reference Modules (Gold Standard)

- **Platform: What is Systems Thinking?** (4.6/5) — narrative voice, inline exercises, scenario-based assessment
- **On-Prem: The Case for On-Prem** (4.4/5) — balanced perspective, deliberate quiz traps, TCO exercise
- **Cloud: AWS Secrets Management** (4.0/5) — envelope encryption diagram, debugging quiz scenarios

## Anti-Patterns to Flag

- "List of facts" style (bullet points without connecting narrative)
- Quiz questions that test recall ("What is the command for X?")
- All active learning back-loaded to the end
- Diagrams with separate legends instead of inline labels
- "Refer to official documentation for details"
- Sections that could be rearranged in any order without losing coherence
