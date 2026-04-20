---
title: "AI Agents and Assistants"
slug: ai/ai-native-work/module-1.2-ai-agents-and-assistants
sidebar:
  order: 2
---

> **AI-Native Work** | Complexity: `[QUICK]` | Time: 30-40 min

## Why This Module Matters

People use “agent” to mean too many different things.

That creates bad workflow decisions:
- over-automation
- unclear accountability
- false expectations

## What You'll Learn

- the difference between chat, assistant, and agent patterns
- when agents help
- when agents add complexity instead of value
- how to choose the right level of autonomy

## The Core Confusion

People often use these words as if they were interchangeable:
- chatbot
- assistant
- copilot
- agent

They are not interchangeable.

If you collapse them into one category, you make poor workflow decisions:
- you automate too much
- you trust the system too early
- you stop designing proper checkpoints

## Simple Distinction

- **chat**: one-off interaction
- **assistant**: helps inside a bounded workflow
- **agent**: can plan, use tools, or act across steps with some autonomy

That autonomy is the important part.

An agent is not just “better chat.” It is a system allowed to do more than answer.

## A Better Mental Model

Think of these as increasing levels of delegated responsibility:

- **chat** helps you think
- **assistant** helps you work
- **agent** helps carry out a bounded process

The more responsibility you delegate, the more you need:
- constraints
- visibility
- review
- rollback paths

## When A Simple Assistant Is Enough

Use an assistant when you want help with:
- drafting
- summarization
- organizing notes
- explaining code
- checking syntax or structure

These tasks benefit from guidance, but they do not require autonomous action.

## When An Agent Actually Helps

Agents help when the task has:
- multiple steps
- tools to call
- a stable goal
- repeatable structure
- clear boundaries for action

Examples:
- inspect a codebase, propose a patch, and run tests
- gather artifacts for a recurring reporting workflow
- apply a fixed review process across many items with checkpoints

## When An Agent Is The Wrong Choice

Avoid agents when:
- the task is mostly one-shot reasoning
- requirements are still vague
- the cost of wrong action is high
- human ownership is unclear
- a checklist or script would solve the problem more simply

This matters because agent systems create coordination cost.

If the work is not inherently multi-step, you are often building ceremony, not value.

## Practical Rule

Do not use agents because they sound advanced.

Use them when the task actually benefits from:
- multiple steps
- tool use
- repeated stateful interaction
- controlled autonomy

## A Safer Delegation Ladder

When introducing AI into real work, climb this ladder gradually:

1. chat only
2. assistant with suggestions
3. assistant with bounded tool use
4. agent with explicit review gates
5. agent with limited autonomous execution in low-risk contexts

Skipping steps usually creates trust problems faster than productivity gains.

## Summary

Agents are not automatically the goal.

They are one pattern among several:
- chat for thinking
- assistants for bounded help
- agents for structured multi-step execution

The right question is not:

> “Can I use an agent here?”

It is:

> “Does this workflow genuinely benefit from delegated action, and do I have enough control to use it safely?”

## Next Module

Continue to [Designing AI Workflows](./module-1.3-designing-ai-workflows/).

## Sources

- [Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents) — Explains the distinction between workflows and agents, with emphasis on when added autonomy is worth the coordination cost.
- [A Practical Guide to Building Agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) — Provides practical guidance on choosing appropriate levels of autonomy and designing bounded agentic systems safely.
