---
title: "Prompting Basics"
slug: ai/foundations/module-1.3-prompting-basics
revision_pending: false
sidebar:
  order: 3
---

> **Complexity**: `[QUICK]`
>
> **Time to Complete**: 30-40 min
>
> **Prerequisites**: Basic comfort with AI chat tools, command-line examples, and the idea that Kubernetes runs workloads in clusters.

---

## Learning Outcomes

- Design task context constraints output format prompts for beginner education and Kubernetes troubleshooting.
- Evaluate prompt uncertainty assumptions and verification boundaries before trusting AI output.
- Diagnose prompt drift instruction leakage and missing source material in multi-step workflows.
- Implement iterative prompting loops that separate draft refinement and validation.

## Why This Module Matters

Hypothetical scenario: your platform team is preparing a short troubleshooting note after a failed Kubernetes rollout, and someone asks an AI assistant to help draft it from a few log excerpts. The first answer sounds fluent, but it invents one command flag, assumes a cloud provider feature that your cluster does not use, and formats the result as a long essay when the team needed a two-column action table. The problem is not that prompting is magic and the team used the wrong spell. The problem is that the task, context, constraints, output format, and verification boundary were never made explicit.

Prompting is disciplined task framing. A useful prompt tells the model what work to do, what information to use, what assumptions to avoid, what shape the answer should take, and how the answer will be judged. Better prompting does not guarantee truth, because a model can still reason from incomplete context or produce a plausible mistake. It does, however, make the interaction easier to inspect, easier to repeat, and easier to connect to a human review workflow.

This module treats prompting as an engineering habit rather than a bag of tricks. You will preserve the simple mental model from the earlier foundations modules, then apply it to beginner education, Kubernetes troubleshooting, structured output, uncertainty handling, and iterative refinement. The goal is not to memorize a perfect prompt template. The goal is to design conversations where the next answer is more likely to be useful, and where the remaining risk is visible enough for a human to verify.

## Prompting Is Task Framing

A prompt is not a spell. It is the way you define the task, the context, the boundaries, and the output you want. When a prompt fails, the root cause is often not that the model needed a more exotic phrase. The root cause is usually that the work itself was underspecified, so the model filled the gaps with common patterns from its training data.

That distinction matters because vague prompts give the model too many valid paths. If you ask, "Explain Kubernetes," the answer could target a school student, a Linux administrator, a cloud architect, or a certification candidate. Each answer could be technically reasonable while still being wrong for your use case. A stronger prompt narrows the target audience, the current knowledge level, the depth, and the shape of the output before the model starts generating.

Think of a prompt like the intake form for a specialist. If you walk into a clinic and say "I feel bad," the clinician has to ask follow-up questions before acting. If you say "I have a fever, started yesterday, no chest pain, and I need to know whether to seek urgent care," the conversation becomes more useful. Prompting works the same way: better initial framing reduces wasted turns and makes follow-up questions sharper.

The most useful beginner framework is simple: Task, Context, Constraints, and Output format. The task states what work should be done. The context supplies the facts the model should use. The constraints prevent dangerous or irrelevant paths. The output format defines how the answer should be shaped so a human or downstream tool can use it.

```text
Task
Context
Constraints
Output format
```

This framework is intentionally plain because beginners need a pattern they can actually remember under pressure. It works for educational explanations, code review, troubleshooting notes, planning documents, and research summaries. It also scales into production workflows, where those same fields become system instructions, retrieved context, schema requirements, and validation checks.

Here is the compact example from the original module. Notice that the prompt does not try to control every possible detail. It names the comparison, the audience, the length, the jargon boundary, and the desired final shape, which is enough to turn a broad topic into a useful first answer.

```text
Task: Compare Docker and Kubernetes.
Context: Audience is a junior engineer with Linux basics.
Constraints: Keep it under 300 words. Avoid jargon where possible.
Output format: short explanation + 3-bullet comparison table.
```

The same idea applies to technical operations. A prompt for Kubernetes troubleshooting should say which cluster version, which symptom, which logs or manifests are available, and what actions are allowed. If the assistant is allowed to suggest only read-only commands first, say that. If the team uses Kubernetes 1.35 and does not want deprecated API advice, say that too.

Pause and predict: what do you think happens if you ask for "a fix" without saying whether the assistant may change cluster state? Most models will provide some confident-looking remediation because "fix" implies action. A safer prompt separates diagnosis from remediation and asks for read-only evidence first, which keeps the model from racing toward a command before the cause is clear.

