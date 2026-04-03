---
title: "Module 2.4: Kubernetes Security Upgrades"
slug: k8s/cks/part2-cluster-hardening/module-2.4-kubernetes-upgrades
sidebar:
  order: 4
lab:
  id: cks-2.4-kubernetes-upgrades
  url: https://killercoda.com/kubedojo/scenario/cks-2.4-kubernetes-upgrades
  duration: "40 min"
  difficulty: advanced
  environment: kubernetes
---
> **Complexity**: `[MEDIUM]` - CKA refresher with security focus
>
> **Time to Complete**: 35-40 minutes
>
> **Prerequisites**: CKA upgrade knowledge, kubeadm experience

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Evaluate** Kubernetes CVEs to determine upgrade urgency and security impact
2. **Implement** security-focused upgrade procedures using kubeadm
3. **Audit** cluster versions to identify components running with known vulnerabilities
4. **Design** an upgrade strategy that minimizes security exposure windows

---

## Why This Module Matters

Running outdated Kubernetes versions is a security risk. Each release patches vulnerabilities—some critical. The CKS exam may ask you to verify versions, understand upgrade paths, or ensure security patches are applied.

This module focuses on the security aspects of upgrades, not the mechanical process (which you know from CKA).

---

## Security Implications of Versions

```
┌─────────────────────────────────────────────────────────────┐
│              VERSION SECURITY LIFECYCLE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Kubernetes Support Model:                                 │
│  ─────────────────────────────────────────────────────────  │
│  • 3 minor versions supported at any time                  │
│  • Security fixes backported to all 3                      │
│  • Older versions: NO SECURITY PATCHES                     │
│                                                             │
│  Example (if current is 1.35):                             │
│  ├── 1.35 ✓ Supported (security patches)                  │
│  ├── 1.34 ✓ Supported (security patches)                  │
│  ├── 1.33 ✓ Supported (security patches)                  │
│  ├── 1.32 ✗ End of life (no patches!)                     │
│  └── 1.31 ✗ Unsupported (vulnerable!)                     │
│                                                             │
│  Risk of running unsupported versions:                     │
│  ⚠️  Known CVEs remain unpatched                           │
│  ⚠️  No security advisories                                │
│  ⚠️  Compliance violations                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Stop and think**: Your cluster is running Kubernetes 1.32 and the current supported versions are 1.33, 1.34, and 1.35. A critical CVE was just announced affecting all versions up to 1.34.2. Your version is out of the support window. What are your options, and how urgent is this?

## Checking Current Versions

```bash
# Check cluster version
kubectl version

# Check all component versions
kubectl get nodes -o wide

# Check control plane component versions
kubectl get pods -n kube-system -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.containers[0].image}{"\n"}{end}' | grep -E "kube-apiserver|kube-controller|kube-scheduler|etcd"

# Check kubelet versions on nodes
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}: {.status.nodeInfo.kubeletVersion}{"\n"}{end}'
```

---

## Understanding CVEs

```
┌─────────────────────────────────────────────────────────────┐
│              KUBERNETES CVE EXAMPLE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CVE-2024-XXXX: Container Escape via Symlink Attack       │
│                                                             │
│  Severity: HIGH (CVSS 8.8)                                 │
│  Affected: v1.26.0 - v1.27.5                               │
│  Fixed: v1.27.6, v1.28.2, v1.29.0                         │
│                                                             │
│  Impact:                                                   │
│  A malicious container can write to host filesystem        │
│  using a specially crafted symlink                         │
│                                                             │
│  Action:                                                   │
│  Upgrade to fixed version immediately                      │
│                                                             │
│  Where to find CVEs:                                       │
│  • kubernetes.io/security                                  │
│  • github.com/kubernetes/kubernetes/security/advisories   │
│  • cve.mitre.org                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Upgrade Process (Security Review)

### Pre-Upgrade Security Checklist

```bash
# 1. Check current version vulnerabilities
kubectl version --short
# Research CVEs for your version

# 2. Review release notes for security fixes
# https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/

# 3. Backup critical components
kubectl get all -A -o yaml > cluster-backup.yaml
ETCDCTL_API=3 etcdctl snapshot save backup.db

# 4. Check deprecation warnings
kubectl api-resources --verbs=list -o name | xargs -n 1 kubectl get --show-labels -A 2>&1 | grep -i deprecated
```

### Kubeadm Upgrade (Quick Review)

