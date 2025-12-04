# Module 4.3: Identity and Access Management

> **Complexity**: `[MEDIUM]`
>
> **Time to Complete**: 30-35 minutes
>
> **Prerequisites**: [Module 4.2: Defense in Depth](module-4.2-defense-in-depth.md)
>
> **Track**: Foundations

---

## Why This Module Matters

Every security incident involves a question: "Who did this?" And every access control decision requires answering: "Should this identity be allowed to do this action on this resource?"

**Identity and Access Management (IAM)** is the foundation of security. It's how you know who's who, and how you decide who can do what. Get it wrong, and you have either an unusable system (too restrictive) or a compromised one (too permissive).

This module teaches you the principles of authentication (proving identity) and authorization (granting access)—concepts that apply whether you're securing a Kubernetes cluster, a cloud account, or an internal application.

> **The Bouncer Analogy**
>
> A nightclub bouncer does two jobs: check your ID (authentication) and decide if you can enter (authorization). These are different questions. You might have valid ID but not be on the guest list. In systems, authentication proves who you are; authorization decides what you can do.

---

## What You'll Learn

- The difference between authentication and authorization
- Authentication factors and methods
- Authorization models (RBAC, ABAC, policies)
- The principle of least privilege in practice
- Token-based authentication and OAuth/OIDC

---

## Part 1: Authentication Fundamentals

### 1.1 What is Authentication?

```
AUTHENTICATION
═══════════════════════════════════════════════════════════════

Authentication answers: "WHO ARE YOU?"

It's the process of verifying that someone is who they claim to be.

AUTHENTICATION FLOW
─────────────────────────────────────────────────────────────
1. CLAIM: "I am alice@example.com"
2. PROOF: Provide password, certificate, or token
3. VERIFY: System checks proof against stored credential
4. RESULT: Authenticated (identity confirmed) or Rejected

WHAT AUTHENTICATION IS NOT
─────────────────────────────────────────────────────────────
✗ Deciding what the user can do (that's authorization)
✗ Tracking what the user did (that's auditing)
✗ Protecting the communication (that's encryption)

Authentication just answers: "Is this really Alice?"
```

### 1.2 Authentication Factors

```
THE THREE AUTHENTICATION FACTORS
═══════════════════════════════════════════════════════════════

SOMETHING YOU KNOW
    Password, PIN, security questions

    + Easy to implement
    - Can be guessed, phished, stolen
    - Users pick weak passwords, reuse them

SOMETHING YOU HAVE
    Phone (SMS, TOTP), hardware key (YubiKey), smart card

    + Harder to steal remotely
    + Proves physical possession
    - Can be lost, stolen, SIM-swapped
    - Requires user to carry device

SOMETHING YOU ARE
    Fingerprint, face, retina, voice

    + Always with you
    + Hard to forge (for now)
    - Can't be changed if compromised
    - Privacy concerns
    - False positives/negatives

MULTI-FACTOR AUTHENTICATION (MFA)
─────────────────────────────────────────────────────────────
Combines two or more factors:

    Password (know) + TOTP (have) = Much stronger

    Attacker needs to compromise BOTH factors,
    which requires different attack techniques.
```

### 1.3 Authentication Methods

| Method | Factor | Security | Usability |
|--------|--------|----------|-----------|
| **Password** | Know | Low (if weak) | High |
| **Password + TOTP** | Know + Have | Medium-High | Medium |
| **Password + Hardware Key** | Know + Have | High | Medium |
| **Certificate (mTLS)** | Have | High | Low (complex setup) |
| **SSO/OIDC** | Delegated | Depends on IdP | High |
| **Passwordless (WebAuthn)** | Have | High | Medium-High |

> **Try This (2 minutes)**
>
> List the authentication methods you use daily:
>
> | Service | Method | Factors | Could be stronger? |
> |---------|--------|---------|-------------------|
> | | | | |
> | | | | |
> | | | | |

---

## Part 2: Authorization Fundamentals

### 2.1 What is Authorization?

