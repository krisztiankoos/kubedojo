# AI/ML Learner Curriculum Plan

## Goal

Design the AI/ML curriculum as a **learner path**, not just a pile of topics.

The current repo already contains strong AI/ML material across:
- `ai-ml-engineering`
- `platform/disciplines/data-ai/*`
- `platform/toolkits/data-ai-platforms/*`
- `on-premises/ai-ml-infrastructure`

The main remaining gap is not broad topic absence. The gap is a **clear progression for learners**, especially for:
- laptop-first learning
- single-GPU / workstation learning
- small private or home-lab AI systems
- moving from notebooks and local experiments into reproducible systems

## Design Principles

1. **Local-first is a valid entry path**
   Many learners will start on a laptop, workstation, or small home server before they ever touch real cluster-scale infrastructure.

2. **Application, model, and platform paths must all exist**
   Not every learner wants to become a model researcher. Not every learner wants to run GPU clusters. The curriculum should support multiple destinations.

3. **Notebooks are a phase, not a destination**
   We should teach notebooks as a useful tool, but also teach when and how to outgrow them.

4. **Home-scale AI is now real**
   Consumer GPUs, quantization, local inference, and lightweight fine-tuning are no longer edge cases. They need explicit curriculum space.

5. **Avoid duplication**
   We should not rewrite topics that already exist elsewhere in the repo. We should add missing bridge modules and cross-link existing advanced material.

## Planned Curriculum Shape

### Layer 1: Foundation Spine

This is the path every AI/ML learner should be able to follow.

#### Phase 0: Setup and Working Environment
- `0.1` Prerequisites & Environment Setup
- `0.2` Home AI Workstation Fundamentals `NEW`
- `0.3` Reproducible Python, CUDA, and ROCm Environments `NEW`
- `0.4` Notebooks, Scripts, and Project Layouts `NEW`

#### Phase 1: AI-Native Development
- existing `ai-native-development` section

#### Phase 2: LLM and Generative AI Fundamentals
- existing `generative-ai` section

#### Phase 3: Retrieval and Context Engineering
- existing `vector-rag` section
- `3.6` Home-Scale RAG Systems `NEW`

#### Phase 4: Frameworks and Agents
- existing `frameworks-agents` section

#### Phase 5: MLOps and LLMOps
- existing `mlops` section
- `5.11` Notebooks to Production for ML/LLMs `NEW`
- `5.12` Small-Team Private AI Platform `NEW`

### Layer 2: Model Builder Path

For learners who want to understand training, tuning, and evaluation deeply.

#### Phase 6: Deep Learning Foundations
- existing `deep-learning` section

#### Phase 7: Advanced GenAI and Safety
- existing `advanced-genai` section
- `7.10` Single-GPU Local Fine-Tuning `NEW`
- `7.11` Multi-GPU and Home-Lab Fine-Tuning `NEW`

#### Phase 8: Multimodal AI
- existing `multimodal-ai` section

#### Phase 9: Classical ML
- existing `classical-ml` section

### Layer 3: Platform and Infrastructure Path

For learners who want to run AI systems in production or private infrastructure.

#### Phase 10: AI Infrastructure Core
- existing `ai-infrastructure` section
- `10.4` Local Inference Stack for Learners `NEW`
- `10.5` Home AI Operations and Cost Model `NEW`

#### Phase 11: Platform Extensions
- existing `platform/disciplines/data-ai/mlops`
- existing `platform/disciplines/data-ai/ai-infrastructure`
- existing `platform/toolkits/data-ai-platforms/ml-platforms`
- existing `on-premises/ai-ml-infrastructure`

### Appendix
- existing `history` section

## Planned New Modules

These are the missing modules that would make the curriculum coherent for learners.

### Priority A: Must Add

1. **Home AI Workstation Fundamentals**
   Hardware planning, RAM/VRAM, storage, thermals, power, PCIe, Linux assumptions, realistic expectations for laptops vs desktops vs small servers.

