---
title: "Module 1.3: Ingress Security"
slug: k8s/cks/part1-cluster-setup/module-1.3-ingress-security
sidebar:
  order: 3
lab:
  id: cks-1.3-ingress-security
  url: https://killercoda.com/kubedojo/scenario/cks-1.3-ingress-security
  duration: "35 min"
  difficulty: advanced
  environment: kubernetes
---
> **Complexity**: `[MEDIUM]` - Critical for external access security
>
> **Time to Complete**: 35-40 minutes
>
> **Prerequisites**: Module 1.1 (Network Policies), CKA Ingress knowledge

---

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Configure** TLS termination on Ingress resources with valid certificates
2. **Implement** security headers and rate limiting via Ingress annotations
3. **Audit** Ingress configurations for exposed admin panels and missing TLS enforcement
4. **Harden** Ingress controllers to prevent information leakage and unauthorized access

---

## Why This Module Matters

Ingress is where your cluster meets the internet. It's the front door—and attackers target front doors. Misconfigured TLS, exposed admin panels, and missing security headers are common vulnerabilities.

CKS tests your ability to harden ingress configurations beyond basic functionality.

> **Security Note**: The ingress-nginx controller was retired on March 31, 2026 and no longer receives security patches. If your clusters still use ingress-nginx, this is a **critical security risk**. Migrate to a maintained controller (Envoy Gateway, Traefik, Cilium, NGINX Gateway Fabric) and consider adopting Gateway API for new deployments. The security principles in this module apply equally to Ingress and Gateway API configurations.

---

## Ingress Attack Surface

```
┌─────────────────────────────────────────────────────────────┐
│              INGRESS SECURITY ATTACK SURFACE                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Internet                                                   │
│     │                                                       │
│     ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              INGRESS CONTROLLER                      │   │
│  │                                                      │   │
│  │  Attack vectors:                                    │   │
│  │  ⚠️  No TLS = data exposed in transit              │   │
│  │  ⚠️  Weak TLS versions (TLS 1.0/1.1)               │   │
│  │  ⚠️  Missing security headers                       │   │
│  │  ⚠️  Path traversal vulnerabilities                │   │
│  │  ⚠️  Exposed status/metrics endpoints              │   │
│  │  ⚠️  No rate limiting                               │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│     │                                                       │
│     ▼                                                       │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   App Service   │  │   API Service   │                  │
│  └─────────────────┘  └─────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## TLS Configuration

### Creating TLS Secrets

```bash
# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=myapp.example.com"

# Create Kubernetes secret
kubectl create secret tls myapp-tls \
  --cert=tls.crt \
  --key=tls.key \
  -n production

# Verify secret
kubectl get secret myapp-tls -n production -o yaml
```

### Ingress with TLS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-ingress
  namespace: production
  annotations:
    # Force HTTPS redirect
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    # Enable HSTS
    nginx.ingress.kubernetes.io/hsts: "true"
    nginx.ingress.kubernetes.io/hsts-max-age: "31536000"
    nginx.ingress.kubernetes.io/hsts-include-subdomains: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp
            port:
              number: 80
```

---

## Security Headers

### Essential Headers

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hardened-ingress
  annotations:
    # Content Security Policy
    nginx.ingress.kubernetes.io/configuration-snippet: |
      add_header X-Frame-Options "SAMEORIGIN" always;
      add_header X-Content-Type-Options "nosniff" always;
      add_header X-XSS-Protection "1; mode=block" always;
      add_header Referrer-Policy "strict-origin-when-cross-origin" always;
      add_header Content-Security-Policy "default-src 'self'" always;
spec:
  # ... rest of spec
```

```
┌─────────────────────────────────────────────────────────────┐
│              SECURITY HEADERS EXPLAINED                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  X-Frame-Options: SAMEORIGIN                               │
│  └── Prevents clickjacking attacks                         │
│                                                             │
│  X-Content-Type-Options: nosniff                           │
│  └── Prevents MIME type sniffing                           │
│                                                             │
│  X-XSS-Protection: 1; mode=block                           │
│  └── Enables browser XSS filtering                         │
│                                                             │
│  Referrer-Policy: strict-origin-when-cross-origin          │
│  └── Controls referrer information leakage                 │
│                                                             │
│  Content-Security-Policy: default-src 'self'               │
│  └── Restricts resource loading sources                    │
│                                                             │
│  Strict-Transport-Security (HSTS)                          │
│  └── Forces HTTPS for specified duration                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **Stop and think**: You've configured TLS on your Ingress with `ssl-redirect: "true"`. But a penetration tester shows they can still access your app over HTTP by sending requests directly to the backend Service's ClusterIP, bypassing the Ingress entirely. What additional protection is needed?

