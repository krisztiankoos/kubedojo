# LLM-native app synthesis — Curriculum gap (build a real LLM app on K8s arc)

Captured 2026-05-14. Stage-1 research brief for #1187. This brief identifies a critical synthesis
gap in the AI/ML Engineering track. While individual specializations—vector storage, inference
servers, agent frameworks, GPU scheduling—are covered in depth across both the AI/ML Engineering
track and the Platform Engineering toolkits, KubeDojo lacks a cohesive integration path that
teaches learners how to stitch these components into a production-ready, Kubernetes-native LLM
application. This brief maps existing coverage, analyzes industry integration patterns, and
proposes a 3-module mini-arc to bridge the gap.

---

## §A. Source summary

### Existing KubeDojo Module Coverage

The synthesis gap is not a content gap—the individual ingredients exist. It is an *integration*
gap: no module in the curriculum teaches the cross-service wiring, failure-mode handling, and
operational discipline that transforms isolated components into a production LLM application.
What follows maps each relevant existing module to its synthesis role and the precise omission
that creates the gap.

#### AI/ML Engineering: Vector RAG section

**`ai-ml-engineering/vector-rag/index.md`**
The entry point for retrieval-backed systems. It maps the specialization path—Vector DBs →
RAG patterns → Evaluation → Home-scale—and provides a coherent narrative for the RAG arc.
The closing navigation, however, routes learners to either `frameworks-agents` or `mlops`
without providing an integration landing point. The fork creates a structural dead-end:
learners who complete both specializations have no module that combines them.
*Synthesis omission*: No "next step" connects RAG infrastructure to inference serving or
observability tooling.

**`ai-ml-engineering/vector-rag/module-1.1-vector-databases-deep-dive.md`**
Covers ANN index theory (HNSW, IVFFlat), collection design, payload indexing, and metadata
filtering for Qdrant, Pinecone, and Weaviate. The operational trade-offs between index types
under production query loads are treated well. The module correctly frames the Vector DB as
a service with its own scaling properties.
*Synthesis omission*: It treats the Vector DB as a standalone endpoint. It does not address
how to manage its lifecycle within a multi-service K8s application: PersistentVolume sizing
for index snapshots, NetworkPolicy rules restricting DB access to the application tier, or
readiness probe configuration that accounts for index hydration time after pod restarts.

**`ai-ml-engineering/vector-rag/module-1.2-building-rag-systems.md`**
Practical RAG pipeline construction: chunking strategies, embedding model selection, retrieval
re-ranking. It establishes the retrieval → augment → generate pattern clearly.
*Synthesis omission*: The RAG pipeline is implemented as a script or notebook. The module does
not address how this pipeline becomes a K8s Deployment—specifically, how to configure resource
limits when running an embedding model alongside retrieval logic, or how to handle ingestion
pipelines as CronJobs or event-driven Argo Workflows.

**`ai-ml-engineering/vector-rag/module-1.3-advanced-rag-patterns.md`**
Covers HyDE, multi-vector retrieval, parent-child chunking, and query routing. These are
application-level patterns that sit above the infrastructure layer.
*Synthesis omission*: Routing decisions (which RAG path to take per query) have latency
implications that interact with K8s HPA thresholds. This cross-layer concern is not addressed.

**`ai-ml-engineering/vector-rag/module-1.4-rag-evaluation-optimization.md`**
Introduces RAG evaluation dimensions—faithfulness, answer relevance, context precision—and
covers RAGAS metrics.
*Synthesis omission*: Evaluation is framed as an offline process. The module does not connect
evaluation to CI/CD gating, the pattern that DeepEval and Promptfoo enable in production.

**`ai-ml-engineering/vector-rag/module-1.6-home-scale-rag-systems.md`**
Addresses minimalist RAG on a single workstation: local embedding, local Qdrant instance,
a Chunk Manifest for reproducibility, and privacy-boundary reasoning. Explicitly targets the
learner who cannot or does not want cloud-hosted services.
*Synthesis omission*: The architecture is intentionally script-based and single-node. The
transition to a distributed, multi-service K8s architecture—where each component scales
independently, restarts independently, and communicates over a pod network—is not addressed.
The Chunk Manifest concept has no K8s-native equivalent (e.g., a ConfigMap or CRD) explored.

