---
description: Review a KubeDojo module against quality standards
---

# Module Quality Review

You are reviewing a KubeDojo CKA curriculum module. Apply these quality standards rigorously.

## Module to Review

Review the file: $ARGUMENTS

If no file specified, ask which module to review.

## Quality Standards Checklist

Score each category 1-10, then provide overall assessment.

### 1. Theory Depth (Weight: 25%)
- [ ] Explains the "why" not just the "what"
- [ ] No handwaving or glossing over complexity
- [ ] Junior-friendly explanations (treats reader as beginner)
- [ ] Builds conceptual understanding before commands

### 2. Practical Value (Weight: 25%)
- [ ] All code/commands are complete and runnable
- [ ] Clear step-by-step instructions
- [ ] Verification steps included (how to check it worked)
- [ ] Realistic scenarios, not toy examples

### 3. Engagement (Weight: 20%)
- [ ] Entertaining analogies that make concepts stick
- [ ] War stories / real-world gotchas
- [ ] "Did You Know?" sections (2-3 per module)
- [ ] Conversational tone, not textbook dry

### 4. Exam Relevance (Weight: 15%)
- [ ] Complexity tag present (`[QUICK]`, `[MEDIUM]`, `[COMPLEX]`)
- [ ] Speed tips for exam scenarios
- [ ] Common mistakes table
- [ ] Aligns with CKA 2025 curriculum

### 5. Structure (Weight: 10%)
- [ ] Clear learning objectives at start
- [ ] Quiz with hidden answers (4+ questions)
- [ ] Hands-on exercise with success criteria
- [ ] Link to next module

### 6. Pedagogical Quality (Weight: 10%)
- [ ] **Practice Drills section** with 5-7 drills
- [ ] **Target times** on all drills (e.g., "Target: 3 minutes")
- [ ] **Troubleshooting drill** (at least 1 "fix this broken..." exercise)
- [ ] **Challenge drill** (at least 1 "no guidance provided" exercise)
- [ ] **Drill variety** (mix of speed, understanding, debugging)
- [ ] **Progressive difficulty** (easier drills first, challenge last)

## Review Process

1. Read the entire module
2. Score each category (1-10)
3. Calculate weighted overall score
4. Identify top 3 strengths
5. Identify top 3 areas for improvement
6. Provide specific, actionable recommendations

## Output Format

```
## Module Review: [Module Name]

### Scores
| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Theory Depth | X/10 | 25% | X.X |
| Practical Value | X/10 | 25% | X.X |
| Engagement | X/10 | 20% | X.X |
| Exam Relevance | X/10 | 10% | X.X |
| Structure | X/10 | 10% | X.X |
| Pedagogical Quality | X/10 | 10% | X.X |
| **Overall** | | | **X.X/10** |

### Strengths
1. ...
2. ...
3. ...

### Areas for Improvement
1. ...
2. ...
3. ...

### Specific Recommendations
- ...
- ...
- ...

### Missing Elements
- [ ] Item that should be added
- [ ] ...
```

## Quality Threshold

- **8.0+**: Ready for publication
- **6.5-7.9**: Needs minor revisions
- **5.0-6.4**: Needs significant work
- **<5.0**: Major rewrite required

Be constructive but honest. The goal is Module 1 quality across all modules.