```
AUTHORIZATION
═══════════════════════════════════════════════════════════════

Authorization answers: "WHAT CAN YOU DO?"

After authentication confirms identity, authorization decides
what that identity is allowed to access.

AUTHORIZATION DECISION
─────────────────────────────────────────────────────────────
INPUTS:
    - WHO: Authenticated identity (alice@example.com)
    - WHAT: Requested action (read, write, delete)
    - WHICH: Target resource (/api/users/123)
    - CONTEXT: Additional factors (time, location, risk)

OUTPUT:
    - ALLOW: Proceed with action
    - DENY: Block action

EXAMPLE:
    Alice requests DELETE /api/users/123

    Check: Does Alice have permission to delete users?
    Check: Can Alice delete this specific user (123)?

    Result: ALLOW or DENY
```

### 2.2 Authorization Models

```
AUTHORIZATION MODELS
═══════════════════════════════════════════════════════════════

ACCESS CONTROL LIST (ACL)
─────────────────────────────────────────────────────────────
Permissions attached directly to resources.

    /api/users:
        alice: read, write
        bob: read
        carol: read, write, delete

    Simple, but doesn't scale. Managing permissions on
    thousands of resources is unwieldy.

ROLE-BASED ACCESS CONTROL (RBAC)
─────────────────────────────────────────────────────────────
Users assigned to roles, roles have permissions.

    Roles:
        viewer: read
        editor: read, write
        admin: read, write, delete

    Assignments:
        alice → editor
        bob → viewer
        carol → admin

    Scales better. Change role, all users update.

ATTRIBUTE-BASED ACCESS CONTROL (ABAC)
─────────────────────────────────────────────────────────────
Policies evaluate attributes of user, resource, context.

    Policy: "Allow if user.department == resource.owner.department
             AND time.hour >= 9 AND time.hour < 17"

    Very flexible. Can express complex rules.
    Can become hard to understand and audit.
```

### 2.3 RBAC in Practice

```
RBAC DESIGN
═══════════════════════════════════════════════════════════════

KUBERNETES RBAC EXAMPLE
─────────────────────────────────────────────────────────────

# Define what actions are allowed (Role)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

# Bind role to identity (RoleBinding)
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

RESULT: Alice can read pods in production namespace.
        Alice cannot write pods.
        Alice cannot read pods in other namespaces.
```

---

## Part 3: The Principle of Least Privilege

### 3.1 What is Least Privilege?

```
PRINCIPLE OF LEAST PRIVILEGE
═══════════════════════════════════════════════════════════════

Grant only the minimum permissions necessary to perform
the required function—no more, no less.

WHY IT MATTERS
─────────────────────────────────────────────────────────────
Compromised Identity:
    Without least privilege: Attacker has broad access
    With least privilege: Attacker access is limited

Accidents:
    Without least privilege: Mistake can affect anything
    With least privilege: Mistake limited to allowed scope

Insider Threats:
    Without least privilege: Employees can access anything
    With least privilege: Access only what job requires
```

### 3.2 Implementing Least Privilege

```
LEAST PRIVILEGE IMPLEMENTATION
═══════════════════════════════════════════════════════════════

1. START WITH ZERO
─────────────────────────────────────────────────────────────
Default deny. No permissions until explicitly granted.

    Bad:  New user → Admin role (convenient!)
    Good: New user → No roles → Request needed access

2. SCOPE PERMISSIONS
─────────────────────────────────────────────────────────────
Narrow by action, resource, and context.

    Too broad: "admin" (can do anything)
    Better: "editor" (can read and write)
    Best: "orders-editor" (can edit orders only)

3. TIME-BOUND ACCESS
─────────────────────────────────────────────────────────────
Temporary elevated permissions for specific tasks.

    Permanent: alice always has production access
    Time-bound: alice gets production access for 4 hours
                to debug specific issue, then revoked

4. SEPARATE CONCERNS
─────────────────────────────────────────────────────────────
Different roles for different functions.

    Bad:  One service account for everything
    Good: Separate accounts for app, monitoring, backup
          Each with only its required permissions
```

### 3.3 Common Violations

| Violation | Risk | Fix |
|-----------|------|-----|
| Everyone is admin | No accountability, full blast radius | Role-based access |
| Shared credentials | Can't attribute actions | Individual accounts |
| Permanent elevated access | Ongoing exposure | Just-in-time access |
| Over-provisioned service accounts | Broad access on compromise | Minimal permissions per service |
| Forgotten accounts | Dormant attack vector | Regular access reviews |

