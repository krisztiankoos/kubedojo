---
revision_pending: true
title: "Anthropic Agent SDK and Runtime Patterns"
slug: ai-ml-engineering/ai-native-development/module-1.10-anthropic-agent-sdk-and-runtime-patterns
sidebar:
  order: 111
---
> **AI/ML Engineering Track** | Complexity: `[MEDIUM]` | Time: 2-3
---
**Reading Time**: 2-3 hours
**Prerequisites**: Claude Code & CLI Deep Dive, CLI AI Coding Agents, Building with AI Coding Assistants, and Model Context Protocol for Agents
---

## What You'll Be Able to Do

By the end of this module, you will:
- explain what the Claude Agent SDK adds beyond a plain chat or client SDK integration
- design an agent loop around tools, permissions, sessions, hooks, and verification
- decide when MCP should be used as the external tool boundary and when built-in tools are enough
- reason about long-running agent risks such as runaway tool usage, context drift, and unsafe autonomy
- choose between hand-rolled orchestration and SDK-managed runtime patterns based on the job

**Why this matters**: many teams understand prompts, model APIs, and tool calling separately, but still do not have a serious runtime model for agents. They wire up a chat loop, add a few tools, and call it an agent. That works until the system needs permissions, long-lived context, retries, observability, or controlled autonomy. The Claude Agent SDK exists to solve that runtime layer directly.

---

## First: What This SDK Actually Is

Anthropic’s current official product name is the **Claude Agent SDK**. [Older references may still call it the Claude Code SDK because it was originally exposed as the harness behind Claude Code](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk/). The important idea is stable even if naming has evolved:

**It gives you Claude Code's agent loop as a library.**

That means you are not just calling a model.
You are getting a packaged runtime with:
- built-in tools
- permission controls
- sessions
- hooks
- MCP integration
- subagent support
- context management for longer runs

This is the core distinction from a plain model client SDK.

With a client SDK, you usually implement:
- the tool loop
- tool permission checks
- message history handling
- retries
- context trimming
- execution controls

With the Agent SDK, much of that scaffolding is part of the runtime itself.

---

## The Runtime Problem Most Teams Underestimate

People often think agent architecture is mainly about:
- prompts
- models
- tool schemas

That is not enough.

A real agent runtime must answer:
- what tools is the agent allowed to use?
- when should it stop?
- how is work resumed across a session?
- how do we inspect what it actually did?
- how do we intervene before it causes damage?
- how do we stop context from degrading over long runs?

The Claude Agent SDK is valuable because it treats these as first-class concerns instead of leaving them as application glue.

---

## The Four Core Layers

You can think about the runtime in four layers.

### 1. Goal Layer

This is the user objective:
- review a pull request
- diagnose a failing service
- prepare a migration plan
- summarize and classify support tickets

The goal should be outcome-based, not step-by-step by default.

### 2. Tool Layer

This is what the agent can actually do.

Built-in tools documented by Anthropic include capabilities such as:
- file reads and edits
- writing new files
- bash command execution
- file discovery and grep-style search
- web search and web fetch
- background monitoring

This is already enough to solve many agent tasks.

### 3. Control Layer

This is where the runtime becomes serious.

You need:
- permissions
- hooks
- checkpoints
- observability
- usage tracking
- approval boundaries

Without this layer, "agentic" usually just means "unsafe scripting with a language model."

### 4. Session Layer

Longer-running work needs continuity.

Sessions matter because real agents often:
- gather context
- act
- verify
- revise
- continue later

If every run is stateless, the system keeps losing momentum or rebuilding context expensively.

---

## The Gather -> Act -> Verify Loop

[Anthropic’s engineering guidance around the Agent SDK maps well to a very practical loop](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk/):

1. gather context
2. take action
3. verify the result
4. repeat if needed

This sounds obvious, but many weak agent systems skip the verify step.

That creates fragile behavior:
- code gets changed without tests
- files get edited without review
- external tools get called without checking side effects
- the agent keeps moving forward on a false assumption

The verify step is what separates a useful agent from a noisy automation loop.

Examples of verification:
- run tests
- lint code
- compare outputs against an expected format
- check whether the target file actually changed
- confirm whether a retrieved answer is grounded in the right source

---

## Built-In Tools vs MCP

One of the most common design mistakes is forcing MCP everywhere.

### Use Built-In Tools When

- the task is local to the workspace
- file operations are enough
- shell access is the real execution surface
- you want simple, direct control

Examples:
- fix failing tests
- refactor a directory
- inspect logs on a working host
- generate documentation from a codebase

### Use MCP When

- the agent needs structured access to external systems
- auth and API behavior should be standardized outside the prompt
- tools should be portable across clients or runtimes
- you want better separation between agent logic and service integration

Examples:
- GitHub issues
- Slack
- internal databases
- ticketing systems
- cloud control planes

