---
title: "Tools, Retrieval, and Boundaries"
slug: ai/ai-building/module-1.3-tools-retrieval-and-boundaries
sidebar:
  order: 3
---

> **AI Building** | Complexity: `[MEDIUM]` | Time: 40-55 min

## Why This Module Matters

Once a learner moves beyond plain prompting, the next temptation is to give the model more power:
- web search
- database lookups
- file access
- external APIs
- internal tools

That can make a system much more useful.

It can also make it much more dangerous.

## What You'll Learn

- the difference between retrieval and tool use
- when retrieval is enough
- when a tool is justified
- how to define boundaries before giving a system more power

## Retrieval And Tools Are Not The Same

### Retrieval

Retrieval means:
- fetch relevant information
- put it into context
- let the model answer using that material

Examples:
- RAG over internal docs
- policy lookup
- search over a handbook

### Tool use

Tool use means:
- the model can call a function or external action
- the system can inspect the result
- the workflow can continue with that result

Examples:
- run a search function
- open a ticket
- query a database
- read a repo file

Retrieval extends knowledge.
Tool use extends capability.

Capability requires more control.

## Good Escalation Path

Do not jump straight from plain prompting to broad autonomous tooling.

Safer progression:

1. prompt only
2. retrieved context
3. bounded read-only tools
4. write-capable tools with review
5. limited autonomous action in low-risk workflows

That is the same pattern good operators use in infrastructure:
increase power only when the control path is ready.

## When Retrieval Is Enough

Use retrieval when the problem is mainly:
- freshness
- bounded knowledge
- source grounding
- document answering

Examples:
- “What does our internal policy say?”
- “What changed in this release note?”
- “Summarize the incident doc using the actual text.”

## When A Tool Is Justified

Use a tool when the system truly needs to:
- fetch live data
- inspect a system state
- transform or validate something externally
- perform an action that plain context cannot do

Examples:
- query a monitoring endpoint
- inspect code files
- check ticket metadata

## Boundaries Before Capability

Before enabling a tool, answer:
- what can it access?
- what can it change?
- who is accountable for the result?
- how is usage logged?
- what is the fallback if it fails?

If those questions are fuzzy, the tool boundary is not ready.

## Practical Rule

Retrieval should usually come before tools.

Why?
- lower risk
- easier to reason about
- easier to debug
- easier to explain to learners and users

Many weak “agent” systems are really just poorly-bounded tool systems pretending to be smarter than they are.

## Example

Bad escalation:
- user asks a question
- system can immediately browse, write, change, and act

Better design:
- first answer from bounded knowledge
- if uncertainty remains, call one read-only tool
- if action is needed, route to a human approval step

## Active Check

You are building an internal documentation assistant.

Which is the better first step?
- give it ticket-creation and edit rights immediately
- start with document retrieval and sourced answers

The better answer is retrieval first.

## Common Mistakes

| Mistake | Why It Fails | Better Move |
|---|---|---|
| using tools because they seem advanced | adds complexity without need | use the smallest capability that solves the task |
| mixing retrieval and action too early | hard to debug and trust | separate knowledge access from action |
| giving write power without review | raises risk fast | start read-only, add approval gates |
| unclear ownership of tool outcomes | creates invisible failures | define operator responsibility explicitly |

## Quick Quiz

1. **What is the core difference between retrieval and tool use?**
   <details>
   <summary>Answer</summary>
   Retrieval adds information to context; tool use allows the system to call functions or external capabilities. Tool use expands what the system can do, not just what it knows.
   </details>

2. **Why should retrieval usually come before tool use in early systems?**
   <details>
   <summary>Answer</summary>
   It is lower risk, easier to validate, easier to debug, and often enough for knowledge-focused tasks.
   </details>

3. **What must be clear before enabling a tool?**
   <details>
   <summary>Answer</summary>
   Access scope, change scope, accountability, logging, and failure handling.
   </details>

## Hands-On Exercise

Pick one assistant idea and write:

1. one retrieval-only version
2. one tool-using version

Then compare:
- what extra value the tool gives
- what extra risk it creates
- whether the tool is justified for v1

## Next Module

Continue to [Evaluation, Iteration, and Shipping v1](./module-1.4-evaluation-iteration-and-shipping-v1/).

## Sources

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — Foundational paper on retrieval-augmented generation, relevant to the module's distinction between adding knowledge and extending capability.
- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — Practical guidance on choosing tools, workflows, and human approvals instead of adding broad autonomy too early.
- [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — Risk framework for tool boundaries, external access, and action-taking systems.
