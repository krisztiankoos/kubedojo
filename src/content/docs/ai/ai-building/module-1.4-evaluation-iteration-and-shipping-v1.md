---
title: "Evaluation, Iteration, and Shipping v1"
slug: ai/ai-building/module-1.4-evaluation-iteration-and-shipping-v1
sidebar:
  order: 4
revision_pending: false
---

> **AI Building** | Complexity: `[MEDIUM]` | Time: 40-55 min | Prerequisites: AI Building Modules 1.1-1.3, basic prompting, basic JSON, basic command-line usage

---

## Learning Outcomes

By the end of this module, you will be able to:

- **Design** a small evaluation set that represents the real job an AI feature must perform.
- **Debug** AI output failures by separating task clarity, context quality, output shape, validation, and model choice.
- **Evaluate** whether a v1 AI feature is bounded, reviewable, and safe enough to ship.
- **Iterate** on one variable at a time so each change teaches you something causal.
- **Compare** prompt changes, context changes, validation changes, and model changes using evidence instead of demos.

## Why This Module Matters

Hypothetical scenario: a product team ships an AI assistant into its internal support workflow after a persuasive demo. The assistant summarizes tickets cleanly, finds the right product area, and drafts polite responses for the three examples everyone practiced with during implementation. Then ordinary Monday traffic arrives, including screenshot-heavy billing complaints, refund requests mixed with outage language, and copied logs that do not resemble the tidy demo cases. The system has not suddenly become worse; the team has finally exposed it to the work it was supposed to handle.

That moment is where many AI projects lose trust, not because the model is useless, but because the team shipped impressions instead of evaluation. The support assistant summarizes emotion well but misses the billing detail, treats a refund request as more important than an outage, or invents an explanation for unfamiliar logs because nobody defined the boundary between useful inference and unsupported guessing. Evaluation is the discipline that turns those surprises into known test cases, iteration is the discipline that changes the system without guessing, and shipping v1 is the discipline that delivers value without pretending the feature is finished.

This module teaches the senior habit behind reliable early AI products: change one thing at a time, measure it against representative examples, and ship only inside the boundary you can explain. You will design a v1 contract, build a small evaluation set, diagnose failures by category, make causal iterations, and decide whether a launch boundary is honest enough for real users. The goal is not to make a tiny benchmark feel grand; the goal is to create enough evidence that the next product decision is based on behavior rather than enthusiasm.

## Start With The Smallest Honest Question

Before tuning the system, ask what job the feature must do well enough to be useful. That question is deliberately smaller than "How do I make it amazing?" or "How do I make it handle every possible user request?" because v1 work succeeds when the task is narrow enough to observe. A useful v1 question names a user, an input type, a task, and a review boundary, so the team can tell the difference between a good answer, a risky answer, and an answer that should not have been attempted.

For example, a support organization might ask whether an AI feature can classify incoming support tickets into one of five queues using only the ticket subject and body while showing the sentence that justifies the classification. That question tells you what input the system receives, what output it must produce, how many labels are allowed, what evidence the system must provide, and what it is not allowed to do. It is not resolving the ticket, sending the reply, changing customer data, or acting without review. The boundary is not a weakness; it is what makes the first version shippable.

A vague AI feature creates vague responsibility, while a bounded AI feature creates visible work. When the scope says "help support with tickets," reviewers will argue about whether a fluent answer feels helpful. When the scope says "suggest one queue label and quote the sentence that supports it," reviewers can inspect specific behavior. That is the difference between a demo and an evaluation target.

### From Idea To v1 Contract

Use a v1 contract before you write prompts because prompts are implementation details, while the contract is the product promise. A contract is a small agreement between the builder, the reviewer, and the user. It says what the feature does, what it refuses to do, how people will judge output quality, and what happens when evidence is uncertain or missing. Without that agreement, prompt changes tend to chase symptoms because nobody has written down the actual job.

| Contract Field | Good v1 Example | Weak v1 Example |
|---|---|---|
| User job | Route support tickets to the right queue faster | Help support with tickets |
| Input | Ticket subject and body only | Any customer conversation |
| Output | One queue label, confidence note, supporting quote | Helpful analysis |
| Success condition | Correct queue on at least most representative examples, with no unsupported quote | Looks useful in demos |
| Human review | Triage owner accepts or changes the queue before routing | The system routes directly |
| Refusal behavior | Mark as `needs_human_review` when no evidence supports a queue | Guess the most likely queue |

The weak version is tempting because it feels flexible, but flexibility without a reviewable surface usually means the team cannot tell what has improved. The strong version creates a testable surface because it names the user's job, the allowed input, the expected output, the success condition, the review point, and the refusal behavior. A senior builder does not ask whether the feature feels intelligent; a senior builder asks whether the feature performs a defined job under known constraints.

Pause and predict: if the contract requires a supporting quote, what should happen when the ticket mentions a refund request but omits the account information required to process it? A safe answer does not invent an account ID or recommend issuing a refund; it marks the missing field and routes the case for human review. That one prediction already shows why the contract is more than a planning document. It becomes the standard used by evaluation, validation, and launch review.

Your team might propose a feature called "Use AI to handle customer escalations." A stronger v1 contract would be: "For new customer escalation emails, draft a two-paragraph internal summary for the escalation manager, including the requested action, the affected account, and a quote from the email for each claim. If any field is missing, mark it as `unknown` instead of guessing." Notice what changed. The feature no longer handles the escalation; it prepares a reviewable summary, names required fields, requires evidence, and defines uncertainty.

## Evaluation Does Not Need To Be Fancy

For a beginner-friendly first system, evaluation can be simple: representative examples, expected output shape, pass/fail criteria, and notes on failure patterns. The point is not statistical perfection, and a tiny evaluation set is not a scientific benchmark. It is a steering wheel. It tells you whether a change moved the system in the direction you intended, helps you notice regression, gives reviewers shared evidence, and forces the team to define quality before arguing about optimization.