```bash
# On control plane
sudo apt update
sudo apt install -y kubeadm=1.35.0-*

# Plan the upgrade
sudo kubeadm upgrade plan

# Apply upgrade
sudo kubeadm upgrade apply v1.35.0

# Upgrade kubelet and kubectl
sudo apt install -y kubelet=1.35.0-* kubectl=1.35.0-*
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```

---

## Security-Focused Upgrade Considerations

### 1. API Deprecations

```yaml
# Old API (may be removed in new version)
apiVersion: extensions/v1beta1
kind: Ingress

# New API
apiVersion: networking.k8s.io/v1
kind: Ingress
```

### 2. Admission Controller Changes

```bash
# Check if PodSecurityPolicy is being removed
# (Removed in 1.25, use Pod Security Admission instead)
kubectl get psp 2>&1 | grep -q "the server doesn't have" && echo "PSP already removed"
```

### 3. Feature Gate Changes

```yaml
# Some security features graduate from beta to stable
# Check if feature gates need updating in API server

# Example: PodSecurity feature (stable since 1.25)
- --feature-gates=PodSecurity=true  # May not be needed anymore
```

---

> **What would happen if**: You upgrade the API server to 1.35 first (correct order), but a junior admin accidentally upgrades one worker node's kubelet to 1.35 before upgrading the controller-manager (still on 1.33). Does this violate the version skew policy? What could break?

## Version Skew Policy

```
┌─────────────────────────────────────────────────────────────┐
│              VERSION SKEW RULES                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  kube-apiserver:                                           │
│  └── Must be newest component in cluster                   │
│                                                             │
│  kube-controller-manager, kube-scheduler:                  │
│  └── Same or one minor version older than API server       │
│                                                             │
│  kubelet:                                                  │
│  └── Same, one, or two minor versions older               │
│  └── Never newer than API server                           │
│                                                             │
│  kubectl:                                                  │
│  └── One minor version newer or older                      │
│                                                             │
│  Why this matters for security:                            │
│  • Inconsistent versions can have unexpected behavior      │
│  • Security fixes may not work with version mismatches    │
│  • Upgrade API server first, then other components        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Checking for Security Updates

```bash
# Check Kubernetes security announcements
# https://kubernetes.io/docs/reference/issues-security/security/

# Check specific component for CVEs
trivy image registry.k8s.io/kube-apiserver:v1.30.0

# Check node OS for security updates
apt list --upgradable 2>/dev/null | grep -i security

# Use kube-bench to verify security settings after upgrade
./kube-bench run --targets=master
```

---

## Upgrade Rollback

### When to Rollback

```
┌─────────────────────────────────────────────────────────────┐
│              ROLLBACK TRIGGERS                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Rollback if upgrade causes:                               │
│  ─────────────────────────────────────────────────────────  │
│  • API server not starting                                 │
│  • Authentication failures                                 │
│  • RBAC not working                                        │
│  • Networking issues (CNI incompatibility)                 │
│  • Admission controller rejecting valid workloads          │
│                                                             │
│  DO NOT rollback for:                                      │
│  ─────────────────────────────────────────────────────────  │
│  • Deprecated API warnings (fix your manifests)            │
│  • Feature changes (adapt your workflows)                  │
│  • Known issues with workarounds                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Rollback Commands

```bash
# Check previous kubelet version
journalctl -u kubelet | grep "Kubelet version" | head -1

# Downgrade kubelet (if needed)
sudo apt install kubelet=<previous-version>
sudo systemctl restart kubelet

# Note: kubeadm doesn't support direct downgrade
# For control plane, restore from etcd backup
```

---

## Real Exam Scenarios

### Scenario 1: Verify Upgrade Readiness

```bash
# Check current versions match
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}: {.status.nodeInfo.kubeletVersion}{"\n"}{end}'

# All should show same version
# Inconsistent versions = security risk

# Check for deprecated APIs in use
kubectl get --raw /metrics | grep apiserver_requested_deprecated
```

### Scenario 2: Post-Upgrade Security Verification

```bash
# After upgrade, verify security settings
# 1. Check API server is running
kubectl get pods -n kube-system | grep apiserver

# 2. Verify RBAC is working
kubectl auth can-i create pods --as=developer

# 3. Check admission controllers
kubectl get pods -n kube-system -o yaml | grep admission

# 4. Run kube-bench
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs job/kube-bench
```

### Scenario 3: Find Version with CVE Fix

```bash
# Question: "Upgrade cluster to version that fixes CVE-2024-XXXX"

# 1. Research CVE (exam may provide info)
# 2. Find fixed version
kubectl version --short

# 3. Plan upgrade
kubeadm upgrade plan | grep -E "v1\.[0-9]+\.[0-9]+"

# 4. Execute upgrade to fixed version
```