```markdown
### ROLE
You are a Senior SRE specialized in Kubernetes Python automation.

### TASK
Write a script to audit ImagePullPolicy settings across a cluster.

### CONSTRAINTS
- Library: `kubernetes-python-client`
- Logic: Flag any container using 'Always' for images with the 'stable' tag.
- Format: Markdown table with columns [Namespace, PodName, ContainerName, Policy].

### CONTEXT
The cluster uses RBAC; assume the ServiceAccount has 'list' permissions on pods across all namespaces.
```

That example works because each part removes a different kind of ambiguity. The role tunes the level and domain. The task tells the model what artifact to produce. The constraints prevent the answer from drifting into a different library or a different output format. The context tells the model which access assumptions are valid, which is critical because Kubernetes automation advice changes when the ServiceAccount can only read namespaced resources.

Prompting still has a hard boundary: it improves the question, not the facts. If the cluster state is missing, a prompt cannot invent trustworthy evidence. If the user supplies only a summary of logs, a good answer should say which evidence is absent. Strong prompting therefore includes a verification posture, such as "separate facts from inferences" or "return insufficient context when the provided data does not support a conclusion."

## Context, Constraints, And Output Shape

Context is the material the model should reason from, not a dumping ground for every possible note. Good context is relevant, labeled, and separated from instructions. If you paste raw logs, a ticket comment, and a desired answer into one unmarked block, the model has to infer which text is evidence and which text is instruction. That confusion is one source of instruction leakage, where data accidentally behaves like a new command.

Clear delimiters reduce that risk. You can use section headings, XML-like tags, fenced blocks, or explicit labels such as "evidence" and "requirements." The delimiter style matters less than the separation it creates. Avoid placing raw delimiter characters inline in prose where they can confuse Markdown rendering, and prefer headings or labeled blocks when the prompt will be copied into documentation.

Constraints are not only about tone. In engineering work, constraints often define allowed tools, forbidden assumptions, safety rules, target versions, and parsing requirements. A Kubernetes answer may need to avoid cluster-changing commands until diagnosis is complete. A privacy-sensitive summary may need to exclude personal data. A code-generation prompt may need to produce one file, use a specific library, and avoid network access.

Output shape is the part many beginners skip, even though it is one of the fastest ways to improve reliability. If you need a checklist, ask for a checklist. If you need a JSON object, ask for valid JSON and name the keys. If a teammate will paste the result into a runbook, ask for a short problem statement, evidence table, and command sequence instead of a conversational essay.

Consider this Kubernetes troubleshooting prompt. It preserves the original module's structure while updating the cluster target to Kubernetes 1.35. The important lesson is not the exact wording, but the way the prompt tells the model how to behave before it sees the evidence.

```markdown
### Task
Analyze the provided `kubectl describe pod` output for errors.

### Context
The cluster is running on GKE version 1.35. A recent ConfigMap update was applied to this namespace.

### Constraints
- Do not suggest restarting the pod unless you identify a CrashLoopBackOff.
- Provide the exact `kubectl` command to fix the identified issue.
- Limit the explanation to three bullet points.

### Output Format
Return a YAML object with keys: `issue`, `root_cause`, and `remediation`.
```

Before running this, what output do you expect if the provided pod description contains only `ImagePullBackOff` events and no ConfigMap reference? A well-framed assistant should focus on image retrieval, avoid blaming the ConfigMap without evidence, and keep the answer in the requested YAML shape. If it still blames the ConfigMap, the prompt or the verification step should catch that unsupported inference.

Negative constraints are especially useful when the default advice would be wrong for your environment. Many AI answers assume cloud-managed identity, cluster-admin permissions, or a willingness to install another tool. If those assumptions are false, state them directly. This is not micromanagement; it is environment modeling, the same way an engineer writing a runbook names prerequisites before giving commands.

```yaml
# Example: Prompting with Negative Constraints and Structured Output
role: Kubernetes Security Auditor
task: Review the provided PodSpec for privilege escalation risks.
constraints:
  - Do NOT suggest third-party tools like Kubescape or Trivy.
  - Avoid assuming the presence of an OIDC provider.
  - If no risks are found, explicitly state "No immediate risks identified."
output_format: |
  JSON object with the following keys:
  - risk_level: (High, Medium, Low)
  - findings: List of strings
  - remediation: String (native K8s manifests only)
```

The safest prompts also tell the model what to do when evidence is missing. For example, "If the provided logs do not include the container status, ask for it instead of guessing" creates a useful stop condition. In human terms, it gives the assistant permission to pause. Without that permission, the model may continue with a plausible explanation because it is optimized to be helpful.

There is a tradeoff here. More constraints can produce more predictable output, but too many constraints can make the prompt brittle or internally inconsistent. If the prompt says "be concise," "explain every tradeoff," "include all commands," and "keep it under six lines," the model has to violate something. Good prompting is therefore not maximum instruction count; it is coherent instruction design.

