# KubeDojo Research Report: Phase 1
**Date:** April 1, 2026
**Status:** COMPLETE (Issue #169)

## 1. Executive Summary
This report defines the "Google-Quality" standard for KubeDojo. By benchmarking against the official Kubernetes documentation and the Google SRE Book, and synthesizing pedagogical models (Merrill’s First Principles, 4C/ID), we have established a new blueprint for technical education. The goal is to move from "Fact Listing" to "System Engineering Mastery."

---

## 2. Technical Benchmarking: The "Google Standard"

### A. The Precision Delta
Our audit identified that "Google-quality" documentation is distinguished by its focus on **System Behavior** rather than **User Action**.

| Feature | KubeDojo Baseline | Google Standard |
| :--- | :--- | :--- |
| **Object Definition** | Defined by what it *is* (e.g., "A Service"). | Defined by its role in the **REST API** and its impact on the **Cluster State**. |
| **Mechanics** | Tells you *what* commands to run. | Explains *how* the packet turns (e.g., O(n) vs O(1) in iptables vs IPVS). |
| **Scalability** | High-level mentions of performance. | Deep dives into **Control Plane pressure** (e.g., the transition from Endpoints to EndpointSlices). |
| **Consistency** | Strong emphasis on availability. | Strong emphasis on **Consensus and Quorum** (e.g., the Raft algorithm in etcd). |

### B. Visual Mandates
Official documentation treats diagrams as the "Source of Truth." KubeDojo will adopt a **Hybrid Visual Strategy**:
- **ASCII:** For CLI-based component anatomy and container internals (Git-friendly).
- **Mermaid:** For state-machine logic (Handshakes, Reconciliation loops) and sequence flows.
- **SVG:** For high-level topologies and environment maps.

---

## 3. Pedagogical Framework: Moving to Active Inquiry

### A. Instructional Models
We have selected two primary models based on the complexity of the domain:

1.  **Merrill’s First Principles (The Surgical Approach):** 
    - Used for: **Procedural Tasks** (e.g., "Writing a Dockerfile," "Configuring a CronJob").
    - Pattern: Real-world Problem → Activation of prior knowledge → Demonstration → Guided Application → Professional Integration.
2.  **4C/ID Model (The Holistic Approach):**
    - Used for: **Complex Systems** (e.g., "SRE Troubleshooting," "Bare Metal Networking").
    - Pattern: Focus on "Whole Tasks" (Incident Response) while providing theory as "Supportive Information" and syntax as "Procedural Information" to manage cognitive load.

### B. Active Learning Techniques
- **Socratic Hooks:** Asking "What happens to the IP address if X happens?" before giving the answer.
- **Cognitive Symmetry:** The text must teach the specific mental model required to solve the corresponding lab challenge.

---

## 4. Lab Evolution: From Mimicry to Inquiry

The current lab baseline focuses on "Task Completion" (Step 1, Step 2). The new standard mandates **Inquiry-Based Labs**:

| Pattern | Description | Application in Dojo |
| :--- | :--- | :--- |
| **Kill Chain** | Adversarial progression through a series of gaps. | Used in Security Associate (KCSA) and CKS tracks. |
| **Observability-First** | Perform an action, then use tools (Prometheus/Logs) to "see" it. | Used in SRE and Debugging tracks. |
| **Chaos-Injected** | Introducing random failures during a maintenance task. | Used in On-Premises and Advanced Platform tracks. |
| **JIT Hinting** | Tiered hints that guide the "Where to look" rather than the "What to type." | Standard across all labs. |

---

## 5. Information Architecture Audit: Gap Identification

We have identified three distinct module health categories across the 7 domains:

1.  **Elite Lessons (20%):** High visual/technical depth. Only need "Pedagogical Wrappers" (Outcomes, Scenarios).
2.  **Dry Technical (50%):** Factually accurate but passive. Need "Instructional Energy" and Active Learning hooks.
3.  **Checklist Stubs (30%):** Command-heavy "manuals" with zero teaching. These are the primary targets for **300+ line technical expansions.**

---

## 6. Next Steps: Phase 2
Based on this research, we will now proceed to **Issue #170 (Phase 2)** to formalize the **Dojo-Standard (DS) Framework**—the non-negotiable constitution for all KubeDojo contributors.
