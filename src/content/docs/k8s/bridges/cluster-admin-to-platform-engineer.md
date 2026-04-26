---
title: "From Cluster Admin to Platform Engineer"
sidebar:
  order: 2
---

This bridge is for learners who have CKA, CKAD, CKS, or equivalent cluster administration experience and want to move into platform engineering. It closes the gap between operating Kubernetes resources and designing an internal platform as a product with reliability goals, golden paths, GitOps discipline, service ownership, observability, and adoption mechanics.

## Diagnostic — Are You Ready?

- [ ] You can write an SLO that is neither impossibly tight nor too vague to guide decisions.
- [ ] You can explain the difference between an SLI, an SLO, an SLA, and an error budget.
- [ ] You have shipped a Terraform module, Helm chart, template, or automation path that other people actually used.
- [ ] You know what a golden path is and how it differs from a tutorial or wiki page.
- [ ] You have measured developer cycle time, deployment frequency, lead time, or change failure rate.
- [ ] You have participated in an incident postmortem that identified system and process causes.
- [ ] You can explain GitOps reconciliation and why manual cluster changes create hidden drift.
- [ ] You can describe a service ownership model that includes on-call, documentation, escalation, and lifecycle expectations.
- [ ] You can distinguish platform features from platform products.
- [ ] You can explain why self-service without guardrails becomes operational debt.
- [ ] You can identify when a cluster problem is really an organizational boundary problem.
- [ ] You can say no to a platform feature when it does not improve reliability, delivery speed, compliance, or operability.

## Skills Gap Map

| What you have | What you need | Where to study it |
|---|---|---|
| Kubernetes object fluency | Systems thinking across teams, services, and feedback loops | [What is Systems Thinking?](/platform/foundations/systems-thinking/module-1.1-what-is-systems-thinking/) |
| Cluster troubleshooting | Reliability goals and error-budget decisions | [Reliability Engineering](/platform/foundations/reliability-engineering/) |
| Metrics and logs usage | Observability as a design discipline | [Observability Theory](/platform/foundations/observability-theory/) |
| Security controls | Security principles embedded in platform defaults | [Security Principles](/platform/foundations/security-principles/) |
| Resource administration | Service ownership and operational models | [SRE](/platform/disciplines/core-platform/sre/) |
| YAML delivery | GitOps reconciliation and drift control | [GitOps](/platform/disciplines/delivery-automation/gitops/) |
| One-off automation | Reusable golden paths and developer experience | [Platform Engineering](/platform/disciplines/core-platform/platform-engineering/) |
| Tool familiarity | Tool selection based on user journeys and platform constraints | [Platform Toolkits](/platform/toolkits/) |
| Access management | Secret and policy workflows teams can adopt | [Vault](/platform/toolkits/security-quality/security-tools/module-4.1-vault-eso/) |
| Application deployment | Internal developer portal patterns | [Backstage](/platform/toolkits/infrastructure-networking/platforms/module-7.1-backstage/) |

## Sequenced Path

1. Start with [What is Systems Thinking?](/platform/foundations/systems-thinking/module-1.1-what-is-systems-thinking/).
   Why this step: platform work is about feedback loops, incentives, constraints, and service boundaries, not only cluster state.

2. Continue through [Reliability Engineering](/platform/foundations/reliability-engineering/).
   Why this step: SLOs, error budgets, and reliability tradeoffs are the language used to decide what the platform should optimize.

3. Study [Observability Theory](/platform/foundations/observability-theory/).
   Why this step: platform teams need to make failure modes visible to service teams without turning every user into an observability expert.

4. Move into [SRE](/platform/disciplines/core-platform/sre/).
   Why this step: SRE connects reliability targets, incident response, toil reduction, and operational ownership.

5. Read [Platform Engineering](/platform/disciplines/core-platform/platform-engineering/).
   Why this step: the platform becomes an internal product when it has users, adoption paths, feedback loops, and a support model.

6. Study [GitOps](/platform/disciplines/delivery-automation/gitops/).
   Why this step: reconciliation discipline turns Kubernetes operations into reviewable, repeatable, auditable system change.

7. Add [Argo CD](/platform/toolkits/cicd-delivery/gitops-deployments/module-2.1-argocd/) when you need implementation detail.
   Why this step: tools are easier to evaluate once you understand reconciliation, ownership, promotion, and rollback requirements.

8. Add [Backstage](/platform/toolkits/infrastructure-networking/platforms/module-7.1-backstage/) when you are ready to design developer entry points.
   Why this step: an internal developer portal is useful only when it reflects real service ownership and golden-path workflows.

9. Add [Vault](/platform/toolkits/security-quality/security-tools/module-4.1-vault-eso/) when secrets and identity become platform primitives.
   Why this step: platform teams must make secure defaults easier than unsafe workarounds.

## Anti-patterns

- Treating platform engineering as just YAML at scale.
- Building golden paths nobody uses because no developer workflow was measured first.
- Ignoring developer cycle-time data and optimizing only cluster cleanliness.
- Conflating SRE with an on-call rotation.
- Installing Backstage, Argo CD, or Vault before defining the operating model they serve.
- Creating self-service APIs without ownership, support, deprecation, and incident paths.

## What success looks like

- You can describe platform users, their constraints, and the work they are trying to finish.
- You can define a golden path with defaults, escape hatches, documentation, and support boundaries.
- You can use SLOs and error budgets to prioritize platform work.
- You can identify toil and decide whether to automate, document, delegate, or delete it.
- You can explain how GitOps reduces drift and improves reviewability.
- You can evaluate tools by adoption, operability, and reliability impact instead of feature lists.

## First module to read

Start with [What is Systems Thinking?](/platform/foundations/systems-thinking/module-1.1-what-is-systems-thinking/).
