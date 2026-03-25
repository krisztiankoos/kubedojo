# CLAUDE.md

This file provides guidance to Claude Code when working with the KubeDojo project.

## Project Overview

KubeDojo is a **free, open-source cloud native curriculum** covering:

1. **Fundamentals** — Zero to Terminal, Linux Everyday Use, Philosophy & Design, Cloud Native 101, K8s Basics, Modern DevOps, Linux Deep Dive
2. **Cloud** — Hyperscaler Rosetta Stone, AWS/GCP/Azure Essentials, Architecture Patterns, EKS/GKE/AKS Deep Dives, Advanced Operations, Managed Services, Enterprise & Hybrid
3. **Certifications** — All 5 Kubestronaut certs (CKA, CKAD, CKS, KCNA, KCSA), Extending Kubernetes, 10+ tool-specific certs
4. **Platform Engineering** — Foundations (systems thinking, reliability, observability, security, distributed systems, engineering leadership, advanced networking), Disciplines (SRE, platform eng, GitOps, DevSecOps, MLOps, AIOps, IaC, release eng, chaos eng, FinOps, data eng, AI infrastructure), Toolkits (17 categories, 75+ tools)

**Philosophy**: Quality education should be free. We challenge paid certification courses by providing better content at no cost.

**Website**: https://kube-dojo.github.io/ (MkDocs Material, pinned to mkdocs<2.0.0)

**Ukrainian translation**: ~40% complete (Prerequisites, CKA, CKAD). Uses mkdocs-static-i18n with `.uk.md` suffix files.

## Quality Standards

Every module MUST include (10/10 on the Dojo Scale):

### Structure
- **Complexity tag**: `[QUICK]`, `[MEDIUM]`, or `[COMPLEX]`
- **Time to Complete**: Realistic estimate
- **Prerequisites**: What modules/knowledge needed first
- **Why This Module Matters**: Dramatic opening with real-world scenario (third person)
- **Did You Know?**: Exactly 4 interesting facts per module
- **Common Mistakes**: Table with 6-8 rows (Mistake | Why It Happens | How to Fix)
- **Quiz**: 6-8 questions with hidden answers using `<details>` tags
- **Hands-On Exercise**: Multi-step with clear success criteria (`- [ ]` checklist)
- **Next Module**: Link to continue learning

### Content Quality
- **600-800+ lines minimum** — modules are chapters, not blog posts
- **Theory depth**: Explain "why" not just "what"
- **Junior-friendly**: Treat reader as smart beginner, no assumed knowledge
- **Entertaining**: Analogies, war stories with financial impact, conversational tone
- **Practical**: All code must be runnable, not pseudocode
- **Exam-aligned**: Match official curriculum (for cert tracks)
- **No repetitive numbers**: Avoid using "47" repeatedly (known LLM pattern — vary numbers)