2. **Reproducible Python, CUDA, and ROCm Environments**
   Python envs, package isolation, CUDA/ROCm compatibility, drivers, wheels, containers, avoiding environment drift.

3. **Notebooks, Scripts, and Project Layouts**
   When notebooks help, when they hurt, how to structure notebooks, scripts, data, and outputs without creating chaos.

4. **Home-Scale RAG Systems**
   Embeddings, chunking, vector DB choices, storage footprint, offline/privacy tradeoffs, realistic local deployment patterns.

5. **Notebooks to Production for ML/LLMs**
   Converting exploratory work into reproducible runs, tracked artifacts, deployable code, and reviewable pipelines.

6. **Single-GPU Local Fine-Tuning**
   LoRA-style adaptation, small datasets, VRAM limits, checkpoint handling, evaluation discipline, when local fine-tuning is worth it.

7. **Local Inference Stack for Learners**
   Ollama vs `llama.cpp` vs vLLM vs sglang, who each tool is for, hardware expectations, throughput vs convenience.

### Priority B: Strongly Recommended

8. **Small-Team Private AI Platform**
   What to self-host before Kubeflow-scale complexity: model registry, experiment tracking, simple serving, docs, access control.

9. **Multi-GPU and Home-Lab Fine-Tuning**
   When a learner grows from one GPU to a small multi-GPU or small private cluster setup.

10. **Home AI Operations and Cost Model**
   Power, cooling, GPU utilization, model storage, quantization tradeoffs, when local gets more expensive than cloud.

## Recommended Learner Routes

We should present the curriculum as routes, not just phase numbers.

### Route A: AI Application Engineer

Best for backend or product engineers building LLM applications.

Recommended order:
1. Setup and working environment
2. AI-native development
3. Generative AI
4. Retrieval and context engineering
5. Frameworks and agents
6. MLOps and LLMOps
7. Local inference stack

### Route B: Local-First Independent Builder

Best for learners working from a laptop, workstation, or home server.

Recommended order:
1. Setup and home workstation fundamentals
2. AI-native development
3. Local inference stack
4. Generative AI
5. Home-scale RAG
6. Notebooks to production
7. Single-GPU fine-tuning

### Route C: Model Engineer

Best for learners who want to train, tune, and evaluate models seriously.

Recommended order:
1. Setup and reproducible environments
2. Generative AI
3. Deep learning foundations
4. Advanced GenAI and safety
5. Single-GPU fine-tuning
6. MLOps and LLMOps
7. Multimodal or classical ML depending on interest

### Route D: AI Platform Engineer

Best for platform engineers and infra-heavy operators.

Recommended order:
1. Setup and working environment
2. MLOps and LLMOps
3. AI infrastructure core
4. Platform `data-ai` disciplines
5. ML platforms toolkit
6. On-prem AI/ML infrastructure

## What Should Stay Cross-Linked Instead of Duplicated

These topics already exist and should be treated as advanced extensions, not rewritten as new beginner modules:
- distributed training infrastructure
- GPU provisioning and scheduling at cluster scale
- Kubeflow platform internals
- vLLM and large-scale serving internals
- on-prem AI/ML infrastructure operations
- AIOps and predictive operations

## What This Plan Changes

This plan does **not** require immediate large-scale reorganization of published URLs.

It does require:
- clearer learner-route guidance
- explicit local-first bridge modules
- explicit home-scale fine-tuning and inference coverage
- clearer transition from notebooks and experiments into real systems

## Proposed Execution Order

1. Approve this curriculum map.
2. Create module specs for Priority A modules.
3. Write those modules before broad new-topic expansion.
4. Add route guidance to the AI/ML track index.
5. Cross-link the platform and on-prem advanced sections as extensions.

## Decision

The AI/ML curriculum should be treated as:
- **one main learner track** with a strong foundation spine
- **multiple guided routes** for different learner goals
- **cross-track extensions** for advanced platform and private-infrastructure topics

This is the most learner-friendly design without throwing away the strong content that already exists.
