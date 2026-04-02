# KubeDojo Transformation Playbook
**Version:** 1.0 | **Owner:** Lead Curriculum Engineer

This playbook defines the exact workflow for applying the **Dojo Standard (DS)** across the 568 modules and 142 labs. This is a surgical operation, not a mass-rewrite.

---

## 1. The Pre-Flight Audit (Safety First)
Before touching any file, you MUST perform a **Visual Inventory**.
1.  Open the module.
2.  List every ASCII diagram, Mermaid chart, and complex table.
3.  **The Mandate:** These are "Protected Assets." Any change that removes or simplifies them is a failure.

---

## 2. Categorization & Execution Path

| If the module is... | The Strategy is... | The "Walking" steps |
| :--- | :--- | :--- |
| **Elite/Rich Lesson** | **Surgical Enrichment** | 1. Keep 100% of technical core.<br>2. Add Bloom's outcomes at top.<br>3. Add Scenario framing.<br>4. Add Quiz/Reflection at bottom. |
| **Dry Technical** | **Instructional Infusion** | 1. Add Socratic active-learning hooks.<br>2. Rewrite dry explanations as "Engineering Decisions."<br>3. Add 1-2 new diagrams. |
| **Checklist/Stub** | **Technical Expansion** | 1. **300+ line expansion** required.<br>2. Add the missing "How it Works" (State machine/Loops).<br>3. Use Theory-First Template. |

---

## 3. The Lab Transformation Workflow
1.  **Alignment Check:** Does the lab test the Learning Outcome defined in the text? If no, rewrite the lab objective.
2.  **Challenge Grafting:** Wrap the existing lab steps in a "Scenario."
3.  **The "details" Switch:** Move the "Run this command" steps into `<details>` tags as Hint 3. The main lab body should only have the **Objective**.

---

## 4. The Translation Loop
1.  **Finalize English:** Complete and verify the English version first.
2.  **Synchronous Sync:** Immediately update the corresponding `uk/` file.
3.  **Integrity Check:** Ensure slugs, links, and diagrams match the English source exactly.

---

## 5. Definition of Done (DoD)
A module/lab pair is "Complete" only when:
- [ ] Average Heuristic Score is > 4.5/5.0.
- [ ] Manual diff-review confirms **zero diagram loss**.
- [ ] Passes technical precision check against official specs.
- [ ] Passing verified tests (Phase 3).
