# CLAUDE.md

This file provides guidance to Claude Code when working with the KubeDojo project.

## Project Overview

KubeDojo is a **free, open-source Kubernetes curriculum** with two tracks:
1. **Certifications** - All 5 Kubestronaut certs (CKA, CKAD, CKS, KCNA, KCSA) - ✅ Complete
2. **Platform Engineering** - SRE, GitOps, DevSecOps, MLOps - 🚧 In Progress

**Philosophy**: Quality education should be free. We challenge paid certification courses by providing better content at no cost.

**Current Focus**: Platform Engineering Track (foundations, disciplines, toolkits).

## Quality Standards

Every module MUST include:

### Structure
- **Complexity tag**: `[QUICK]`, `[MEDIUM]`, or `[COMPLEX]`
- **Time to Complete**: Realistic estimate
- **Prerequisites**: What modules/knowledge needed first
- **Why This Module Matters**: Motivate the learning
- **Did You Know?**: 2-3 interesting facts per module
- **Common Mistakes**: Table of pitfalls and solutions
- **Quiz**: Questions with hidden answers using `<details>` tags
- **Hands-On Exercise**: With clear success criteria
- **Next Module**: Link to continue learning

### Content Quality
- **Theory depth**: Explain "why" not just "what"
- **Junior-friendly**: Treat reader as beginner, no assumed knowledge
- **Entertaining**: Analogies, war stories, conversational tone
- **Practical**: All code must be runnable, not pseudocode
- **Exam-aligned**: Match official curriculum (for cert tracks)

### Technical Standards
- kubectl alias: Use `k` consistently (after Module 0.2)
- YAML: 2-space indentation, valid syntax
- Kubernetes version: 1.31+ (current exam version)
- Commands: Complete, not abbreviated

## Curriculum Structure

```
docs/
├── prerequisites/              # Beginners start here
│   ├── philosophy-design/
│   ├── cloud-native-101/
│   ├── kubernetes-basics/
│   └── modern-devops/
│
├── k8s/                        # Kubernetes certifications
│   ├── cka/
│   ├── ckad/
│   ├── cks/
│   ├── kcna/
│   └── kcsa/
│
└── platform/                   # Platform Engineering Track
    ├── foundations/            # Theory (stable)
    │   ├── systems-thinking/
    │   ├── reliability-engineering/
    │   ├── observability-theory/
    │   ├── security-principles/
    │   └── distributed-systems/
    ├── disciplines/            # Applied practices
    │   ├── sre/
    │   ├── platform-engineering/
    │   ├── gitops/
    │   ├── devsecops/
    │   └── mlops/
    └── toolkits/               # Current tools (evolving)
        ├── observability/
        ├── gitops-tools/
        ├── security-tools/
        ├── platforms/
        └── ml-platforms/
```

## Three-Pass Exam Strategy

Core strategy taught throughout curriculum:
1. **Pass 1**: Quick wins (1-3 min tasks) first
2. **Pass 2**: Medium tasks (4-6 min)
3. **Pass 3**: Complex tasks with remaining time

## Practice Environment Approach

- **Lightweight**: kind/minikube for most exercises
- **Multi-node**: kubeadm only when topic requires
- **Mock exams**: Questions + self-assessment, not simulation
- **Recommend killer.sh** for realistic exam simulation

## Commands Available

- `/review-module [path]` - Review single module quality
- `/review-part [dir]` - Review entire part for consistency
- `/verify-technical [path]` - Verify commands and YAML accuracy

## Session Workflow

When starting work on KubeDojo:

1. **READ `STATUS.md` FIRST** - Instant context on current work
2. For new modules, follow existing module structure exactly
3. Run `/review-module` before considering a module complete
4. Update README progress when completing modules/parts

**Before ending a session or after completing modules:**
- **UPDATE `STATUS.md`** - Current work, progress, blockers, notes
- This is mandatory - future sessions depend on it

## Platform Track Guidelines

For Platform Engineering modules:
- **Foundations**: Focus on theory/principles that don't change
- **Disciplines**: Applied practices, mental models, best practices
- **Toolkits**: Current tools with honest comparisons (these will evolve)

Platform modules include additional sections:
- **Current Landscape** - Tools that implement the concept
- **Best Practices** - What good looks like
- **Further Reading** - Books, talks, papers

## Git Workflow

- Single branch: `main`
- Commit style: `feat:`, `docs:`, `fix:` prefixes
- Issue references: Include `#N` when relevant
- Push after completing logical units (module, part)

## Links

- **Repo**: https://github.com/krisztiankoos/kubedojo
- **CNCF Curriculum**: https://github.com/cncf/curriculum
- **CKA Program Changes**: https://training.linuxfoundation.org/certified-kubernetes-administrator-cka-program-changes/