> **War Story: The Over-Privileged CI/CD**
>
> A team gave their CI/CD pipeline admin access to production. "It needs to deploy, and sometimes fix things." One day, a junior engineer's pull request had a typo in the deploy script. The CI/CD deleted the production database.
>
> The pipeline didn't need admin access—it needed deploy permissions and nothing else. After the incident, they scoped CI/CD to only create/update deployments. It can't delete, can't touch databases, can't modify networking.
>
> The recovery took 4 hours. Implementing least privilege took 2 hours. They wished they'd done it first.

---

## Part 4: Token-Based Authentication

### 4.1 How Tokens Work

```
TOKEN-BASED AUTHENTICATION
═══════════════════════════════════════════════════════════════

TRADITIONAL (Session-based)
─────────────────────────────────────────────────────────────
1. User logs in
2. Server creates session, stores in database
3. Server sends session ID (cookie)
4. Client sends session ID with each request
5. Server looks up session in database

    Problem: Stateful. Server must store sessions.
    Problem: Doesn't scale well across servers.

TOKEN-BASED (Stateless)
─────────────────────────────────────────────────────────────
1. User logs in
2. Server creates signed token (JWT)
3. Server sends token to client
4. Client sends token with each request
5. Server validates signature, reads claims

    Benefit: Stateless. No session storage.
    Benefit: Scales easily. Any server can validate.
    Benefit: Can include claims (roles, permissions).
```

### 4.2 JSON Web Tokens (JWT)

```
JWT STRUCTURE
═══════════════════════════════════════════════════════════════

Three parts, base64-encoded, separated by dots:

HEADER.PAYLOAD.SIGNATURE

HEADER
─────────────────────────────────────────────────────────────
{
  "alg": "RS256",    // Signing algorithm
  "typ": "JWT"       // Token type
}

PAYLOAD (Claims)
─────────────────────────────────────────────────────────────
{
  "sub": "alice@example.com",  // Subject (who)
  "aud": "api.example.com",    // Audience (for whom)
  "iat": 1700000000,           // Issued at
  "exp": 1700003600,           // Expires at
  "roles": ["editor"]          // Custom claims
}

SIGNATURE
─────────────────────────────────────────────────────────────
HMAC-SHA256 or RSA signature of header + payload.
Server verifies signature to ensure token wasn't tampered.

CRITICAL: Never trust claims without verifying signature!
```

### 4.3 OAuth 2.0 and OpenID Connect

```
OAUTH 2.0 / OIDC FLOW
═══════════════════════════════════════════════════════════════

┌─────────┐          ┌─────────┐          ┌─────────────┐
│  User   │          │  App    │          │   Identity  │
│         │          │(Client) │          │   Provider  │
└────┬────┘          └────┬────┘          └──────┬──────┘
     │                    │                       │
     │  1. Click "Login   │                       │
     │     with Google"   │                       │
     │───────────────────▶│                       │
     │                    │                       │
     │                    │  2. Redirect to IdP   │
     │◀───────────────────│                       │
     │                    │                       │
     │  3. Login at IdP   │                       │
     │────────────────────┼──────────────────────▶│
     │                    │                       │
     │  4. Redirect back  │                       │
     │    with auth code  │                       │
     │◀───────────────────┼───────────────────────│
     │                    │                       │
     │                    │  5. Exchange code     │
     │                    │     for tokens        │
     │                    │──────────────────────▶│
     │                    │                       │
     │                    │  6. Access + ID token │
     │                    │◀──────────────────────│
     │                    │                       │
     │  7. User is        │                       │
     │     logged in      │                       │
     │◀───────────────────│                       │

OAuth 2.0: Authorization (access token)
OIDC: Authentication (ID token with user info)
```

> **Try This (3 minutes)**
>
> Decode a JWT at jwt.io. Examine:
> - What's in the header?
> - What claims are in the payload?
> - When does it expire?
> - What would happen if you changed a claim without re-signing?

---

## Part 5: Service Identity

### 5.1 Machine-to-Machine Authentication