#### AI/ML Engineering: Frameworks and Agents section

**`ai-ml-engineering/frameworks-agents/module-1.3-langgraph-for-agents.md`**
Covers LangGraph's stateful graph execution model, node/edge design, and conditional routing.
Teaches multi-step agentic workflows with explicit state transitions.
*Synthesis omission*: LangGraph state persistence requires a checkpointer (Redis, Postgres).
The module does not address running the checkpointer as a K8s StatefulSet or configuring the
graph to reconnect after pod eviction.

**`ai-ml-engineering/frameworks-agents/module-1.5-building-ai-agents.md`**
Compares LangChain, LlamaIndex, and CrewAI. Covers Sub-Question Query Engines and multi-agent
orchestration including tool calling and memory injection. Includes a containerization example
and K8s Job usage.
*Synthesis omission*: While containerization is touched on, the module focuses on application
code. It does not address service-to-service authentication patterns (how the agent app
authenticates with a vLLM endpoint behind a ClusterIP service), context-window budget
management under high concurrency, or the failure modes specific to multi-agent workflows on
K8s (pod preemption mid-task, OOMKilled agents losing in-flight state).

**`ai-ml-engineering/frameworks-agents/module-1.6-agent-memory-planning.md`**
Covers memory taxonomy (in-context, external, procedural) and planning patterns (ReAct, MRKL).
External memory backends—vector stores, key-value stores—are discussed.
*Synthesis omission*: Memory backend selection is discussed in isolation. The module does not
cover how to deploy and operate a Redis or Postgres memory backend as a K8s StatefulSet, or
how to configure connection pooling when many agent pods share a single backend.

#### AI/ML Engineering: AI Infrastructure section

**`ai-ml-engineering/ai-infrastructure/module-1.3-vllm-sglang-inference.md`**
Excellent coverage of PagedAttention, continuous batching, and the KV-cache management model.
Provides a K8s Deployment manifest for vLLM and discusses tensor parallelism across multiple
GPU pods. This is the strongest infrastructure module in the track.
*Synthesis omission*: It treats inference as an isolated endpoint. It does not teach how an
application should handle vLLM's specific failure modes from the client side: KV-cache
saturation (503 responses at high concurrency), VRAM OOM evictions, or how to configure retry
logic in the orchestrator app that is appropriate for long-context generation tasks.

#### AI/ML Engineering: MLOps section

**`ai-ml-engineering/mlops/module-1.11-notebooks-to-production-for-ml-llms.md`**
Covers the full journey from experimental notebook to a containerized, CI/CD-managed ML
service. This is the closest existing module to the synthesis goal.
*Synthesis omission*: The production service pattern is focused on a single model serving path.
It does not address the multi-service dependency graph of an LLM-native app (inference backend
+ vector DB + orchestration layer + memory backend), cross-service health checks, rolling
updates that preserve in-flight requests, or distributed tracing across all four layers.

**`ai-ml-engineering/mlops/module-1.12-small-team-private-ai-platform.md`**
Addresses the full private AI platform for small teams: self-hosted models, cost constraints,
internal API gateway patterns.
*Synthesis omission*: The platform-level view abstracts away application architecture. It does
not address how a developer building an application on top of this platform should structure
their service, handle inference failures, or implement evals before deploying a new prompt
version.

#### AI/ML Engineering: Bridges section

**`ai-ml-engineering/bridges/ai-builder-to-platform-engineer.md`**
Connects the experience of an AI application builder to the platform engineering discipline.
Provides a conceptual bridge but not an implementation one.
*Synthesis omission*: Navigational, not instructional. No hands-on wiring of components.

**`ai-ml-engineering/bridges/home-lab-to-private-ai-infra.md`**
Bridges single-workstation AI setups to private infrastructure deployments.
*Synthesis omission*: Infrastructure-focused, not application-architecture focused.