### Technical Standards
- kubectl alias: Use `k` consistently (after Module 0.2)
- YAML: 2-space indentation, valid syntax
- Kubernetes version: 1.35+ (current exam version)
- Commands: Complete, not abbreviated
- Code blocks: Always specify language (```bash, ```yaml, ```go)

## Site Structure

```
Site tabs: Home | What's New | Fundamentals | Cloud | Certifications | Platform Engineering

docs/
├── prerequisites/              # Fundamentals tab
│   ├── zero-to-terminal/       # 10 modules — absolute beginner
│   ├── philosophy-design/      # 4 modules
│   ├── cloud-native-101/       # 5 modules
│   ├── kubernetes-basics/      # 8 modules
│   └── modern-devops/          # 6 modules
│
├── linux/                      # Also in Fundamentals tab
│   └── foundations/
│       ├── everyday-use/       # 5 bridge modules (after Zero to Terminal)
│       ├── system-essentials/  # 4 modules (kernel, processes)
│       ├── container-primitives/ # 4 modules (namespaces, cgroups)
│       └── networking/         # 4 modules (TCP/IP, iptables)
│   ├── security/hardening/     # 4 modules
│   └── operations/             # 16 modules (performance, troubleshooting, shell, sysadmin)
│
├── cloud/                      # Cloud tab
│   ├── hyperscaler-rosetta-stone.md  # Cross-provider comparison
│   ├── aws-essentials/         # 12 modules
│   ├── gcp-essentials/         # 12 modules
│   ├── azure-essentials/       # 12 modules
│   ├── architecture-patterns/  # 4 modules (vendor-neutral)
│   ├── eks-deep-dive/          # 5 modules
│   ├── gke-deep-dive/          # 5 modules
│   ├── aks-deep-dive/          # 4 modules
│   ├── advanced-operations/    # 10 modules
│   ├── managed-services/       # 10 modules
│   └── enterprise-hybrid/      # 10 modules
│
├── k8s/                        # Certifications tab
│   ├── extending/              # 8 modules (controllers, operators, webhooks)
│   ├── cka/                    # 39+ modules
│   ├── ckad/                   # 28+ modules
│   ├── cks/                    # 30+ modules
│   ├── kcna/                   # 21 modules
│   ├── kcsa/                   # 25 modules
│   └── ...                     # 10+ tool-specific certs
│
└── platform/                   # Platform Engineering tab
    ├── foundations/
    │   ├── systems-thinking/           # 4 modules
    │   ├── reliability-engineering/    # 5 modules
    │   ├── observability-theory/       # 4 modules
    │   ├── security-principles/        # 4 modules
    │   ├── distributed-systems/        # 3 modules
    │   ├── engineering-leadership/     # 6 modules (incidents, postmortems, on-call)
    │   └── advanced-networking/        # 6 modules (DNS, CDN, BGP, WAF)
    ├── disciplines/
    │   ├── sre/                  # 7 modules
    │   ├── platform-engineering/ # 6 modules
    │   ├── gitops/               # 6 modules
    │   ├── devsecops/            # 6 modules
    │   ├── mlops/                # 6 modules
    │   ├── aiops/                # 6 modules
    │   ├── iac/                  # 6 modules
    │   ├── release-engineering/  # 5 modules
    │   ├── chaos-engineering/    # 5 modules
    │   ├── finops/               # 6 modules
    │   ├── data-engineering/     # 6 modules
    │   └── ai-infrastructure/    # 6 modules
    └── toolkits/                 # 17 categories, 75+ tool modules
```

## Working with Gemini

KubeDojo uses a **multi-agent workflow** with Gemini via the ai_agent_bridge.

### Bridge Command
```bash
python scripts/ai_agent_bridge/__main__.py ask-gemini "prompt" --task-id "id" --stdout-only
```
Default model: `gemini-3.1-pro-preview`

### Gemini's Roles

**1. Adversary Reviewer (primary role)**
- Send completed work to Gemini for review BEFORE closing any issue
- Gemini catches: version inaccuracies, missing ACs, scope gaps, technical errors, Russicisms in Ukrainian translations
- If Gemini says NEEDS CHANGES, address feedback before closing
- Post Gemini's review as a comment on the issue

**2. Translator (Ukrainian)**
- Gemini produces good Ukrainian translations (99-100% of original length)
- Quality: 9-10/10 for Ukrainian language
- Must follow the glossary at `docs/uk-glossary.md` and rules in memory (`reference_gemini_ukrainian_rules.md`)

**3. Content Drafter (with expansion)**
- Gemini can write first drafts of modules (~350-400 lines)
- These drafts need Claude expansion to reach full quality (700-900+ lines)
- Workflow: Gemini drafts → Claude reads draft → Claude expands with more depth, tables, diagrams, code examples
- Use the writer prompt at `scripts/prompts/module-writer.md` when asking Gemini to draft

**4. Curriculum Planner**
- Gemini is good at identifying gaps and proposing structure
- Always push back if suggestions duplicate existing content (Gemini sometimes misses what already exists)
- Cross-reference Gemini's suggestions against the actual `docs/` directory

### What Gemini Cannot Do Well
- **Write full-depth modules from scratch** — produces outlines (~140-400 lines) instead of rich curriculum (~700-900 lines)
- **Track existing content** — sometimes suggests additions for topics already covered (Vault, Velero, KEDA were all flagged as "missing" when they already had deep modules)

### Multi-Agent Content Pipeline
For new modules, the optimal workflow is:
1. **Plan** with Gemini (gap analysis, module specs, structure)
2. **Draft** — either Gemini drafts (needs expansion) or Claude writes directly (full quality)
3. **Expand** — if Gemini drafted, Claude agent reads and expands to full depth
4. **Review** — Gemini adversary review (score, flag issues)
5. **Fix** — address Gemini feedback
6. **Commit** — with nav updates, READMEs, changelog

## Three-Pass Exam Strategy

Core strategy taught throughout certification tracks:
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

1. **READ `STATUS.md` FIRST** — instant context on current work
2. For new modules, use the writer prompt at `scripts/prompts/module-writer.md`
3. Run `/review-module` before considering a module complete
4. Update README progress when completing modules/parts
5. Send to Gemini for adversary review before closing issues

**Before ending a session or after completing modules:**
- **UPDATE `STATUS.md`** — current work, progress, blockers, notes
- This is mandatory — future sessions depend on it

## New Content Checklist

Every time new modules or content is added, do ALL of these BEFORE committing:

1. **mkdocs.yml nav** — add to navigation
2. **Parent README** — add module to the section's README table
3. **index.md** — update status table if significant
4. **changelog.md** — add entry for significant additions
5. **Build** — `source .venv/bin/activate && NO_MKDOCS_2_WARNING=1 mkdocs build` — verify 0 warnings
6. **Verify no orphaned modules** — every .md file should be in nav or be a .uk.md

## Ukrainian Translation

- **i18n plugin**: mkdocs-static-i18n with `docs_structure: suffix`
- **File naming**: `module-name.uk.md` alongside `module-name.md`
- **Glossary**: `docs/uk-glossary.md` — standardized K8s term translations
- **Audit script**: `bash scripts/translation-audit.sh <file.uk.md>`
- **Nav translations**: in mkdocs.yml under `nav_translations`
- **Rules**: No Russicisms, code blocks stay English, translate prose/headers/quiz/tables
- **Server restart required** after adding new .uk.md files — i18n plugin builds at startup

## Git Workflow

- Single branch: `main`
- Commit style: `feat:`, `docs:`, `fix:` prefixes
- Issue references: Include `#N` when relevant
- Push after completing logical units (module, part)
- Never push without building first (0 warnings)

## Build & Serve

```bash
source .venv/bin/activate
NO_MKDOCS_2_WARNING=1 mkdocs build          # Build (verify 0 warnings)
NO_MKDOCS_2_WARNING=1 mkdocs serve --dev-addr 127.0.0.1:8001 --no-livereload --clean  # Serve locally
```

Note: MkDocs 2.0 will break everything. Versions pinned in `requirements.txt`. Future migration: Zensical (drop-in replacement by Material team).

## Links

- **Repo**: https://github.com/kube-dojo/kube-dojo.github.io
- **CNCF Curriculum**: https://github.com/cncf/curriculum
- **CKA Program Changes**: https://training.linuxfoundation.org/certified-kubernetes-administrator-cka-program-changes/
- **Writer Prompt**: `scripts/prompts/module-writer.md`
- **Translation Glossary**: `docs/uk-glossary.md`
- **AI Agent Bridge**: `scripts/ai_agent_bridge/`
