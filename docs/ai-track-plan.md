# AI Track Plan

## Positioning

This track is not a replacement for `AI/ML Engineering`.

It exists for learners who need:
- AI literacy from zero
- practical AI working habits before deep engineering
- a safe bridge into AI-native workflows

The differentiation is important:
- `AI` teaches how to understand and use AI well
- `AI/ML Engineering` teaches how to build, deploy, and operate AI/ML systems

## Why This Track Exists

KubeDojo already covers advanced AI/ML engineering well, but it has a learner-access gap:
- a person can reach the site with zero AI context
- they may need AI literacy long before they need RAG, fine-tuning, MLOps, or inference infrastructure
- AI usage is becoming a general technical skill, not only a specialist discipline

So the new top-level `AI` track should serve:
- beginners
- self-learners
- cloud-native learners who need safe AI habits
- technical practitioners who want AI-native work before AI/ML engineering

## Scope

The initial AI track has two sections.

### 1. AI Foundations

Goal: build conceptual confidence and safe usage habits.

Modules:
1. `What Is AI?`
2. `What Are LLMs?`
3. `Prompting Basics`
4. `How to Verify AI Output`
5. `Privacy, Safety, and Trust`
6. `Using AI for Learning, Writing, Research, and Coding`

### 2. AI-Native Work

Goal: turn AI from a novelty into a disciplined workflow tool.

Modules:
1. `Practical AI Tool Use`
2. `AI Agents and Assistants`
3. `Designing AI Workflows`
4. `Human-in-the-Loop Habits`

## Explicit Boundaries

This track should not drift into:
- generic consumer-AI hype content
- deep model training theory
- vector databases, GPU scheduling, vLLM, or MLOps
- “AI replaces humans” framing

Those belong elsewhere:
- `AI/ML Engineering`
- `Platform`
- `On-Premises`

## Default Learner Route

```text
AI Foundations
   |
AI-Native Work
   |
AI/ML Engineering (optional advanced path)
```

### Common entry points

- absolute beginner curious about AI:
  `AI Foundations`
- learner using AI for study and work:
  `AI Foundations -> AI-Native Work`
- technical learner moving toward builder workflows:
  `AI Foundations -> AI-Native Work -> AI/ML Engineering`

## Acceptance Criteria For Initial Delivery

- top-level `AI` track exists in the repo and navigation
- section hubs exist for `AI Foundations` and `AI-Native Work`
- all initial module route anchors exist as real pages
- homepage reflects the new track clearly
- planning and implementation are tracked on GitHub with explicit ACs
- the site build passes

## Follow-On Work

Likely next section after the initial launch:
- `AI for Kubernetes and Platform Work`

That would be the differentiator layer:
- AI-assisted YAML review
- AI-assisted troubleshooting and incident support
- trust boundaries for infra work
- AI for study and operator workflows
