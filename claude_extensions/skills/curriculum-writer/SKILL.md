---
name: curriculum-writer
description: Write KubeDojo curriculum modules. Use when creating modules, writing theory, exercises, quizzes. Triggers on "write module", "create module", "new module".
---

# Curriculum Writer Skill

Expert skill for writing new KubeDojo curriculum modules. Ensures consistent structure, tone, and quality across all educational content.

## When to Use
- Creating new curriculum modules
- Expanding existing module content
- Writing theory sections, exercises, or quizzes

## Module Template

```markdown
# Module X.Y: [Topic Name]

> **Complexity**: `[QUICK]` | `[MEDIUM]` | `[COMPLEX]`
>
> **Time to Complete**: X-Y minutes
>
> **Prerequisites**: [List required modules or knowledge]

---

## Why This Module Matters

[2-3 paragraphs explaining WHY this topic matters for CKA and real-world K8s admin]

> **The [Topic] Analogy**
>
> [Memorable analogy that makes the concept stick]

---

## What You'll Learn/Build

[Clear statement of learning objectives or what they'll create]

---

## Part 1: [First Major Section]

### 1.1 [Subsection]

[Content with code examples]

> **Did You Know?**
>
> [Interesting fact related to this subsection]

### 1.2 [Subsection]

[More content]

> **Gotcha: [Common Mistake]**
>
> [Warning about a common pitfall]

---

## Part 2: [Second Major Section]

[Continue pattern...]

> **War Story: [Catchy Title]**
>
> [Real-world incident that illustrates why this matters]

---

## Did You Know?

- **[Fact 1]**: [Interesting detail]
- **[Fact 2]**: [Interesting detail]
- **[Fact 3]**: [Interesting detail]

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| [Mistake 1] | [What goes wrong] | [How to fix/avoid] |
| [Mistake 2] | [What goes wrong] | [How to fix/avoid] |
| [Mistake 3] | [What goes wrong] | [How to fix/avoid] |

---

## Quiz

1. **[Question 1]**
   <details>
   <summary>Answer</summary>
   [Detailed answer explaining why]
   </details>

2. **[Question 2]**
   <details>
   <summary>Answer</summary>
   [Detailed answer explaining why]
   </details>

3. **[Question 3]**
   <details>
   <summary>Answer</summary>
   [Detailed answer explaining why]
   </details>

4. **[Question 4]**
   <details>
   <summary>Answer</summary>
   [Detailed answer explaining why]
   </details>

---

## Hands-On Exercise

**Task**: [Clear description of what to do]

**Setup** (if needed):
```bash
[Any setup commands]
```

**Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Success Criteria**:
- [ ] [Verifiable outcome 1]
- [ ] [Verifiable outcome 2]
- [ ] [Verifiable outcome 3]

**Verification**:
```bash
[Commands to verify success]
```

---

## Next Module

[Module X.Z: Next Topic](module-X.Z-next-topic.md) - [Brief description]
```

## Writing Guidelines

### Tone
- Conversational, not academic
- Empathetic to learner struggles
- Confident but not arrogant
- Use "you" and "we" freely

### Analogies
- One memorable analogy per module minimum
- Connect K8s concepts to familiar real-world things
- Analogies should illuminate, not oversimplify

### War Stories
- At least one per module
- Must have real consequences (time lost, money lost, outage)
- End with a lesson learned
- Can be anonymized but should feel authentic

### Code Examples
- All code must be complete and runnable
- Use realistic names (not foo/bar)
- Show expected output where helpful
- Include verification steps

### Technical Accuracy
- Align with CKA 2025 curriculum
- Use current Kubernetes version (1.31+)
- Note when something is deprecated
- Link to official docs for deep dives

### Quiz Questions
- Test understanding, not memorization
- Answers should explain "why"
- Mix of conceptual and practical
- 4 questions per module

### Complexity Tags
- `[QUICK]`: Can be done in exam in 1-3 minutes
- `[MEDIUM]`: Takes 4-6 minutes in exam
- `[COMPLEX]`: Requires 8+ minutes or troubleshooting

## Quality Checklist

Before considering a module complete:

- [ ] All structural elements present
- [ ] At least one memorable analogy
- [ ] At least one war story
- [ ] 2-3 "Did You Know?" facts
- [ ] Common mistakes table filled
- [ ] 4 quiz questions with detailed answers
- [ ] Hands-on exercise with verification
- [ ] All code tested and working
- [ ] Links to next module
- [ ] Proofread for clarity
