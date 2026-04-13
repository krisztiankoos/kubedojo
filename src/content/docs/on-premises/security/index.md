---
title: "Security & Compliance"
sidebar:
  order: 0
---

On-premises Kubernetes gives you physical control that cloud never can -- but that control comes with responsibility. You own the hardware, the network perimeter, the key material, and every audit artifact. These modules cover the security and compliance concerns unique to self-hosted infrastructure.

---

## Modules

| Module | Topics | Complexity |
|--------|--------|------------|
| [Module 6.1: Physical Security & Air-Gapped Environments](module-6.1-air-gapped/) | Datacenter controls, disconnected clusters, Harbor registry, image mirroring, sneakernet updates, air-gapped GitOps | Advanced |
| [Module 6.2: Hardware Security (HSM/TPM)](module-6.2-hardware-security/) | HSMs for key management, TPM measured boot, Vault + PKCS#11, on-prem KMS replacement, LUKS + TPM disk encryption | Advanced |
| [Module 6.3: Enterprise Identity (AD/LDAP/OIDC)](module-6.3-enterprise-identity/) | Active Directory integration, LDAP, Keycloak, Dex OIDC, RBAC group mapping, SSO for dashboards | Medium |
| [Module 6.4: Compliance for Regulated Industries](module-6.4-compliance/) | HIPAA physical controls, SOC 2, PCI DSS scope isolation, data sovereignty, K8s audit policy, evidence collection | Advanced |
| [Workload Identity with SPIFFE/SPIRE](module-6.5-workload-identity-spiffe/) | SPIFFE standard, SPIRE server and agent, node attestation, workload attestation, identity federation, mTLS | Advanced |
| [Secrets Management on Bare Metal](module-6.6-secrets-management-vault/) | HashiCorp Vault on-prem, auto-unseal with HSMs, External Secrets Operator, CSI Secrets Store, dynamic credentials | Advanced |
| [Policy as Code & Governance](module-6.7-policy-as-code/) | OPA Gatekeeper, Kyverno, mutating webhooks, image signature verification, compliance automation, guardrails | Medium |
| [Zero Trust Architecture](module-6.8-zero-trust-architecture/) | Microsegmentation, identity-based routing, default deny policies, CNI network policies, Istio/Cilium strict mTLS | Advanced |

---

## Prerequisites

- [Fundamentals](../../prerequisites/) -- Cloud Native 101, Kubernetes Basics
- [CKS](../../k8s/cks/) -- Kubernetes security concepts
- [Planning & Economics](../planning/) -- Datacenter planning context
- [Networking](../networking/) -- Network segmentation and BGP

---

## Who This Section Is For

- **Security engineers** responsible for hardening on-premises Kubernetes clusters
- **Compliance officers** mapping regulatory frameworks to Kubernetes infrastructure
- **Platform teams** integrating enterprise identity systems with Kubernetes RBAC
- **Infrastructure architects** designing air-gapped or classified environments