---

> **Pause and predict**: After upgrading from 1.34 to 1.35, you run `kube-bench` and see 3 new [FAIL] results that weren't there before the upgrade. You didn't change any configuration. How is that possible?

## Managed Kubernetes Upgrades

```
┌─────────────────────────────────────────────────────────────┐
│              MANAGED K8S UPGRADE CONSIDERATIONS             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  EKS (AWS):                                                │
│  • Control plane upgraded separately from nodes            │
│  • Managed node groups can auto-upgrade                    │
│  • eksctl upgrade cluster                                  │
│                                                             │
│  GKE (GCP):                                                │
│  • Release channels for automatic upgrades                 │
│  • Maintenance windows for planned upgrades                │
│  • gcloud container clusters upgrade                       │
│                                                             │
│  AKS (Azure):                                              │
│  • Auto-upgrade channel available                          │
│  • Node image upgrades separate                            │
│  • az aks upgrade                                          │
│                                                             │
│  Security note:                                            │
│  Managed K8s often behind latest version (for stability)   │
│  Check provider's security patch timeline                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **Kubernetes has quarterly releases** (every ~4 months). Each release gets about 14 months of patch support.

- **CVE severity doesn't always mean exploitability.** Some "critical" CVEs require very specific conditions. Read the full advisory.

- **The Kubernetes Security Response Committee** handles vulnerability reports. They coordinate fixes across supported versions.

- **Auto-upgrading production clusters is risky.** Many organizations run one version behind latest to benefit from community bug discovery.

---

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| Skipping versions | May break components | Upgrade one minor at a time |
| Upgrading workers before control plane | Version skew violation | Control plane first |
| Not checking deprecations | Workloads may break | Review release notes |
| No backup before upgrade | Can't rollback | Always backup etcd |
| Running unsupported versions | No security patches | Keep within support window |

---

## Quiz

1. **Your security team receives a CVE advisory for a container escape vulnerability affecting Kubernetes 1.33 through 1.34.3. Your production cluster runs 1.34.1. The fix is in 1.34.4 and 1.35.0. You have a change freeze for the next two weeks. What do you recommend, and what interim mitigations could you apply?**
   <details>
   <summary>Answer</summary>
   A container escape CVE is critical -- it could allow an attacker to break out of a container and access the host node. Recommend an emergency patch to 1.34.4 (patch version upgrade, minimal risk) even during the change freeze. If the freeze is absolutely unbreakable, apply interim mitigations: restrict pod security with Pod Security Admission in `enforce` mode using the `restricted` profile, ensure AppArmor/seccomp profiles are applied to all workloads, disable privileged containers, and increase monitoring with Falco rules targeting container escapes. But these are stopgaps -- the upgrade should happen as soon as possible because known CVEs get actively exploited.
   </details>

2. **After upgrading your cluster from 1.34 to 1.35, you run `kubectl get nodes` and notice worker node `node-2` shows version 1.33 -- it was missed during the upgrade. The API server is 1.35. Is this a security problem even though the cluster "works"?**
   <details>
   <summary>Answer</summary>
   Yes, this is a security problem on multiple levels. First, the kubelet version skew policy allows kubelets up to 2 minor versions older than the API server, so 1.33 is technically within skew for a 1.35 API server -- but just barely. However, 1.33 won't receive security patches much longer (only 3 versions are supported), and any security fixes in 1.34 and 1.35 are not applied to that node. Second, the node may lack security features introduced in newer versions. Third, inconsistent versions make security auditing unreliable -- kube-bench results differ per node. Upgrade node-2 immediately to 1.35 to maintain a consistent security posture.
   </details>

3. **You run `kubeadm upgrade plan` and it shows an available upgrade to 1.35.0. A colleague says "just run `kubeadm upgrade apply` and we're done." What security-critical steps are they skipping before and after the upgrade?**
   <details>
   <summary>Answer</summary>
   Before upgrade: (1) Back up etcd with `etcdctl snapshot save` -- if the upgrade fails, you need to recover. (2) Review the release notes for security-relevant changes, deprecated APIs, and removed features. (3) Check for deprecated API usage with `kubectl get --raw /metrics | grep apiserver_requested_deprecated`. (4) Verify current workloads are healthy as a baseline. After upgrade: (1) Upgrade kubelet and kubectl on the control plane node. (2) Upgrade worker nodes one at a time with drain/uncordon. (3) Run `kube-bench` to verify security configuration survived the upgrade. (4) Verify RBAC, admission controllers, and audit logging are still functioning. (5) Check that security contexts on running pods are enforced.
   </details>

4. **Your organization runs three clusters: dev (1.33), staging (1.34), and production (1.34). Kubernetes 1.36 is released, making 1.33 unsupported. The dev team says "it's just dev, we don't need to upgrade." Why is this thinking dangerous from a security perspective?**
   <details>
   <summary>Answer</summary>
   Running an unsupported version in dev is dangerous because: (1) Dev clusters often have access to production secrets, container registries, and cloud credentials. An exploited CVE in dev could lead to production compromise. (2) Dev clusters are often less hardened than production, making them easier targets. (3) No security patches means known vulnerabilities accumulate over time. (4) Developers may test and deploy images from a compromised dev cluster to production. (5) Compliance requirements often apply to all environments, not just production. The upgrade path: dev to 1.34, then staging and production to 1.35, maintaining dev always at or near production version.
   </details>

---

## Hands-On Exercise

**Task**: Practice pre-upgrade security assessment and post-upgrade verification.

```bash
# Step 1: Create a test namespace to verify state before/after "upgrade"
kubectl create namespace upgrade-test

