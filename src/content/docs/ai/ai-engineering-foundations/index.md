---
title: "AI Engineering Foundations"
slug: ai/ai-engineering-foundations
sidebar:
  order: 1
  label: "AI Engineering Foundations"
---

> **AI Engineering Foundations** | 12 planned modules | prompt, context, harness, and Symphony

## Purpose

This section teaches the engineering layer between casual AI tool use and production agent operations.

The organizing model is the prompt | context | harness triplet.

Prompt work defines the instruction interface.

Context work manages what the model sees on each turn.

Harness work turns repeated agent work into enforceable, observable systems.

The final arc applies those layers to Symphony-style orchestration, where issue contracts, lifecycle hooks, and multi-agent review loops become a control plane for AI-assisted engineering.

Stage-0 planning lives in the internal brief: [docs/research/ai-engineering-foundations-stage0-2026-05-15.html](../../../../docs/research/ai-engineering-foundations-stage0-2026-05-15.html).

## Planned Modules

| Module | Topic | Status |
|---|---|---|
| 1.1 | Prompt Fundamentals | planned |
| 1.2 | Prompt Debugging and Evaluation | planned |
| 1.3 | Prompt Libraries and Contracts | planned |
| 2.1 | [Context Engineering Fundamentals](module-2.1-context-fundamentals/) | drafting |
| 2.2 | Repository Engineering for Agents | planned |
| 2.3 | Retrieval, Tools, and Memory Boundaries | planned |
| 3.1 | Harness Fundamentals | planned |
| 3.2 | Guardrails, Gates, and Traces | planned |
| 3.3 | Agent Runtime Operations | planned |
| 4.1 | Symphony Control Plane | planned |
| 4.2 | Multi-Agent Review Loops | planned |
| 4.3 | Symphony Capstone | planned |

## Reading Path

Start with prompt fundamentals if you need the instruction-design baseline.

Move to context fundamentals when the same prompt behaves differently across fresh sessions, agents, repositories, or model windows.

Use the harness modules when good individual sessions need to become repeatable team workflows.

Use the Symphony capstone only after the lower layers feel boring enough to operate.