## Weak Prompts, Better Prompts, And Prompt Drift

The fastest way to feel the difference is to compare a weak prompt with a better one. The weak version below is not technically wrong. It is just too broad to be useful for a specific learner, because it leaves the audience, depth, analogy, and output shape undefined.

```text
Explain Kubernetes.
```

A better version keeps the same topic but gives the assistant a target. The model can now decide what to include and what to leave out because it knows the learner already understands Linux and Docker but has never used a cluster. That boundary is the difference between a generic encyclopedia answer and a useful bridge from existing knowledge to new concepts.

```text
Explain Kubernetes to a beginner who knows Linux and Docker but has never used a cluster.
Use plain language, one analogy, and a short list of the core objects to learn first.
```

The second prompt is better because the audience is clear, the expected level is clear, the answer shape is constrained, and the model is less likely to drift into advanced material. It also gives the human reviewer a quick way to judge the result. If the answer uses advanced networking terminology without explanation, it violated the prompt. If it produces a long architecture essay instead of a short list, it violated the prompt.

Prompt drift happens when the model gradually moves away from the original goal across a long conversation or a complex prompt. This can happen because the conversation accumulates side topics, because later instructions conflict with earlier ones, or because the model overweights recent text. The practical fix is not to scold the model. The fix is to restate the task boundary, summarize the accepted facts, and ask for a constrained next step.

For technical teams, prompt drift becomes expensive when AI output is copied into docs, tickets, or automation without checking whether it still matches the original problem. A troubleshooting assistant may begin by diagnosing `CrashLoopBackOff`, then drift into generic restart advice, then suggest a command that hides evidence. A good workflow forces each step to name evidence, confidence, and remaining uncertainty before moving to action.

The professional iteration below adds a role, a narrower task, a context bridge, a negative constraint, and a table format. It is still not a guarantee of correctness, but it is much easier to evaluate because the valid answer space is smaller.

```text
Role: Senior DevOps Educator
Task: Explain the Kubernetes Control Plane (kube-apiserver, etcd, scheduler, controller-manager).
Context: The user understands centralized server architectures but is new to distributed consensus.
Constraint: Do NOT use the 'Ship Captain' analogy. Use a 'Restaurant Kitchen' analogy instead.
Format: Use a Markdown table to map each component to a kitchen role.
```

Which approach would you choose here and why: one long prompt that explains all of Kubernetes, or two shorter prompts where the first explains the control plane and the second asks for a beginner self-check? The two-step version is usually easier to verify because each answer has one job. It also lets you correct a bad analogy or missing concept before the model builds more content on top of it.

The deeper lesson is that prompts act like contracts. A contract does not make the other party perfect, but it clarifies obligations and makes violations visible. In prompting, the obligations are the task, the evidence boundary, the constraints, and the output shape. When those obligations are explicit, a human can review the answer against the prompt instead of judging only whether it sounds confident.

## Iteration Beats Giant Prompts

Many learners assume the model should give the perfect answer in one try. That expectation creates bloated prompts, hidden contradictions, and disappointing results. In real work, a better pattern is to ask for a first draft, inspect what is missing, refine with a narrow follow-up, and verify the final result against source material. Iteration is not failure; it is how you keep the conversation observable.

A giant prompt can be tempting because it feels thorough. You can include background, examples, edge cases, policy rules, formatting requirements, and a demand for perfect accuracy. The problem is that each extra instruction competes for attention, and some instructions may conflict. When the output is wrong, you then have a debugging problem: was the context bad, was the constraint unclear, was the output format too strict, or was the task itself too broad?

An iterative loop separates those concerns. First, ask for a draft or diagnosis. Second, ask the model to identify missing evidence or assumptions. Third, ask for a revised answer that uses only confirmed facts. Fourth, verify the result manually or with a deterministic tool. This pattern is slower than a single prompt only when the single prompt works perfectly, which is not the case you should design around.

For beginner education, iteration also improves learning. If you ask for an explanation and then ask the model to quiz you, you can see whether the explanation created the right mental model. If the quiz reveals confusion, you refine the explanation. This is the same teaching cycle a good instructor uses: explain, check, adapt, and practice.

For operations, iteration keeps risk visible. A first prompt might request a diagnosis table with columns for symptom, evidence, likely cause, and missing evidence. A second prompt might ask for read-only commands to gather the missing evidence. A third prompt might ask for remediation options, explicitly ranked by reversibility. Each step has a narrower blast radius than asking for "the fix" immediately.

The key is to preserve state deliberately between turns. Do not rely on the model to remember every nuance from a long chat. Summarize the accepted facts, unresolved questions, and current objective before asking for the next action. That summary becomes a checkpoint, and it gives you a place to catch drift before it becomes a misleading final answer.

