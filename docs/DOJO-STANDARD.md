# The KubeDojo Standard (DS Framework)
**Status:** MANDATORY | **Version:** 1.0

This document defines the non-negotiable quality standards for KubeDojo content. Every module and lab must adhere to these principles to maintain "Google-level" technical authority and elite pedagogical value.

---

## 1. Pillar I: Technical Authority (The "Google" Standard)

KubeDojo does not just list commands; it explains **System Behavior**.

### 1.1 Precision Mandates
- **The Reconciliation Loop:** Any module involving a Kubernetes resource (Pod, Service, Ingress) MUST explain the Controller reconciliation logic (Observe → Diff → Act).
- **The Low-Level Path:** Networking modules MUST trace packets through the Linux kernel (iptables, IPVS, Netfilter). Security modules MUST explain kernel primitives (Cgroups, Namespaces, AppArmor).
- **Scalability Context:** Technical explanations must include complexity analysis (e.g., O(n) vs O(1)) and its impact on cluster scale.
- **Authoritative Tone:** Use industry-standard terminology. Never over-simplify to the point of technical inaccuracy.

---

## 2. Pillar II: Instructional Design (The "University" Standard)

We use specialized models based on the cognitive complexity of the domain.

### 2.1 Merrill’s First Principles (For Procedural Mastery)
*Use for: Installation guides, CLI tools, syntax-heavy tasks.*
1.  **Task-Centered:** Start with a real-world problem (e.g., "The image is too big").
2.  **Activation:** Connect to previous modules.
3.  **Demonstration:** Show the standard way to solve it.
4.  **Application:** Learner solves a similar but distinct problem.
5.  **Integration:** Reflection on how to use this in a production environment.

### 2.2 4C/ID Model (For Complex Engineering)
*Use for: Architecture, SRE Troubleshooting, Bare Metal Networking.*
- **Learning Tasks:** The module is built around a complex "Whole Task" (e.g., "Restore a split-brain etcd cluster").
- **Supportive Info:** Theory provided upfront to build the mental model.
- **Procedural Info:** Syntax and command references provided "just-in-time" to prevent cognitive overload.

### 2.3 Bloom’s Taxonomy
Every module must start with 3-5 explicit **Learning Outcomes** using high-level action verbs:
- *Level 4 (Analyze):* "Deconstruct the BGP handshake..."
- *Level 5 (Evaluate):* "Judge the security posture of an RBAC role..."
- *Level 6 (Create):* "Design a resilient multi-tier architecture..."

---

## 3. Pillar III: Visual Architecture (The "Visual Truth")

Diagrams are not decorations; they are the **Explanation Foundational Layer**.

### 3.1 The Visual Matrix
- **ASCII (MANDATORY):** Used for "What's in the Box" (Container anatomy, Node components). Git-friendly and CLI-aligned.
- **Mermaid (MANDATORY):** Used for "Logic & Sequence." Sequence diagrams for handshakes, Flowcharts for reconciliation loops.
- **SVG (RESERVED):** Used for high-level environment topologies and global architecture.

### 3.2 Preservation Mandate
- **NEVER** delete an existing ASCII diagram during a rewrite.
- All diagrams must be labeled with a figure number and a descriptive caption.

---

## 4. Pillar IV: Lab Engineering (The "Inquiry" Standard)

Labs must move from **Mimicry** (Copy-Paste) to **Inquiry** (Decision-Making).

### 4.1 Challenge Patterns
- **Kill Chain:** Progressive adversarial challenges.
- **Observability-First:** "Do X, then find the proof in the logs/metrics."
- **Chaos-Injected:** Introduce failures while the learner is performing a task.

### 4.2 Feedback Loop
- **JIT Hinting:** Provide tiered hints (Hint 1: Concept → Hint 2: Component → Hint 3: Command).
- **The "Why" Verification:** Every lab must end with a reflection question: "Why did the system react this way when you changed X?"

---

## 5. Pillar V: Quality Gates

No content is merged unless it passes:
1.  **The Diff Audit:** Manual verification that no visual data was lost.
2.  **The Precision Audit:** Fact-checking against official K8s/Linux specifications.
3.  **The Constructive Alignment Audit:** Ensuring the text actually teaches the mental model required by the lab.