## TLS Version Enforcement

### Disable Weak TLS Versions

```yaml
# ConfigMap for nginx-ingress-controller
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-ingress-controller
  namespace: ingress-nginx
data:
  # Minimum TLS version
  ssl-protocols: "TLSv1.2 TLSv1.3"

  # Strong cipher suites only
  ssl-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384"

  # Enable HSTS globally
  hsts: "true"
  hsts-max-age: "31536000"
  hsts-include-subdomains: "true"
  hsts-preload: "true"
```

### Per-Ingress TLS Settings

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: strict-tls-ingress
  annotations:
    # Require client certificate (mTLS)
    nginx.ingress.kubernetes.io/auth-tls-verify-client: "on"
    nginx.ingress.kubernetes.io/auth-tls-secret: "production/ca-secret"

    # Specific TLS version for this ingress
    nginx.ingress.kubernetes.io/ssl-prefer-server-ciphers: "true"
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls
```

---

## Mutual TLS (mTLS)

```
┌─────────────────────────────────────────────────────────────┐
│              MUTUAL TLS AUTHENTICATION                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Standard TLS:                                             │
│  Client ──────► Server presents certificate                │
│         ◄────── Client verifies server                     │
│  (One-way verification)                                    │
│                                                             │
│  Mutual TLS:                                               │
│  Client ──────► Server presents certificate                │
│         ◄────── Client verifies server                     │
│  Client ──────► Client presents certificate                │
│         ◄────── Server verifies client                     │
│  (Two-way verification)                                    │
│                                                             │
│  Use cases:                                                │
│  • Service-to-service authentication                       │
│  • API clients with certificates                           │
│  • Zero-trust architectures                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Configure mTLS

```bash
# Create CA secret for client verification
kubectl create secret generic ca-secret \
  --from-file=ca.crt=ca.crt \
  -n production
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mtls-ingress
  namespace: production
  annotations:
    # Enable client certificate verification
    nginx.ingress.kubernetes.io/auth-tls-verify-client: "on"
    # CA to verify client certs
    nginx.ingress.kubernetes.io/auth-tls-secret: "production/ca-secret"
    # Depth of verification
    nginx.ingress.kubernetes.io/auth-tls-verify-depth: "1"
    # Pass client cert to backend
    nginx.ingress.kubernetes.io/auth-tls-pass-certificate-to-upstream: "true"
spec:
  tls:
  - hosts:
    - secure-api.example.com
    secretName: api-tls
  rules:
  - host: secure-api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: secure-api
            port:
              number: 443
```

---

> **What would happen if**: You configure mTLS on your Ingress, requiring client certificates. A legitimate user's certificate expires over the weekend. What happens to their requests, and how should you design your certificate lifecycle to prevent this?

> **Pause and predict**: Your Ingress uses TLS 1.2 minimum. A compliance audit says you need TLS 1.3 *only*. What percentage of legitimate clients might you break, and how would you plan this migration?

## Rate Limiting

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rate-limited-ingress
  annotations:
    # Limit requests per second
    nginx.ingress.kubernetes.io/limit-rps: "10"

    # Limit connections
    nginx.ingress.kubernetes.io/limit-connections: "5"

    # Burst allowance
    nginx.ingress.kubernetes.io/limit-burst-multiplier: "5"

    # Custom error when rate limited
    nginx.ingress.kubernetes.io/server-snippet: |
      limit_req_status 429;
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
```

---

## Protecting Sensitive Paths

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: protected-paths
  annotations:
    # Block access to sensitive paths
    nginx.ingress.kubernetes.io/server-snippet: |
      location ~ ^/(admin|metrics|health|debug) {
        deny all;
        return 403;
      }

    # Or require authentication
    nginx.ingress.kubernetes.io/auth-url: "https://auth.example.com/verify"
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app
            port:
              number: 80
```