Iteration also helps you decide when prompting is no longer the right tool. If three refinement turns still cannot produce a grounded answer, the problem may be missing evidence, unclear ownership, or a workflow that requires a different system. A better prompt cannot replace logs, tests, domain review, or a real source of truth. Knowing when to stop prompting is part of prompting well.

## Uncertainty And Verification Boundaries

Strong prompts ask for uncertainty because confident language is not the same as verified truth. A model can produce a fluent answer even when the evidence is incomplete, stale, or outside the provided context. If your prompt rewards certainty, the answer may hide the exact gaps a human needs to inspect. If your prompt rewards calibrated uncertainty, the answer can separate facts, inferences, assumptions, and next checks.

This distinction is especially important in AI-assisted technical work. Kubernetes commands, API versions, cloud-provider features, and library behavior change over time. A model may remember a pattern that used to be common, or blend two similar tools into one answer. Prompting should therefore create a verification boundary: what may be answered from the provided context, what requires documentation, and what must be tested in the environment.

A useful verification-oriented prompt might say, "Use only the pasted manifest and events for diagnosis; if you need cluster-wide context, list the exact read-only command needed to obtain it." That wording prevents the model from silently importing assumptions. It also produces a useful next action when the answer cannot be completed from the current evidence.

Another useful pattern is to ask for a confidence label with evidence, not just a number. A bare confidence score can look scientific while adding little value. A better answer says, "High confidence because the event shows image authentication failure," or "Low confidence because the logs do not include the container exit reason." The explanation lets a human inspect whether the confidence is justified.

Be careful with prompts that ask the model to "think step by step" in every situation. For some tasks, a concise rationale or evidence table is enough and safer to share. For other tasks, such as debugging a multi-condition failure, explicit reasoning can help expose assumptions. The practical rule is to ask for the amount of reasoning that helps verification, not the most verbose reasoning possible.

Verification boundaries are also ethical boundaries. If the task involves privacy, security, compliance, or operational risk, the prompt should name what data is allowed, what data must be excluded, and who reviews the result. Prompting does not transfer accountability to the model. The person or team using the output still owns the decision to act.

## Worked Example: From Vague To Reviewable

The easiest way to practice prompting basics is to transform a vague request into a reviewable request one layer at a time. Suppose you start with the sentence "Help me write a note about a broken deployment." That sentence communicates frustration, but it does not communicate the audience, the evidence, the desired output, the allowed assumptions, or the review standard. A model can still produce an answer, but almost any answer could be defended because the original request created no meaningful boundaries.

The first improvement is to name the actual task. "Draft an incident-note outline for a Kubernetes deployment that failed readiness after a ConfigMap change" is already much better than "help me write a note." It tells the model that the output is a draft, not a final incident report, and that the subject is a readiness failure, not a general deployment problem. It also tells the human reviewer what kind of answer to expect before reading the first paragraph.

The second improvement is to add context that the model should use. Context is not a memory test for the model; it is the evidence packet you want it to reason from. If the context says the namespace, workload name, recent change, observed event, and missing evidence, the assistant can keep its reasoning anchored. If the context omits those details, the assistant may invent common deployment-failure patterns that sound plausible but do not match the situation.

The third improvement is to state constraints that prevent premature action. In the deployment scenario, a good constraint might say, "Do not suggest deleting, restarting, or rolling back anything until the diagnosis lists supporting evidence and missing evidence." That sentence is valuable because it changes the assistant's default posture. Instead of optimizing for a quick fix, the model is being asked to preserve evidence and move in a controlled sequence.

The fourth improvement is to choose an output shape that supports review. A paragraph can be readable, but a table often makes uncertainty easier to inspect. For this kind of diagnosis, columns like Observed Fact, Inference, Confidence, Missing Evidence, and Next Read-Only Check are useful because they force the model to separate what was supplied from what it believes. A reviewer can then scan for unsupported inferences before any action is taken.

The fifth improvement is to ask for a stop condition. A stop condition tells the assistant what to do when the answer cannot be completed responsibly. For example, "If the evidence does not support a root cause, say `insufficient context` and list the smallest evidence request needed next." That instruction is not a magic guarantee, but it gives the model a permitted behavior other than guessing, which is exactly what you want in incomplete troubleshooting.

Once those layers are in place, the prompt becomes easier to test. You can paste an evidence packet that contains only a missing ConfigMap event and ask whether the assistant stays within the provided facts. If the answer claims that the Deployment template has the wrong `configMapKeyRef`, it has overreached unless the manifest was provided. If it says the event indicates a missing ConfigMap and requests the relevant manifest or full pod description, the prompt is doing useful work.