The first evaluation set should contain ordinary examples, not only clean examples, dramatic examples, or examples that make the model look good. You want the messy middle because that is where the feature will live. A useful first set includes easy successes, normal cases, ambiguous cases, malformed inputs, edge cases with high business risk, cases where the correct answer is "I do not know," cases where the model must cite evidence, and cases where the model must refuse unsupported action. Keep the set small enough that a human can still read every output.

Representative does not mean random. Representative means the examples resemble the work the system will actually face, including the work that worries you most. If the feature handles support tickets, include real ticket shapes with mixed issues, missing details, and conflicting urgency. If the feature summarizes meetings, include meetings with interruptions, action items, decisions, and unclear ownership. If the feature answers document questions, include questions where the answer is absent. If the feature extracts fields, include missing fields, repeated fields, and conflicting fields.

### A Minimal Eval Record

One evaluation record can be written as JSON, and the format below is deliberately plain. It is not tied to a specific evaluation framework or vendor. It is just structured enough to compare expected and actual behavior, and that is enough to start a useful loop. The record gives the system an input, the reviewer an expected result, the evaluator evidence to check, and the team a place to record risk.

```json
{
  "id": "ticket-routing-001",
  "input": {
    "subject": "Refund requested after duplicate billing",
    "body": "I was charged twice for my April invoice. Please refund the duplicate charge."
  },
  "expected": {
    "queue": "billing",
    "required_evidence": "charged twice"
  },
  "risk": "low",
  "notes": "Straightforward billing ticket."
}
```

The exact schema can vary, but the habit matters more than the tool. You are writing down the input, the expected behavior, the evidence required to justify that behavior, and the reason the case belongs in the set. When a case later fails, the team can discuss the failure against a written expectation instead of relying on memory. When expectations change, the change can be recorded as a product decision rather than silently edited to make the score look better.

### Pass And Fail Criteria

A pass/fail rule should be concrete enough that two reviewers usually agree. Weak criteria sound like "good summary," "helpful answer," "mostly correct," "looks reasonable," or "user would like it." Those phrases are too soft because AI systems fail in subtle ways. A beautiful answer with one unsupported claim is not a pass if groundedness is required, and a confident classification is not a pass if the label is outside the allowed list.

Stronger criteria say that the output includes the requested action, the affected account, and no unsupported claims. They say the classification must use only one label from the approved label set, the answer must cite a document excerpt that contains the answer, missing evidence must produce `unknown` instead of a guess, and the draft must not perform the action because it only prepares text for human review. These rules expose the difference between fluent output and reliable output.

Before running this, what output do you expect from a case where the customer wants a refund but the account ID is missing? The expected output might be `queue: billing`, `account_id: unknown`, and `next_step: ask human for account lookup`. That is a better test than another clean success case because clean success proves the happy path, while a refusal or escalation case proves the boundary.

## A Practical v1 Loop

```text
pick one task
   ->
collect representative examples
   ->
define what success looks like
   ->
run the system
   ->
inspect failures
   ->
change one thing at a time
```

The "one thing at a time" rule matters because an evaluation loop is supposed to teach causality, not just produce a better-looking output. If you change the prompt, model, context, and output format together, you learn almost nothing from the result. The score might improve, but you cannot tell whether the improvement came from a clearer instruction, better retrieval, stricter shape, or a more capable model. A team that cannot explain why quality improved cannot reliably improve it again, and a team that cannot identify what caused a regression cannot safely ship.

A variable can be the task definition, the examples in the evaluation set, the context retrieved for the model, the prompt instruction, the output schema, the validation rule, the review workflow, the model choice, a model parameter, or a fallback path. Changing one variable does not mean making one word edit; it means making one kind of intervention. You may rewrite the prompt to clarify citation requirements, but you should not rewrite the prompt, add retrieval, change the label set, and switch models in the same iteration.

### Worked Iteration Scenario: Ticket Routing

Hypothetical scenario: a team is building a v1 support-ticket router that must output one queue label, one supporting quote from the ticket, and `needs_human_review` when evidence is insufficient. The allowed queues are `billing`, `technical_support`, `account_access`, `sales`, and `needs_human_review`. The feature is intentionally assistive; a triage owner accepts or changes the suggestion before routing. That boundary lets the team evaluate classification quality without granting the system operational authority.

The team starts with a mixed-issue input that is realistic enough to reveal a product rule. The customer mentions duplicate billing and invoice-page access in the same ticket, so the expected behavior is not obvious until the business priority is written down. Billing is money-impacting, so the team decides that duplicate charge takes priority and the access problem should be captured as a secondary issue.

```json
{
  "subject": "Charged twice and cannot access invoice",
  "body": "I was charged twice this month. I also cannot open the invoice page because it says permission denied. Please fix this today."
}
```

The expected output records the priority decision. This is important because the expected answer is not simply "whatever sounds most plausible." It is the product's chosen behavior for a class of mixed tickets, and future prompt or model changes should be judged against that behavior.

```json
{
  "queue": "billing",
  "supporting_quote": "I was charged twice this month.",
  "secondary_issue": "account_access"
}
```

The first prompt lists the labels but does not explain conflict handling. That omission is common because the builder understands the business priority and assumes the model will infer it. The model does not have private policy knowledge, so it may choose the most concrete symptom rather than the most important business issue.

```text
Classify this support ticket into the best queue:
billing, technical_support, account_access, or sales.

Ticket:
Subject: Charged twice and cannot access invoice
Body: I was charged twice this month. I also cannot open the invoice page because it says permission denied. Please fix this today.
```

The model returns a plausible but wrong answer. It focuses on the permission-denied phrase, which is concrete and operational, but it misses the billing-first priority. The failure is not random; it reveals that the task definition lacks a conflict rule.

