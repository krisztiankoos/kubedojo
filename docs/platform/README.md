# Platform Engineering Track

> **Beyond Certifications** - Deep practitioner knowledge for SRE, Platform Engineering, DevSecOps, and MLOps.

---

## Why This Track Exists

Kubernetes certifications teach you *how* to use Kubernetes. This track teaches you *how to run production systems* on Kubernetes - the disciplines, principles, and tools that separate operators from practitioners.

This is for people who:
- Have Kubernetes fundamentals (or certifications)
- Want to understand theory, not just tools
- Need to make technology decisions at work
- Want to implement best practices, not just pass exams

---

## Structure

```
platform/
├── foundations/        # Theory that doesn't change
│   ├── systems-thinking/
│   ├── reliability-engineering/
│   ├── observability-theory/
│   ├── security-principles/
│   └── distributed-systems/
│
├── disciplines/        # Applied practices
│   ├── sre/
│   ├── platform-engineering/
│   ├── gitops/
│   ├── devsecops/
│   ├── mlops/
│   └── iac/                # Infrastructure as Code
│
└── toolkits/           # Current tools (will evolve)
    ├── observability/      # Prometheus, OTel, Grafana
    ├── gitops-tools/       # ArgoCD, Flux
    ├── security-tools/     # Vault, OPA, Falco
    ├── platforms/          # Backstage, Crossplane
    ├── ml-platforms/       # Kubeflow, MLflow
    └── iac-tools/          # Terraform, OpenTofu, Pulumi
```

---

## Reading Order

### Start with Foundations

Theory that applies everywhere. Read these first - they don't change.

| Track | Why Start Here |
|-------|---------------|
| [Systems Thinking](foundations/systems-thinking/) | Mental models for complex systems |
| [Reliability Engineering](foundations/reliability-engineering/) | Failure theory, redundancy, risk |
| [Distributed Systems](foundations/distributed-systems/) | CAP, consensus, consistency |
| [Observability Theory](foundations/observability-theory/) | What to measure and why |
| [Security Principles](foundations/security-principles/) | Zero trust, threat modeling |

### Then Pick a Discipline

Applied practices - how to do the work.

| Discipline | Best For |
|------------|----------|
| [SRE](disciplines/sre/) | Operations, reliability, on-call |
| [Platform Engineering](disciplines/platform-engineering/) | Developer experience, self-service |
| [GitOps](disciplines/gitops/) | Deployment, reconciliation |
| [DevSecOps](disciplines/devsecops/) | Security integration, compliance |
| [MLOps](disciplines/mlops/) | ML lifecycle, model serving |
| [Infrastructure as Code](disciplines/iac/) | IaC patterns, testing, drift management |

### Reference Toolkits as Needed

Tools change. Use these as reference when implementing.

| Toolkit | When to Use |
|---------|-------------|
| [Observability](toolkits/observability/) | Setting up monitoring/tracing |
| [GitOps Tools](toolkits/gitops-tools/) | Implementing ArgoCD/Flux |
| [Security Tools](toolkits/security-tools/) | Policy, secrets, runtime security |
| [Platforms](toolkits/platforms/) | Building internal platforms |
| [ML Platforms](toolkits/ml-platforms/) | ML infrastructure |
| [IaC Tools](toolkits/iac-tools/) | Terraform, OpenTofu, Pulumi, Ansible |

---

## Module Format

Every module includes:

- **Why This Matters** - Real-world motivation
- **Theory** - Principles and mental models
- **Current Landscape** - Tools that implement this
- **Hands-On** - Practical implementation
- **Best Practices** - What good looks like
- **Common Mistakes** - Anti-patterns to avoid
- **Further Reading** - Books, talks, papers

---

## Status

🚧 **This track is under development.**

| Section | Status |
|---------|--------|
| Foundations | 📋 Planned |
| Disciplines | 📋 Planned |
| Toolkits | 📋 Planned |

---

## Prerequisites

Before starting this track, you should have:
- Kubernetes basics (or completed [Prerequisites](../prerequisites/))
- Some production experience (helpful but not required)
- Curiosity about "why" not just "how"

---

*"Tools change. Principles don't."*
