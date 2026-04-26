---
title: "From AI Builder to AI Platform Engineer"
sidebar:
  order: 1
---

This bridge is for learners who can build AI applications with generative AI, RAG, embeddings, fine-tuning, or agentic workflows and want to operate AI infrastructure for other teams. It closes the gap between app-level AI skill and platform-level responsibility for Kubernetes operations, GPU scheduling, model serving, multi-tenancy, data infrastructure, governance, cost control, and reliability.

## Diagnostic — Are You Ready?

- [ ] You have served an LLM behind concurrent traffic and measured latency, throughput, saturation, and error rate.
- [ ] You can explain the difference between prompt latency, prefill time, decode time, queue time, and total request latency.
- [ ] You know what NVLink topology means for distributed training and multi-GPU placement.
- [ ] You have debugged a CUDA OOM or can explain the memory impact of batch size, sequence length, KV cache, and model weights.
- [ ] You can describe GPU quotas, priority classes, taints, tolerations, and scheduling constraints in Kubernetes.
- [ ] You have operated a vector database or retrieval system beyond a single-user demo.
- [ ] You can explain how model serving differs from ordinary stateless HTTP serving.
- [ ] You can describe when KServe, Seldon, vLLM, Triton, and custom serving stacks are appropriate.
- [ ] You can explain why multi-tenant AI workloads need isolation across data, models, secrets, GPUs, and network paths.
- [ ] You know how training data lineage, model registry, approval, rollback, and audit trails affect production AI systems.
- [ ] You can identify cost drivers for inference, fine-tuning, batch jobs, and training clusters.
- [ ] You can define ownership boundaries between app teams, data teams, ML teams, and platform teams.

## Skills Gap Map

| What you have | What you need | Where to study it |
|---|---|---|
| AI application development | Distributed systems thinking for shared platforms | [Distributed Systems](/platform/foundations/distributed-systems/) |
| Prompt and RAG experience | Reliability targets for model-serving workloads | [Reliability Engineering](/platform/foundations/reliability-engineering/) |
| Single-service deployment | AI infrastructure as a platform discipline | [AI Infrastructure](/platform/disciplines/data-ai/ai-infrastructure/) |
| Model experimentation | MLOps governance and lifecycle management | [MLOps](/platform/disciplines/data-ai/mlops/) |
| Basic container use | Kubernetes workload scheduling and isolation | [CKA](/k8s/cka/) |
| API integration | Production inference serving patterns | [KServe](/ai-ml-engineering/ai-infrastructure/) |
| Local model serving | High-throughput LLM serving operations | [vLLM](/platform/toolkits/data-ai-platforms/ml-platforms/module-9.4-vllm/) |
| GPU awareness | GPU-aware scheduling and runtime constraints | [AI Infrastructure](/platform/disciplines/data-ai/ai-infrastructure/) |
| Vector search usage | Data platform reliability and scale | [MLOps](/platform/disciplines/data-ai/mlops/) |
| Cloud API consumption | Private infrastructure and on-premises constraints | [On-Premises AI/ML Infrastructure](/on-premises/ai-ml-infrastructure/) |

## Sequenced Path

1. Start with [Distributed Systems](/platform/foundations/distributed-systems/).
   Why this step: AI platforms are distributed systems with shared bottlenecks, retries, queues, placement constraints, and partial failure.

2. Continue with [Reliability Engineering](/platform/foundations/reliability-engineering/).
   Why this step: model serving needs explicit SLOs for latency, freshness, availability, correctness boundaries, and degradation behavior.

3. Study [AI Infrastructure](/platform/disciplines/data-ai/ai-infrastructure/).
   Why this step: this is the discipline layer that connects GPUs, schedulers, serving runtimes, data paths, isolation, and operating models.

4. Study [MLOps](/platform/disciplines/data-ai/mlops/).
   Why this step: platform engineers must support model lifecycle, experiment tracking, registry workflows, approvals, rollout, rollback, and audit.

5. Use [KServe](/ai-ml-engineering/ai-infrastructure/) when you need Kubernetes-native model-serving patterns.
   Why this step: KServe exposes how inference services map to autoscaling, revisions, routing, runtimes, and production deployment concerns.

6. Use [vLLM](/platform/toolkits/data-ai-platforms/ml-platforms/module-9.4-vllm/) when LLM throughput is the central constraint.
   Why this step: vLLM makes memory layout, batching, KV cache behavior, and serving efficiency visible.

7. Use [Triton](/platform/toolkits/data-ai-platforms/ml-platforms/) when serving heterogeneous model types.
   Why this step: Triton is useful when the platform must support multiple frameworks, accelerators, batching strategies, and model formats.

8. Add [On-Premises AI/ML Infrastructure](/on-premises/ai-ml-infrastructure/) if private GPU infrastructure is the target.
   Why this step: private AI infrastructure adds procurement, power, cooling, network fabric, shared storage, and hardware lifecycle constraints.

9. Return to [Platform Engineering](/platform/disciplines/core-platform/platform-engineering/) once the technical pieces are clear.
   Why this step: the platform only succeeds when teams can consume it through reliable golden paths and clear support boundaries.

## Anti-patterns

- Assuming OpenAI API integration skill transfers directly to operating LLM serving infrastructure.
- Ignoring GPU memory accounting until production traffic arrives.
- Building inference systems without rate-limit, queue-depth, saturation, and tail-latency instrumentation.
- Treating vector databases as ordinary CRUD stores without recall, freshness, indexing, and capacity planning.
- Letting every team invent its own model-serving path.
- Treating governance as a document instead of a workflow embedded in model lifecycle tooling.

## What success looks like

- You can explain how a model request moves through routing, queuing, batching, GPU execution, and response streaming.
- You can set GPU quotas and scheduling constraints that prevent one team from starving another.
- You can define serving SLOs that include latency, availability, saturation, and degradation behavior.
- You can choose between KServe, Seldon, vLLM, Triton, and custom serving based on platform requirements.
- You can connect model registry, rollout, rollback, observability, and audit needs into one operating model.
- You can design AI infrastructure that application teams can consume without becoming platform experts.

## First module to read

Start with [Platform Disciplines: AI Infrastructure](/platform/disciplines/data-ai/ai-infrastructure/).
