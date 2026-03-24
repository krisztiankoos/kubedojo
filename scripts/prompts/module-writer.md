# KubeDojo Module Writer Prompt

Use this prompt to write new curriculum modules. Replace the variables in {{BRACKETS}}.

---

## PROMPT

TASK: Write a complete KubeDojo educational module.

### Module Specification

- **Title**: {{MODULE_TITLE}}
- **File path**: {{FILE_PATH}}
- **Complexity**: {{[QUICK] | [MEDIUM] | [COMPLEX]}}
- **Time to Complete**: {{TIME}}
- **Prerequisites**: {{PREREQUISITES}}
- **Next Module**: {{NEXT_MODULE_LINK}}

### Topic Coverage

{{5-7 BULLET POINTS OF WHAT TO COVER}}

### Hands-On Exercise Concept

{{EXERCISE_DESCRIPTION}}

---

### Quality Standard: 10/10 on the Dojo Scale

**LENGTH**: 600-800 lines minimum. This is a deep, rich learning module — not an outline or reference doc.

**REQUIRED SECTIONS** (in this exact order):

1. **Title and metadata** — H1 title, complexity tag, time estimate, prerequisites
2. **Why This Module Matters** — Open with a dramatic, real-world scenario written in third person. A real incident, a real company (anonymized if needed), real financial impact. Make the reader feel why this topic matters viscerally. Then transition to what they will learn. 2-3 paragraphs minimum.
3. **Core content sections** (3-6 sections) — Each section should include:
   - Clear explanations with analogies (treat the reader as a smart beginner)
   - Runnable code blocks (bash, YAML, Go, Python — whatever fits)
   - ASCII diagrams where architecture or flow needs visualization
   - Tables for comparisons, decision matrices, or reference data
   - "War Story" or practical example within the section
4. **Did You Know?** — Exactly 4 interesting facts. Include real numbers, dates, or surprising details. Each fact should teach something the reader won't forget.
5. **Common Mistakes** — Table with 6-8 rows. Columns: Mistake | Why It Happens | How to Fix It. Be specific — not generic advice.
6. **Quiz** — 6-8 questions using `<details><summary>Question</summary>Answer</details>` format. Mix conceptual and practical questions. Answers should be thorough (3-5 sentences explaining WHY).
7. **Hands-On Exercise** — Multi-step practical exercise with:
   - Setup instructions (if needed)
   - 4-6 progressive tasks (easy → challenging)
   - Solutions in `<details>` tags
   - Clear success criteria checklist using `- [ ]` format
8. **Next Module** — Link to the next module with a one-line teaser

**TONE**:
- Conversational but authoritative — like a senior engineer mentoring you
- Explain "why" before "what" — motivation before instruction
- Use analogies from everyday life to explain abstract concepts
- Be direct and practical — no filler, no corporate-speak
- When discussing tools, be honest about trade-offs (no marketing language)

**TECHNICAL STANDARDS**:
- All commands must be complete and runnable (not pseudocode)
- YAML: 2-space indentation, valid syntax
- Code blocks must specify the language (```bash, ```yaml, ```go, etc.)
- Use `k` alias for kubectl (after explaining it once)
- Kubernetes version: 1.35+

**WHAT TO AVOID**:
- Do NOT repeat the number 47 in timestamps, durations, or counts (this is a known LLM pattern — vary your numbers)
- Do NOT use generic corporate examples — use realistic engineering scenarios
- Do NOT write thin outlines — every section needs depth, examples, and explanation
- Do NOT skip the exercise — it's the most important part for learning
- Do NOT use emojis

**REFERENCE**: Study the structure and depth of existing KubeDojo modules for calibration. Each module should feel like a chapter in a technical book, not a blog post.