#### Platform Engineering: ML Platforms toolkit

The Platform Engineering track covers individual tools at depth from the *operator's* seat:

- **`module-9.4-vllm`**: Platform operator perspective on vLLM—installation, GPU allocation,
  scaling configuration. Complements the AI infra module but does not address the application
  developer consumption patterns.
- **`module-9.5-ray-serve`**: Ray Serve as a platform component for multi-model pipelines and
  fractional GPU sharing. Platform operator lens; not the application developer.
- **`module-9.7-gpu-scheduling`**: NVIDIA GPU Operator, MIG partitioning, time-slicing.
  Focuses on making GPUs available; does not connect to right-sizing GPU requests from
  application-layer inference workload metrics.
- **`module-9.8-kserve`**: KServe for serverless inference, canary rollouts, and multi-model
  serving via InferenceService CRDs. Does not address the developer perspective: what KServe
  is abstracting away, and how to write a client that gracefully degrades when a model scales
  to zero.
- **`module-9.10-bentoml`**: BentoML for OCI-compliant model packaging and service
  composition. Does not address wiring BentoML services to an external LangGraph orchestrator.

*Common omission across all Platform toolkit modules*: They address the platform operator
configuring tools for others. None address the application developer consuming these platforms.

---

### Industry Integration Anchors

Each anchor exemplifies a specific integration pattern that the proposed mini-arc teaches
concretely. The HTTP status code of the canonical repository is noted in brackets.

**vLLM** (vLLM Team, `github.com/vllm-project/vllm`) [200]
The industry standard for high-throughput LLM inference in open-model deployments.
PagedAttention enables near-theoretical GPU memory utilization; continuous batching eliminates
head-of-line blocking. The key integration pattern: the *OpenAI-compatible inference backend*.
Applications use the same client code against both hosted APIs and self-hosted vLLM, enabling
local-to-cloud portability. For the synthesis arc, vLLM is the inference backend in Module 3.1
and the source of the failure modes that Module 3.2 must handle.

**BentoML** (`github.com/bentoml/BentoML`) [200]
The unified deployment framework that packages model weights, inference logic, preprocessing,
and API surface into a single OCI-compliant Bento artifact. Integration pattern: *service
composition*—multiple model services (embedding model + generator model) are defined as
BentoML Services with explicit dependency graphs, then deployed as a single unit. More portable
than hand-crafting multi-container Deployments. The synthesis arc references BentoML as an
alternative deployment shape when the learner's inference stack is a BentoML service tree.

**KServe** (`github.com/kserve/kserve`) [200]
The K8s-native model serving platform, built on Knative and Istio. Integration pattern:
*inference-as-a-platform*—models are declared as `InferenceService` CRDs; the platform handles
autoscaling (including scale-to-zero), canary rollouts via traffic splitting, and multi-model
serving behind a single endpoint. For the synthesis arc, KServe represents the "mature platform"
endpoint of a progression—learners who have completed the mini-arc understand what KServe is
abstracting away, rather than treating it as a black box.

**Ray Serve** (`github.com/ray-project/ray`) [200]
Built on Ray's distributed execution model. Integration pattern: *pipeline parallelism*—distinct
stages of an inference pipeline (embedding, retrieval, generation, post-processing) are defined
as separate Ray Serve Deployments that scale independently and communicate over Ray's object
store. The right pattern when processing stages have heterogeneous resource requirements: a
CPU-heavy retrieval stage and a GPU-heavy generation stage should not scale in lockstep.

**DeepEval** (`github.com/confident-ai/deepeval`) [200]
A Python-native testing framework for LLM applications. Integration pattern: *evals-as-unit-
tests*—RAG faithfulness, answer relevance, and context recall are implemented as pytest-style
assertions that run in CI. The pattern enforces that every change to a prompt or retrieval
pipeline passes a deterministic quality gate before deployment. Module 3.3 implements this.