```
SERVICE AUTHENTICATION
═══════════════════════════════════════════════════════════════

HUMANS                              SERVICES
─────────────────────────────────────────────────────────────
Password + MFA                      API Keys
Interactive login                   Automated, non-interactive
One person, many sessions           One service, many instances
Can verify manually                 Must be automated

SERVICE AUTHENTICATION METHODS
─────────────────────────────────────────────────────────────

API KEYS
    Long-lived secret string
    Simple but risky if leaked
    Hard to rotate across many instances

CLIENT CERTIFICATES (mTLS)
    Cryptographic identity
    Strong, hard to steal
    Complex PKI management

SHORT-LIVED TOKENS
    Get token from identity provider
    Token expires quickly (hours)
    Even if leaked, limited window

    Kubernetes: ServiceAccount tokens
    AWS: IAM roles for pods (IRSA)
    Cloud: Workload identity
```

### 5.2 Kubernetes Service Accounts

```yaml
# Service Account with minimal permissions
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: production
---
# Role with only needed permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-role
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  resourceNames: ["my-app-config"]  # Specific resource only
  verbs: ["get"]
---
# Bind service account to role
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-binding
  namespace: production
subjects:
- kind: ServiceAccount
  name: my-app
  namespace: production
roleRef:
  kind: Role
  name: my-app-role
  apiGroup: rbac.authorization.k8s.io
---
# Pod using the service account
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  namespace: production
spec:
  serviceAccountName: my-app
  automountServiceAccountToken: true  # Only if needed!
  containers:
  - name: app
    image: myapp:v1
```

### 5.3 Workload Identity

```
WORKLOAD IDENTITY (Cloud-Native)
═══════════════════════════════════════════════════════════════

Problem: How do pods authenticate to cloud services?

OLD WAY (Static credentials)
─────────────────────────────────────────────────────────────
Pod has AWS access key stored as secret
    - Long-lived credentials
    - If leaked, attacker has cloud access
    - Hard to rotate across pods

NEW WAY (Workload Identity)
─────────────────────────────────────────────────────────────
Pod gets temporary cloud credentials via Kubernetes identity

┌────────────────────────────────────────────────────────────┐
│                                                            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐ │
│  │    Pod      │     │ Kubernetes  │     │    Cloud    │ │
│  │             │     │   OIDC      │     │    IAM      │ │
│  │ ServiceAcct │────▶│   Provider  │────▶│             │ │
│  └─────────────┘     └─────────────┘     └─────────────┘ │
│                                                  │        │
│  1. Pod presents K8s token                       │        │
│  2. K8s OIDC signs token                         │        │
│  3. Cloud IAM trusts K8s OIDC                    │        │
│  4. Pod gets temporary cloud credentials         │        │
│                                                  ▼        │
│                                          ┌─────────────┐ │
│                                          │  S3, RDS,   │ │
│                                          │  etc.       │ │
│                                          └─────────────┘ │
└────────────────────────────────────────────────────────────┘

AWS: IAM Roles for Service Accounts (IRSA)
GCP: Workload Identity
Azure: Azure AD Workload Identity
```

---

## Did You Know?

- **OAuth was invented in 2006** by Blaine Cook while building Twitter's API. He needed a way to let third-party apps post tweets without giving them user passwords.

- **TOTP codes change every 30 seconds** by design. The server and your phone share a secret; both compute HMAC(secret, time/30). Same algorithm, same result, no communication needed.

- **Kubernetes defaulted to auto-mounting service account tokens** until v1.24. Now you have to explicitly request it, implementing least privilege by default.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Same password everywhere | One breach compromises all | Unique passwords + password manager |
| No MFA on critical systems | Single factor easily bypassed | MFA everywhere possible |
| Overly broad roles | More access than needed | Granular, purpose-specific roles |
| Long-lived tokens | Large exposure window if leaked | Short-lived tokens, refresh flow |
| Shared service accounts | Can't attribute actions | One account per service |
| No access review | Permissions accumulate | Regular audits, remove unused |

---

## Quiz

1. **What's the difference between authentication and authorization?**
   <details>
   <summary>Answer</summary>

   **Authentication** answers "Who are you?" — It verifies the claimed identity by checking proof (password, certificate, token).

   **Authorization** answers "What can you do?" — It determines whether the authenticated identity is allowed to perform a specific action on a specific resource.

   They're sequential: You must authenticate (prove identity) before authorization (check permissions). A valid identity doesn't automatically mean access is granted.

   Example: Alice authenticates with password+MFA. She's confirmed as Alice. Then authorization checks: Can Alice delete this file? Maybe yes, maybe no—depends on her permissions.
   </details>

