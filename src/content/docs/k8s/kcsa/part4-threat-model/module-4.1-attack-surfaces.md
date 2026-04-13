---
title: "Module 4.1: Attack Surfaces"
slug: k8s/kcsa/part4-threat-model/module-4.1-attack-surfaces
sidebar:
  order: 2
---
> **Complexity**: `[MEDIUM]` - Threat awareness
>
> **Time to Complete**: 25-30 minutes
>
> **Prerequisites**: [Module 3.5: Network Policies](/k8s/kcsa/part3-security-fundamentals/module-3.5-network-policies/)

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Identify** Kubernetes attack surfaces across API server, kubelet, etcd, and container runtime
2. **Evaluate** which attack vectors pose the highest risk in a given cluster configuration
3. **Assess** external vs. internal threat actors and their likely entry points
4. **Design** attack surface reduction strategies by disabling unnecessary endpoints and features

---

## Why This Module Matters

To defend a system, you must understand how it can be attacked. The attack surface is the sum of all points where an attacker can try to enter or extract data. Kubernetes has a large attack surface due to its complexity—understanding it helps you prioritize security efforts.

Threat modeling is a core security skill, and KCSA tests your ability to identify and assess attack vectors.

---

## What is an Attack Surface?

```
┌─────────────────────────────────────────────────────────────┐
│              ATTACK SURFACE DEFINITION                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Attack Surface = All entry points an attacker can target  │
│                                                             │
│  LARGER ATTACK SURFACE:                                    │
│  • More exposed services                                   │
│  • More open ports                                         │
│  • More users with access                                  │
│  • More complex configurations                             │
│  = More opportunities for attackers                        │
│                                                             │
│  SMALLER ATTACK SURFACE:                                   │
│  • Minimal exposed services                                │
│  • Restricted network access                               │
│  • Few privileged users                                    │
│  • Simple, hardened configurations                         │
│  = Fewer opportunities for attackers                       │
│                                                             │
│  GOAL: Minimize attack surface while maintaining function  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Kubernetes Attack Surfaces

```
┌─────────────────────────────────────────────────────────────┐
│              KUBERNETES ATTACK SURFACE MAP                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  EXTERNAL ATTACK SURFACE (from outside cluster)            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Kubernetes API server                            │   │
│  │  • Ingress/Load Balancers                           │   │
│  │  • NodePort services                                │   │
│  │  • SSH to nodes                                     │   │
│  │  • Cloud provider APIs                              │   │
│  │  • Container registries                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  INTERNAL ATTACK SURFACE (from inside cluster)             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Pod-to-pod networking                            │   │
│  │  • Kubernetes API (from pods)                       │   │
│  │  • kubelet API                                      │   │
│  │  • etcd                                             │   │
│  │  • Service account tokens                           │   │
│  │  • Secrets                                          │   │
│  │  • Host filesystem (if mounted)                     │   │
│  │  • Container runtime                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  SUPPLY CHAIN ATTACK SURFACE                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Container images                                 │   │
│  │  • Base images                                      │   │
│  │  • Application dependencies                         │   │
│  │  • CI/CD pipelines                                  │   │
│  │  • Helm charts/manifests                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Stop and think**: Your cluster has strong RBAC, encrypted secrets, and Pod Security Standards enforced. But the API server has a public endpoint. How does this single exposure point undermine all your other controls?

## External Attack Surface

### API Server Exposure