**Promptfoo** (`github.com/promptfoo/promptfoo`) [200]
A YAML-driven evaluation and red-teaming framework. Integration pattern: *prompt regression
testing*—test cases verify output format, safety constraints, and factual grounding across
model versions and parameter changes. Natively integrates with GitHub Actions; can block a PR
if a prompt change degrades output quality beyond a configured threshold.

**LangSmith** (LangChain Inc., `docs.langchain.com/langsmith`) [308 → 200]
**LangFuse** (`github.com/langfuse/langfuse`) [200]
Both provide distributed tracing for multi-step LLM application calls. Integration pattern:
*request provenance*—every LLM call, retrieval operation, and tool invocation captured as a
span with latency, token counts, and cost attribution. LangSmith is the hosted option;
LangFuse is the self-hosted, open-source alternative appropriate for private infrastructure.
Module 3.3 teaches both as configuration options, not as mutually exclusive choices.

**NVIDIA GPU Operator** (`github.com/NVIDIA/gpu-operator`) [200]
The foundation layer that makes GPU resources available to K8s workloads: device plugin, DCGM
exporter for metrics, MIG configurator, and time-slicing. The synthesis arc does not re-teach
GPU Operator setup (covered in module-9.7) but builds on it: Module 3.1 assumes the operator
is installed and focuses on resource request sizing and DCGM metrics for HPA targets.

**Qdrant** (`github.com/qdrant/qdrant`) [200]
The vector database used as the concrete memory backend throughout the mini-arc. Chosen because
it supports both in-memory (development) and on-disk (production) modes from the same binary,
ships an official Helm chart, and exposes Prometheus metrics natively—all properties that
matter for the K8s integration patterns the arc teaches.

---

## §B. Curriculum slot proposal

### Existing-module coverage map

| Module | Location | Synthesis Role | Coverage | The Missing Stitch |
|--------|----------|----------------|----------|--------------------|
| vector-rag/index.md | ai-ml-engineering | Navigation | Partial | No integration landing point after the fork |
| module-1.1-vector-databases-deep-dive | ai-ml-engineering/vector-rag | Memory layer | Deep—standalone | K8s lifecycle: PV sizing, NetworkPolicy, readiness probes |
| module-1.2-building-rag-systems | ai-ml-engineering/vector-rag | Retrieval pipeline | Deep—script | K8s Deployment shape, CronJob ingestion |
| module-1.4-rag-evaluation-optimization | ai-ml-engineering/vector-rag | Quality gate | Deep—offline | CI/CD integration for eval gating |
| module-1.6-home-scale-rag-systems | ai-ml-engineering/vector-rag | Local prototype | Deep—single-node | Transition to distributed K8s topology |
| module-1.3-langgraph-for-agents | ai-ml-engineering/frameworks-agents | State machine | Deep—code | Checkpointer as K8s StatefulSet, reconnect after eviction |
| module-1.5-building-ai-agents | ai-ml-engineering/frameworks-agents | Orchestrator | Deep—code | Service-to-service auth, context budget, failure modes |
| module-1.6-agent-memory-planning | ai-ml-engineering/frameworks-agents | Memory taxonomy | Deep—concepts | Redis/Postgres as StatefulSets, connection pooling |
| module-1.3-vllm-sglang-inference | ai-ml-engineering/ai-infrastructure | Inference backend | Deep—isolated | Client-side failure handling: 503/OOM, retry strategy |
| module-1.11-notebooks-to-production | ai-ml-engineering/mlops | Production path | Partial | Multi-service dependency graph, distributed tracing |
| module-9.4-vllm | platform/toolkits/ml-platforms | Inference tool | Deep—operator | Application developer consumption patterns |
| module-9.5-ray-serve | platform/toolkits/ml-platforms | Pipeline tool | Deep—operator | Application developer consumption patterns |
| module-9.7-gpu-scheduling | platform/toolkits/ml-platforms | GPU substrate | Deep—operator | Right-sizing from inference workload metrics |
| module-9.8-kserve | platform/toolkits/ml-platforms | Serving platform | Deep—operator | Developer perspective: what KServe abstracts |
| module-9.10-bentoml | platform/toolkits/ml-platforms | Packaging tool | Deep—operator | Wiring BentoML services to external orchestrators |

