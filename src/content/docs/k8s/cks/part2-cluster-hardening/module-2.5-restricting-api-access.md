---
title: "Module 2.5: Restricting API Access"
slug: k8s/cks/part2-cluster-hardening/module-2.5-restricting-api-access
sidebar:
  order: 5
lab:
  id: cks-2.5-restricting-api-access
  url: https://killercoda.com/kubedojo/scenario/cks-2.5-restricting-api-access
  duration: "35 min"
  difficulty: advanced
  environment: kubernetes
---
> **Complexity**: `[MEDIUM]` - Essential for cluster security
>
> **Time to Complete**: 35-40 minutes
>
> **Prerequisites**: Module 2.3 (API Server Security), networking basics

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Configure** API server network restrictions using firewall rules and CIDR allowlists
2. **Implement** authentication webhooks and OIDC integration for API access control
3. **Audit** API access patterns to detect unauthorized or anomalous requests
4. **Design** multi-layer API access controls combining network, authentication, and RBAC

---

## Why This Module Matters

The Kubernetes API is the crown jewel—access to it means control over everything. While RBAC controls what authenticated users can do, restricting WHO can even reach the API is equally important.

**The Tesla Cryptojacking Incident:** In 2018, attackers compromised Tesla's cloud infrastructure not through a sophisticated zero-day, but by finding a Kubernetes API server that was exposed to the internet without password protection. Because the administrative dashboard was openly accessible, the attackers deployed cryptomining containers and stole AWS credentials that were stored in plaintext. This incident perfectly illustrates the catastrophic business impact of an exposed API: once the control plane is breached, the entire cluster—and potentially the underlying cloud environment—is compromised.

This module covers network-level and authentication-based API access restrictions to prevent such scenarios.

---

## API Access Attack Surface

```
┌─────────────────────────────────────────────────────────────┐
│              API ACCESS ATTACK SURFACE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Internet                                                   │
│     │                                                       │
│     ├──► API Server :6443  ← Exposed?                      │
│     │                                                       │
│     ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              ATTACK VECTORS                          │   │
│  │                                                      │   │
│  │  1. Direct API access from internet                 │   │
│  │     → Brute force auth, exploit vulnerabilities     │   │
│  │                                                      │   │
│  │  2. Compromised pod in cluster                      │   │
│  │     → Uses mounted token to call API                │   │
│  │                                                      │   │
│  │  3. Compromised node                                │   │
│  │     → Uses kubelet credentials                      │   │
│  │                                                      │   │
│  │  4. Stolen kubeconfig                               │   │
│  │     → Direct cluster access from anywhere           │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Stop and think**: Your API server is accessible at a public IP on port 6443. It requires client certificates for authentication. An attacker can't authenticate, but they can reach the endpoint. What attacks are still possible even without valid credentials?

## Network-Level Restrictions

### Firewall Rules (External)

```bash
# Only allow API access from specific IPs
# On cloud: Security Groups, Firewall Rules, NSGs

# AWS Security Group example:
# Inbound rule: TCP 6443 from 10.0.0.0/8 (internal only)

# iptables on API server node
sudo iptables -A INPUT -p tcp --dport 6443 -s 10.0.0.0/8 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 6443 -s 192.168.1.0/24 -j ACCEPT  # Admin VPN
sudo iptables -A INPUT -p tcp --dport 6443 -j DROP
```

### Private API Endpoint

```yaml
# EKS: Enable private endpoint, disable public
aws eks update-cluster-config \
  --name my-cluster \
  --resources-vpc-config endpointPrivateAccess=true,endpointPublicAccess=false

# GKE: Private cluster
gcloud container clusters create private-cluster \
  --enable-private-endpoint \
  --master-ipv4-cidr 172.16.0.0/28

# AKS: Private cluster
az aks create \
  --name myAKSCluster \
  --enable-private-cluster
```

---

## Kubernetes-Native Network Restrictions

### API Server NetworkPolicy (Limited)

```yaml
# Note: NetworkPolicy doesn't directly apply to API server
# But you can restrict which pods can reach it

# Block pods from directly accessing API server IP
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-api-direct
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  # Allow DNS
  - to:
    - namespaceSelector: {}
    ports:
    - port: 53
      protocol: UDP
  # Allow everything except API server
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 10.96.0.1/32  # Kubernetes service IP
```

### API Server Bind Address

```yaml
# /etc/kubernetes/manifests/kube-apiserver.yaml
spec:
  containers:
  - command:
    - kube-apiserver
    # Bind only to specific interface
    - --bind-address=10.0.0.10  # Internal IP only
    # Or bind to all (less secure)
    - --bind-address=0.0.0.0