```
┌─────────────────────────────────────────────────────────────┐
│              API SERVER ATTACK SURFACE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PUBLIC API SERVER                                         │
│  • Accessible from internet                                │
│  • Target for brute force                                  │
│  • Target for credential stuffing                          │
│  • Vulnerable to API exploits                              │
│                                                             │
│  ATTACK SCENARIOS:                                         │
│  1. Stolen credentials → Full cluster access               │
│  2. Anonymous auth enabled → Information disclosure        │
│  3. API vulnerability → Remote code execution              │
│  4. RBAC misconfiguration → Privilege escalation           │
│                                                             │
│  MITIGATIONS:                                              │
│  • Private API endpoint (VPN/bastion required)             │
│  • Strong authentication (OIDC, certificates)              │
│  • Disable anonymous auth                                  │
│  • Network firewall rules                                  │
│  • API audit logging                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Ingress Attack Surface

```
┌─────────────────────────────────────────────────────────────┐
│              INGRESS ATTACK SURFACE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WHAT'S EXPOSED:                                           │
│  • Ingress controller (nginx, traefik, etc.)               │
│  • Backend applications through ingress                    │
│  • TLS termination point                                   │
│                                                             │
│  ATTACK SCENARIOS:                                         │
│  1. Ingress controller vulnerability                       │
│  2. Application vulnerabilities (OWASP Top 10)             │
│  3. Misrouted traffic (host header attacks)                │
│  4. TLS/certificate issues                                 │
│  5. Path traversal to unintended backends                  │
│                                                             │
│  MITIGATIONS:                                              │
│  • Keep ingress controller updated                         │
│  • WAF (Web Application Firewall)                          │
│  • Strict ingress rules                                    │
│  • Strong TLS configuration                                │
│  • Rate limiting                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Internal Attack Surface

### From a Compromised Pod

```
┌─────────────────────────────────────────────────────────────┐
│              POD-LEVEL ATTACK SURFACE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SCENARIO: Attacker compromises application in pod         │
│                                                             │
│  WHAT THEY CAN ACCESS:                                     │
│                                                             │
│  ALWAYS AVAILABLE:                                         │
│  ├── Container filesystem                                  │
│  ├── Environment variables (may contain secrets)           │
│  ├── Mounted volumes                                       │
│  └── Network (all pods by default)                         │
│                                                             │
│  IF TOKEN MOUNTED (default):                               │
│  ├── Kubernetes API access                                 │
│  ├── Service account permissions                           │
│  └── Secrets accessible via RBAC                           │
│                                                             │
│  IF MISCONFIGURED:                                         │
│  ├── privileged: true → Host access                        │
│  ├── hostPath mounts → Host filesystem                     │
│  ├── hostNetwork → Host network                            │
│  ├── hostPID → Host processes                              │
│  └── Excessive RBAC → Cluster compromise                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Kubelet Attack Surface

```
┌─────────────────────────────────────────────────────────────┐
│              KUBELET ATTACK SURFACE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  KUBELET API (port 10250)                                  │
│  • /exec - Execute commands in containers                  │
│  • /run - Run commands                                     │
│  • /pods - List pods                                       │
│  • /logs - Read logs                                       │
│                                                             │
│  ATTACK SCENARIOS:                                         │
│  1. Anonymous kubelet access → Execute in any container    │
│  2. Node compromise → Kubelet credentials stolen           │
│  3. Network access to kubelet → Bypass API server auth     │
│                                                             │
│  MITIGATIONS:                                              │
│  • Disable anonymous auth                                  │
│  • Disable read-only port (10255)                          │
│  • Network isolation for kubelet                           │
│  • Node authorization mode                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Pause and predict**: An attacker compromises a pod that has `automountServiceAccountToken: false` and runs as non-root with no capabilities. What attack surface remains available to them from inside this hardened container?

## Attack Surface by Actor

