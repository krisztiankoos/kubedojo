# AI/ML Engineering Curriculum Modernization Plan (April 2026)

Based on a codebase review of the current AI/ML Engineering curriculum, here is the modernization plan to bring the content up to date with the latest 2026 developments.

## 1. Outdated References to Update

Apply the following find/replace updates across the content repository. 

**Model Version Bumps:**
- `claude-3` → `claude-4.6` (including `-opus`, `-sonnet`, `-haiku` variants)
  - **Targets:** `src/content/docs/ai-ml-engineering/vector-rag/*`, `ai-native-development/*`, `frameworks-agents/*`, `multimodal-ai/*`
- `gpt-4-turbo` / `gpt-4` → `gpt-5`
  - **Targets:** `src/content/docs/ai-ml-engineering/ai-native-development/*`, `generative-ai/*`, `frameworks-agents/*`
- `llama 2` → `llama 4`
  - **Targets:** `src/content/docs/ai-ml-engineering/advanced-genai/*`, `history/*`, `generative-ai/*`, `vector-rag/*`
- `gemini-pro` / `gemini-pro-vision` → `gemini-3.5-pro` (or latest `gemini-3.x` equivalent)
  - **Targets:** `src/content/docs/ai-ml-engineering/multimodal-ai/module-5.2-vision-ai.md`

**Framework/Library Updates:**
- **LangChain:** Update references from 0.1.x patterns to 0.4+ APIs. Replace monolithic chains (e.g., `LLMChain`) with LCEL (LangChain Expression Language) and LangGraph.
  - **Targets:** `src/content/docs/ai-ml-engineering/frameworks-agents/module-4.1-langchain-fundamentals.md`, `vector-rag/*`, `mlops/*`
- **LlamaIndex:** Update from 0.9.x to the latest 1.x modular architecture.
  - **Targets:** `src/content/docs/ai-ml-engineering/frameworks-agents/module-4.4-llamaindex.md`, `module-4.5-building-ai-agents.md`
- **Kubeflow:** Ensure all YAMLs, definitions, and component decorators utilize Kubeflow Pipelines v2 (KFP v2) syntax instead of legacy v1.
  - **Targets:** `src/content/docs/ai-ml-engineering/mlops/module-10.5-advanced-kubernetes.md`, `module-10.8-ml-pipelines.md`

---

## 2. Missing 2026 Topics — New Modules to Write

Here are the 8 critical new modules needed to close the gap between 2024/2025 AI and the 2026 reality.

**1. Working with 1M+ Token Context & Prompt Caching**
- **Target Phase:** Phase 2 (Generative AI) or Phase 3 (Vector Search & RAG)
- **Scope:** Deep dive into effectively utilizing Claude 4.6 and Gemini 3.x's massive context windows. Covers needle-in-a-haystack retrieval limitations, zero-shot learning with massive context, and optimizing costs through prompt and prefix caching. 
- **Why it matters in 2026:** Massive context windows have fundamentally altered the "RAG vs. Context" debate. In many scenarios, simple RAG pipelines are being replaced by dropping entire repositories/books into context and utilizing prompt caching to keep inference costs low and latencies fast.

**2. Reasoning Models: System 2 Thinking (o1, o3, DeepSeek R1)**
- **Target Phase:** Phase 2 (Generative AI)
- **Scope:** Explores the paradigm shift introduced by OpenAI's o-series, DeepSeek R1, and Claude's reasoning models. Covers test-time compute scaling, reinforcement learning for reasoning (RL-R), chain-of-thought verification, and when to use reasoning models vs. standard LLMs.
- **Why it matters in 2026:** Reasoning models require entirely different prompting paradigms (less micromanagement, more goal-orientation) and have distinct cost/latency tradeoffs.

**3. Model Context Protocol (MCP) & Standardized Tools**
- **Target Phase:** Phase 4 (Frameworks & Agents)
- **Scope:** Comprehensive guide to building and consuming MCP (Model Context Protocol) servers. Teaches how to connect AI agents to databases, APIs, and file systems using a unified, standardized protocol rather than writing custom JSON schemas for every model.
- **Why it matters in 2026:** MCP has become the definitive industry standard for tool use, solving the fragmentation problem and allowing "plug-and-play" capabilities for agents like Claude Code, Cursor, and custom LangGraph agents.