### Using NetworkPolicies with Ingress

```yaml
# Allow only ingress controller to reach backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-ingress-only
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
      podSelector:
        matchLabels:
          app.kubernetes.io/name: ingress-nginx
    ports:
    - port: 80
```

---

## Ingress Controller Hardening

### Secure Ingress Controller Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  template:
    spec:
      containers:
      - name: controller
        image: registry.k8s.io/ingress-nginx/controller:v1.9.0
        securityContext:
          # Don't run as root
          runAsNonRoot: true
          runAsUser: 101
          # Read-only filesystem
          readOnlyRootFilesystem: true
          # No privilege escalation
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
            add:
            - NET_BIND_SERVICE
        # Resource limits
        resources:
          limits:
            cpu: "1"
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 256Mi
```

---

## Real Exam Scenarios

### Scenario 1: Enable TLS on Ingress

```bash
# Create TLS certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /tmp/tls.key -out /tmp/tls.crt \
  -subj "/CN=webapp.example.com"

# Create secret
kubectl create secret tls webapp-tls \
  --cert=/tmp/tls.crt \
  --key=/tmp/tls.key \
  -n production

# Update existing ingress to use TLS
kubectl patch ingress webapp -n production --type=json -p='[
  {"op": "add", "path": "/spec/tls", "value": [
    {"hosts": ["webapp.example.com"], "secretName": "webapp-tls"}
  ]}
]'
```

### Scenario 2: Force HTTPS Redirect

```bash
# Add SSL redirect annotation
kubectl annotate ingress webapp -n production \
  nginx.ingress.kubernetes.io/ssl-redirect="true"
```

### Scenario 3: Add Security Headers

```bash
kubectl annotate ingress webapp -n production \
  nginx.ingress.kubernetes.io/configuration-snippet='
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
  '
```

---

## Did You Know?

- **HSTS preloading** adds your domain to browsers' built-in HTTPS-only list. Once you're on it, browsers will never make HTTP requests to your domain.

- **TLS 1.0 and 1.1 are deprecated.** PCI-DSS compliance requires TLS 1.2 minimum since 2018.

- **nginx-ingress vs ingress-nginx**: There are TWO ingress controllers often confused. `ingress-nginx` (kubernetes/ingress-nginx) is the official one; `nginx-ingress` is from NGINX Inc.

- **Let's Encrypt with cert-manager** can automate TLS certificate issuance. Many production clusters use this instead of manual certificate management.

---

## Common Mistakes

| Mistake | Why It Hurts | Solution |
|---------|--------------|----------|
| No TLS on ingress | Data exposed in transit | Always configure TLS |
| Using self-signed certs in prod | Browser warnings, no trust | Use proper CA (Let's Encrypt) |
| Missing HSTS header | Downgrade attacks possible | Enable HSTS with long max-age |
| Exposing /metrics endpoint | Information leakage | Block or authenticate |
| No rate limiting | DoS vulnerability | Configure rate limits |

---

## Quiz

1. **A security scanner reports that your production Ingress is serving HTTP traffic alongside HTTPS. Users who type `http://app.example.com` get the application without encryption. What annotation fixes this, and what broader security header should accompany it to prevent future downgrades?**
   <details>
   <summary>Answer</summary>
   Add `nginx.ingress.kubernetes.io/ssl-redirect: "true"` to force HTTP-to-HTTPS redirects. However, redirects alone don't prevent downgrade attacks -- an attacker can intercept the initial HTTP request before the redirect. Enable HSTS (HTTP Strict Transport Security) with `nginx.ingress.kubernetes.io/hsts: "true"` and `hsts-max-age: "31536000"`. HSTS tells browsers to always use HTTPS for your domain, eliminating the vulnerable HTTP request entirely after the first visit.
   </details>