```
┌─────────────────────────────────────────────────────────────┐
│              THREAT ACTORS                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  EXTERNAL ATTACKER                                         │
│  • No initial access                                       │
│  • Targets: Exposed services, stolen credentials           │
│  • Goal: Initial foothold                                  │
│                                                             │
│  COMPROMISED POD                                           │
│  • Limited container access                                │
│  • Targets: Other pods, secrets, API, container escape     │
│  • Goal: Lateral movement, escalation                      │
│                                                             │
│  MALICIOUS INSIDER                                         │
│  • Legitimate credentials                                  │
│  • Targets: Abuse permissions, plant backdoors             │
│  • Goal: Data theft, persistence                           │
│                                                             │
│  SUPPLY CHAIN ATTACKER                                     │
│  • Compromises trusted components                          │
│  • Targets: Images, dependencies, CI/CD                    │
│  • Goal: Widespread compromise                             │
│                                                             │
│  EACH ACTOR HAS DIFFERENT ATTACK SURFACE                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Reducing Attack Surface

### Principle: Minimize Exposure

```
┌─────────────────────────────────────────────────────────────┐
│              ATTACK SURFACE REDUCTION                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  NETWORK                                                   │
│  ☐ Private API server endpoint                             │
│  ☐ Network policies (default deny)                         │
│  ☐ No unnecessary NodePort/LoadBalancer services           │
│  ☐ Firewall rules for node access                          │
│                                                             │
│  AUTHENTICATION                                            │
│  ☐ Disable anonymous auth (API server, kubelet)            │
│  ☐ Short-lived credentials                                 │
│  ☐ Strong authentication (MFA, certificates)               │
│                                                             │
│  WORKLOADS                                                 │
│  ☐ No privileged containers                                │
│  ☐ No host namespace sharing                               │
│  ☐ Read-only root filesystem                               │
│  ☐ Disable service account token mounting                  │
│  ☐ Minimal container images                                │
│                                                             │
│  NODES                                                     │
│  ☐ Minimal OS (Bottlerocket, Flatcar)                      │
│  ☐ Disable SSH if possible                                 │
│  ☐ Regular patching                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **The median time to detect a breach** in cloud environments is over 200 days. Attack surface reduction means fewer places to hide.

- **70% of breaches** involve lateral movement after initial access. Reducing internal attack surface is as important as perimeter security.

- **Container images average 400+ packages** - each is part of your attack surface. Minimal images dramatically reduce exposure.

- **The Kubernetes API server** is one of the most common targets because it provides direct cluster access.

---

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| Public API server | Direct attack target | Private endpoint + VPN |
| Default ServiceAccount tokens | Unnecessary API access | Disable auto-mounting |
| Allow-all network policies | Full lateral movement | Default deny |
| Privileged pods | Host compromise possible | Pod Security Standards |
| Fat container images | Large attack surface | Minimal/distroless images |

---

## Quiz

1. **A penetration tester discovers that your cluster's API server is publicly accessible, the kubelet read-only port (10255) is open on all nodes, and several services use NodePort. Rank these three exposures by risk and explain your reasoning.**
   <details>
   <summary>Answer</summary>
   The public API server presents the highest risk because it serves as the gateway to complete cluster control. If an attacker leverages stolen credentials or exploits an API vulnerability, they can completely compromise the environment. The kubelet read-only port is the second highest risk, as it exposes pod names, namespaces, and resource usage without authentication. This provides attackers with valuable reconnaissance data and potentially reveals secrets stored in environment variables. Finally, NodePort services pose the lowest relative risk since they only expose specific applications rather than cluster infrastructure, limiting the attack surface to the vulnerabilities of that specific application.
   </details>

2. **An attacker compromises a pod that has `automountServiceAccountToken: false`, runs as non-root, has no capabilities, and has a read-only filesystem. What attack options remain available from inside this hardened container?**
   <details>
   <summary>Answer</summary>
   Even in a hardened container, an attacker can still leverage the network to scan the flat pod network and discover other services, unless strict egress NetworkPolicies are enforced. They can also attempt to reach the cloud metadata service (169.254.169.254) to steal cloud IAM credentials. Furthermore, the attacker can read environment variables that might contain injected secrets or access any volumes mounted to the pod. Because the container shares the host's kernel, they could also attempt kernel-level exploits for privilege escalation. This scenario illustrates why defense in depth is essential, as runtime security and network controls must complement pod-level hardening.
   </details>

3. **Your team reduced the external attack surface by making the API server private and using an ingress controller. A security consultant says you've "shifted risk, not eliminated it." What do they mean?**
   <details>
   <summary>Answer</summary>
   By introducing an ingress controller, the external attack surface shifts from the API server directly to the ingress component itself. The ingress controller is now internet-facing and becomes the primary entry point, meaning any vulnerability in it (like Nginx CVEs or header injection flaws) can be exploited. While the API server is safer behind a VPN or bastion, those remote access solutions introduce their own risks, such as VPN credential theft or bastion host compromise. The consultant highlights that attack surfaces are often moved and reshaped rather than completely eliminated. The most effective strategy is to minimize the exposed components and rigorously harden what remains accessible through WAFs, strict routing rules, and continuous monitoring.
   </details>