**4. Computer Use and Browser Automation Agents**
- **Target Phase:** Phase 4 (Frameworks & Agents)
- **Scope:** Building agents that can control GUIs and browsers autonomously using Anthropic's Computer Use API and the OpenAI Operator. Covers coordinate-based visual grounding, DOM navigation, and designing secure boundaries for headless browser agents.
- **Why it matters in 2026:** AI has broken out of the API/text boundary. UI automation is a massive leap in agentic capabilities, moving from pure text manipulation to universal task execution on standard operating systems.

**5. Next-Gen Agentic Frameworks (Letta, AutoGen 0.4+, CrewAI 0.5+)**
- **Target Phase:** Phase 4 (Frameworks & Agents)
- **Scope:** Shifts focus from sequential chains to true autonomous multi-agent systems. Explores event-driven agents, OS-like persistent memory (using Letta, formerly MemGPT), and highly concurrent orchestration.
- **Why it matters in 2026:** Frameworks have matured. Production agents are no longer just loops of text generation; they are stateful, asynchronous, multi-actor systems with persistent long-term memory.

**6. High-Performance LLM Inference (vLLM & sglang)**
- **Target Phase:** Phase 11 (AI Infrastructure)
- **Scope:** State-of-the-art serving architectures for self-hosted open-weights models (Llama 4, DeepSeek V3, Qwen 3). Covers continuous batching, KV cache management, prefix caching, and speculative decoding using vLLM 0.6+ and sglang.
- **Why it matters in 2026:** As enterprises deploy more powerful open-source models locally or on private clouds, achieving high throughput and low latency at scale is the primary engineering bottleneck.

**7. Modern PEFT: Beyond Standard LoRA (DoRA & PiSSA)**
- **Target Phase:** Phase 7 (Advanced GenAI)
- **Scope:** Moving beyond basic LoRA to modern fine-tuning techniques like Weight-Decomposed Low-Rank Adaptation (DoRA) and PiSSA. Focuses on aligning open-weights models for highly specific domain tasks with minimal compute.
- **Why it matters in 2026:** The frontier of fine-tuning has evolved to offer near full-parameter performance with fraction-of-a-percent parameter updates, enabling extremely efficient local model customization.

**8. Multimodal-First AI Design**
- **Target Phase:** Phase 5 (Multimodal AI)
- **Scope:** Designing systems around natively multimodal models (Gemini 3, GPT-5) that process text, audio, image, and video simultaneously in the same latent space without relying on bolt-on encoders (STT/TTS).
- **Why it matters in 2026:** Native multimodal capabilities unlock new use cases like real-time video analysis and native voice interaction with near-zero latency, rendering pipeline-based multimodal approaches obsolete.

---

## 3. Deprecated Practices to Remove or Mark Legacy

To keep the curriculum focused on state-of-the-art engineering, the following topics should be explicitly marked as **Legacy** or removed:

1. **Monolithic LangChain Abstractions:** `LLMChain`, `SequentialChain`, and heavy Python class-based wrappers should be marked deprecated. The modern standard is LCEL (LangChain Expression Language), raw SDKs, or LangGraph.
2. **Basic / Naive RAG without Caching:** Demote basic semantic search-only RAG to introductory theory. Standard RAG modules should now assume Parent-Document Retrieval, Hybrid Search, and Prompt Caching by default.
3. **Custom JSON Tool Schemas:** Writing bespoke JSON schemas to bind tools to LLMs should be marked as a legacy anti-pattern, pointing students directly to **MCP (Model Context Protocol)** instead.
4. **Standard LoRA for Fine-Tuning:** Mark standard LoRA as effectively superseded by more advanced PEFT methods (DoRA/PiSSA) for robust enterprise fine-tuning.
5. **Kubeflow Pipelines v1 (KFP v1):** Any remaining references or code snippets utilizing KFP v1 syntax must be marked as legacy.

---

## 4. Priority Order

When rolling out these updates, tackle them in the following order of impact:

1. **High Priority (Immediate Impact on Agentic/GenAI workflows)**
   - Create **Reasoning Models** module (Changes fundamental prompting/routing).
   - Create **Model Context Protocol (MCP)** module (Crucial for modern agent integration).
   - Create **1M+ Token Context & Prompt Caching** module (Fundamentally shifts the RAG paradigm).
2. **Medium Priority (Codebase Health & Modernization)**
   - Execute the **Outdated Reference find/replaces** (Crucial for maintaining student trust).
   - Create **Computer Use and Browser Automation** module.
   - Create **Next-Gen Agentic Frameworks** module.
3. **Infrastructure & Fine-Tuning Priority**
   - Create **High-Performance LLM Inference (vLLM)** module.
   - Create **Modern PEFT (DoRA & PiSSA)** module.
   - Create **Multimodal-First AI Design** module.
