# Module 4.5: Threat Modeling & Supply Chain Theory

> **Complexity**: `[MEDIUM]` - Core security mindset
>
> **Time to Complete**: 20-30 minutes
>
> **Prerequisites**: Module 4.1 (Attack Surfaces), Module 4.4 (Supply Chain)

---

## Outline
- Map threats with the 4C model (Cloud, Cluster, Container, Code)
- Lightweight threat-modeling workflow for Kubernetes
- Supply chain risk concepts: provenance, SBOM, signatures, policy
- Mitigation matrix to guide deeper modules and hands-on labs

---

## The 4C Model Applied
- **Cloud**: IAM misuse, network exposure, metadata service abuse.
- **Cluster**: Control plane compromise, etcd exposure, malicious admission plugins.
- **Container**: Privilege escalation, unbounded syscalls, kernel attack surface.
- **Code**: Vulnerable dependencies, poisoned images, secrets in repos.

## Threat-Modeling Workflow (Lightweight)
- **Assets & boundaries**: Identify sensitive data paths (e.g., `kubectl` → API server → etcd).
- **Entry points**: API server, ingress, CI/CD pipeline, image registry.
- **Abuse cases**: What happens if an attacker gains cluster-admin? If an admission webhook is compromised? If a base image is poisoned?
- **Mitigations & owners**: Assign controls to teams (platform, security, service owners) and document residual risk.

## Supply Chain Risk (Conceptual)
- **Provenance**: Trace how images/manifests were built; prefer reproducible builds.
- **SBOM**: Inventory dependencies to reason about exposure when CVEs land.
- **Signatures/attestations**: Sign images and manifests; attest build steps and provenance.
- **Policy gates**: Admission checks (conceptual, tool-agnostic) enforce signature/SBOM requirements before pods run.

## Mitigation Matrix (Examples)
| Threat | Mitigation (Conceptual) |
|--------|-------------------------|
| Compromised admission webhook | Isolate/webhook authn+authz, mTLS, minimal RBAC scopes, fail-closed with safe defaults |
| Registry poisoning | Enforce signed images, pin digests, restrict registry egress, scan SBOMs pre-admission |
| Node escape attempts | Use seccomp/AppArmor, drop capabilities, prefer distroless/minimal bases |
| Stolen kubeconfig | Short-lived creds, client cert rotation, least-privilege RBAC, MFA where supported |

## What to Do with Findings
- Document high-risk gaps and open issues to track fixes.
- Align mitigations with curriculum updates (Issue #14) so content stays current.
- Keep hands-on labs separate; this module is theory-first to inform later exercises.