2. **During a compliance audit for PCI-DSS, the auditor flags that your Ingress controller accepts TLS 1.1 connections. You check the Ingress annotations and see no TLS version configuration. Where is the TLS version configured for nginx-ingress, and what's the minimum version for PCI-DSS compliance?**
   <details>
   <summary>Answer</summary>
   TLS version settings are configured at the controller level in the nginx-ingress ConfigMap (not per-Ingress annotations): set `ssl-protocols: "TLSv1.2 TLSv1.3"` in the ConfigMap `nginx-ingress-controller` in the `ingress-nginx` namespace. PCI-DSS requires TLS 1.2 as the minimum since 2018. TLS 1.0 and 1.1 have known vulnerabilities (POODLE, BEAST) and must be disabled. Also configure strong cipher suites to prevent weak encryption even under TLS 1.2.
   </details>

3. **Your SOC team detects that an attacker is embedding your application inside an iframe on a phishing site to steal credentials. Which security header stops this attack, and what other headers should you add as defense-in-depth?**
   <details>
   <summary>Answer</summary>
   `X-Frame-Options: DENY` (or `SAMEORIGIN` if you need self-framing) prevents the page from being embedded in iframes on other sites, stopping clickjacking. For defense-in-depth, also add: `X-Content-Type-Options: nosniff` (prevents MIME type sniffing), `X-XSS-Protection: 1; mode=block` (enables browser XSS filtering), `Referrer-Policy: strict-origin-when-cross-origin` (controls referrer leakage), and `Content-Security-Policy: default-src 'self'` (restricts resource loading sources). These are configured via the `configuration-snippet` annotation in nginx-ingress.
   </details>

4. **You need to expose an internal API that only trusted partners should access. Passwords are not secure enough. Your team suggests mutual TLS. Walk through the steps to configure mTLS on a Kubernetes Ingress -- what secrets do you need and what happens when an unauthorized client connects?**
   <details>
   <summary>Answer</summary>
   For mTLS, you need two secrets: a TLS secret (`kubectl create secret tls`) with the server certificate and key, and a generic secret containing the CA certificate (`kubectl create secret generic ca-secret --from-file=ca.crt`) used to verify client certificates. Configure annotations: `auth-tls-verify-client: "on"` and `auth-tls-secret: "namespace/ca-secret"`. When an unauthorized client connects without a valid client certificate signed by your CA, the TLS handshake fails with a 400 error before any application code executes. This is stronger than password auth because certificates are cryptographically verified and can't be phished.
   </details>

---

## Hands-On Exercise

**Task**: Secure an ingress with TLS and security headers.

```bash
# Setup
kubectl create namespace secure-app
kubectl run webapp --image=nginx -n secure-app
kubectl expose pod webapp --port=80 -n secure-app

# Step 1: Create TLS certificate and secret
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=webapp.local"

kubectl create secret tls webapp-tls \
  --cert=tls.crt --key=tls.key \
  -n secure-app

# Step 2: Create secure ingress
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webapp
  namespace: secure-app
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      add_header X-Frame-Options "DENY" always;
      add_header X-Content-Type-Options "nosniff" always;
      add_header X-XSS-Protection "1; mode=block" always;
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - webapp.local
    secretName: webapp-tls
  rules:
  - host: webapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: webapp
            port:
              number: 80
EOF

# Step 3: Verify configuration
kubectl describe ingress webapp -n secure-app

# Step 4: Test (add to /etc/hosts: 127.0.0.1 webapp.local)
# curl -k https://webapp.local -I | grep -E "X-Frame|X-Content|X-XSS"

# Cleanup
kubectl delete namespace secure-app
```

**Success criteria**: Ingress uses TLS and returns security headers.

---

## Summary

**TLS Requirements**:
- Always use TLS for external traffic
- Minimum TLS 1.2, prefer TLS 1.3
- Store certificates in Kubernetes secrets

**Security Headers**:
- X-Frame-Options: Prevent clickjacking
- X-Content-Type-Options: Prevent MIME sniffing
- HSTS: Force HTTPS

**Rate Limiting**:
- Protect against DoS attacks
- Configure per-ingress limits

**Best Practices**:
- Force HTTPS redirect
- Use NetworkPolicies with ingress
- Protect sensitive paths
- Harden ingress controller pod

---

## Next Module

[Module 1.4: Node Metadata Protection](../module-1.4-node-metadata/) - Protecting cloud provider metadata services.
