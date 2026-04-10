# Migration Deduplication Decisions

Source: `ai-ml-engineering`
Compared against: `k8s, cloud, linux, prerequisites, platform`
Modules audited: 8


## ai-ml-engineering/advanced-genai/module-7.1-fine-tuning-llms.md

- No recommendations (dispatch_failed)

## ai-ml-engineering/advanced-genai/module-7.2-lora-parameter-efficient-fine-tuning.md

- **cloud/aws-essentials/module-1.6-ecr.md** — overlap: `no` → action: `none`
  - The candidate covers AWS Elastic Container Registry, which is unrelated to Generative AI fine-tuning and denoising models.
- **platform/disciplines/reliability-security/devsecops/module-4.3-security-cicd.md** — overlap: `no` → action: `none`
  - The candidate discusses CI/CD security and vulnerability scanning, completely unrelated to AI model fine-tuning.
- **platform/toolkits/infrastructure-networking/networking/module-5.1-cilium.md** — overlap: `no` → action: `none`
  - The candidate focuses on Kubernetes networking and eBPF with Cilium, whereas the source is about parameter-efficient AI fine-tuning.
- **k8s/cba/module-1.2-backstage-plugin-development.md** — overlap: `no` → action: `none`
  - The candidate is about extending the Backstage developer portal, which has no overlap with Generative AI model architecture.
- **k8s/ica/module-1.1-istio-installation-architecture.md** — overlap: `no` → action: `none`
  - The candidate covers service mesh architecture and installation, unrelated to machine learning or LoRA.

## ai-ml-engineering/advanced-genai/module-7.3-diffusion-models.md

- **k8s/kcna/part3-cloud-native-architecture/module-3.7-community-collaboration.md** — overlap: `no` → action: `none`
  - Focuses on CNCF governance, working groups, and community contribution, which is completely unrelated to AI code generation or diffusion models.
- **platform/disciplines/data-ai/aiops/module-6.1-aiops-foundations.md** — overlap: `no` → action: `none`
  - Covers AI applied to IT operations (AIOps), maturity models, and observability, rather than generative AI architectures or code generation systems.
- **platform/toolkits/security-quality/security-tools/module-4.3-falco.md** — overlap: `no` → action: `none`
  - Deals with Kubernetes runtime security and threat detection using Falco, which is unrelated to generative AI or machine learning models.
- **platform/toolkits/infrastructure-networking/networking/module-5.1-cilium.md** — overlap: `no` → action: `none`
  - Explores eBPF, container networking, and network policies, with no connection to diffusion models or code generation.
- **k8s/extending/module-1.7-scheduler-plugins.md** — overlap: `no` → action: `none`
  - Focuses on extending the Kubernetes scheduler with custom plugins, completely distinct from AI and machine learning model architectures.

## ai-ml-engineering/advanced-genai/module-7.4-rlhf-alignment.md

- **k8s/cka/part0-environment/module-0.5-exam-strategy.md** — overlap: `no` → action: `none`
  - The source covers AI/ML alignment and RLHF training pipelines, while this candidate focuses on time management and test-taking strategies for the Kubernetes CKA exam.
- **k8s/cks/part0-environment/module-0.1-cks-overview.md** — overlap: `no` → action: `none`
  - The source is about training generative AI models, whereas this candidate provides an introductory overview of the Kubernetes CKS certification format and domains.
- **k8s/cks/part0-environment/module-0.4-exam-strategy.md** — overlap: `no` → action: `none`
  - The source details the stages of AI alignment, while this candidate discusses task classification and security-specific strategies for the CKS exam.
- **k8s/kcna/part1-kubernetes-fundamentals/module-1.1-what-is-kubernetes.md** — overlap: `no` → action: `none`
  - The source is about RLHF and modern AI alternatives, while this candidate introduces fundamental orchestration concepts for Kubernetes.
- **k8s/kcna/part0-introduction/module-0.1-kcna-overview.md** — overlap: `no` → action: `none`
  - The source focuses on advanced Generative AI architectures, whereas this candidate outlines the KCNA exam structure and study approach.

## ai-ml-engineering/advanced-genai/module-7.5-advanced-generation-techniques.md

- **k8s/cka/part1-cluster-architecture/module-1.3-helm.md** — overlap: `no` → action: `none`
  - The candidate covers Kubernetes package management (Helm), which is completely unrelated to Constitutional AI and advanced generation techniques.
- **k8s/cks/part3-system-hardening/module-3.1-apparmor.md** — overlap: `no` → action: `none`
  - The candidate covers Linux container security (AppArmor), which does not overlap with AI generation or Constitutional AI.