```json
{
  "queue": "account_access",
  "reason": "The user cannot open the invoice page because of permission denied."
}
```

The team records the failure as a diagnosis rather than a complaint. This table is small, but it captures the input, the failure, the suspected cause, the one change to try, and the current result. The "pending" cell is a useful reminder that a proposed fix is not a fix until the same case and regression cases are rerun.

| Iteration | Input | Failure | Diagnosis | Change | Result |
|---|---|---|---|---|---|
| baseline | duplicate charge plus invoice access error | routed to `account_access` | no priority rule for mixed tickets | add priority rule only | pending |

The team changes one thing: it adds a billing-first priority rule. It does not change the model, add retrieval, rewrite the schema, or add a second classifier. This is the one-variable rule in practice. If the result improves, the team can attribute the improvement to the new priority rule; if the result worsens, the team knows what to undo.

```text
Classify this support ticket into one queue:
billing, technical_support, account_access, sales, or needs_human_review.

Priority rule:
If the ticket includes a billing problem and another problem, choose billing first.
If evidence is insufficient, choose needs_human_review.

Return JSON with:
queue
supporting_quote
secondary_issue

Ticket:
Subject: Charged twice and cannot access invoice
Body: I was charged twice this month. I also cannot open the invoice page because it says permission denied. Please fix this today.
```

The revised prompt now returns the expected result on the target example. That is encouraging but not enough because a fix for one example can break another example. A phrase-specific rule can look successful while making the system brittle, so the team must rerun related non-target cases.

```json
{
  "queue": "billing",
  "supporting_quote": "I was charged twice this month.",
  "secondary_issue": "account_access"
}
```

The next example checks whether the new rule over-routes ordinary account-access cases to billing. The customer explicitly says there is no billing issue, so a billing-first rule should not trigger. This kind of regression check keeps the team from celebrating a one-case fix that damages the rest of the set.

```json
{
  "subject": "Cannot log in after password reset",
  "body": "I reset my password, but the login page still rejects it. I do not have any billing issue."
}
```

The output remains correct, so the team can make a precise statement: adding a billing-first conflict rule fixed the mixed billing/access example without breaking the tested account-access example. That is real learning. It is not just better output; it is a causal improvement tied to a product rule.

```json
{
  "queue": "account_access",
  "supporting_quote": "the login page still rejects it",
  "secondary_issue": null
}
```

### What The Team Did Not Do

The team did not immediately switch to a larger model, add more examples before diagnosing the visible failure, rewrite the whole prompt in a new style, add a second classifier, or hide the failure because the answer looked reasonable. It inspected the failure, named the cause, made one targeted change, reran the example, and checked for regression. That is the v1 loop, and it is also the habit that separates useful iteration from prompt thrashing.

Suppose the same ticket router later returns the correct queue with a weak quote. The queue is `billing`, but the supporting quote is "Please fix this today." The failure is not classification; it is evidence selection. The first change should clarify that the supporting quote must contain the phrase or sentence that directly proves the selected queue, because changing the model would make the experiment noisier.

```json
{
  "queue": "billing",
  "supporting_quote": "Please fix this today.",
  "secondary_issue": "account_access"
}
```

## What To Change First

When an AI output fails, start with the cheapest explanation that would account for the failure. A practical order is to clarify the task, improve context, improve output shape, add validation, and only then compare models or advanced settings. The hierarchy is not a law, but it prevents a common mistake: using model choice to avoid diagnosis. If the task is vague, more context may not help. If the context is missing, a stricter schema will not create facts. If the output shape is unclear, validation will be hard to write.

Hypothetical scenario: a team builds an AI feature that answers questions about an internal deployment runbook. A user asks, "Can I restart the payment worker during business hours?" The system answers, "Yes, restarting the worker is usually safe if you monitor logs afterward." The expected answer is no because the runbook says payment workers must be restarted only during the approved maintenance window unless incident command approves an exception. The team could switch models, add a stricter format, add validation, improve retrieval, or clarify the task, but a disciplined iteration starts with the first likely cause.

The current task says the following, and it sounds reasonable at first glance. It is still underspecified because it does not say what to do when the runbook contains a policy restriction, whether safety constraints override general advice, or whether the answer must include a quote. The missing rule is not technical; it is a product and safety rule.

```text
Answer the user's question using the runbook.
```

The first fix clarifies the task while keeping the same model and context. It tells the system to use only the supplied excerpt, state restrictions before operational advice, quote the source, and fail closed when the excerpt does not answer the question. This change targets the actual failure: the answer ignored a restriction present in the available policy text.

```text
Answer the user's question using only the runbook excerpt.
If the runbook includes a restriction, state the restriction before any operational advice.
Include one exact quote from the excerpt.
If the excerpt does not answer the question, say "not enough information."
```

With that change, the answer becomes reviewable. It says no, names the maintenance-window restriction, quotes the supporting sentence, and marks the status as answered. If this resolves the failure across related examples, the model was not the first problem. The task was too loose.

```json
{
  "answer": "No. The runbook restricts payment worker restarts to the approved maintenance window unless incident command approves an exception.",
  "quote": "Payment workers must be restarted only during the approved maintenance window unless incident command approves an exception.",
  "status": "answered"
}
```

If task clarity is not enough, context becomes the next suspect. A user might ask who can approve an exception, and the current excerpt might say "incident command" without defining that role. The answer below may be directionally right but incomplete because it quotes the exception phrase without defining who belongs to incident command. In that case, the change should improve retrieval so the policy definition section is included with the restart section. The task is already clear; the missing piece is information.

```json
{
  "answer": "Incident command can approve an exception.",
  "quote": "unless incident command approves an exception",
  "status": "answered"
}
```

Output shape becomes the next lever when the answer is basically correct but hard to audit. A paragraph can contain the decision, quote, and review note, but reviewers and validators need predictable fields. The schema below does not make the model smarter. It makes the output easier to inspect, score, and reject when required fields are missing.