This example also shows why prompt quality and evidence quality are separate concerns. A weak prompt with strong evidence may still produce a messy answer, but a strong prompt with weak evidence should still refuse to overclaim. That refusal is a feature, not a failure. In operational work, a model that clearly says what it cannot determine is often more useful than one that produces a confident remediation from incomplete data.

Now consider the same request from a documentation perspective. If the desired output is an internal note for junior engineers, the prompt should ask for plain language, short sections, and a clear distinction between symptom and cause. If the desired output is a ticket update for senior SREs, the prompt can be denser and more specific. Audience changes the answer, so audience belongs in the prompt rather than in the user's unstated expectations.

The review standard should also change with the audience. For a junior-facing note, you might require definitions for `ConfigMap`, `volume mount`, and `readiness`. For a senior-facing note, you might require exact evidence, omitted speculation, and links to runbook sections. In both cases, the model needs to know what "good" means. Without that standard, it may optimize for fluent writing instead of useful writing.

The same layered method applies outside Kubernetes. If you ask for help planning a study schedule, the task is the schedule, the context is your available time and current skill level, the constraints are deadlines and topics, and the output format might be a weekly plan. If you ask for help reviewing code, the task is review, the context is the diff and design goal, the constraints are style or safety rules, and the output format might be findings ordered by severity.

This is why the framework is portable. It does not depend on a specific vendor, model family, or secret phrase. It depends on making the work visible. The model can then use the visible structure to produce a more relevant answer, and the human can use the same structure to evaluate whether the answer did what was requested. That shared structure is the practical value of prompting basics.

There is one more habit that helps: write the prompt so another human could understand the task without reading your mind. If the prompt would confuse a teammate, it will probably confuse the model too. This rule keeps you honest because it turns prompting into normal communication. You are not trying to manipulate a system with incantations; you are specifying work for a language tool that responds to the structure you provide.

When the first answer arrives, resist the urge to immediately ask for "better." Name the specific defect instead. "The answer mixes facts and assumptions; rewrite it with separate Fact, Inference, and Missing Evidence sections" is much better than "make it more accurate." Specific critique gives the model a target, while vague dissatisfaction invites another broad guess. Iteration works best when each follow-up repairs one identified weakness.

If the answer is structurally good but technically questionable, do not keep prompting as though wording alone will solve it. Move to verification. Check the command against official documentation, run a harmless equivalent in a test environment, or ask a domain reviewer to inspect the claim. The prompt can help organize the next check, but it should not be treated as the source of truth for the check itself.

If the answer is technically plausible but poorly shaped, the next prompt can focus on formatting. Ask for a table, a checklist, or a shorter executive summary using only the already accepted facts. This separation keeps content review and style review from getting tangled. Teams often lose time because they ask for a prettier answer before deciding whether the answer is correct.

If the answer is both wrong and poorly shaped, go back to the task boundary rather than patching the output line by line. Restate the audience, evidence, constraints, and output format, then ask for a fresh attempt. Sometimes the best iteration is a reset with a better prompt. A long conversation full of corrections can become harder for the model to follow than a clean prompt that summarizes the accepted state.

The worked example should leave you with a practical checklist for your own prompts. Can a reviewer identify the task? Can they see the context the answer is allowed to use? Can they see the constraints that prevent unsafe or irrelevant advice? Can they tell what output shape is expected? Can they tell what the model should do when evidence is missing? If any answer is no, improve the prompt before blaming the model.

In professional settings, this habit has a social benefit as well as a technical one. Clear prompts make handoffs easier because teammates can see what was requested and what was provided. They can challenge the context, adjust the constraints, or add a verification step without debating hidden intent. The prompt becomes part of the work record, not a private conversation that must be reinterpreted later.

The final version of a good prompt is often shorter than the messy draft that produced it. Once you know the task, context, constraints, output format, and verification boundary, you can remove filler and repeated warnings. Concision is useful when it follows clarity. It is dangerous only when it removes the information the model and reviewer need to do the work responsibly.

You can also test a prompt by changing one input and watching whether the answer changes in the right way. If the audience changes from senior SREs to junior engineers, the explanation should become more patient and less abbreviated. If the evidence changes from a missing ConfigMap event to an image pull event, the diagnosis should move with the evidence. A prompt that produces nearly the same answer for different inputs is probably too generic.

Another useful test is to remove a key piece of evidence and see whether the assistant notices. If the full pod description is absent, the answer should ask for it or clearly mark the missing information. If the answer pretends the missing evidence exists, the prompt needs a stronger uncertainty boundary. This small test helps you distinguish a prompt that merely sounds structured from one that actually protects against unsupported claims.