This is the practical rule:

[**Built-in tools are the local execution surface. MCP is the external integration surface.**](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk/)

Trying to replace one with the other usually makes the system worse.

---

## Permissions Are Not a Detail

The official docs emphasize permissions, and for good reason.

Agent systems fail socially before they fail technically when operators do not know:
- what the agent can do
- what the agent just did
- what the agent still wants to do

The right permission model depends on the task.

### Low-Risk Tasks

Examples:
- read-only repo analysis
- documentation drafts
- code review comments

Good default:
- broad read
- restricted write
- no destructive shell actions

### Medium-Risk Tasks

Examples:
- local bug fixes
- test repair
- internal refactors

Good default:
- scoped write access
- controlled shell tools
- clear checkpoints or approval rules

### High-Risk Tasks

Examples:
- production operations
- external system mutations
- credential-adjacent tasks

Good default:
- narrow tools
- human approval gates
- auditability and rollback paths

The bad pattern is giving broad autonomy because the demo felt impressive.

---

## Sessions and Long-Running Work

The Agent SDK exposes sessions because useful work often extends beyond one short exchange.

Why sessions matter:
- the agent can continue work without rehydrating everything from scratch
- cost and latency can improve because context reuse is possible
- user intent and intermediate reasoning stay coherent across steps

But sessions introduce responsibility:
- stale assumptions can persist
- weak early decisions can contaminate later work
- hidden drift becomes harder to notice

So session design needs discipline:
- keep goals explicit
- checkpoint important state
- [compact context deliberately](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk/)
- avoid letting weak intermediate notes become permanent truth

Long-lived memory is only useful if it remains trustworthy.

---

## Hooks and Runtime Control

Hooks matter because they let you intercept and shape behavior without rewriting the agent loop itself.

This is operationally powerful.

Hooks are useful for:
- approval checks before sensitive actions
- logging and audit trails
- policy enforcement
- post-tool validation
- side-channel notifications

Examples:
- block writes outside an allowed directory
- require review before any `Bash` command that mutates infra
- capture all external tool calls to a monitoring stream
- auto-run a verifier after file edits

This is where the SDK becomes more than convenience.
It becomes a controllable runtime.

---

## Subagents and Decomposition

The overview docs also expose subagents as a first-class capability.

That matters because many tasks benefit from specialization:
- one agent investigates
- one agent edits
- one agent verifies

But subagents are not free.

They add:
- coordination cost
- context boundaries
- more places to lose accountability

Use them when:
- tasks decompose naturally
- [the work is meaningfully parallelizable](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk/)
- verification boundaries are clear

Do not use them just because "multi-agent" sounds advanced.

A single well-controlled agent is often better than three loosely controlled ones arguing with each other.

---

## When the Agent SDK Beats Hand-Rolled Loops

The Agent SDK is usually the better choice when:
- you want Claude Code-style autonomy in your own app
- you need built-in tools quickly
- you care about sessions and longer loops
- you need permissions, hooks, and observability without rebuilding them
- the workload fits an iterative gather/act/verify pattern

Examples:
- coding assistants inside an internal platform
- on-call triage agents
- repo maintenance bots
- research assistants that read, synthesize, and verify

In those cases, reinventing the runtime usually wastes time.

---

## When a Hand-Rolled Loop Is Still Better

You may not want the full agent harness when:
- the task is simple request/response inference
- tools are extremely narrow and deterministic
- you need provider-neutral orchestration across many models
- every step must be explicitly scripted by your application
- the operational risk of autonomy is higher than the productivity benefit

Examples:
- one-shot classification
- simple retrieval with fixed workflow
- strict transactional workflows
- regulated pipelines with no discretionary tool use

In those cases, a client SDK plus explicit orchestration may be cleaner.

The right question is not:
"Is the Agent SDK more powerful?"

It is:
"Does this task benefit from an agent runtime or from explicit workflow control?"

---

## The Biggest Runtime Mistakes

### Mistake 1: Treating the SDK Like a Fancy Chat Wrapper

If you do not think about permissions, sessions, hooks, or verification, you are probably not really using the runtime.

### Mistake 2: Giving the Agent Too Many Tools Too Early

More tools increase reach and failure surface at the same time.

### Mistake 3: Confusing MCP With Agent Logic

MCP should expose structured capabilities. It should not carry the burden of the whole runtime design.

### Mistake 4: Ignoring Verification

Without verification, the agent accumulates silent errors.

### Mistake 5: Running Long Sessions Without Compaction Discipline

Long context is helpful until it becomes clutter. Then it starts degrading reasoning quality and cost.

---

## A Healthy Design Pattern

For most teams, the safest first pattern looks like this:

1. narrow goal
2. small tool set
3. explicit permissions
4. session enabled
5. one or two hooks for validation
6. a verification step after any meaningful action
7. clear escalation path to a human