```json
{
  "status": "answered | not_enough_information",
  "decision": "yes | no | conditional | unknown",
  "answer": "string",
  "supporting_quote": "string",
  "review_note": "string"
}
```

Validation becomes useful once the output shape is stable. Validation can check that `status` and `decision` are allowed values, that `supporting_quote` is present when the status is `answered`, that the answer does not claim certainty when the status is `not_enough_information`, that the quote appears in the supplied context, and that the output is parseable JSON. Validation catches broken outputs before a person trusts them, and it helps separate formatting failures from reasoning failures.

Only after the task, context, shape, and validation are reasonable should model choice become the main lever. A stronger model may handle more complex reasoning, a smaller model may be cheaper and sufficient, a model with larger context may support longer documents, and a model with stronger structured-output behavior may reduce parsing failures. The point is not "never change models." The point is that model changes are expensive to interpret because they can improve one behavior while changing others.

| Observed Failure | First Suspect | Better First Change | Why |
|---|---|---|---|
| Answer violates business priority | Task clarity | Add explicit priority rule | The model cannot infer private policy |
| Answer lacks required fact | Context | Retrieve or supply the missing source | The model cannot cite absent information |
| Answer is correct but hard to review | Output shape | Use a stable schema | Review needs predictable fields |
| Answer has invalid JSON | Validation and schema | Validate and retry or fail closed | Broken structure blocks automation |
| Answer requires complex judgment after other fixes | Model choice | Compare models on the same eval set | Capability may now be the constraint |

Which approach would you choose here and why: a document Q&A assistant says contractors may access staging, but the retrieved policy says contractors may access staging only after manager approval and security training. A good first change is task clarity: require the answer to preserve conditions and quote the exact sentence that contains the condition. A good second change is output shape: add separate fields for `decision`, `conditions`, and `supporting_quote`. A model switch is not the first move because the supplied context already contains the answer.

## Build A Runnable Eval Harness

A v1 eval can start as a small script because the first goal is repeatability, not platform sophistication. You need repeatable inputs, visible expectations, consistent scoring, and a habit of inspecting failures. The following harness does not call an AI model; it simulates evaluation mechanics using saved outputs. That makes it runnable anywhere and keeps attention on the shape of the loop before you add provider integration.

Create a file named `eval_cases.jsonl`. Each line is an independent case with an expected queue, required evidence, and saved actual output. The third case is intentionally wrong because a useful harness should show you failures clearly, not just print a comforting score.

```json
{"id":"ticket-001","expected_queue":"billing","required_evidence":"charged twice","actual":{"queue":"billing","supporting_quote":"I was charged twice this month."}}
{"id":"ticket-002","expected_queue":"account_access","required_evidence":"login page still rejects it","actual":{"queue":"account_access","supporting_quote":"the login page still rejects it"}}
{"id":"ticket-003","expected_queue":"needs_human_review","required_evidence":"missing account ID","actual":{"queue":"billing","supporting_quote":"customer wants a refund"}}
```

Create a file named `run_eval.py`. The script loads each JSONL record, checks whether the queue matches, checks whether the supporting quote contains the required evidence, prints a per-case result, and prints a total. It is intentionally small enough that a beginner can audit the scoring logic instead of treating the harness as magic.

```python
import json
from pathlib import Path


def evidence_matches(required: str, quote: str) -> bool:
    return required.lower() in quote.lower()


def score_case(case: dict) -> dict:
    actual = case["actual"]
    queue_ok = actual.get("queue") == case["expected_queue"]
    quote_ok = evidence_matches(
        case["required_evidence"],
        actual.get("supporting_quote", ""),
    )
    passed = queue_ok and quote_ok
    return {
        "id": case["id"],
        "passed": passed,
        "queue_ok": queue_ok,
        "quote_ok": quote_ok,
        "expected_queue": case["expected_queue"],
        "actual_queue": actual.get("queue"),
    }


def main() -> None:
    path = Path("eval_cases.jsonl")
    cases = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    results = [score_case(case) for case in cases]
    passed = sum(1 for result in results if result["passed"])

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"{status} {result['id']} "
            f"queue_ok={result['queue_ok']} "
            f"quote_ok={result['quote_ok']} "
            f"expected={result['expected_queue']} "
            f"actual={result['actual_queue']}"
        )

    print(f"\npassed={passed} total={len(results)}")


if __name__ == "__main__":
    main()
```

Run it from the directory that contains the two files. The output should show two passes and one failure. That failure is useful because it tells the team that `ticket-003` was routed to billing when the expected output was `needs_human_review`, and it also tells the team that the quote did not contain the required evidence.

```bash
.venv/bin/python run_eval.py
```

Reading eval output is a skill. A score is a signal, not a verdict, so a failing example might mean the system is wrong, the expected answer is wrong, the input is ambiguous, the system is missing context, the output schema is too loose, validation is too strict, or the task definition omitted a business rule. Do not silently edit expected outputs to make the score better. If expectations change, record why, because evaluation is part of the product specification.

Eval notes are part of the artifact, not an afterthought. A weak note says "bad answer," which teaches nothing. A better note says, "Routed refund case to billing even though account ID was missing; expected `needs_human_review` because workflow cannot process refund without account lookup." That note names the failure pattern, the expected boundary, and the workflow reason behind the expectation. Over time, notes become a map of product decisions and remaining risk.

### Senior Practice: Separate Quality Gates

A v1 AI feature often needs more than one gate because different gates catch different failures. Schema validation can reject malformed output, but it cannot judge whether the business policy is correct. Human review can catch judgment failures, but reviewers should not waste time repairing invalid JSON. Regression examples catch drift against known cases, but they do not prove every safety property. Layered gates make failure visible earlier and reduce the chance that one overloaded review step misses a predictable problem.