Teams can make these tests lightweight by keeping a few saved examples. One example should contain enough evidence for a confident answer. Another should contain partial evidence that requires a careful question. A third should contain a misleading detail that the assistant must not overinterpret. These examples act like unit tests for prompt behavior, and they reveal prompt drift before the prompt becomes part of a repeated workflow.

The point is not to make prompting formal for its own sake. The point is to make the behavior inspectable before people rely on it. When a prompt is clear, a reviewer can say exactly what failed: the assistant ignored the audience, used evidence it did not have, violated the output format, skipped uncertainty, or rushed to action. That precision makes improvement possible.

In short, a prompt is healthy when it helps both the model and the reviewer do less guessing. If either party must infer the task, the evidence, the constraints, or the standard of success, the prompt still needs work.

## Patterns & Anti-Patterns

For a quick introductory module, the main pattern is enough: make the prompt a small contract. Use clear task framing, supply relevant context, state constraints, request a specific output shape, and include a verification boundary when the answer affects decisions. This pattern works because it converts a vague conversation into a reviewable artifact.

The pattern scales when you turn it into a reusable prompt card. A team can keep small prompt cards for explanation, troubleshooting, summarization, and review. Each card should include a purpose, input expectations, output format, and review checklist. The card is not meant to freeze the conversation forever; it is meant to give everyone a consistent starting point.

| Pattern | When to Use It | Why It Works | Scaling Consideration |
|---|---|---|---|
| Task, Context, Constraints, Output format | You need a first useful answer from a broad topic. | It removes the most common ambiguity before generation starts. | Keep the template short enough that people actually use it. |
| Evidence-first troubleshooting | You need help diagnosing logs, manifests, or incidents. | It separates observed facts from suggested fixes. | Add a review step before any state-changing command. |
| Iterative draft and refine | You are producing docs, notes, explanations, or plans. | It makes each turn inspectable and easier to correct. | Summarize accepted facts between turns to prevent drift. |

Anti-patterns are usually attractive because they feel faster. A vague prompt is quick to write. A giant prompt feels comprehensive. A prompt trick feels like insider knowledge. The cost appears later, when the answer is inconsistent, unsupported, hard to parse, or impossible to audit.

| Anti-Pattern | What Goes Wrong | Better Alternative |
|---|---|---|
| Asking for "the best answer" with no audience or context | The model optimizes for a generic average answer. | Name the audience, prior knowledge, and decision the answer supports. |
| Solving trust with wording alone | The output may still be wrong because evidence is missing. | Add verification steps, source checks, and explicit uncertainty handling. |
| One giant kitchen-sink prompt | Instructions conflict and failures are hard to debug. | Split analysis, drafting, refinement, and validation into separate turns. |

The safest habit is to treat every prompt as a draft of a workflow. If the workflow needs evidence, include evidence. If the workflow needs a reviewer, include the reviewer. If the workflow needs deterministic validation, write that validation outside the prompt. The model can assist, but the workflow carries the quality standard.

## Decision Framework

Use prompting when the task benefits from language reasoning, transformation, explanation, summarization, or draft generation. Use a different tool when the task requires authoritative state, deterministic computation, secret handling, or direct changes to production systems. This distinction prevents a common beginner mistake: trying to prompt around problems that should be solved with tests, scripts, documentation, monitoring, or human review.

| Situation | Use Prompting When | Use Something Else When |
|---|---|---|
| Learning a concept | You need an explanation matched to your current knowledge. | You need an authoritative specification or exact exam objective. |
| Troubleshooting | You have logs or manifests and want hypotheses plus next checks. | You need current cluster state that was not provided. |
| Writing documentation | You need a structured draft from known facts. | The source facts are missing, disputed, or confidential. |
| Generating commands | You need candidate commands for review. | The command will mutate production without a human approval step. |
| Producing structured output | You can validate the schema afterward. | Incorrect output would silently corrupt a downstream system. |

When choosing a prompt shape, start with the smallest structure that protects the work. For a casual explanation, Task plus Context may be enough. For a runbook draft, add Constraints and Output format. For troubleshooting, add evidence labels and uncertainty rules. For automation, add schema validation outside the model and reject malformed output instead of asking the prompt to carry all reliability.

The decision framework also helps you decide how much to iterate. If the cost of a wrong answer is low, one or two turns may be fine. If the answer affects infrastructure, security, money, or user trust, use more explicit evidence checks and human review. The prompt should match the risk level, not the user's impatience.

## Did You Know?