```

---

## Authentication Restrictions

### Disable Anonymous Authentication

```yaml
# API server flag
- --anonymous-auth=false

# Verification
curl -k https://<api-server>:6443/api/v1/namespaces
# Should return 401 Unauthorized
```

### Client Certificate Requirements

```yaml
# Require client certificates (mutual TLS)
- --client-ca-file=/etc/kubernetes/pki/ca.crt

# Clients must present valid certificate signed by CA
# This is default in kubeadm clusters
```

### Token Validation

```yaml
# Configure token authentication
- --service-account-key-file=/etc/kubernetes/pki/sa.pub
- --service-account-issuer=https://kubernetes.default.svc

# Optional: External OIDC provider
- --oidc-issuer-url=https://accounts.example.com
- --oidc-client-id=kubernetes
- --oidc-username-claim=email
- --oidc-groups-claim=groups
```

---

> **Pause and predict**: You create a NetworkPolicy that blocks pods in the `production` namespace from reaching the API server's ClusterIP (10.96.0.1). But pods can still use `kubectl` from inside the container. What did you miss? (Hint: how does `kubectl` resolve `kubernetes.default.svc`?)

## Webhook Authentication

```
┌─────────────────────────────────────────────────────────────┐
│              WEBHOOK AUTHENTICATION                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Request ──► API Server ──► Webhook ──► Response           │
│                               │                             │
│                               ▼                             │
│                      ┌─────────────────┐                   │
│                      │ Auth Service    │                   │
│                      │                 │                   │
│                      │ - Validate token│                   │
│                      │ - Return user   │                   │
│                      │   info          │                   │
│                      └─────────────────┘                   │
│                                                             │
│  Use cases:                                                │
│  • Custom authentication systems                           │
│  • Integration with SSO                                    │
│  • Additional validation logic                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Configure Webhook Authentication

```yaml
# API server flags
- --authentication-token-webhook-config-file=/etc/kubernetes/webhook-config.yaml
- --authentication-token-webhook-cache-ttl=2m

# /etc/kubernetes/webhook-config.yaml
apiVersion: v1
kind: Config
clusters:
- name: auth-service
  cluster:
    certificate-authority: /etc/kubernetes/pki/webhook-ca.crt
    server: https://auth.example.com/authenticate
users:
- name: api-server
  user:
    client-certificate: /etc/kubernetes/pki/webhook-client.crt
    client-key: /etc/kubernetes/pki/webhook-client.key
contexts:
- context:
    cluster: auth-service
    user: api-server
  name: webhook
current-context: webhook
```

---

## API Rate Limiting

### EventRateLimit Admission

```yaml
# Enable admission controller
- --enable-admission-plugins=EventRateLimit
- --admission-control-config-file=/etc/kubernetes/admission-config.yaml

# /etc/kubernetes/admission-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: EventRateLimit
  path: /etc/kubernetes/event-rate-limit.yaml

# /etc/kubernetes/event-rate-limit.yaml
apiVersion: eventratelimit.admission.k8s.io/v1alpha1
kind: Configuration
limits:
- type: Namespace
  qps: 50
  burst: 100
- type: User
  qps: 10
  burst: 20
```

### API Priority and Fairness

```yaml
# Kubernetes 1.20+: API Priority and Fairness
# Controls API request queuing and priority

# Check current flow schemas
kubectl get flowschemas

# Check priority levels
kubectl get prioritylevelconfigurations

# Example: Lower priority for batch workloads
apiVersion: flowcontrol.apiserver.k8s.io/v1beta3
kind: FlowSchema
metadata:
  name: batch-jobs-low-priority
spec:
  priorityLevelConfiguration:
    name: low-priority
  matchingPrecedence: 1000
  rules:
  - subjects:
    - kind: ServiceAccount
      serviceAccount:
        name: batch-runner
        namespace: batch
    resourceRules:
    - apiGroups: ["batch"]
      resources: ["jobs"]
      verbs: ["*"]
```

---

## Audit and Monitor API Access

### API Access Logging

```yaml
# Audit policy to log all API access attempts
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# Log all authentication attempts
- level: RequestResponse
  omitStages:
  - RequestReceived
  resources:
  - group: "authentication.k8s.io"

# Log failed requests
- level: Metadata
  omitStages:
  - RequestReceived
```

### Monitoring API Metrics

```bash
# Check API server metrics
kubectl get --raw /metrics | grep apiserver_request

# Authentication failures
kubectl get --raw /metrics | grep authentication_attempts

# Rate limiting metrics
kubectl get --raw /metrics | grep apiserver_flowcontrol
```

