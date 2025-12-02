---
description: Review all modules in a KubeDojo curriculum part for consistency and quality
---

# Part Review - Consistency & Quality Check

You are reviewing an entire part of the KubeDojo CKA curriculum. This checks both individual module quality AND cross-module consistency.

## Part to Review

Review the directory: $ARGUMENTS

Example: `docs/cka/part0-environment/`

If no directory specified, ask which part to review.

## Review Process

### Phase 1: Inventory
1. List all module files in the part
2. Check file naming consistency
3. Verify module numbering sequence

### Phase 2: Structure Consistency
Check that ALL modules have:
- [ ] Complexity tag in header (`[QUICK]`, `[MEDIUM]`, `[COMPLEX]`)
- [ ] Time to Complete estimate
- [ ] Prerequisites listed
- [ ] "Why This Module Matters" section
- [ ] Opening analogy (after "Why This Module Matters")
- [ ] "Did You Know?" section(s) (2-3 facts)
- [ ] Common Mistakes table
- [ ] Quiz with hidden answers (`<details>` tags) (4+ questions)
- [ ] Hands-On Exercise with Success Criteria
- [ ] **Practice Drills section** (5-7 drills with target times)
- [ ] "Next Module" link

### Phase 2.5: Pedagogical Quality (NEW)
Check practice and retention elements:
- [ ] **Practice Drill Count**: Each module should have 5-7 drills
- [ ] **Drill Variety**: Mix of speed tests, troubleshooting, challenges
- [ ] **Target Times**: All drills should have target completion times
- [ ] **Broken/Error Exercises**: At least 1 troubleshooting drill per module
- [ ] **Challenge Variants**: At least 1 "no guidance" challenge drill per module
- [ ] **Cumulative Quiz**: Part has a cumulative quiz file (`partX-cumulative-quiz.md`)

### Phase 3: Content Flow
- [ ] Modules build on each other logically
- [ ] No concept introduced without prior explanation
- [ ] Consistent terminology across modules
- [ ] Cross-references between related modules

### Phase 4: Technical Consistency
- [ ] Code formatting consistent (same style)
- [ ] Command examples use same aliases (`k` vs `kubectl`)
- [ ] YAML indentation consistent (2 spaces)
- [ ] Same verification patterns

### Phase 5: Individual Module Scores
For each module, provide quick scores:
- Theory: X/10
- Practical: X/10
- Engagement: X/10

## Output Format

```
## Part Review: [Part Name]

### Inventory
| # | Module | File | Status |
|---|--------|------|--------|
| 0.1 | Cluster Setup | module-0.1-*.md | ✅ |
| 0.2 | Shell Mastery | module-0.2-*.md | ✅ |
| ... | ... | ... | ... |

### Structure Consistency
| Element | Present in All? | Missing From |
|---------|-----------------|--------------|
| Complexity tag | ✅/❌ | [list] |
| Did You Know | ✅/❌ | [list] |
| Quiz | ✅/❌ | [list] |
| ... | ... | ... |

### Content Flow Assessment
- Flow quality: X/10
- Issues: [list any gaps or jumps]

### Module Scores Summary
| Module | Theory | Practical | Engagement | Pedagogy | Avg |
|--------|--------|-----------|------------|----------|-----|
| 0.1 | X | X | X | X | X.X |
| 0.2 | X | X | X | X | X.X |
| ... | ... | ... | ... | ... | ... |
| **Part Avg** | X.X | X.X | X.X | X.X | **X.X** |

### Pedagogical Assessment
| Element | Status | Details |
|---------|--------|---------|
| Practice Drills | X/Y modules | [which modules missing] |
| Drill Variety | ✅/❌ | Speed tests, troubleshooting, challenges |
| Target Times | X/Y drills | [count with times vs total] |
| Error/Fix Exercises | X/Y modules | [which have troubleshooting drills] |
| Challenge Drills | X/Y modules | [which have no-guidance challenges] |
| Cumulative Quiz | ✅/❌ | partX-cumulative-quiz.md exists |
| Spaced Repetition | ✅/❌ | Cross-module review references |

**Pedagogy Score**: X/10
- 10: All elements present, excellent variety
- 8-9: Most elements present, good variety
- 6-7: Some elements missing
- <6: Significant pedagogical gaps

### Top Issues to Address
1. [Most critical issue]
2. [Second issue]
3. [Third issue]

### Recommendations
- [Specific actionable items]
```

## Quality Thresholds

**Part Average:**
- **8.0+**: Part is complete and polished
- **7.0-7.9**: Minor improvements needed
- **6.0-6.9**: Some modules need work
- **<6.0**: Part needs significant revision

**Consistency:**
- All structural elements should be present in 100% of modules
- Any missing element is flagged for addition