| Gate | Catches | Example |
|---|---|---|
| Schema validation | malformed output | missing `queue` field |
| Grounding check | unsupported claims | quote not found in context |
| Policy check | unsafe action | suggests refund without account ID |
| Human review | judgment failures | ambiguous customer intent |
| Regression eval | quality drift | old success case starts failing |

## Inspect Failures Like A Practitioner

Inspection is where real learning happens because a passing score can hide weak reasoning, and a failing score can reveal a missing product rule. Treat each failure as a diagnostic case. You are not only asking how to make one example pass; you are asking what class of failure the example represents. That question prevents overfitting because the fix should address the class, not the exact phrase that happened to appear in one input.

Use a small taxonomy when reviewing outputs. The taxonomy does not need to be perfect, but it should help reviewers move from vague frustration to specific diagnosis. When the output chooses a reasonable but wrong interpretation, the first move is usually task clarity. When the output guesses or gives generic advice, the first move is usually context. When the conclusion is right but the quote is weak, tighten evidence rules. Specific diagnosis leads to specific fixes.

| Failure Type | Symptom | Usual First Move |
|---|---|---|
| Task ambiguity | output chooses a reasonable but wrong interpretation | clarify task or priority |
| Missing context | output guesses or gives generic advice | improve retrieval or supplied context |
| Bad evidence | output conclusion is right but quote is weak | tighten evidence rules |
| Shape drift | fields missing or inconsistent | define schema and validation |
| Unsafe action | output exceeds allowed authority | add boundary and review rule |
| Hallucinated detail | output invents facts | require grounding and fail closed |
| Over-refusal | output says unknown when evidence exists | improve context selection or instruction balance |
| Regression | old passing case fails after change | isolate the changed variable |

When you fix one example, ask whether the fix generalizes. A bad fix mentions the exact input phrase because it is trying to win one case. A good fix names the underlying rule because it is trying to improve the product. Phrase-specific prompt patches are tempting because they are cheap, but cheap changes still need discipline.

```text
If the user says "charged twice and cannot access invoice", choose billing.
```

The better version describes the class of mixed tickets. It still needs evaluation, and it may still need exceptions, but it is much more likely to generalize. The difference is the same as writing a unit test for one string versus writing a product rule for a category of work.

```text
If a ticket includes both a billing problem and another problem, choose billing first.
```

Comparison records help the team keep that discipline. At minimum, record the date, evaluation set version, change made, examples improved, examples worsened, remaining failure pattern, and decision. This does not need to become bureaucracy. A small table is enough, especially when it captures tradeoffs rather than hiding them.

| Date | Change | Improved | Worsened | Decision |
|---|---|---|---|---|
| 2026-04-25 | Added billing-first priority rule | mixed billing/access case | none in small set | keep and expand mixed-issue cases |
| 2026-04-25 | Required quote to contain queue evidence | weak quote case | one account case now over-refuses | revise evidence instruction |

The second row matters because not every change is clean. A change can improve evidence quality while increasing refusal, and that does not automatically make the change bad. It means the team must decide which tradeoff is acceptable for the v1 job. Evidence-focused changes often make systems more conservative, and the launch boundary should reflect that behavior.

```text
If the ticket mentions "April invoice", route to billing.
```

That instruction is risky because it routes one known example correctly but fails the class of related examples. A May duplicate charge should still route to billing, while a tax invoice permission issue may not be a billing problem. The rule is phrase-specific instead of behavior-specific.

```text
If the ticket reports a charge, refund, invoice amount, payment failure, or duplicate billing, route to billing unless required account information is missing.
```

The category rule is still imperfect, but it is much more likely to generalize. It also contains a boundary for missing information, which matters because many real support workflows cannot safely act without an account identifier or other required field. The lesson is not that prompts should become long rulebooks. The lesson is that product rules belong somewhere explicit, and the evaluation set should show whether those rules hold.

## What Shipping v1 Really Means

A good v1 is useful, bounded, explainable, and reviewable. A bad v1 is open-ended, hard to evaluate, trusted too much, and much harder to debug once users depend on it. Shipping v1 does not mean shipping a toy. It means shipping the smallest version that creates real value inside a controlled boundary. For AI features, the boundary is part of the product, not a temporary embarrassment.

If the feature summarizes tickets for humans, do not silently route tickets. If the feature drafts replies, do not send them automatically. If the feature answers document questions, do not answer without source text. If the feature extracts fields, do not invent missing fields. If the feature recommends actions, do not execute actions until the review path is mature. The v1 boundary should match the evidence you have, and evidence from a small eval set supports a small launch rather than broad autonomy.

Signs of readiness are practical rather than theatrical. The use case is narrow, failure modes are visible, humans can review outcomes where needed, examples show typical success and typical failure, and the system reduces work instead of adding ambiguity. A v1 can ship with known limitations because known limitations can be documented, reviewed, and improved. It should not ship with hidden limitations because hidden limitations become production surprises.

Signs that the feature is not ready are equally concrete. You still cannot describe success in one sentence, every demo depends on a carefully phrased prompt, wrong outputs look too plausible to detect, nobody owns validation, or the system performs actions you cannot comfortably audit. Those warnings do not mean the idea is bad. They mean the boundary is not ready. Narrow the scope, add examples, clarify success, add review, reduce authority, and evaluate again.

The launch boundary should answer who can use the feature, what inputs are allowed, what outputs it can produce, and what happens when confidence is low or evidence is missing. For the ticket router, the first launch might be internal triage only, English-language support tickets with subject and body, suggested queue and supporting quote, no automatic routing, `needs_human_review` for missing or conflicting evidence, and a weekly review of failed or overridden suggestions. This launch is not glamorous, but it creates value by reducing triage effort without pretending the classifier is an autonomous support agent.