---

## Real Exam Scenarios

### Scenario 1: Restrict API to Internal Network

```bash
# Check current API server bind address
kubectl get pods -n kube-system -l component=kube-apiserver -o yaml | grep bind-address

# Edit to bind to internal interface only
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml

# Change:
# --bind-address=0.0.0.0
# To:
# --bind-address=10.0.0.10  # Internal IP

# API server will restart automatically
```

### Scenario 2: Verify Anonymous Access Disabled

```bash
# Test anonymous access
curl -k https://<api-server>:6443/api/v1/namespaces

# If anonymous is disabled, should get:
# {"kind":"Status","apiVersion":"v1","status":"Failure","message":"Unauthorized",...}

# If anonymous is enabled, may get namespace list or partial data
# Fix by adding --anonymous-auth=false to API server
```

### Scenario 3: Configure API Access for Specific Users

```bash
# Create kubeconfig for specific user with limited network access
kubectl config set-cluster restricted \
  --server=https://internal-api.example.com:6443 \
  --certificate-authority=/path/to/ca.crt

kubectl config set-credentials limited-user \
  --client-certificate=/path/to/user.crt \
  --client-key=/path/to/user.key

kubectl config set-context limited \
  --cluster=restricted \
  --user=limited-user
```

---

> **What would happen if**: A developer's laptop with a valid kubeconfig file is stolen. The kubeconfig has cluster-admin credentials and the API server is publicly accessible. What's the blast radius, and what controls would have limited the damage?

## Defense in Depth for API

```
┌─────────────────────────────────────────────────────────────┐
│              API ACCESS DEFENSE LAYERS                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Network                                          │
│  └── Firewall, private endpoint, VPN                       │
│                                                             │
│  Layer 2: TLS                                              │
│  └── Mutual TLS, certificate validation                    │
│                                                             │
│  Layer 3: Authentication                                   │
│  └── No anonymous, OIDC, client certs                      │
│                                                             │
│  Layer 4: Authorization                                    │
│  └── RBAC with least privilege                            │
│                                                             │
│  Layer 5: Admission                                        │
│  └── Rate limiting, validation                             │
│                                                             │
│  Layer 6: Audit                                            │
│  └── Log all access, monitor anomalies                     │
│                                                             │
│  All layers should be active!                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Did You Know?

- **The Kubernetes API server by default binds to 0.0.0.0**, making it accessible from all network interfaces. This is convenient but potentially dangerous.

- **Cloud providers offer private clusters** where the API server has no public IP at all. Access is only through VPN or bastion hosts.

- **API Priority and Fairness** (APF) replaced the older max-in-flight limits in Kubernetes 1.20. It provides fairer queuing during overload.

- **Some organizations use API gateways** in front of the Kubernetes API for additional security, logging, and rate limiting.

---

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| Public API endpoint | Anyone can attempt auth | Private endpoint + VPN |
| No firewall rules | Network-level exposure | Restrict to known IPs |
| Anonymous auth enabled | Unauthenticated access | --anonymous-auth=false |
| No rate limiting | DoS vulnerability | EventRateLimit admission |
| Not monitoring access | Can't detect attacks | Enable audit logging |

---

## Quiz

1. **Your SOC team detects thousands of failed authentication attempts against the API server from an external IP address. The API server is exposed publicly with `--bind-address=0.0.0.0`. No brute-force succeeded yet. What immediate and long-term actions do you take?**
   <details>
   <summary>Answer</summary>
   Immediate: Block the attacking IP with firewall rules (`iptables -A INPUT -s <attacker-ip> -p tcp --dport 6443 -j DROP`). Verify no successful authentications from that IP in audit logs. Long-term: Change `--bind-address` to an internal IP or use a cloud provider private endpoint to remove public API access entirely. Require VPN for external access. Enable the EventRateLimit admission controller to throttle requests. Configure API Priority and Fairness to deprioritize unauthenticated traffic. Enable audit logging if not already configured to detect future attempts. Even though no brute-force succeeded, the public endpoint is an unnecessary attack surface.
   </details>

2. **A developer's laptop is stolen at a conference. Their kubeconfig contains a client certificate for the production cluster, which has a public API endpoint. The certificate doesn't expire for 364 more days. What's the blast radius and how do you revoke access?**
   <details>
   <summary>Answer</summary>
   Blast radius depends on the RBAC permissions bound to the certificate's CN/O fields -- if it's cluster-admin, full cluster compromise is possible. Kubernetes has no built-in certificate revocation. Options: (1) Rotate the cluster CA certificate (drastic -- breaks all existing certificates). (2) Add the stolen certificate's CN to a deny list using a webhook authorizer. (3) If using OIDC, disable the user's account immediately. (4) Restrict the API server to private endpoint/VPN so the stolen cert is useless without network access. This incident highlights why short-lived credentials (OIDC tokens, bound SA tokens) are preferred over long-lived certificates, and why private API endpoints are critical.
   </details>

3. **Your cluster's API server uses `--authorization-mode=AlwaysAllow` because "RBAC was too complicated" for the dev team. A security audit flags this. The team argues that authentication is strong (client certs) so authorization doesn't matter. Explain why they're wrong with a concrete attack scenario.**
   <details>
   <summary>Answer</summary>
   With `AlwaysAllow`, any authenticated user can do anything: read all secrets (database passwords, TLS keys, API tokens), create privileged pods that escape to the host, delete production workloads, modify RBAC to grant others access, and access the cloud metadata service. Concrete scenario: a developer with a valid client cert could `kubectl get secrets -A` to read every secret in every namespace, including admin credentials they shouldn't have. With RBAC (`--authorization-mode=Node,RBAC`), each user gets only the permissions they need. The Node authorizer additionally restricts kubelets to their own node's resources. Authentication proves identity; authorization enforces what that identity can do. Both are essential.
   </details>

4. **You notice a compromised pod is making API calls despite having `automountServiceAccountToken: false`. Investigation shows the pod is using a token from a different source. Where could the token have come from, and how do you prevent this?**
   <details>
   <summary>Answer</summary>
   Possible token sources: (1) A token was injected via environment variable from a Secret or ConfigMap. (2) The attacker obtained a token from another pod via network access. (3) A legacy ServiceAccount token Secret exists and is mounted as a volume. (4) The application was configured with credentials in code or a mounted kubeconfig. Prevention: use NetworkPolicy to block pods from reaching the API server IP, audit all Secrets for tokens and kubeconfigs, remove legacy SA token Secrets, scan environment variables for credentials, and combine `automountServiceAccountToken: false` with RBAC restrictions on the ServiceAccount. Defense in depth means restricting at both the token-mounting level and the network level.
   </details>

---

## Hands-On Exercise

**Task**: Audit and verify API access restrictions.

```bash
# Step 1: Check API server configuration
echo "=== API Server Config ==="
kubectl get pods -n kube-system -l component=kube-apiserver -o yaml | grep -E "bind-address|anonymous-auth|authorization-mode"

