Here is a comprehensive reorganization plan that modernizes the KubeDojo AI/ML curriculum for the 2026 landscape, adhering to all your constraints.

# AI/ML Curriculum 2026 Reorganization Plan

## Executive Summary & Order Priorities
The original curriculum (inherited from neural-dojo) treated Machine Learning as a traditional 2023-era data science discipline, pushing deployment (MLOps) and infrastructure to the very end while front-loading Deep Learning. 

For a **2026 AI Engineer**, the paradigm has flipped: composing agentic applications and deploying them to production (LLMOps) is the core job. Training foundational models from scratch (Deep Learning) or using Classical ML has become a specialized track rather than the starting point.

**Priorities for the 2026 Learner:**
1. **Tooling First:** Master AI-Native Development (CLI agents, Agent IDEs) immediately. You cannot build AI efficiently without using AI effectively.
2. **Applied GenAI & Agents:** Learn LLMs, RAG, and Agents before learning how backpropagation works. 
3. **Shift-Left on Deployment:** MLOps/LLMOps and K8s Infrastructure must be learned *immediately* after building agents, not as an afterthought at the end of the course.
4. **Foundations Later:** Deep Learning, PyTorch, and Classical ML are moved to the later phases as "Under the Hood" knowledge.

---

## 1. New Phase Order & Rationale

### Phase 0: Prerequisites (Unchanged)
- **Rationale:** Foundational setup remains necessary.

### Phase 1: AI-Native Development (Expanded)
- **Rationale:** In 2026, AI tools (Claude Code, Agent IDEs) are table stakes. Engineers must learn how to collaborate with AI before building AI systems.
- **Current Modules:** AI coding tools, local models, Claude Code, agent IDEs, CLI agents, prompt eng, code gen, debugging, tools.

### Phase 2: Generative AI Fundamentals
- **Rationale:** Core LLM mechanics. You need to understand context windows, tokens, and basic generation before utilizing RAG or Agents.
- **Current Modules:** intro to LLMs, tokenization, text generation.
- **Reassignments In:** *Code generation models* (moved from Phase 7).

### Phase 3: Vector Search & RAG
- **Rationale:** The most ubiquitous enterprise AI pattern. Flows naturally from text generation.
- **Current Modules:** embeddings, vector spaces, vector DBs, RAG systems, RAG vs finetuning, advanced RAG.

### Phase 4: Frameworks & Agents
- **Rationale:** Evolving from static RAG to dynamic, autonomous agents.
- **Current Modules:** LangChain, tools/function calling, CoT, LangGraph, LlamaIndex, advanced agentic, agents in production.

### Phase 5: MLOps & LLMOps *(Previously Phase 10)*
- **Rationale:** **The most critical shift.** In 2026, once you build an agent, you need to deploy it. Pushing MLOps to Phase 10 is an outdated batch-training mindset. Today's engineers need Docker, CI/CD, and K8s immediately after learning to build apps.
- **Current Modules:** devops fundamentals, Docker, CI/CD for ML, K8s for ML, advanced K8s ML, experiment tracking, data versioning, pipeline orchestration, model deployment, monitoring.

### Phase 6: AI Infrastructure & Scaling *(Previously Phase 11)*
- **Rationale:** Naturally follows MLOps. Once deployed on Kubernetes, you must manage cloud resources, GPUs, and operational logging.
- **Current Modules:** cloud management, AIOps log analysis.

### Phase 7: Advanced GenAI & AI Safety *(Merged Phases 7 & 9)*
- **Rationale:** Fine-tuning, RLHF, and Safety go hand-in-hand. You should not learn fine-tuning without understanding alignment, red teaming, and evaluation frameworks.
- **Current Modules:** fine-tuning, diffusion, RLHF, constitutional AI, alignment, red teaming, LLM evaluation.

### Phase 8: Multimodal AI *(Previously Phase 5)*
- **Rationale:** A specialized domain. Best explored after mastering text-based agents, MLOps, and basic fine-tuning.
- **Current Modules:** speech, vision, video.

### Phase 9: Deep Learning Foundations *(Previously Phase 6)*
- **Rationale:** In 2026, most developers consume models via APIs or open-source weights. Building neural networks from scratch and doing manual backprop is now "under the hood" knowledge for specialists.
- **Current Modules:** Python ML, neural nets from scratch, PyTorch, training, CNNs, transformers, backprop.

### Phase 10: Classical ML *(Previously Phase 8)*
- **Rationale:** Tabular and time-series data remain important for enterprise, but they represent the "old guard" of ML. Placed here for complete foundational knowledge.
- **Current Modules:** tabular, time-series, AutoML/feature stores.

### Appendix A: History of AI/ML *(Previously Phase 12)*
- **Rationale:** Historical context is valuable but shouldn't block the practical learning path. Moved to an appendix.
- **Current Modules:** history of AI/ML.

---

## 2. Module Reassignments & Regrouping

| Module | Moving From | Moving To | Why? |
| :--- | :--- | :--- | :--- |
| **Code Generation Models** | Phase 7 (Adv GenAI) | Phase 2 (GenAI Fundamentals) | Code generation is now a fundamental text-generation capability for developers, not an "advanced" niche topic. It pairs perfectly with basic LLM mechanics. |
| **AI Safety Modules (All 3)** | Phase 9 (AI Safety) | Phase 7 (Adv GenAI & Safety) | Safety, evaluation, and red-teaming are inextricably linked to Fine-Tuning and RLHF. They must be taught together to ensure responsible model adaptation. |
| **MLOps Modules (All 8)** | Phase 10 | Phase 5 | Deployment and operationalizing agents is the bottleneck in 2026. Students need this immediately after building their first agent in Phase 4. |
| **AI Infrastructure (All 2)** | Phase 11 | Phase 6 | Infrastructure is the physical layer of MLOps. It must directly follow deployment concepts. |

---

## 3. Recommended New Modules for 2026

To fully modernize the curriculum without dropping any existing content, consider adding the following modules to flesh out the 2026 reality:

*   **Phase 1 (AI-Native Dev):** 
    *   *Model Context Protocol (MCP):* Connecting local data sources, APIs, and tools securely to agentic IDEs.
*   **Phase 4 (Frameworks & Agents):** 
    *   *Multi-Agent Orchestration Systems:* Moving beyond single-agent architectures to supervisor/worker and swarm patterns.
*   **Phase 5 (MLOps & LLMOps):** 
    *   *Prompt & Context Versioning:* Git for prompts and system instructions, which is entirely distinct from traditional data versioning.
*   **Phase 6 (AI Infrastructure):**
    *   *Serverless GPU Inference:* Optimizing cold starts, KV caching, and scaling tools like vLLM/Ollama in production.
*   **Phase 8 (Multimodal AI):**
    *   *Real-Time Streaming Agents:* Handling WebRTC, low-latency audio, and streaming vision processing (the GPT-4o / Gemini 2.0 paradigm).