| Boundary | v1 Decision |
|---|---|
| Users | internal triage team only |
| Inputs | new English-language support tickets with subject and body |
| Outputs | suggested queue, supporting quote, secondary issue |
| Authority | suggestion only; no automatic routing |
| Escalation | `needs_human_review` for missing or conflicting evidence |
| Monitoring | weekly review of failed and overridden suggestions |

Exercise scenario: your team wants the AI system to read a ticket, choose a refund amount, and issue the refund, but you have a small eval set and no production history. A safer v1 reads the ticket, identifies whether a refund may be relevant, extracts the requested amount and evidence, and prepares a review note for a billing specialist. This version still helps because it reduces reading and summarization work, but it does not move money. It keeps authority with a person, which is how early AI shipping should feel: useful, bounded, and reviewable.

## Operating The Loop After Launch

Shipping v1 is not the end of evaluation; it is the beginning of real feedback. Production inputs will teach you things the first eval set missed, and that does not mean the first eval set failed. It means the world is larger than your sample. The right response is to fold new learning back into the loop: sample human overrides, convert user complaints into examples, inspect validation failures, and narrow the launch boundary when a serious failure appears.

Track signals that match the v1 job. For a ticket router, useful signals include the percentage of suggestions accepted by humans, the percentage changed by humans, top queue confusion pairs, examples marked `needs_human_review`, validation failure rate, unsupported quote rate, time saved during triage, and reviewer comments. Avoid vanity metrics such as total AI calls, average response length, or demo applause because they do not prove reliability or value. Track behavior that maps to the job.

Human overrides are not embarrassing; they are product signals. When a triage owner changes `account_access` to `billing`, ask whether the priority rule was missing, the evidence was present but ignored, the ticket was ambiguous, the expected label was wrong, or the label taxonomy was too coarse. Each answer leads to a different change. Do not treat all overrides as model errors because some are product taxonomy errors, workflow errors, or unresolved policy decisions.

Expand scope only when the current boundary is stable. Stable does not mean perfect; it means failure modes are known, reviewable, and acceptable for the use case. A reasonable expansion might move from one support queue to five queues, from an internal pilot to a larger internal group, from suggestion-only to auto-routing low-risk cases, from English tickets to a second supported language, or from weekly review to daily monitoring during a high-volume launch. Each expansion should bring new examples because a broader launch needs broader evaluation.

Evaluation examples are product assets, not throwaway test data. They encode user jobs, policy decisions, and failure boundaries. They help onboard new builders, help reviewers challenge changes, and help future teams understand why v1 behaves the way it does. Store them where the team can review them, version them, discuss disputed examples, and retire examples only when the product boundary changes and the reason is clear. A mature AI team does not just have prompts; it has evals, notes, review rules, and launch boundaries.

## Patterns & Anti-Patterns

Pattern: write the v1 contract before prompt tuning. Use this when the team can describe the feature idea but cannot yet agree on what counts as success. It works because the contract moves hidden product assumptions into a reviewable artifact, and it scales by becoming the shared reference for eval cases, prompt instructions, validation rules, and launch notes. The tradeoff is that the team must make uncomfortable boundary decisions earlier, but those decisions are cheaper before code and users depend on them.

Pattern: score representative examples before expanding scope. Use this when the first demo looks promising and stakeholders want to launch broadly. It works because the examples reveal whether the feature handles normal inputs, ambiguous inputs, and cases where refusal is correct. It scales by turning new production failures into new cases rather than scattered anecdotes. The tradeoff is that evaluation slows the first launch slightly, but it prevents much slower recovery from an avoidable trust failure.

Pattern: keep iteration records short and causal. Use this when multiple people are changing prompts, schemas, retrieval settings, and models. It works because the record names the variable changed, the cases improved, the cases worsened, and the decision. It scales because future maintainers can see why the feature behaves as it does. The tradeoff is that every change needs a small written explanation, but that writing replaces long arguments about what happened.

Anti-pattern: treating the demo as the evaluation. Teams fall into this when the first examples are chosen by the builder and rehearsed during implementation. The demo may be useful for explaining the product idea, but it is weak evidence because it filters out the messy middle. The better alternative is to keep the demo, then immediately run representative and risky cases that the prompt was not rehearsed against.

Anti-pattern: switching models before diagnosing the failure. Teams fall into this because model changes are easy to try and can produce visibly better prose. The problem is that a better-looking answer can hide missing task rules, missing context, weak output shape, or absent validation. The better alternative is to follow the priority ladder: task, context, shape, validation, then model comparison on the same eval set.

Anti-pattern: shipping broad authority from narrow evidence. Teams fall into this when a helpful assistant feels so good that they want it to perform the action instead of preparing the action for review. The risk is that the evaluation set proves only a small behavior while the launch grants much larger authority. The better alternative is to ship bounded usefulness first and expand authority only when examples, validation, human review, and rollback support the new boundary.

## Decision Framework

Use the v1 shipping decision as a sequence of questions rather than a mood check. First, can you state the user job, input boundary, output shape, and review point in one sentence? If not, keep contracting before evaluating. Second, do you have representative examples that include ordinary cases, ambiguous cases, risky cases, and refusal cases? If not, build the eval set before arguing about model quality. Third, do failures map to named categories such as task ambiguity, missing context, bad evidence, shape drift, unsafe action, hallucinated detail, over-refusal, or regression? If not, inspect before changing.

Once diagnosis is clear, choose the smallest intervention that targets the failure. If the model chooses a plausible but wrong business priority, clarify the task. If the answer lacks a fact that is absent from the supplied material, improve context. If the answer is correct but hard to review, stabilize the output shape. If the output breaks automation, add validation and fail closed. If the task, context, shape, and validation are already strong but the system still cannot perform the reasoning, compare models on the same examples.