### Output-shape recommendation: Mini-Arc

Three options were considered:

**Option A — Sidebar restructure**: add cross-references between existing modules. Cost: minimal.
Outcome: insufficient. The missing content is the integration glue between modules. Cross-references
cannot teach what is not written.

**Option B — Single bridge module**: add one module that synthesizes the integration. Outcome:
the integration domain (four specializations, cross-service failure handling, distributed tracing,
eval CI/CD) exceeds single-module scope without degenerating into a listicle. A "patterns" module
that does not force the learner to build anything teaches nothing.

**Option C — Mini-arc (recommended)**: three focused modules in a new `synthesis-apps/` section,
each with a single learning outcome that builds on the previous. The arc has sufficient space to
teach integration glue, not just list it. The three modules build a single application
progressively. Each module ends with a working artifact that is the substrate for the next.

The mini-arc lives in `src/content/docs/ai-ml-engineering/synthesis-apps/`.

### Proposed Modules

#### Module 3.1: The LLM-Native Stack — Inference and Memory on Kubernetes

**Slug**: `ai-ml-engineering/synthesis-apps/module-3.1-llm-native-stack-k8s`
**Parent directory**: `src/content/docs/ai-ml-engineering/synthesis-apps/`
**Prerequisites**: module-1.3-vllm-sglang-inference, module-1.1-vector-databases-deep-dive,
module-9.7-gpu-scheduling
**Estimated word count**: 3,500
**Learning outcome**: The learner can deploy vLLM and Qdrant as coordinated K8s services,
configure their internal networking and resource boundaries, and verify the stack is healthy
before any application code touches it.

Section outline:

1. *Architecture first, tools second*. Maps the LLM-native stack to a four-layer diagram:
   GPU substrate → inference backend → vector memory → orchestration layer. Establishes the
   vocabulary (and the layer responsibility boundaries) used throughout the arc.

2. *GPU provisioning for inference workloads*. Assumes NVIDIA GPU Operator is installed.
   Focuses on ResourceQuota configuration for namespaced GPU allocation and the difference
   between requesting a full GPU, a MIG slice, and a time-shared GPU for an inference workload.
   Does not re-teach GPU Operator setup.

3. *vLLM as a K8s service*. Advances beyond the isolated Deployment in module-1.3 to a
   production-shaped manifest: ConfigMap for model parameters, separate PVC for model weights,
   liveness/readiness probes that check the `/health/ready` endpoint (not just process
   liveness), and a ClusterIP Service that restricts inference access to the application
   namespace via NetworkPolicy.

4. *Qdrant on Kubernetes*. Helm-chart deployment with an explicit PVC for index persistence,
   Prometheus ServiceMonitor for DCGM and Qdrant metrics, and a readiness probe that waits for
   index hydration (the `/readiness` endpoint behavior after restart versus after first start).

5. *Verifying the stack end-to-end*. Using `kubectl exec` and curl to confirm the vLLM
   OpenAI-compatible endpoint responds, the Qdrant health endpoint is green, and a
   cross-service call from a temporary pod in the application namespace succeeds through the
   NetworkPolicy boundary.

6. *Failure injection*. A structured exercise: delete the vLLM pod, observe Qdrant probe
   behavior; delete the Qdrant pod, observe what a client would see. This is not a gotcha—it
   is the foundation for Module 3.2's error-handling code. Learners who skip this section
   cannot write the retry logic in Module 3.2 with any understanding of what they are handling.

#### Module 3.2: Wiring the LLM App — The Orchestration Layer

**Slug**: `ai-ml-engineering/synthesis-apps/module-3.2-wiring-the-llm-app`
**Parent directory**: `src/content/docs/ai-ml-engineering/synthesis-apps/`
**Prerequisites**: module-3.1-llm-native-stack-k8s, module-1.5-building-ai-agents,
module-1.3-langgraph-for-agents, module-1.6-agent-memory-planning
**Estimated word count**: 4,000
**Learning outcome**: The learner can build and deploy a LangGraph-based orchestration service
that calls the Module 3.1 vLLM and Qdrant backends, persists conversation state in a
K8s-native Redis StatefulSet, and handles the backend failure modes identified in Module 3.1.

