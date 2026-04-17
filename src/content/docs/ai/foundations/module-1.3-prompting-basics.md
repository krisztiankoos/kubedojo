---
title: "Prompting Basics"
slug: ai/foundations/module-1.3-prompting-basics
sidebar:
  order: 3
---

> **AI Foundations** | Complexity: `[QUICK]` | Time: 30-40 min

## Why This Module Matters

Prompting is not magic. It is task framing.

Most bad AI output starts with vague goals, missing constraints, or weak context. Better prompting does not guarantee truth, but it makes the interaction far more useful.

## What You'll Learn

- how to ask for the right kind of output
- how to add context, constraints, and format
- how to iterate instead of expecting one-shot perfection
- when prompting is the wrong fix for a bad workflow

## A Strong Prompt Usually Includes

- **goal**: what you want
- **context**: what the model needs to know
- **constraints**: limits, tone, format, boundaries
- **evaluation standard**: what counts as good

## Better Prompting Habits

- ask for a specific output shape
- tell the model what assumptions to avoid
- request uncertainty when the answer is unclear
- prefer short iterative loops over giant kitchen-sink prompts

## Weak Prompt vs Better Prompt

Weak:

```text
Explain Kubernetes.
```

Better:

```text
Explain Kubernetes to a beginner who knows Linux and Docker but has never used a cluster.
Use plain language, one analogy, and a short list of the core objects to learn first.
```

## Common Mistakes

- asking broad questions with no audience or format
- trying to solve trust problems with prompt wording alone
- overfitting to “prompt tricks” instead of clarity

## Next Module

Continue to [How to Verify AI Output](./module-1.4-how-to-verify-ai-output/).