That is enough to build a serious agent without pretending you already need a fully autonomous digital employee.

---

## How This Fits With the Rest of the Track

This module sits between two nearby ideas:

- earlier modules in `ai-native-development` teach coding agents and MCP from a user/operator perspective
- later platform and infrastructure modules teach how to run larger systems safely

This module is the bridge between those layers.

It answers:
- how do I package agent behavior as a runtime?
- how do I control that runtime?
- when should I trust the harness, and when should I keep explicit orchestration?

That is the real engineering question.

---

## Key Takeaways

- the Claude Agent SDK is not just a model wrapper; it is a runtime harness with tools, permissions, sessions, hooks, and context management
- built-in tools are best for local execution, while MCP is best for structured external integrations
- the gather -> act -> verify loop is the right mental model for serious agents
- sessions, hooks, and permissions are what turn an agent from a demo into an operable system
- the Agent SDK is strongest when you want controlled autonomy, not when you need a tightly scripted deterministic workflow

---

<!-- v4:generated type=no_quiz model=codex turn=1 -->
## Quiz


**Q1.** Your team built an internal coding assistant by looping a chat model over a few custom tool calls. It can edit files, but after longer tasks it loses track of what it already tried, repeats failed steps, and sometimes makes changes without checking whether they worked. What runtime capabilities are missing, and why would the Claude Agent SDK be a better fit than a plain client SDK here?

<details>
<summary>Answer</summary>
The system is missing core runtime features such as session handling, verification, permission controls, retries, and context management for longer runs. The Claude Agent SDK is a better fit because it provides Claude Code's agent loop as a library, including built-in tools, sessions, hooks, MCP integration, subagent support, and longer-run context handling. A plain client SDK would leave the team to build that runtime scaffolding themselves.
</details>

**Q2.** Your platform team wants an agent to refactor a local codebase, fix failing tests, and generate updated docs from files already in the workspace. One engineer proposes exposing everything through MCP because “agents should use MCP for all tools.” Based on the module, what is the better design choice and why?

<details>
<summary>Answer</summary>
The better design is to use built-in tools, not MCP, for this job. The task is local to the workspace, depends on file operations and shell execution, and does not require structured access to external systems. The module’s rule is that built-in tools are the local execution surface, while MCP is the external integration surface. Forcing MCP everywhere would add unnecessary complexity.
</details>

**Q3.** An on-call team wants an agent to update records in a cloud control plane and create follow-up tickets in external systems. They also need authentication and API behavior handled consistently across clients. Should they rely mainly on built-in tools or MCP, and what is the reasoning?

<details>
<summary>Answer</summary>
They should use MCP for those external integrations. The module recommends MCP when the agent needs structured access to external systems, when auth and API behavior should be standardized outside the prompt, and when tools should be portable across clients or runtimes. Built-in tools are better for local execution, but cloud control planes and ticketing systems are exactly the kind of external systems MCP is meant to expose.
</details>

**Q4.** Your team gives an agent broad shell access so it can help with production incidents. During a maintenance window, operators realize they cannot tell what the agent already changed, what it is about to do next, or where approval should have happened. What permission and control pattern should have been used instead?

<details>
<summary>Answer</summary>
The team should have used a high-risk permission model: narrow tools, human approval gates, and strong auditability with rollback paths. The module stresses that permissions are not a detail, especially for production operations and external mutations. They also should have used hooks and checkpoints so sensitive actions could be intercepted, logged, validated, or blocked before damage occurred.
</details>

**Q5.** A repo-maintenance agent gathers context, edits several files, and immediately moves on to another task without checking whether the edits actually solved the problem. A day later, the team discovers the first change broke the build and all later work was based on that mistake. Which part of the runtime loop was skipped, and what should verification have looked like?

<details>
<summary>Answer</summary>
The agent skipped the verify step in the gather -> act -> verify loop. Verification should have included checks such as running tests, linting code, confirming the target files changed as intended, or comparing outputs against expected results. The module explains that verification is what prevents agents from continuing on false assumptions and accumulating silent errors.
</details>

**Q6.** A support operations team enables long-lived sessions so an agent can resume work across several days. After a week, the agent keeps reusing an outdated assumption from early in the session, and that stale note keeps shaping later decisions. According to the module, what session discipline is missing?

<details>
<summary>Answer</summary>
The missing discipline is explicit goal management, checkpointing important state, deliberate context compaction, and avoiding weak intermediate notes becoming permanent truth. The module says sessions are useful for continuity, cost, and latency, but they introduce risks such as stale assumptions, hidden drift, and contaminated later decisions if session state is not maintained carefully.
</details>

**Q7.** A manager asks for a “multi-agent” redesign of a straightforward analysis task because it sounds more advanced. The proposed setup uses one subagent to investigate, one to edit, and one to verify, even though the work is sequential and small. Based on the module, should the team adopt subagents here?

