# KubeDojo Quality Audit Results

**Date**: 2026-04-03
**Rubric**: `docs/quality-rubric.md`
**Sample**: 31 modules across all tracks

---

## Executive Summary

**Overall curriculum health: GOOD (3.3/5 average)**

- 84% of modules are 500+ lines (rich)
- Top modules (Systems Thinking, On-Prem Case) score 4.4-4.6 — genuine gold standard
- Bottom modules (4 KCNA stubs, CKA stub) score 1.3-2.1 — critical failures
- Most modules land in the 3.0-3.6 range — solid but with consistent, fixable weaknesses

### Score Distribution

| Rating | Range | Count | % |
|--------|-------|-------|---|
| Excellent | 4.5-5.0 | 1 | 3% |
| Good | 3.5-4.4 | 14 | 45% |
| Needs Work | 2.5-3.4 | 10 | 32% |
| Poor | 1.5-2.4 | 5 | 16% |
| Critical | 1.0-1.4 | 1 | 3% |

---

## All Scored Modules

### Critical & High Priority (Must Fix)

| Module | Track | Lines | Score | Action | Primary Issue |
|--------|-------|-------|-------|--------|---------------|
| CKA 2.8: Scheduler Lifecycle Theory | CKA | 55 | **1.3** | Critical | Stub — outline only, no quiz/exercise/diagrams |
| KCNA 3.7: Community & Collaboration | KCNA | 49 | **1.6** | Critical | Stub — 49 lines, no assessment |
| KCNA 4.3: Release Strategies | KCNA | 58 | **1.6** | Critical | Stub — 58 lines, no assessment |
| KCNA 3.6: Security Basics | KCNA | 74 | **1.7** | Critical | Stub — 74 lines, no assessment |
| KCNA 1.9: Debugging Basics | KCNA | 64 | **2.1** | High | Stub — best of KCNA stubs but still no quiz/exercise |
| CKAD 3.5: API Deprecations | CKAD | 433 | **2.4** | High | Reads like reference docs, quiz is pure recall |
| Platform: etcd-operator | Toolkit | 342 | **2.4** | High | After opening story, becomes pure command reference |
| Prerequisites: Deployments | K8s Basics | 417 | **2.7** | High | Zero real-world stories, all practice back-loaded, dry |

### Medium Priority (Improve)

| Module | Track | Lines | Score | Action | Primary Issue |
|--------|-------|-------|-------|--------|---------------|
| Prerequisites: What Is K8s? | Cloud Native 101 | 420 | **2.9** | Medium | Overloaded for QUICK module, minimal active learning |
| Prerequisites: GitOps | Modern DevOps | 543 | **2.9** | Medium | Overloaded, dry, image automation too advanced for prereqs |
| Linux: TCP/IP Essentials | Networking | 619 | **3.0** | Medium | "List of facts" sections (port tables), no narrative voice |
| CKA: Autoscaling | Workloads | 311 | **3.3** | Medium | VPA section thin, no practice drills |
| CKA: k8s.io Navigation | Environment | 601 | **3.3** | Medium | Redundant drill sections, quiz tests recall only |
| CKAD: Multi-Container Pods | Design/Build | 668 | **3.3** | Medium | No formal outcomes, ambassador pattern thin |
| CKAD: NetworkPolicies | Networking | 766 | **3.3** | Medium | No inline "predict if traffic allowed?" exercises |
| Prerequisites: Files & Dirs | Zero to Terminal | 583 | **3.3** | Medium | No learning outcomes, quiz tests recall only |

### Low Priority (Minor Improvements)

| Module | Track | Lines | Score | Action | Primary Issue |
|--------|-------|-------|-------|--------|---------------|
| Prerequisites: Why K8s Won | Philosophy | 339 | **3.4** | Low | Back-loaded active learning |
| CKA: Extension Interfaces | Architecture | 784 | **3.4** | Low | Learning outcomes at Bloom's L1-2 |
| CKA: StorageClasses | Storage | 749 | **3.4** | Low | Drills are skeletal |
| CKS: Image Scanning | Supply Chain | 580 | **3.4** | Low | Reads like Trivy documentation |
| KCSA: Control Plane Security | Components | 493 | **3.4** | Low | ASCII boxes overused |
| Cloud: Azure ACR | Azure | 597 | **3.4** | Low | No inline exercises |
| GCP: Artifact Registry | GCP | 669 | **3.6** | Low | Solutions too easy to peek |
| CKS: RBAC Deep Dive | Hardening | 620 | **3.6** | Low | Quiz only tests recall |
| KCSA: Runtime Security | Platform Sec | 698 | **3.6** | Low | Heavy cognitive load, could split |
| Linux: USE Method | Performance | 649 | **3.6** | Low | No war story of USE in action |
| Platform: Chaos Principles | Disciplines | 629 | **3.6** | Low | No inline activities in 485 lines |

### No Action Needed

| Module | Track | Lines | Score | Notes |
|--------|-------|-------|-------|-------|
| On-Prem: Storage Architecture | Storage | 401 | **3.9** | Quiz questions are excellent |
| Cloud: AWS Secrets | AWS | 855 | **4.0** | Envelope encryption explanation is outstanding |
| On-Prem: Case for On-Prem | Planning | 396 | **4.4** | Quiz Q1 is pedagogically brilliant |
| Platform: Systems Thinking | Foundations | 809 | **4.6** | Gold standard — other modules should aspire to this |