4. **A supply chain attacker plants a malicious image that looks identical to your legitimate application. It passes all your runtime security controls — no privileged access, no shell spawns, no suspicious syscalls. It simply exfiltrates data through normal HTTPS connections. Which attack surface category does this exploit, and what controls could detect it?**
   <details>
   <summary>Answer</summary>
   This scenario exploits the supply chain attack surface, where malicious code enters the environment through a trusted artifact like a container image. Runtime security tools often fail to detect this because the attacker relies on normal application behavior, such as standard HTTPS connections, to exfiltrate data. To detect this threat, you must implement image signing verification at the admission controller level to reject untampered or unsigned images. Additionally, conducting Software Bill of Materials (SBOM) analysis can reveal unexpected or malicious dependencies before deployment. Finally, enforcing strict egress NetworkPolicies and monitoring DNS for connections to unknown domains can block or detect the exfiltration attempts at the network layer.
   </details>

5. **Your lead developer requests to run their debugging pod with `hostNetwork: true` to troubleshoot a node-level routing issue, promising they've placed it behind a default-deny NetworkPolicy. Why is this configuration still a massive expansion of the pod's attack surface, and what specific capabilities does it grant despite the NetworkPolicy?**
   <details>
   <summary>Answer</summary>
   A pod with `hostNetwork: true` uses the node's IP and network stack, completely bypassing Kubernetes NetworkPolicies, which only apply to the pod network. This configuration allows the pod to bind to any port on the node, potentially impersonating legitimate node services or intercepting traffic. Furthermore, it can sniff all unencrypted traffic on the node's interfaces and access node-local services listening on localhost, such as the kubelet's internal endpoints. It might also gain unfettered access to the cloud provider's metadata service (169.254.169.254) if not blocked at the node level. The attack surface is effectively identical to a compromised cluster node, making it an unacceptable risk for standard debugging.
   </details>

---

## Hands-On Exercise: Attack Surface Assessment

**Scenario**: Review this cluster configuration and identify attack surface concerns:

```yaml
# API Server flags
--anonymous-auth=true
--authorization-mode=AlwaysAllow

# Kubelet config
authentication:
  anonymous:
    enabled: true
readOnlyPort: 10255

# Sample pod
apiVersion: v1
kind: Pod
spec:
  hostNetwork: true
  hostPID: true
  containers:
  - name: app
    image: ubuntu:latest
    securityContext:
      privileged: true
```

**List the attack surface issues:**

<details>
<summary>Attack Surface Issues</summary>

**API Server:**
1. `anonymous-auth=true` - Anyone can access API without authentication
2. `authorization-mode=AlwaysAllow` - No authorization, all requests permitted

**Kubelet:**
3. `anonymous.enabled: true` - Kubelet API accessible without auth
4. `readOnlyPort: 10255` - Information disclosure, pod enumeration

**Pod:**
5. `hostNetwork: true` - Pod uses host network, can sniff traffic
6. `hostPID: true` - Pod can see all host processes
7. `privileged: true` - Full host access, container escape trivial
8. `ubuntu:latest` - Large image with many packages, mutable tag

**Impact**:
- External attackers can access API without auth
- Any compromised pod has full host access
- Kubelet accessible for container execution
- Information readily available for reconnaissance

</details>

---

## Summary

Attack surface is the sum of all entry points:

| Surface Type | Examples | Reduction Strategy |
|-------------|----------|-------------------|
| **External** | API server, Ingress, NodePort | Private endpoints, firewalls |
| **Internal** | Pod network, kubelet, API from pods | Network policies, disable tokens |
| **Supply Chain** | Images, dependencies, CI/CD | Scanning, signing, minimal images |

Key principles:
- What's not exposed can't be attacked
- Minimize privileges at every layer
- Assume breach, limit blast radius
- Different actors have different attack surfaces

---

## Next Module

[Module 4.2: Common Vulnerabilities](../module-4.2-vulnerabilities/) - Understanding CVEs and misconfigurations in Kubernetes.