Section outline:

1. *From graph code to K8s Deployment*. Converting a LangGraph application that works locally
   into a containerized service. Focuses on configuration management: replacing hardcoded URLs
   with env vars sourced from K8s Secrets and ConfigMaps that reference Service DNS names
   (`vllm.inference-ns.svc.cluster.local`). Explains why Service DNS is the right abstraction
   (not IP addresses, not Ingress hostnames for internal calls).

2. *Service-to-service authentication*. No production vLLM or Qdrant deployment should be
   open to all cluster traffic. Implements a shared-secret pattern using K8s Secrets and shows
   how to verify NetworkPolicy is enforcing the intended access boundary with `kubectl exec`
   probes from pods in and out of the allowed namespace.

3. *State persistence: Redis as a K8s StatefulSet*. Deploying Redis for LangGraph
   checkpointing. Covers StatefulSet headless service discovery, PersistentVolumeClaim per
   replica, and connection pool configuration for a multi-replica orchestration Deployment
   where many pods share one Redis leader.

4. *Context-window budget management*. LangGraph's conversation history grows with each turn.
   Implements a token-counting middleware that truncates history before it hits vLLM's context
   window limit. Explains why this is the application's responsibility, not the inference
   backend's—the backend cannot know which turns are worth preserving for the current task.

5. *Handling vLLM failure modes*. The failure modes from Module 3.1 become application logic:
   KV-cache saturation (503 from vLLM) → exponential backoff with jitter. VRAM OOM eviction
   (pod restarted, in-flight request dropped) → checkpoint the LangGraph state before the
   long-generation call so the user can retry without losing context.

6. *End-to-end smoke test*. A pytest suite that hits the orchestration service's API, verifies
   retrieval happened (by checking a Qdrant query log), and asserts the response is coherent.
   This test is the prerequisite for Module 3.3's CI integration, not an optional exercise.

#### Module 3.3: Production Gates — Evals, Observability, and Scaling

**Slug**: `ai-ml-engineering/synthesis-apps/module-3.3-production-gates`
**Parent directory**: `src/content/docs/ai-ml-engineering/synthesis-apps/`
**Prerequisites**: module-3.2-wiring-the-llm-app, module-1.4-rag-evaluation-optimization
**Estimated word count**: 3,800
**Learning outcome**: The learner can gate deployments with automated RAG evals, trace requests
across all four application layers, and configure HPA targets using inference-specific metrics
rather than CPU utilization.

Section outline:

1. *Why "it works" is not a production gate*. The distinction between functional correctness
   (the app returns a response) and quality correctness (the response is faithful, relevant, and
   not hallucinated). Establishes that eval gates are a CI/CD concern, not a post-deployment
   one. Grounds the section in the failure class that module-1.4 introduced.

2. *DeepEval integration*. Implementing faithfulness and answer relevance tests as pytest
   assertions against a golden dataset of 10-20 question-answer pairs that lives in version
   control alongside the application code. The test suite runs in a GitHub Actions job that
   calls the deployed evaluation endpoint, not a mock—this is intentional.

3. *Promptfoo for prompt regression*. YAML-based prompt test cases that verify output format,
   safety constraints, and factual grounding across prompt versions. Configuring a Promptfoo CI
   step that blocks merge if any test degrades beyond a defined threshold. Explains the
   threshold-setting decision as a product decision, not an infrastructure one.

4. *Distributed tracing with LangSmith or LangFuse*. Instrumenting the LangGraph application
   to emit traces. LangSmith (hosted) is the default configuration; LangFuse (self-hosted K8s
   Deployment, `github.com/langfuse/langfuse`) is the alternative for private infrastructure.
   Shows how to correlate a user request ID across vLLM spans, Qdrant query spans, and
   LangGraph node spans using a common trace ID injected at the orchestration layer.