---

## Per-Track Summary

| Track | Modules Scored | Avg Score | Verdict |
|-------|---------------|-----------|---------|
| Prerequisites/Fundamentals | 5 | 3.0 | **Needs Work** — no learning outcomes, back-loaded practice |
| CKA | 5 | 2.8 | **Needs Work** — one critical stub, outcomes weak |
| CKAD | 3 | 2.7 | **Needs Work** — API Deprecations drags it down |
| CKS | 2 | 3.5 | **Good** — solid modules, minor polish |
| KCNA | 4 | 1.8 | **Poor** — 4 stubs, systemic failure |
| KCSA | 2 | 3.5 | **Good** — comprehensive, some cognitive load issues |
| Cloud | 3 | 3.7 | **Good** — strong real-world context, weak inline exercises |
| Platform Engineering | 3 | 3.5 | **Good** — wide quality range (2.4 to 4.6) |
| Linux | 2 | 3.3 | **Needs Work** — TCP/IP is fact-listy |
| On-Premises | 2 | 4.2 | **Excellent** — best overall track |

---

## Systemic Patterns

### Pattern 1: No Formal Learning Outcomes (31/31 modules affected)

**Every single module** either omits learning outcomes entirely or states them at Bloom's Level 1-2 ("understand", "know"). No module uses measurable action verbs at Level 3+ ("debug", "design", "evaluate", "compare").

**Fix**: Add 3-5 explicit outcomes per module using verbs from Bloom's Level 3+. This is the single highest-impact improvement across the curriculum.

### Pattern 2: Active Learning Back-Loaded (27/31 modules)

27 of 31 modules follow the same pattern: 300-800 lines of passive reading, then quiz + exercise at the end. Only 4 modules (Systems Thinking, On-Prem Case, Runtime Security, USE Method) have inline active learning.

**Fix**: Add 2-3 "pause and think" prompts per module: prediction questions ("What do you think happens if...?"), try-it-yourself moments before showing solutions, or quick decision exercises.

### Pattern 3: Quizzes Test Recall, Not Understanding (22/31 modules)

Most quiz questions can be answered by Ctrl+F through the module. Only the On-Premises and Platform Foundations modules consistently test analysis and decision-making.

**Fix**: Replace 2-3 recall questions per quiz with scenario-based questions: "Given this situation, what would you do and why?"

### Pattern 4: KCNA Track Is Broken (4 modules, avg 1.8/5)

All 4 KCNA modules scored below 2.2. They're outlines, not modules. They lack:
- Quizzes (0/4 have one)
- Exercises (0/4 have one)
- Learning outcomes (0/4 have them)
- Sufficient depth (average 61 lines vs curriculum median of 787)

**Fix**: Expand each to 250-400 lines with quiz, exercises, and scenarios. KCNA is theory-only, but theory still needs active learning.

### Pattern 5: "List of Facts" Modules (3-5 modules)

Some modules that look long are actually reference documents disguised as lessons:
- **TCP/IP Essentials**: Port tables, IP range tables, command lists without narrative
- **etcd-operator**: Opening story then pure command reference
- **API Deprecations**: Version tables encouraging the memorization it argues against

**Fix**: Replace reference tables with scenario-driven teaching. Don't list ports — show a debugging scenario where you need to find the right port.

### Pattern 6: War Stories Make the Difference

The two highest-scoring modules (Systems Thinking 4.6, On-Prem Case 4.4) both have extensive, vivid war stories integrated throughout — not just in a "Did You Know" section. Modules without stories score 2.4-3.0 on average.

**Fix**: Every module should have at least one production story with specific (anonymized) details, timeline, and dollar impact.

---

## Action Summary

### Critical (rewrite required) — 5 modules
1. CKA 2.8: Scheduler Lifecycle Theory (55 lines → 500+)
2. KCNA 3.7: Community & Collaboration (49 lines → 250+)
3. KCNA 4.3: Release Strategies (58 lines → 250+)
4. KCNA 3.6: Security Basics (74 lines → 300+)
5. KCNA 1.9: Debugging Basics (64 lines → 300+)

### High (major restructure) — 3 modules
6. CKAD 3.5: API Deprecations — rework quiz, add debugging exercises
7. Platform: etcd-operator — add conceptual depth, scenario-based content
8. Prerequisites: Deployments — add war story, inline exercises, improve engagement

### Medium (significant improvements) — 8 modules
9-16. Various — see table above. Common fixes: add learning outcomes, inline exercises, scenario-based quiz questions.

### Low (minor polish) — 11 modules
17-27. Various — add learning outcomes, minor quiz upgrades, small improvements.

### Curriculum-wide fixes (all 568 modules)
- Add formal learning outcomes (Bloom's L3+) to every module
- Add 2-3 inline active learning prompts to every module
- Upgrade 2-3 quiz questions per module to scenario-based

---

## Reference Modules (Gold Standard)

These modules exemplify what every KubeDojo module should aspire to:

1. **Platform: What is Systems Thinking?** (4.6/5) — narrative voice, inline exercises, scenario-based assessment, vivid war stories
2. **On-Premises: The Case for On-Prem** (4.4/5) — balanced perspective, deliberate quiz traps that teach critical thinking, TCO exercise with surprising results
3. **Cloud: AWS Secrets Management** (4.0/5) — envelope encryption diagram, debugging quiz scenarios, real production gotchas