- The 2020 GPT-3 paper "Language Models are Few-Shot Learners" helped popularize in-context learning by showing that examples inside a prompt can change task behavior without updating model weights.
- OpenAI's 2022 instruction-following paper showed that reinforcement learning from human feedback could make language models better at following user intent than models trained only for next-token prediction.
- Kubernetes 1.35 is the version target for this curriculum, which is why examples in this module avoid old cluster-version assumptions and deprecated operational advice.
- JSON Schema began as an IETF draft effort long before current AI tooling, but its validation mindset is useful for AI workflows that need structured model output.

## Common Mistakes

| Mistake | Why It Happens | How to Fix It |
|---|---|---|
| Asking a broad question with no audience | The user knows the audience implicitly, but the model does not. | Add the learner role, prior knowledge, and decision the answer should support. |
| Treating confident wording as verification | Fluent text feels authoritative, especially when it uses familiar terminology. | Ask for evidence, uncertainty, missing data, and a separate source-check step. |
| Mixing instructions with raw evidence | Logs, ticket comments, and requirements are pasted into one undifferentiated block. | Label instructions, evidence, constraints, and output format in separate sections. |
| Overloading one prompt with every requirement | The writer tries to prevent all failure modes in one turn. | Split analysis, drafting, refinement, and validation into smaller prompts. |
| Ignoring output shape | The answer is useful but hard to paste into a runbook, ticket, or script. | Request a table, checklist, JSON object, or short sections before generation starts. |
| Using prompt tricks instead of clear constraints | Teams copy phrases that seemed to work once without understanding why. | State the real task, context, constraints, and evaluation standard directly. |
| Asking for a fix before asking for evidence | Operational pressure rewards fast action over careful diagnosis. | Require read-only diagnosis first, then ask for reversible remediation options. |

## Quiz

<details>
<summary>1. Your team asks an AI assistant to "Explain Kubernetes" for a new hire. The result is long, generic, and full of advanced terms. What should you change first?</summary>

Define the audience, prior knowledge, and output shape before asking again. A better prompt would say that the learner knows Linux and Docker but has never used a cluster, then ask for plain language, one analogy, and a short list of core objects. This fixes the main failure because the original prompt had no context or constraints. It also gives you a clear way to evaluate whether the next answer stayed beginner-friendly.
</details>

<details>
<summary>2. A troubleshooting assistant keeps mixing raw pod events with your instructions and then suggests actions that were not requested. How do you diagnose the prompt design problem?</summary>

This is a prompt drift and instruction leakage problem caused by weak separation between instructions and evidence. The fix is to label the task, context, constraints, raw evidence, and output format in separate sections. The answer should also tell the model which text is evidence and which text is instruction. That makes the response easier to review because unsupported claims can be traced back to missing or mislabeled evidence.
</details>

<details>
<summary>3. You need a Kubernetes troubleshooting answer, but the pasted data does not include the container exit reason. What should a good prompt require the assistant to do?</summary>

The prompt should require the assistant to state uncertainty and ask for the missing evidence instead of guessing. A strong answer might say that the current data is insufficient to identify the exit reason and list the exact read-only command needed next. This protects the workflow because it separates facts from inferences. It also prevents the model from hiding a weak assumption behind confident language.
</details>

<details>
<summary>4. A teammate writes one giant prompt with background, examples, edge cases, style rules, and validation demands. The answer is inconsistent. What workflow should replace it?</summary>

Use an iterative prompting loop that separates draft, refinement, and validation. First ask for a focused draft or diagnosis, then inspect what is missing, then ask a narrow follow-up, and finally verify the result against source material. This works better because each turn has one job and is easier to debug. If the model drifts, you can restate the accepted facts before continuing.
</details>

<details>
<summary>5. Your team wants predictable, reusable output for comparing Docker and Kubernetes for junior engineers. Which prompt structure best fits the task?</summary>

Use the Task, Context, Constraints, Output format structure. The task names the comparison, the context names the junior audience, the constraints set length and jargon limits, and the output format asks for a short explanation plus a comparison table. This design makes the response more predictable than an open-ended prompt. It also helps reviewers decide whether the result matches the original need.
</details>

<details>
<summary>6. A manager says prompting does not work because AI answers are weak during incident reviews, but the team provides no source material and no review step. What is the real issue?</summary>

The real issue is the workflow, not prompt wording alone. Prompting cannot replace logs, timelines, source documents, or accountable human review. A better prompt can ask for missing evidence and separate facts from assumptions, but it cannot create trustworthy evidence that was never provided. The team should fix the source-material and verification boundaries before expecting better output.
</details>

<details>
<summary>7. Engineers keep sharing secret prompt tricks, yet their outputs remain unreliable. What habit should replace that behavior?</summary>