2. **Why is multi-factor authentication more secure than single factor?**
   <details>
   <summary>Answer</summary>

   MFA requires multiple independent proofs of identity from different factor categories:
   - Something you know (password)
   - Something you have (phone, hardware key)
   - Something you are (biometrics)

   An attacker must compromise ALL factors to succeed. Different factors require different attack techniques:
   - Passwords: Phishing, guessing, database breaches
   - TOTP: Device theft, SIM swapping
   - Hardware keys: Physical theft

   Single factor: Attacker needs one technique.
   Multi-factor: Attacker needs multiple different techniques simultaneously.

   The probability of successful attack drops significantly with each factor added.
   </details>

3. **What is the principle of least privilege and how do you implement it?**
   <details>
   <summary>Answer</summary>

   **Least privilege**: Grant only the minimum permissions necessary to perform a required function.

   Implementation:
   1. **Default deny**: Start with no permissions; add only what's needed
   2. **Scope narrowly**: Limit by action (read vs write), resource (specific items), context (time, location)
   3. **Use roles**: Group related permissions, assign roles instead of individual permissions
   4. **Time-bound access**: Grant elevated access temporarily, not permanently
   5. **Separate concerns**: Different accounts for different functions
   6. **Regular review**: Audit permissions, remove unused access

   Example: A deployment service doesn't need to delete production databases. Grant only deploy permissions.
   </details>

4. **Why are short-lived tokens preferred over long-lived credentials?**
   <details>
   <summary>Answer</summary>

   Short-lived tokens limit exposure:

   **Long-lived credentials** (API keys, passwords):
   - If stolen, attacker has access until key is rotated
   - May never be discovered as stolen
   - Hard to rotate across many systems
   - Exposure window: unlimited

   **Short-lived tokens** (JWT, OAuth tokens):
   - Expire automatically (minutes to hours)
   - If stolen, attacker has limited time window
   - New tokens issued regularly
   - Exposure window: token lifetime only

   Even if an attacker gets a short-lived token, they have hours, not forever. Regular token refresh also forces re-authentication, catching revoked access.
   </details>

---

## Hands-On Exercise

**Task**: Design an IAM strategy for a microservices application.

**Scenario**: You're building an e-commerce platform with:
- Web frontend (user-facing)
- API gateway
- Order service
- Inventory service
- Payment service
- PostgreSQL database
- Redis cache

**Part 1: User Authentication (10 minutes)**

Design the user authentication flow:

| Component | Authentication Method | Factors |
|-----------|----------------------|---------|
| Web login | | |
| API access | | |
| Admin panel | | |

**Part 2: Service Authorization (10 minutes)**

Design service-to-service permissions:

| Service | Can Access | Permissions | Cannot Access |
|---------|------------|-------------|---------------|
| API Gateway | Order Service | read, write | |
| Order Service | | | |
| Inventory Service | | | |
| Payment Service | | | |

**Part 3: Database Access (10 minutes)**

Design database access:

| Service | Database Access | Tables | Operations |
|---------|-----------------|--------|------------|
| Order Service | PostgreSQL | orders, order_items | SELECT, INSERT, UPDATE |
| | | | |
| | | | |

**Part 4: Kubernetes RBAC (10 minutes)**

Write a ServiceAccount and Role for the Order Service:

```yaml
# Your YAML here
```

**Success Criteria**:
- [ ] User auth uses MFA for sensitive operations
- [ ] Each service has only permissions it needs
- [ ] No service has more database access than required
- [ ] RBAC follows least privilege

---

## Further Reading

- **"OAuth 2.0 Simplified"** - Aaron Parecki. Clear explanation of OAuth flows and best practices.

- **"Identity and Data Security for Web Development"** - Jonathan LeBlanc. Practical guide to implementing authentication.

- **NIST SP 800-63** - Digital Identity Guidelines. The authoritative standard for authentication assurance levels.

---

## Next Module

[Module 4.4: Secure by Default](module-4.4-secure-by-default.md) - Building security into systems from the start, not bolting it on later.