Finally, decide the launch boundary from the evidence you actually have. Ship to a small internal group when the job is narrow, failures are visible, review is assigned, and rollback is possible. Run another iteration when one or two important failure classes remain but the boundary is otherwise clear. Narrow scope and retest when the feature is useful only for a subset of inputs. Do not ship yet when wrong outputs are hard to detect, the feature performs actions you cannot audit, or nobody owns post-launch monitoring.

## Did You Know?

1. **Small eval sets are useful when they are representative**: a carefully chosen set of normal, ambiguous, and risky examples can reveal more than a large set of clean demo cases because it forces the system through the decisions that actually matter.

2. **A correct answer can still fail evaluation**: if the answer lacks required evidence, uses the wrong schema, or exceeds its authority, it should fail even when the prose sounds right because the product requirement is broader than fluency.

3. **Changing models can hide product bugs**: a stronger model may compensate for vague instructions during demos, but the missing task rule can still cause production failures later when inputs become less rehearsed.

4. **Refusal behavior is part of quality**: a system that says `not enough information` at the right time is often safer and more useful than a system that always tries to answer with confidence.

## Common Mistakes

| Mistake | Why It Happens | How to Fix It |
|---|---|---|
| tuning without examples | progress feels fast because every prompt edit produces new prose | define a small evaluation set first and record expected behavior before changing prompts |
| changing too many things at once | the team wants a quick visible improvement and bundles prompt, context, schema, and model changes | change one variable per iteration and rerun target plus regression examples |
| shipping broad autonomy first | the demo feels capable enough to justify more authority than the eval set proves | ship bounded usefulness first and keep risky actions behind human review |
| treating demos as evidence | rehearsed examples are easier to remember and more persuasive in meetings | test representative cases that include ordinary, ambiguous, risky, and refusal examples |
| fixing one example with phrase-specific rules | prompt patches are cheap and can make one failing case pass quickly | write rules for the failure class and verify that related cases still pass |
| switching models before diagnosing failures | a stronger model may improve the surface output and hide the actual cause | follow the priority order before model changes and compare models only on the same eval set |
| ignoring refusal cases | builders focus on successful answers and forget that absence of evidence is common | include examples where escalation, `unknown`, or `not enough information` is the correct behavior |

## Quiz

<details>
<summary>1. Your team builds a meeting-summary feature. It works on three clean meetings but fails when a meeting has unclear ownership for action items. What should you do before rewriting the whole prompt?</summary>

Add representative evaluation examples that include unclear ownership, then define what the system should do in that case. For example, the expected behavior might be to write `owner_unknown` rather than inventing an owner. This is better than a full prompt rewrite because the failure first needs a clear success rule. Once the rule exists, a prompt or schema change can be judged against evidence instead of taste.

</details>

<details>
<summary>2. A support-ticket classifier routes "charged twice and cannot access invoice" to `account_access`, but your business rule says billing issues take priority. Which first change best follows the one-variable rule?</summary>

Add one explicit priority rule that says billing issues take precedence when a ticket contains billing plus another issue. Keep the model, context, and output schema unchanged for that iteration so the team can attribute the result to the priority rule. Then rerun the failing case and check whether ordinary account-access examples still pass. That regression check prevents a one-case fix from becoming a broader routing bug.

</details>

<details>
<summary>3. A document Q&A system answers from the right policy section but does not include a quote. Reviewers cannot tell whether the answer is grounded. What should you change before changing models?</summary>

Improve the evidence instruction and output shape before changing models. Require fields such as `answer`, `supporting_quote`, and `status`, then add validation that the quote appears in the supplied context. The issue is reviewability and grounding, not necessarily model capability. A model switch might produce nicer prose, but it would not by itself create the audit trail reviewers need.

</details>

<details>
<summary>4. Your eval score improves after you change the prompt, switch models, add retrieval, and rewrite the schema in the same run. Why is this result hard to trust?</summary>

The team cannot tell which change caused the improvement. The model switch may have helped, the retrieval change may have supplied missing facts, the schema may have made scoring easier, or the prompt may have fixed the actual issue. Because too many variables changed, the iteration produced a result but not clear learning. The safer next move is to split the changes and compare them against the same examples.

</details>

<details>
<summary>5. A refund assistant correctly identifies refund intent, but the customer account ID is missing. The system suggests issuing a refund anyway. What should the expected v1 behavior be?</summary>

The system should escalate or mark the output as not ready for action because the required account information is missing. A strong v1 behavior would extract the refund request, mark `account_id` as `unknown`, and route the case for human review. It should not perform or recommend an irreversible action when required information is absent. This answer evaluates whether the feature is bounded, reviewable, and safe enough to ship.

</details>

<details>
<summary>6. A team wants to expand an internal ticket-suggestion feature into automatic routing for all queues. Their current eval set only covers one queue and a handful of examples. What should you recommend?</summary>

Do not expand directly to all automatic routing. First broaden the evaluation set across the target queues, include ambiguous and risky examples, and verify the review or rollback path. A safer expansion might auto-route only low-risk cases while keeping human review for ambiguous cases. The launch boundary should grow with the evidence rather than with the team's excitement.

</details>

<details>
<summary>7. A model gives a fluent answer that says contractors may access staging. The supplied policy says contractors may access staging only after manager approval and security training. What is the best diagnosis?</summary>

The system dropped an important condition from the context. The first fix should clarify that conditions must be preserved and require a supporting quote, because the necessary information was already present. A structured output with a `conditions` field can also help reviewers inspect whether the answer retained the policy restriction. Switching models is not the first move because the failure is instruction and structure before capability.

</details>

## Hands-On Exercise

You will design and iterate a v1 evaluation plan for one AI feature. Choose a feature that is small enough to test, such as support ticket routing, meeting action-item extraction, internal document Q&A, release-note summarization, incident update drafting, or sales lead classification. Avoid broad ideas like "AI support agent" or "AI operations assistant" because those labels hide too many jobs. Your goal is to turn a vague feature into a bounded v1 with evidence.