- **cloud/gcp-essentials/module-2.8-cloud-functions.md** — overlap: `no` → action: `none`
  - The candidate focuses on GCP event-driven architecture and serverless functions, unrelated to AI text generation models.
- **cloud/gcp-essentials/module-2.7-cloud-run.md** — overlap: `no` → action: `none`
  - The candidate discusses GCP serverless containers (Cloud Run), which is unrelated to the AI concepts in the source module.
- **linux/security/hardening/module-4.3-selinux.md** — overlap: `no` → action: `none`
  - The candidate covers Linux security modules (SELinux), completely distinct from Constitutional AI and model training.

## ai-ml-engineering/ai-infrastructure/module-11.1-cloud-ai-services.md

- **cloud/enterprise-hybrid/module-10.10-enterprise-finops.md** — overlap: `partial` → action: `keep_both`
  - FinOps focuses on financial anomaly detection and cost management, whereas the source module focuses on operational infrastructure anomalies and AI services.
- **cloud/enterprise-hybrid/module-10.3-compliance.md** — overlap: `no` → action: `keep_both`
  - No overlap. This module covers continuous compliance and security posture management, which is unrelated to Cloud AI operations.
- **cloud/gke-deep-dive/module-6.2-gke-networking.md** — overlap: `no` → action: `keep_both`
  - No overlap. This module focuses on Kubernetes networking, eBPF, and routing, unrelated to AI infrastructure.
- **platform/toolkits/observability-intelligence/aiops-tools/module-10.4-building-custom-aiops.md** — overlap: `yes` → action: `cross_reference`
  - The source provides a conceptual overview of AIOps and cloud management systems, while this candidate provides a hands-on, deep-dive implementation. They should cross-reference each other.
- **k8s/cka/part2-workloads-scheduling/module-2.9-autoscaling.md** — overlap: `partial` → action: `cross_reference`
  - The CKA module covers standard Kubernetes reactive autoscaling (HPA/VPA), whereas the source focuses on AI-driven predictive autoscaling. Cross-referencing allows for comparing both approaches.

## ai-ml-engineering/ai-infrastructure/module-11.2-aiops.md

- **cloud/gcp-essentials/module-2.10-operations.md** — overlap: `partial` → action: `cross_reference`
  - Both discuss log-based metrics, but Candidate 1 is specific to Google Cloud's operational tools, while the source focuses on AI-driven insights across generalized logs.
- **platform/disciplines/delivery-automation/gitops/module-3.4-drift-detection.md** — overlap: `no` → action: `keep_both`
  - Candidate focuses on GitOps configuration drift, which is entirely separate from the AI-driven log anomaly detection covered in the source.
- **platform/toolkits/observability-intelligence/aiops-tools/module-10.4-building-custom-aiops.md** — overlap: `partial` → action: `keep_both`
  - The source covers high-level concepts and use cases of AIOps, whereas the candidate is a hands-on guide to architecting and building custom AIOps services.
- **k8s/kcsa/part5-platform-security/module-5.3-runtime-security.md** — overlap: `no` → action: `keep_both`
  - Candidate is dedicated to Kubernetes runtime security (AppArmor, SELinux, Seccomp), which has no intersection with AI-based log analysis.
- **k8s/kcna/part3-cloud-native-architecture/module-3.7-community-collaboration.md** — overlap: `no` → action: `keep_both`
  - Candidate focuses on CNCF community structures and governance, completely unrelated to the technical log analysis covered in the source.

## ai-ml-engineering/ai-native-development/module-1.1-ai-coding-tools-landscape.md

- **prerequisites/cloud-native-101/module-1.4-cloud-native-ecosystem.md** — overlap: `no` → action: `none`
  - Candidate covers the Cloud Native (CNCF) ecosystem, which is entirely distinct from AI coding tools.
- **k8s/extending/module-1.1-api-deep-dive.md** — overlap: `no` → action: `none`
  - Candidate covers Kubernetes API and extensibility, unrelated to AI development tools.
- **k8s/cks/part0-environment/module-0.1-cks-overview.md** — overlap: `no` → action: `none`
  - Candidate is an overview of the CKS exam, which has no overlap with AI coding tools.
- **cloud/azure-essentials/module-3.4-blob.md** — overlap: `no` → action: `none`
  - Candidate covers Azure Blob Storage and Data Lake, unrelated to AI coding agents and IDEs.
- **linux/foundations/everyday-use/module-0.2-environment-permissions.md** — overlap: `no` → action: `none`
  - Candidate covers Linux environment variables and permissions, completely separate from AI coding tools.