# CLAUDE.md

This file provides guidance to Claude Code when working with the KubeDojo project.

## Project Overview

KubeDojo is a **free, open-source Kubernetes certification curriculum** covering all 5 certifications required for Kubestronaut status (CKA, CKAD, CKS, KCNA, KCSA).

**Philosophy**: Quality education should be free. We challenge paid certification courses by providing better content at no cost.

**Current Focus**: CKA (Certified Kubernetes Administrator) curriculum aligned with the 2025 exam changes.

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
- **Exam-aligned**: Match CKA 2025 curriculum exactly

### Technical Standards
- kubectl alias: Use `k` consistently (after Module 0.2)
- YAML: 2-space indentation, valid syntax
- Kubernetes version: 1.31+ (current exam version)
- Commands: Complete, not abbreviated

## Curriculum Structure

```
docs/cka/
├── part0-environment/         # Setup & exam technique
├── part1-cluster-architecture/ # 25% of exam
├── part2-workloads-scheduling/ # 15% of exam
├── part3-services-networking/  # 20% of exam
├── part4-storage/              # 10% of exam
├── part5-troubleshooting/      # 30% of exam
└── part6-mock-exams/           # Speed drills & practice
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

1. Check GitHub issues for current priorities
2. Review Issue #14 for curriculum monitoring status
3. For new modules, follow existing module structure exactly
4. Run `/review-module` before considering a module complete
5. Update README progress when completing modules/parts

## CKA 2025 Curriculum Alignment

**Added (must cover)**:
- Helm
- Kustomize
- Gateway API
- CRDs & Operators
- Pod Security Admission

**Deprioritized (mention but don't emphasize)**:
- etcd backup/restore
- Cluster upgrades
- Infrastructure provisioning

## Git Workflow

- Single branch: `main`
- Commit style: `feat:`, `docs:`, `fix:` prefixes
- Issue references: Include `#N` when relevant
- Push after completing logical units (module, part)

## Links

- **Repo**: https://github.com/krisztiankoos/kubedojo
- **CNCF Curriculum**: https://github.com/cncf/curriculum
- **CKA Program Changes**: https://training.linuxfoundation.org/certified-kubernetes-administrator-cka-program-changes/