5. *HPA for the inference tier*. Configuring Horizontal Pod Autoscaler targets for the vLLM
   Deployment. Standard CPU/memory metrics are insufficient for GPU inference: this section
   uses DCGM's `DCGM_FI_DEV_GPU_UTIL` via the Prometheus adapter as a custom HPA metric,
   and shows request queue depth from vLLM's `/metrics` endpoint as an alternative target.
   Explains why GPU utilization is a lagging signal and why queue depth is the preferred
   leading indicator for latency-sensitive workloads.

6. *The production readiness checklist*. A concrete list of what the three modules have built,
   what the learner can now modify independently, and what the next learning frontier is:
   multi-tenant isolation, model hot-swapping, fine-tune deployment pipelines. Each item in
   the checklist has a testable criterion—not a reference list but a verification checklist.

### Pedagogical justification

The mini-arc follows the synthesis level of Bloom's revised taxonomy. At the end of the
prerequisite modules, learners are in the analysis phase: they can describe, compare, and
evaluate individual components. Synthesis—creating a novel artifact by combining components—
requires a dedicated instructional space that provides the model answer for an integration
problem that has no obvious correct solution.

The anti-listicle constraint from the KubeDojo pedagogical framework applies directly here.
A single "LLM App Integration Patterns" module would degenerate into a list of patterns with
no mechanism forcing the learner to confront the cross-service concerns that make integration
hard: what happens when two services restart in the wrong order, how to budget context window
capacity across multiple inference calls, and why a working app needs an eval gate before it
is a reliable app.

The three-module arc forces each of these concerns by making the previous module's working
artifact the substrate for the next module's failure injection. A learner who short-circuits
to Module 3.3 will not have the failure-mode vocabulary to understand why the eval gates exist
or what they are catching. The sequencing mirrors a real production deployment: get the backing
services running and verified (Module 3.1), wire the application layer and handle failures
(Module 3.2), gate the result with automated quality checks and scale it correctly (Module 3.3).

This arc does not adopt an "end-to-end capstone" framing. Capstone projects ask learners to
demonstrate prior knowledge. This arc teaches new knowledge—the integration glue—that cannot
be inferred from the prerequisite modules. The distinction matters for curriculum positioning:
this arc is instructional, not evaluative.

---

## §C. References

All URLs verified via `curl -s -o /dev/null -w "%{http_code}"` on 2026-05-14. Status codes
noted in brackets. 308 indicates a redirect to a valid destination.

- vLLM Team. *vLLM: High-throughput and memory-efficient inference engine for LLMs and
  vision-language models.* `github.com/vllm-project/vllm`. [200]

- BentoML Team. *BentoML: The unified framework for model serving.* `github.com/bentoml/BentoML`.
  [200]

- KServe Project. *KServe: Kubernetes-native model inference platform.*
  `github.com/kserve/kserve`. [200]

- Ray Project. *Ray Serve: Scalable model serving library for building online inference APIs.*
  `github.com/ray-project/ray`. [200]

- Confident AI. *DeepEval: Unit testing framework for LLM applications.*
  `github.com/confident-ai/deepeval`. [200]

- Promptfoo Team. *Promptfoo: Test and red-team your LLM prompts.*
  `github.com/promptfoo/promptfoo`. [200]

- LangChain Inc. *LangSmith: Unified platform for debugging, testing, and monitoring LLM
  applications.* `docs.langchain.com/langsmith`. [308 → 200]

- LangFuse. *LangFuse: Open-source LLM engineering platform for tracing, evals, and prompt
  management.* `github.com/langfuse/langfuse`. [200]

- NVIDIA. *GPU Operator: Automates the management of all NVIDIA GPU software components
  needed to provision GPU resources in Kubernetes.*
  `github.com/NVIDIA/gpu-operator`. [200]

- Qdrant Team. *Qdrant: High-performance vector similarity search engine and vector database.*
  `github.com/qdrant/qdrant`. [200]
