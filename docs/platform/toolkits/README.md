# Toolkits

> **Current tools for platform engineering** - Practical guides to the most important cloud-native tools

## About Toolkits

Toolkits are hands-on guides to specific tools. Unlike Foundations (timeless theory) and Disciplines (practices), toolkits evolve with the ecosystem. We focus on CNCF-graduated and widely-adopted tools.

## Structure

| Toolkit | Focus | Modules |
|---------|-------|---------|
| [Observability](observability/) | Prometheus, OpenTelemetry, Grafana, Loki, Pixie, Hubble | 7 |
| [GitOps & Deployments](gitops-deployments/) | ArgoCD, Argo Rollouts, Flux, Helm | 4 |
| [CI/CD Pipelines](ci-cd-pipelines/) | Dagger, Tekton, Argo Workflows | 3 |
| [IaC Tools](iac-tools/) | Terraform, OpenTofu, Pulumi, Ansible | 6 |
| [Security Tools](security-tools/) | Vault, OPA/Gatekeeper, Falco, Tetragon, KubeArmor | 6 |
| [Networking](networking/) | Cilium, Service Mesh | 2 |
| [Scaling & Reliability](scaling-reliability/) | Karpenter, KEDA, Velero | 3 |
| [Platforms](platforms/) | Backstage, Crossplane, cert-manager | 3 |
| [Developer Experience](developer-experience/) | K9s, Telepresence, Local K8s | 3 |
| [ML Platforms](ml-platforms/) | Kubeflow, MLflow, Feature Stores | 3 |
| [AIOps Tools](aiops-tools/) | Anomaly detection, Event correlation | 4 |
| [Source Control](source-control/) | GitLab, Gitea/Forgejo, GitHub Advanced | 1 |
| [Code Quality](code-quality/) | SonarQube, Semgrep, CodeQL, Snyk, Trivy | 2 |
| [Container Registries](container-registries/) | Harbor, Zot, Dragonfly | 3 |
| [K8s Distributions](k8s-distributions/) | k3s, k0s, MicroK8s | 3 |
| **Total** | | **53** |

## How to Use Toolkits

1. **Read Foundations first** - Understand the theory
2. **Read Disciplines** - Understand the practices
3. **Pick tools based on need** - Not everything applies
4. **Hands-on practice** - Toolkits include exercises
5. **Stay current** - Tools evolve, check release notes

## Tool Selection Philosophy

We include tools that are:

- **CNCF Graduated/Incubating** - Community validation
- **Production-proven** - Battle-tested at scale
- **Actively maintained** - Regular releases, active community
- **Interoperable** - Works with the ecosystem

## Prerequisites

Before diving into toolkits:

- Complete relevant [Foundations](../foundations/) modules
- Understand the [Discipline](../disciplines/) the tool supports
- Have a Kubernetes cluster (kind/minikube for learning)

## Start Learning

Pick a toolkit based on your current focus:

- **Starting observability?** Begin with [Prometheus](observability/module-1.1-prometheus.md)
- **Implementing GitOps?** Start with [ArgoCD](gitops-deployments/module-2.1-argocd.md)
- **Managing infrastructure?** Check out [Terraform](iac-tools/module-5.1-terraform.md)
- **Building a platform?** Check out [Backstage](platforms/module-7.1-backstage.md)