<details>
<summary>Answer</summary>
Probably not. The module says subagents should be used when tasks decompose naturally, work is meaningfully parallelizable, and verification boundaries are clear. In a small, sequential task, subagents would add coordination cost, context boundaries, and more places to lose accountability. A single well-controlled agent is often the better design.
</details>

<!-- /v4:generated -->
<!-- v4:generated type=no_exercise model=codex turn=1 -->
## Hands-On Exercise


**Goal:** Build a small Claude Agent SDK prototype that uses a gather -> act -> verify loop, applies scoped permissions, adds one runtime hook, and clearly separates built-in tools from MCP-style external integrations.

- [ ] Create a new working directory for the exercise and initialize a minimal project structure for an agent runtime experiment.
  ```bash
  mkdir anthropic-agent-runtime-lab
  cd anthropic-agent-runtime-lab
  mkdir prompts logs workspace
  touch README.md runner.py policy.md
  ```

- [ ] Write a short task definition in `policy.md` for an agent that can inspect files in `workspace/`, propose a change, and verify the result before finishing.
  Suggested constraints:
  - built-in tools may read and edit files only inside `workspace/`
  - destructive shell actions are not allowed
  - verification must run before the task is marked complete

- [ ] Add a small sample target in `workspace/notes.txt` with intentionally messy content the agent can improve, such as duplicated lines, inconsistent bullets, or missing summary text.
  ```bash
  cat > workspace/notes.txt <<'EOF'
  Runtime design notes
  - tools matter
  - tools matter
  - permissions unclear
  - no verify step yet
  EOF
  ```

- [ ] Implement a simple runner in `runner.py` that models these stages:
  - gather context from `workspace/notes.txt`
  - act by proposing or applying a cleanup
  - verify by checking the file changed as expected
  - stop if verification fails

- [ ] Add one explicit runtime control rule to the runner, such as blocking edits outside `workspace/` or rejecting commands that contain `rm`, `sudo`, or network access.

- [ ] Add one hook-like behavior in the runner that logs each stage to `logs/run.log`, including:
  - task goal
  - tools requested
  - action taken
  - verification result

- [ ] Document which actions would remain built-in tool work and which would move to MCP if the agent later needed external systems.
  Add examples in `README.md` for both categories:
  - built-in: local file read, edit, grep, shell verification
  - MCP: GitHub issues, Slack messages, ticket creation, cloud APIs

- [ ] Run the prototype once on the sample file and inspect the output artifacts.
  ```bash
  python3 runner.py
  echo "----- notes.txt -----"
  cat workspace/notes.txt
  echo "----- run.log -----"
  cat logs/run.log
  ```

- [ ] Intentionally trigger one blocked action in the runner, such as an attempted write outside `workspace/`, and confirm the permission rule prevents it.
  ```bash
  python3 runner.py --simulate-blocked-write
  ```

- [ ] Verify that the exercise demonstrates the runtime pattern, not just text generation.
  Check that your prototype includes:
  - a goal
  - a constrained tool surface
  - a control decision
  - a verification step
  - a durable session artifact such as `logs/run.log`

- [ ] Extend the design with a short note describing when a hand-rolled loop is still sufficient and when the full Agent SDK runtime would be the better choice.

Verification commands:
```bash
ls -R
cat workspace/notes.txt
cat logs/run.log
python3 runner.py --simulate-blocked-write
grep -R "verify" -n .
```

Success criteria:
- The prototype follows a clear gather -> act -> verify loop.
- At least one permission boundary is enforced and demonstrated.
- A hook or hook-like logging mechanism records runtime behavior.
- The exercise distinguishes built-in tools from MCP external integrations correctly.
- Verification produces concrete evidence that the agent’s action succeeded or was safely blocked.

<!-- /v4:generated -->
## Next Modules

- [Building with AI Coding Assistants](./module-1.9-building-with-ai-coding-assistants/)
- [Model Context Protocol (MCP) for Agents](../frameworks-agents/module-1.8-model-context-protocol/)
- [Computer Use and Browser Automation Agents](../frameworks-agents/module-1.9-computer-use-agents/)

## Sources

- [anthropic.com: building agents with the claude agent sdk](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk/) — Anthropic’s engineering post explicitly says the Claude Code SDK is being renamed to the Claude Agent SDK and explains that it is the harness behind Claude Code.
- [New capabilities for building agents on the Anthropic API](https://www.anthropic.com/news/agent-capabilities-api/) — This announcement provides adjacent context on Anthropic’s agent-building primitives such as MCP connectivity, code execution, files, and longer-lived context.
- [Claude Agents](https://www.anthropic.com/solutions/agents) — This product overview is useful for learners who want the higher-level framing of where Anthropic positions agents and Claude Code in the broader platform.