Replace prompt superstition with disciplined clarity. The team should state who the answer is for, what the answer should do, what assumptions it must avoid, how it should be structured, and how it will be verified. Tricks may appear to help in isolated examples, but they rarely solve missing context or weak review. Clear task framing is more transferable across models and workflows.
</details>

## Hands-On Exercise

Exercise scenario: you are helping a new teammate use AI to draft a short Kubernetes 1.35 troubleshooting note for a pod that failed after a ConfigMap update. You do not need a live cluster for this exercise. The purpose is to design prompts that preserve task context constraints output format, expose uncertainty assumptions, avoid prompt drift instruction leakage, and support an iterative prompting loop.

Start with this evidence packet as your only source material. The packet is intentionally incomplete, so your prompt should not ask the model to produce a final confident remediation immediately. Your job is to make the assistant separate evidence from inference and ask for missing information when needed.

- Namespace: `training`
- Workload: `api-demo`
- Recent change: ConfigMap `api-demo-config` updated
- Reported symptom: one pod did not become ready after rollout
- Known event excerpt: `Warning Failed MountVolume.SetUp failed for volume "config": configmap "api-demo-config" not found`
- Missing evidence: full pod description, deployment manifest, and rollout history

- [ ] Task 1: Design task context constraints output format prompt that asks for an evidence-first diagnosis table, not a final fix.
- [ ] Task 2: Add uncertainty assumptions and verification boundaries so the assistant must identify missing evidence before suggesting remediation.
- [ ] Task 3: Diagnose prompt drift instruction leakage risks by labeling which text is instruction and which text is evidence.
- [ ] Task 4: Implement iterative prompting loop follow-ups for draft, refinement, and validation.
- [ ] Task 5: Write success criteria that a human reviewer can use before trusting the final AI output.

<details>
<summary>Solution sketch for Task 1</summary>

A strong first prompt would say: "Task: analyze the evidence packet for likely Kubernetes 1.35 readiness causes. Context: a pod in namespace training failed after a ConfigMap update. Constraints: use only the evidence packet, do not suggest state-changing commands yet, separate facts from inferences, and mark unsupported claims. Output format: Markdown table with columns Evidence, Possible Cause, Confidence, Missing Evidence, Next Read-Only Check." This design keeps the first answer diagnostic rather than action-oriented.
</details>

<details>
<summary>Solution sketch for Task 2</summary>

Add a sentence such as: "If the evidence is insufficient, say which specific information is missing instead of guessing." You can also require the assistant to use labels like Fact, Inference, and Assumption. The key is to reward calibrated uncertainty rather than fluent confidence. In this scenario, the assistant can mention the missing ConfigMap event, but it should not claim the deployment manifest is wrong until the manifest is provided.
</details>

<details>
<summary>Solution sketch for Task 3</summary>

Separate the prompt into sections named Instructions, Evidence Packet, Constraints, and Output Format. Do not mix raw event text with commands like "summarize this" in the same paragraph. This labeling reduces instruction leakage because the model can distinguish the data it should inspect from the instructions it should follow. It also helps a human reviewer see whether the assistant used the right source material.
</details>

<details>
<summary>Solution sketch for Task 4</summary>

Use three follow-ups. First, ask the assistant to list missing evidence and read-only checks. Second, after you provide the missing data, ask for a revised diagnosis that uses only confirmed facts. Third, ask for a validation checklist a human should complete before taking action. This iterative prompting loop prevents the model from treating the first incomplete packet as enough for a final remediation.
</details>

<details>
<summary>Solution sketch for Task 5</summary>

Good success criteria include: every conclusion maps to provided evidence, unsupported assumptions are labeled, missing evidence is requested, no state-changing command appears before diagnosis, and the output shape matches the requested table or checklist. These criteria make the prompt reviewable. They also remind the team that prompting improves the draft but does not replace verification.
</details>

## Sources

- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)
- [Training Language Models to Follow Instructions with Human Feedback](https://arxiv.org/abs/2203.02155)
- [OpenAI prompting guide](https://developers.openai.com/api/docs/guides/prompting)
- [OpenAI prompt engineering guide](https://developers.openai.com/api/docs/guides/prompt-engineering)
- [OpenAI optimizing LLM accuracy guide](https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy)
- [OpenAI migration guide with structured output notes](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [Anthropic prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Anthropic use XML tags](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags)
- [Anthropic chain complex prompts](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-prompts)
- [Google Gemini prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- [Kubernetes documentation](https://kubernetes.io/docs/home/)
- [Kubernetes API reference](https://kubernetes.io/docs/reference/kubernetes-api/)

## Next Module

Continue to [How to Verify AI Output](./module-1.4-how-to-verify-ai-output/) to practice checking claims, sources, and operational recommendations before you trust an AI-generated answer.