# Step 2: Test anonymous access (from within cluster)
echo "=== Anonymous Access Test ==="
kubectl run curlpod --image=curlimages/curl --rm -it --restart=Never -- \
  curl -sk https://kubernetes.default.svc/api/v1/namespaces 2>&1 | head -5

# Step 3: Check if API is accessible externally
echo "=== External Access Check ==="
API_IP=$(kubectl get svc kubernetes -o jsonpath='{.spec.clusterIP}')
echo "API Server internal IP: $API_IP"
# In production, also check external IP/DNS

# Step 4: Review authentication methods
echo "=== Authentication Config ==="
kubectl get pods -n kube-system -l component=kube-apiserver -o yaml | grep -E "client-ca|oidc|token|webhook"

# Step 5: Check for rate limiting
echo "=== Rate Limiting ==="
kubectl get pods -n kube-system -l component=kube-apiserver -o yaml | grep -E "EventRateLimit|admission-control"

# Step 6: Review flow schemas (API Priority and Fairness)
echo "=== Flow Schemas ==="
kubectl get flowschemas --no-headers | head -5

# Success criteria:
# - Anonymous access denied
# - Multiple auth methods configured
# - Rate limiting or APF active
```

**Success criteria**: Identify current API access restrictions and verify anonymous access is blocked.

---

## Summary

**Network Restrictions**:
- Private API endpoints
- Firewall rules
- VPN-only access

**Authentication Restrictions**:
- Disable anonymous auth
- Require client certificates
- OIDC for user authentication

**Rate Limiting**:
- EventRateLimit admission
- API Priority and Fairness

**Defense in Depth**:
- Layer all restrictions
- Audit everything
- Monitor for anomalies

**Exam Tips**:
- Know how to check bind-address
- Understand anonymous-auth implications
- Practice verifying API accessibility

---

## Part 2 Complete!

You've finished **Cluster Hardening** (15% of CKS). You now understand:
- RBAC deep dive and escalation prevention
- ServiceAccount security and token management
- API server security configuration
- Kubernetes upgrade security
- Restricting API access

**Next Part**: [Part 3: System Hardening](../part3-system-hardening/module-3.1-apparmor/) - AppArmor, seccomp, and OS-level security.