### Step 1: Write The v1 Contract

Write a short contract with the user, input, output, allowed actions, disallowed actions, success condition, review boundary, and refusal or escalation behavior. The contract should be specific enough that another person could write evaluation examples from it without interviewing you again. If you struggle to name disallowed actions, the feature is probably still too broad.

Success criteria:

- [ ] The job can be described in one sentence.
- [ ] The input boundary is clear.
- [ ] The output is reviewable by a human.
- [ ] The feature has at least one explicit disallowed action.
- [ ] The refusal behavior is defined.

<details>
<summary>Example solution</summary>

For a support ticket router, the v1 contract could say: "For new English-language support tickets, suggest one queue from an approved list, include the quote that supports the selected queue, mark missing evidence as `needs_human_review`, and require a triage owner to accept or change the suggestion before routing." The disallowed action is automatic routing, and the refusal behavior is explicit. This contract is narrow enough to evaluate because it names inputs, outputs, authority, and review.

</details>

### Step 2: Create Five Evaluation Examples

Create five examples with one easy success, two normal cases, one ambiguous case, and one case where refusal or escalation is correct. For each example, write the input, expected output, required evidence, risk level, and notes about why the example matters. The examples should test the contract, not the model's ability to charm you with fluent prose.

Success criteria:

- [ ] At least one example is messy or ambiguous.
- [ ] At least one example expects refusal or escalation.
- [ ] Every expected output maps to the v1 contract.
- [ ] Required evidence is specific enough to inspect.
- [ ] The examples are not all hand-picked happy paths.

<details>
<summary>Example solution</summary>

For the ticket router, include a straightforward billing case, a straightforward account-access case, a technical-support case with copied logs, a mixed billing and access case, and a refund request with missing account information. The missing-account case should expect `needs_human_review`, not a guessed refund recommendation. The mixed case should encode the priority rule so reviewers can tell whether billing-first behavior is deliberate.

</details>

### Step 3: Run A Manual Evaluation

Use manual outputs, saved model outputs, or a small script like the one in this module. For each example, mark pass or fail, failure type, likely diagnosis, and the first change to try. Use failure categories such as task ambiguity, missing context, bad evidence, shape drift, unsafe action, hallucinated detail, over-refusal, and regression. The goal is to debug the feature, not simply to produce a score.

Success criteria:

- [ ] Every failure has a named failure type.
- [ ] Every failure has a diagnosis, not just a complaint.
- [ ] The first proposed change targets the diagnosis.
- [ ] You do not change more than one variable in the proposed iteration.
- [ ] You record at least one case that should be rerun for regression.

<details>
<summary>Example solution</summary>

If the mixed billing and access case routes to `account_access`, label the failure as task ambiguity and diagnose the missing priority rule. The first change should add a billing-first rule while keeping the model, context, and schema unchanged. Rerun the mixed case plus at least two non-target cases, including one pure account-access case, to verify that the new rule did not over-route unrelated tickets.

</details>

### Step 4: Perform One Iteration

Choose one failure and apply one change, such as adding a priority rule, adding missing context, requiring a supporting quote, changing the output schema, adding validation for missing fields, narrowing the allowed labels, or adding a refusal rule. Rerun the same example, then rerun at least two other examples to check for regression. Record the before and after output because the written comparison is what turns the change into learning.

Success criteria:

- [ ] The iteration changes one variable only.
- [ ] The before and after outputs are recorded.
- [ ] The diagnosis explains why the change should help.
- [ ] At least two non-target examples are rerun.
- [ ] You can state whether the change improved, worsened, or did not affect the eval set.

<details>
<summary>Example solution</summary>

The iteration adds only this rule: "If a ticket includes both a billing problem and another problem, choose billing first unless required account information is missing." The target mixed case changes from `account_access` to `billing`, while a pure login failure remains `account_access` and a missing-account refund case remains `needs_human_review`. The decision is to keep the rule and add more mixed-issue examples before expanding scope.

</details>

### Step 5: Evaluate Whether v1 Can Ship

Make a launch recommendation: ship to a small internal group, run another iteration before shipping, narrow the scope and retest, or do not ship yet. Justify the recommendation with evidence, including what works, what still fails, what humans must review, what the system must not do, and what signal you will monitor after launch. A responsible answer can say "not yet" when the evidence is not strong enough.

Success criteria:

- [ ] The recommendation is tied to eval results.
- [ ] Known failure modes are documented.
- [ ] The launch boundary is explicit.
- [ ] Human review is assigned where risk remains.
- [ ] The system has a rollback, disablement, or fallback plan.

<details>
<summary>Example solution</summary>

Ship only to the internal triage team if the eval set shows reliable queue suggestions, quote support, and correct escalation for missing evidence. Keep automatic routing disabled, monitor human overrides, review unsupported quote failures weekly, and keep a simple disablement path that returns the workflow to manual triage. If the mixed cases still fail or wrong outputs are hard to detect, narrow scope and rerun the eval before launch.

</details>

## Sources

- [OpenAI Evals](https://github.com/openai/evals)
- [OpenAI Evals guide](https://platform.openai.com/docs/guides/evals)
- [OpenAI Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs)
- [OpenAI Prompt Engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [NIST AI RMF Playbook](https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Anthropic Evaluation Tool docs](https://docs.anthropic.com/en/docs/test-and-evaluate/eval-tool)
- [AWS Bedrock model evaluation docs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation.html)
- [Google Vertex AI evaluation overview](https://cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview)
- [Azure AI Foundry evaluation guidance](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-approach-gen-ai)

## Next Module

From here, continue to:

- [AI/ML Engineering: AI-Native Development](../../ai-ml-engineering/ai-native-development/)
- or [AI/ML Engineering: Generative AI](../../ai-ml-engineering/generative-ai/)