# Step 2: Deploy test workload with security context
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: security-test
  namespace: upgrade-test
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
  - name: app
    image: busybox
    command: ["sleep", "3600"]
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
EOF

# Step 3: Capture pre-upgrade state (always backup before upgrade!)
echo "=== Pre-Upgrade State Capture ==="
kubectl get all -n upgrade-test -o yaml > /tmp/pre-upgrade-backup.yaml
echo "Backup saved to /tmp/pre-upgrade-backup.yaml"

# Step 4: Check current cluster versions
echo "=== Current Versions ==="
kubectl version --short 2>/dev/null || kubectl version

echo "=== Node Versions ==="
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}: {.status.nodeInfo.kubeletVersion}{"\n"}{end}'

# Step 5: Check for deprecated API usage (important before upgrades)
echo "=== Checking Deprecated APIs ==="
# Look for deprecated API versions in our resources
kubectl get pod security-test -n upgrade-test -o yaml | grep "apiVersion"

# Step 6: Verify RBAC still works (key post-upgrade check)
echo "=== RBAC Verification ==="
kubectl auth can-i list pods -n upgrade-test --as=system:serviceaccount:upgrade-test:default

# Step 7: Run security verification (simulates post-upgrade checks)
echo "=== Security Context Verification ==="
kubectl get pod security-test -n upgrade-test -o jsonpath='{.spec.securityContext}' && echo ""
kubectl get pod security-test -n upgrade-test -o jsonpath='{.spec.containers[0].securityContext}' && echo ""

# Step 8: Verify pod is running correctly
echo "=== Pod Status ==="
kubectl get pod security-test -n upgrade-test

# Step 9: Check for kube-bench findings (would run on actual node)
echo "=== Security Benchmark Check ==="
echo "On control plane, would run: ./kube-bench run --targets=master"
echo "On worker nodes, would run: ./kube-bench run --targets=node"

# Step 10: Verify NetworkPolicy support (important for security)
echo "=== Testing NetworkPolicy Support ==="
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-policy
  namespace: upgrade-test
spec:
  podSelector:
    matchLabels:
      app: security-test
  policyTypes:
  - Ingress
  - Egress
EOF

kubectl get networkpolicy -n upgrade-test

# Cleanup
echo "=== Cleanup ==="
kubectl delete namespace upgrade-test
rm -f /tmp/pre-upgrade-backup.yaml

echo ""
echo "=== Exercise Complete ==="
echo "Key upgrade security checks performed:"
echo "1. ✓ Backed up cluster state"
echo "2. ✓ Checked versions for consistency"
echo "3. ✓ Verified no deprecated APIs in use"
echo "4. ✓ Confirmed RBAC working"
echo "5. ✓ Validated security contexts"
echo "6. ✓ Verified NetworkPolicy support"
```

**Success criteria**: Successfully perform pre-upgrade backup, version audit, and post-upgrade security verification checklist.

---

## Summary

**Version Security**:
- Only 3 minor versions receive patches
- Unsupported = vulnerable
- Upgrade regularly

**Upgrade Order**:
1. Control plane (API server first)
2. Controllers and scheduler
3. Worker node kubelets

**Security Checks Post-Upgrade**:
- API server running
- RBAC working
- Admission controllers active
- Run kube-bench

**Exam Tips**:
- Know how to check versions
- Understand version skew policy
- Be aware of deprecation impacts

---

## Next Module

[Module 2.5: Restricting API Access](../module-2.5-restricting-api-access/) - Network and authentication restrictions for the API server.
