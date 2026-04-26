---
revision_pending: true
title: "What Are LLMs?"
slug: ai/foundations/module-1.2-what-are-llms
sidebar:
  order: 2
---

> **AI Foundations** | Complexity: `[QUICK]` | Time: 40-55 min

## Why This Module Matters

Most people now meet AI through large language models before they understand what those systems are.

That creates bad habits quickly:
- treating them like search engines
- treating them like experts
- treating them like minds
- treating them like autocomplete and therefore underestimating them

All four mental models are incomplete.

If you want to use LLMs well, you need a model that is honest enough to explain both:
- why they are surprisingly useful
- why they fail in ways that feel weird and dangerous

## What You'll Learn

By the end of this module, you should be able to:
- explain what an LLM does in practical terms
- distinguish tokens, context, and next-token prediction
- analyze why LLMs can be useful without being reliably truthful
- decide when an LLM is appropriate and when another tool is better

## Start With The Simplest Honest Description

An LLM is a model [trained on large amounts of text to predict the next most likely token in a sequence](https://arxiv.org/abs/2005.14165).

That sounds almost too simple.

But at scale, this simple mechanism produces [surprisingly capable behaviors](https://en.wikipedia.org/wiki/Large_language_model):
- explanation
- rewriting
- summarization
- code completion
- translation
- structured output

The most important sentence in this module is:

> prediction is not the same as understanding

If you remember that, you will avoid a large fraction of beginner mistakes.

## Tokens, Context, and Prediction

These three ideas explain most of the system behavior learners notice.

### Tokens

Models do not read text exactly the way humans do.

They process [tokens](https://en.wikipedia.org/wiki/Large_language_model), which may be:
- whole words
- pieces of words
- punctuation
- formatting markers

This matters because [limits are measured in tokens, not pages](https://en.wikipedia.org/wiki/Context_window).

If a model says it has a large context window, that means it can consider a larger token budget, not that it suddenly “understands” everything inside it.

### Context

Context is the information currently available to the model during the interaction.

That may include:
- your prompt
- prior messages
- attached documents
- retrieved snippets
- tool outputs

If the right information is missing, the model cannot reliably use it.

This is one reason people think a model is “dumb” in one situation and “brilliant” in another:
- often the context changed
- not necessarily the model itself

### Next-Token Prediction

At the core, the model repeatedly does something like:

```text
given everything so far, what token is most likely to come next?
```

This process happens token by token.

At scale, it creates outputs that feel:
- conversational
- coherent
- adaptive
- sometimes strategic

That explains both the power and the risk.

## Pause And Think

If a model gives a polished explanation of a topic that never appeared in the provided context, what should you suspect first?

Not hidden wisdom.

Usually:
- prior training patterns
- plausible reconstruction
- confident guessing

That is useful sometimes.

It is also exactly how fabrication happens.

## The Strongest Useful Mental Model

An LLM is best thought of as:
- a strong pattern-completion engine
- a language interface over learned statistical structure
- a system that is often helpful before it is reliable

This is better than:
- “it thinks like a person”
- “it is just autocomplete”

Why?

Because “thinks like a person” gives it too much credit, while “just autocomplete” ignores the scale and flexibility of the behaviors it can produce.

## Why LLMs Feel So Smart

LLMs are strong at:
- producing fluent language
- adapting tone and style
- summarizing across large inputs
- generating plausible structure
- following constrained output formats

Humans naturally associate those traits with intelligence.

But these are not the same as:
- truth
- judgment
- grounded expertise
- consistent reasoning

This mismatch is the root of many beginner mistakes.

## What LLMs Usually Do Well

LLMs are often strong at:
- drafting
- rewriting
- summarizing
- brainstorming
- translating between formats
- explaining ideas at different levels

These are tasks where:
- language fluency matters
- multiple good answers are acceptable
- exact truth is not the only criterion

## What LLMs Often Do Poorly

LLMs often struggle with:
- precise factual grounding without sources
- knowing when they should stop and say “I don’t know”
- maintaining reliability on ambiguous tasks
- separating likely from verified
- handling missing context honestly

These are not edge cases.

They are normal consequences of how the systems work.

## LLMs Are Not Search Engines

Search systems are built to [retrieve known information](https://developer.mozilla.org/en-US/docs/Glossary/search_engine).

LLMs are built to generate language that fits the context and learned patterns.

Sometimes those overlap.

But if you ask an LLM for factual answers without:
- retrieval
- sources
- verification

you are often asking the wrong tool to do the wrong job.

This is why a strong user asks:

> “Do I need generation, retrieval, or both?”

## LLMs Are Also Not People

LLMs do not have:
- human stakes
- lived experience
- internal honesty
- genuine accountability

They can imitate all of those in language.

That is exactly why trust discipline matters.

If a system can sound:
- careful
- wise
- apologetic
- confident

then your trust must come from verification, not tone.

## Worked Example: Same Task, Better Framing

Weak prompt:

```text
Explain Kubernetes to me.
```

Better prompt:

```text
Explain Kubernetes to a beginner who already knows Linux and Docker.

Use:
- one analogy
- five essential concepts
- one warning about a common misunderstanding

If something here would require deeper study, label it as advanced.
```

The second prompt is better because it gives:
- audience
- structure
- constraints
- scope control

That does not guarantee truth.

It does improve task fit.

## Did You Know?

- **Tokens are a real design constraint**: a model’s context behavior depends heavily on how much relevant information can fit, not just how “smart” the model seems.
- **Fluent errors are normal**: many LLM failures are not obvious nonsense; they are plausible mistakes delivered in smooth language.
- **Task shape changes output quality**: better scope, clearer audience, and output constraints often help more than vague “be smarter” prompts.
- **The same model can feel inconsistent for non-mysterious reasons**: context changes, ambiguity changes, and prompt shape changes often explain the difference.

## Common Mistakes

| Mistake | Why It Fails | Better Move |
|---|---|---|
| treating LLMs like factual databases | generation is not retrieval | use retrieval or verify against sources |
| trusting confidence of tone | style is not truth | separate fluency from evidence |
| assuming more tokens means real understanding | context size is not judgment | ask what is actually grounded |
| giving vague prompts and blaming the model alone | task ambiguity lowers output quality | define audience, format, and scope |
| assuming “bigger model” removes the need to verify | scale improves capability, not perfect reliability | keep trust boundaries |
| asking for certainty where the context is incomplete | pushes the model toward confident guessing | allow uncertainty explicitly |

## Quick Quiz

1. **Why is “next-token prediction” still a useful explanation even though LLM behavior feels much richer than that phrase sounds?**
   <details>
   <summary>Answer</summary>
   Because it explains the core mechanism honestly. The richness comes from scale, training, and context, but the underlying process still helps explain why the system can be fluent without being reliably truthful.
   </details>

2. **Why is “the model sounded certain” a weak trust signal?**
   <details>
   <summary>Answer</summary>
   Because LLMs are optimized for coherent language generation, and confidence of tone can appear even when the underlying answer is guessed, incomplete, or wrong.
   </details>

3. **What is the practical difference between context and knowledge in an LLM interaction?**
   <details>
   <summary>Answer</summary>
   Context is the information currently available in the interaction. “Knowledge” is whatever patterns the model learned during training. Good performance often depends on putting the right information into context rather than assuming the model already has it.
   </details>

4. **When is an LLM often a better fit than a search engine?**
   <details>
   <summary>Answer</summary>
   When the task is drafting, reframing, summarizing, or explaining. Search is stronger when the core need is current or source-grounded factual retrieval.
   </details>

5. **Why is “just autocomplete” too weak as a mental model?**
   <details>
   <summary>Answer</summary>
   Because it ignores how much useful structure, adaptation, formatting, and task performance can emerge from large-scale token prediction over rich context.
   </details>

6. **What should you ask before trusting an LLM answer on an important topic?**
   <details>
   <summary>Answer</summary>
   What part of this answer is grounded, what part needs verification, and whether this task required retrieval or external evidence rather than language generation alone.
   </details>

## Hands-On Exercise

Take one real task and run it in two versions:

1. a vague prompt
2. a scoped prompt with:
   - audience
   - output format
   - explicit uncertainty allowance
   - boundaries on what the model should not assume

Then compare:
- clarity
- usefulness
- how easy the answer is to verify

**Success Criteria**:
- [ ] you can explain how prompt structure changed the output
- [ ] you identify which claims still require verification
- [ ] you can state whether the task was really generation, retrieval, or both

## Summary

LLMs are powerful because language is a flexible interface to many tasks.

They are risky because fluency, confidence, and correctness are not the same thing.

A strong learner does not reduce them to either:
- magic minds
or
- useless autocomplete

Instead, a strong learner understands:
- tokens
- context
- prediction
- trust boundaries

That is what turns LLM use from novelty into disciplined practice.

## Next Module

Continue to [Prompting Basics](./module-1.3-prompting-basics/).

## Sources

- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) — Canonical GPT-3 paper showing large autoregressive language models performing next-token prediction with broad downstream capabilities.
- [Large language model](https://en.wikipedia.org/wiki/Large_language_model) — Overview of how LLMs tokenize text and what language tasks they commonly perform.
- [Context window](https://en.wikipedia.org/wiki/Context_window) — Explains the amount of text a model can consider at once and why those limits are measured in tokens.
- [Search engine](https://developer.mozilla.org/en-US/docs/Glossary/search_engine) — Concise definition of search engines as systems for retrieving relevant information in response to a query.
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — Foundational transformer paper that underpins most modern large language model architectures.
