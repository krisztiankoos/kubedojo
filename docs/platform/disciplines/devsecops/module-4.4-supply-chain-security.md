# Module 4.4: Supply Chain Security

> **Discipline Module** | Complexity: `[COMPLEX]` | Time: 40-45 min

## Prerequisites

Before starting this module:
- **Required**: [Module 4.3: Security in CI/CD](module-4.3-security-cicd.md) — Pipeline security
- **Required**: Understanding of container registries and image distribution
- **Recommended**: Basic cryptography concepts (signing, verification)
- **Helpful**: Experience with package managers (npm, pip, go modules)

---

## Why This Module Matters

You've locked down your code. Your pipeline has security gates. Your containers are scanned.

**But where did that base image come from?**

**Who maintains that npm package with 50 million weekly downloads?**

**Can you prove your production binary matches your source code?**

Supply chain attacks target the weakest link—not your code, but everything around it. The 2020 SolarWinds attack compromised 18,000 organizations through one malicious update. The 2021 Codecov breach exposed secrets from 29,000 repositories.

After this module, you'll understand:
- How software supply chain attacks work
- SBOM (Software Bill of Materials) generation and use
- Image signing and verification with Sigstore
- SLSA framework for supply chain integrity
- Practical defenses at each layer

---

## Understanding the Software Supply Chain

### The Attack Surface

```
┌─────────────────────────────────────────────────────────────────┐
│                 SOFTWARE SUPPLY CHAIN ATTACK SURFACE            │
│                                                                 │
│  SOURCE                DEPENDENCIES            BUILD            │
│  ┌─────────┐          ┌─────────┐          ┌─────────┐         │
│  │ Your    │          │ Direct  │          │ Build   │         │
│  │ code    │◀─────────│ deps    │◀─────────│ process │         │
│  │         │          │         │          │         │         │
│  │ Attack: │          │ Attack: │          │ Attack: │         │
│  │ Insider │          │ Typosquat│         │ Inject  │         │
│  │ Commit  │          │ Hijack  │          │ malware │         │
│  └─────────┘          └────┬────┘          └─────────┘         │
│                            │                                    │
│                       ┌────▼────┐                               │
│                       │Transitive│                              │
│                       │ deps    │                               │
│                       │         │                               │
│                       │ Attack: │                               │
│                       │ Hidden  │                               │
│                       │ in tree │                               │
│                       └─────────┘                               │
│                                                                 │
│  ARTIFACTS            DISTRIBUTION          RUNTIME             │
│  ┌─────────┐          ┌─────────┐          ┌─────────┐         │
│  │ Images  │─────────▶│ Registry│─────────▶│ Cluster │         │
│  │ Binaries│          │ CDN     │          │ Servers │         │
│  │         │          │         │          │         │         │
│  │ Attack: │          │ Attack: │          │ Attack: │         │
│  │ Tamper  │          │ MITM    │          │ Replace │         │
│  │ before  │          │ Poison  │          │ at      │         │
│  │ sign    │          │ cache   │          │ deploy  │         │
│  └─────────┘          └─────────┘          └─────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Real Supply Chain Attacks

| Attack | Year | Impact | Vector |
|--------|------|--------|--------|
| **SolarWinds** | 2020 | 18,000 orgs, including US gov | Build process injection |
| **Codecov** | 2021 | 29,000 repos exposed | CI script tampering |
| **Log4Shell** | 2021 | Millions of apps | Transitive dependency |
| **ua-parser-js** | 2021 | 8M weekly downloads | Maintainer compromise |
| **event-stream** | 2018 | 2M weekly downloads | New maintainer attack |
| **PyPI typosquatting** | Ongoing | Thousands of installs | Package name confusion |

---

## Software Bill of Materials (SBOM)

### What is an SBOM?

An SBOM is a complete inventory of components in your software:

```
┌─────────────────────────────────────────────────────────────┐
│                        SBOM                                  │
│                                                              │
│  Application: my-web-app v1.2.3                             │
│  Build Date: 2024-01-15                                     │
│  Build Tool: docker 24.0.7                                  │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ COMPONENTS                                               ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ pkg:npm/express@4.18.2                                   ││
│  │ pkg:npm/lodash@4.17.21                                   ││
│  │ pkg:npm/axios@1.6.0                                      ││
│  │ pkg:apk/alpine-baselayout@3.4.3                         ││
│  │ pkg:apk/openssl@3.1.4                                   ││
│  │ ... (hundreds more)                                      ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  RELATIONSHIPS                                               │
│  express@4.18.2 ──depends-on──▶ body-parser@1.20.2         │
│  body-parser@1.20.2 ──depends-on──▶ bytes@3.1.2            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Why SBOMs Matter

**Without SBOM (Log4Shell scenario):**
```
Security Team: "Are we affected by Log4Shell?"
Developer 1: "I don't think we use Log4j..."
Developer 2: "Let me grep the codebase..."
Developer 3: "What about that Java service?"
[3 weeks later]
Developer 1: "Found it in a transitive dependency!"
```

**With SBOM:**
```bash
$ grype sbom:./my-app.sbom --only-vuln-id CVE-2021-44228
NAME     INSTALLED  FIXED-IN  VULNERABILITY
log4j    2.14.1     2.17.1    CVE-2021-44228 Critical
```

Time to answer: 3 seconds vs 3 weeks.

### SBOM Formats

| Format | Origin | Best For |
|--------|--------|----------|
| **SPDX** | Linux Foundation | License compliance, legal |
| **CycloneDX** | OWASP | Security, vulnerability tracking |
| **SWID** | ISO | Enterprise asset management |

### Generating SBOMs

**Syft (by Anchore):**
```bash
# Generate SBOM from container image
syft myapp:latest -o spdx-json > sbom.spdx.json

# Generate SBOM from directory
syft dir:./src -o cyclonedx-json > sbom.cdx.json
```

**Trivy:**
```bash
# Generate SBOM from container image
trivy image --format spdx-json myapp:latest > sbom.spdx.json

# Generate SBOM from filesystem
trivy fs --format cyclonedx ./src > sbom.cdx.json
```

**In Docker Build:**
```bash
# Docker BuildKit native SBOM
docker buildx build --sbom=true -t myapp:latest .

# Attach SBOM as attestation
docker buildx build --attest type=sbom -t myapp:latest .
```

### Scanning SBOMs for Vulnerabilities

```bash
# Grype (Anchore)
grype sbom:./sbom.cdx.json

# Trivy
trivy sbom ./sbom.spdx.json

# Output
NAME      VERSION   VULNERABILITY  SEVERITY
lodash    4.17.20   CVE-2021-23337 HIGH
axios     0.21.0    CVE-2021-3749  MEDIUM
```

---

## Did You Know?

1. **US Executive Order 14028 (May 2021)** requires SBOMs for all software sold to the federal government. This single order catalyzed the entire industry's SBOM adoption.

2. **The average enterprise application contains 528 open source components**, but most organizations can only account for about 10% of them without automated SBOM generation.

3. **Sigstore was founded in 2020** by Google, Red Hat, and Purdue University. It provides free code signing for open source—and has already signed over 20 million artifacts.

4. **The SLSA framework name** is pronounced "salsa" and stands for Supply chain Levels for Software Artifacts. It was created by Google based on their internal Binary Authorization system that secures their entire production environment.

---

## Image Signing with Sigstore

### Why Sign Images?

```
┌─────────────────────────────────────────────────────────────┐
│              WITHOUT SIGNING                                 │
│                                                              │
│  CI/CD ──build──▶ Registry ◀──pull── Cluster                │
│                       │                                      │
│                   Trust the                                  │
│                   registry?                                  │
│                   What if                                    │
│                   compromised?                               │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│              WITH SIGNING                                    │
│                                                              │
│  CI/CD ──build──▶ Sign ──▶ Registry ◀──pull── Verify ──▶ K8s│
│            │                              │                  │
│      Private key                    Verify signature         │
│      (secure)                       matches trusted key      │
│                                                              │
│  Even if registry compromised, unsigned images rejected     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### The Sigstore Ecosystem

```
┌─────────────────────────────────────────────────────────────┐
│                    SIGSTORE ECOSYSTEM                        │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Cosign  │    │  Fulcio  │    │  Rekor   │              │
│  │          │    │          │    │          │              │
│  │  Sign &  │───▶│  Issue   │───▶│ Record   │              │
│  │  verify  │    │  certs   │    │ in log   │              │
│  │  images  │    │  (OIDC)  │    │ (immut.) │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       │                                                      │
│       │    ┌──────────────────────────────────────────┐     │
│       └───▶│  No long-lived keys to manage!           │     │
│            │  Sign with your identity (GitHub, Google) │     │
│            │  Transparent log proves when signed       │     │
│            └──────────────────────────────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Signing with Cosign

**Installation:**
```bash
# macOS
brew install cosign

# Linux
curl -LO https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
chmod +x cosign-linux-amd64
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
```

**Keyless signing (recommended):**
```bash
# Sign image (opens browser for OIDC auth)
cosign sign ghcr.io/myorg/myapp:v1.0.0

# This will:
# 1. Authenticate you via OIDC (GitHub, Google, etc.)
# 2. Get ephemeral certificate from Fulcio
# 3. Sign the image
# 4. Record signature in Rekor transparency log
```

**Verify signature:**
```bash
# Verify image was signed by specific identity
cosign verify ghcr.io/myorg/myapp:v1.0.0 \
  --certificate-identity developer@example.com \
  --certificate-oidc-issuer https://accounts.google.com

# Verify image was signed by GitHub Actions in specific repo
cosign verify ghcr.io/myorg/myapp:v1.0.0 \
  --certificate-identity-regexp 'https://github.com/myorg/myapp/.github/workflows/.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

### GitHub Actions: Sign Images

```yaml
name: Build, Sign, Push
on:
  push:
    tags: ['v*']

jobs:
  build-and-sign:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write  # Required for keyless signing

    steps:
      - uses: actions/checkout@v4

      - name: Install Cosign
        uses: sigstore/cosign-installer@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}

      - name: Sign image
        env:
          COSIGN_EXPERIMENTAL: "true"
        run: |
          cosign sign --yes ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
```

### Kubernetes Admission Control

**Kyverno policy to require signed images:**
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-signed-images
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-signature
      match:
        any:
          - resources:
              kinds:
                - Pod
      verifyImages:
        - imageReferences:
            - "ghcr.io/myorg/*"
          attestors:
            - entries:
                - keyless:
                    subject: "https://github.com/myorg/*"
                    issuer: "https://token.actions.githubusercontent.com"
```

**Sigstore Policy Controller:**
```yaml
apiVersion: policy.sigstore.dev/v1alpha1
kind: ClusterImagePolicy
metadata:
  name: signed-images-policy
spec:
  images:
    - glob: "ghcr.io/myorg/**"
  authorities:
    - keyless:
        identities:
          - issuerRegExp: "https://token.actions.githubusercontent.com"
            subjectRegExp: "https://github.com/myorg/.*"
```

---

## The SLSA Framework

### What is SLSA?

SLSA (Supply chain Levels for Software Artifacts) is a framework for achieving supply chain integrity.

```
┌─────────────────────────────────────────────────────────────┐
│                     SLSA LEVELS                              │
│                                                              │
│  Level 0: No guarantees                                     │
│  ─────────────────────                                       │
│  No provenance, no verification                              │
│                                                              │
│  Level 1: Provenance                                        │
│  ───────────────────                                         │
│  Build process documented                                    │
│  Provenance generated automatically                          │
│                                                              │
│  Level 2: Tamper Resistant                                  │
│  ─────────────────────────                                   │
│  Hosted build service                                        │
│  Authenticated provenance                                    │
│                                                              │
│  Level 3: Hardened Builds                                   │
│  ────────────────────────                                    │
│  Isolated, ephemeral build environment                       │
│  Non-falsifiable provenance                                  │
│                                                              │
│  Level 4: (Future)                                          │
│  Two-person review, hermetic builds                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### SLSA Requirements by Level

| Requirement | L1 | L2 | L3 |
|-------------|:--:|:--:|:--:|
| Scripted build | ✓ | ✓ | ✓ |
| Build service | | ✓ | ✓ |
| Provenance generated | ✓ | ✓ | ✓ |
| Authenticated provenance | | ✓ | ✓ |
| Isolated build | | | ✓ |
| Ephemeral environment | | | ✓ |
| Non-falsifiable provenance | | | ✓ |

### Generating SLSA Provenance

**GitHub Actions with SLSA Generator:**
```yaml
name: SLSA Build
on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        id: build
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}

  provenance:
    needs: build
    permissions:
      actions: read
      id-token: write
      packages: write
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v1.9.0
    with:
      image: ghcr.io/${{ github.repository }}
      digest: ${{ needs.build.outputs.digest }}
      registry-username: ${{ github.actor }}
    secrets:
      registry-password: ${{ secrets.GITHUB_TOKEN }}
```

### Verifying SLSA Provenance

```bash
# Install SLSA verifier
go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

# Verify container image provenance
slsa-verifier verify-image ghcr.io/myorg/myapp@sha256:abc123 \
  --source-uri github.com/myorg/myapp \
  --source-tag v1.0.0

# Verify artifact provenance
slsa-verifier verify-artifact myapp-linux-amd64 \
  --provenance-path myapp-linux-amd64.intoto.jsonl \
  --source-uri github.com/myorg/myapp
```

---

## War Story: The Dependency That Wasn't

A security researcher discovered something interesting in a fintech company's production Kubernetes cluster.

**The Discovery:**

Running a routine SBOM comparison:
```bash
# Compare production SBOM to build SBOM
diff <(jq '.components[].name' build-sbom.json | sort) \
     <(jq '.components[].name' prod-sbom.json | sort)

> pkg:npm/debug-production-helper@1.0.0
```

A package in production that wasn't in the build?

**The Investigation:**

```bash
# Check npm registry
npm info debug-production-helper
# Not found in public registry

# Check internal registry
curl internal-npm.company.com/debug-production-helper
# Package exists, uploaded 3 months ago

# Check who uploaded
# "service-account-compromised" ← Red flag!
```

**What Happened:**
1. Attacker compromised a service account
2. Published malicious package to internal registry
3. Added dependency during manual "debugging"
4. Package exfiltrated environment variables (including secrets)

**The Response:**
1. Rotate all secrets exposed to affected pods
2. Remove malicious package
3. Implement:
   - SBOM comparison in deploy pipeline
   - Package signing for internal registry
   - Alert on new dependencies not in build

**The Lesson:**

Without SBOM comparison, they'd never have noticed. The malicious package was designed to look like a debugging tool and had no obvious malicious behavior—it just quietly logged environment variables to an external endpoint.

---

## Dependency Management Security

### Dependency Confusion Attacks

```
┌─────────────────────────────────────────────────────────────┐
│              DEPENDENCY CONFUSION ATTACK                     │
│                                                              │
│  Your package.json:                                          │
│  "internal-utils": "1.0.0"  ← Private package               │
│                                                              │
│  Attacker publishes to public npm:                          │
│  "internal-utils": "99.0.0" ← Malicious, higher version     │
│                                                              │
│  npm install behavior:                                       │
│  "99.0.0 > 1.0.0, use public version!" ← Attack succeeds    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Defenses:**

```json
// package.json - Use scoped packages
{
  "dependencies": {
    "@mycompany/internal-utils": "1.0.0"
  }
}
```

```ini
# .npmrc - Scope to private registry
@mycompany:registry=https://npm.mycompany.com
```

### Typosquatting Defense

```
┌─────────────────────────────────────────────────────────────┐
│                   TYPOSQUATTING                              │
│                                                              │
│  Legitimate:        Typosquats:                             │
│  lodash             1odash (one not L)                      │
│  express            expres (missing s)                      │
│  moment             momnet (transposed)                     │
│  react              reakt, reactt                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Defenses:**
```bash
# Use lockfiles
npm ci  # Install from lockfile exactly
pip install --require-hashes -r requirements.txt

# Verify package checksums
# requirements.txt with hashes
requests==2.28.0 \
    --hash=sha256:7c5599b102feddaa661c826c56ab4fee28bfd17f5...
```

### Lockfile Best Practices

| Language | Lockfile | Command |
|----------|----------|---------|
| npm | package-lock.json | `npm ci` |
| yarn | yarn.lock | `yarn install --frozen-lockfile` |
| pip | requirements.txt (with hashes) | `pip install --require-hashes` |
| poetry | poetry.lock | `poetry install` |
| go | go.sum | `go mod verify` |

### Renovate/Dependabot Security Updates

```yaml
# renovate.json
{
  "extends": ["config:base"],
  "vulnerabilityAlerts": {
    "enabled": true,
    "labels": ["security"]
  },
  "packageRules": [
    {
      "matchUpdateTypes": ["patch", "minor"],
      "matchCurrentVersion": "!/^0/",
      "automerge": true
    },
    {
      "matchPackagePatterns": ["*"],
      "matchUpdateTypes": ["major"],
      "labels": ["major-update"]
    }
  ]
}
```

---

## Build Provenance and Reproducibility

### What is Provenance?

Provenance answers: "Where did this artifact come from?"

```json
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "subject": [{
    "name": "myapp",
    "digest": {"sha256": "abc123..."}
  }],
  "predicateType": "https://slsa.dev/provenance/v0.2",
  "predicate": {
    "builder": {
      "id": "https://github.com/myorg/myapp/actions/runs/123"
    },
    "buildType": "https://github.com/slsa-framework/slsa-github-generator",
    "invocation": {
      "configSource": {
        "uri": "git+https://github.com/myorg/myapp@refs/tags/v1.0.0",
        "digest": {"sha1": "def456..."},
        "entryPoint": ".github/workflows/release.yml"
      }
    },
    "materials": [{
      "uri": "git+https://github.com/myorg/myapp@refs/tags/v1.0.0",
      "digest": {"sha1": "def456..."}
    }]
  }
}
```

### Reproducible Builds

Goal: Same source → Same binary (bit-for-bit identical)

**Challenges:**
- Timestamps in binaries
- Random build IDs
- Non-deterministic ordering
- Environment differences

**Solutions:**
```dockerfile
# Dockerfile: Reproducible builds
FROM golang:1.21 AS builder

# Pin versions
ENV CGO_ENABLED=0
ENV GOOS=linux

# Use specific commit, not branch
COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Reproducible build flags
RUN go build \
    -ldflags="-s -w -buildid=" \
    -trimpath \
    -o /app

# Minimal runtime
FROM scratch
COPY --from=builder /app /app
ENTRYPOINT ["/app"]
```

```yaml
# GitHub Actions: Consistent environment
jobs:
  build:
    runs-on: ubuntu-22.04  # Pin runner version
    env:
      SOURCE_DATE_EPOCH: 0  # Reproducible timestamps
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| No SBOM | Can't answer "are we affected?" | Generate SBOM for every build |
| SBOM not stored | Can't query old versions | Store SBOMs with artifacts |
| Unsigned images | Can't verify origin | Sign with Cosign/Sigstore |
| No admission control | Unsigned images can deploy | Require signatures in cluster |
| Using `latest` tags | Non-reproducible | Pin versions, use digests |
| No lockfile | Dependency confusion | Lock all dependencies |
| Trust public packages | Typosquatting, hijacking | Verify sources, use SCA |

---

## Quiz: Check Your Understanding

### Question 1
Your SBOM shows you use log4j 2.14.1. A CVE is announced for log4j 2.x < 2.17. You don't directly import log4j. What's happening and what should you do?

<details>
<summary>Show Answer</summary>

**What's happening:**
Log4j is a transitive dependency—something you depend on depends on it.

**Investigation:**
```bash
# Find the dependency path
# Maven
mvn dependency:tree -Dincludes=org.apache.logging.log4j

# Gradle
gradle dependencies | grep -A5 log4j

# npm
npm ls log4j
```

**Resolution options:**

1. **Update the direct dependency:**
   If `spring-boot-starter` pulls in log4j, update spring-boot-starter

2. **Force version override:**
   ```xml
   <!-- Maven -->
   <dependencyManagement>
     <dependencies>
       <dependency>
         <groupId>org.apache.logging.log4j</groupId>
         <artifactId>log4j-core</artifactId>
         <version>2.17.1</version>
       </dependency>
     </dependencies>
   </dependencyManagement>
   ```

3. **Exclude and add fixed version:**
   ```xml
   <dependency>
     <groupId>com.example</groupId>
     <artifactId>some-library</artifactId>
     <exclusions>
       <exclusion>
         <groupId>org.apache.logging.log4j</groupId>
         <artifactId>log4j-core</artifactId>
       </exclusion>
     </exclusions>
   </dependency>
   ```

**Key lesson:** This is why SBOMs matter—they show transitive dependencies SAST can't see.

</details>

### Question 2
You're implementing image signing. A developer asks: "If we're already scanning images for vulnerabilities, why do we need signing too?"

<details>
<summary>Show Answer</summary>

**Scanning and signing solve different problems:**

**Vulnerability scanning** answers:
- Does this image have known CVEs?
- Are the dependencies up to date?
- Are there misconfigurations?

**Image signing** answers:
- Was this image built by our CI/CD?
- Has it been tampered with since build?
- Can I trust the image source?

**Scenarios where scanning isn't enough:**

1. **Registry compromise:**
   Attacker replaces your nginx:v1 with backdoored image.
   Scan passes (no known CVEs), but it's not YOUR image.

2. **Build system compromise:**
   Malware injected during build.
   Scan can't detect custom backdoors without signatures.

3. **Unsigned old image:**
   Someone deploys an ancient, unscanned image.
   Signing policy prevents this entirely.

**Defense in depth:**
```
Build → Scan → Sign → Push → Verify → Deploy
         │       │              │
    Find CVEs  Prove origin   Enforce policy
```

Both are needed. Scanning finds vulnerabilities. Signing proves authenticity.

</details>

### Question 3
What SLSA level is achieved by: "We build in GitHub Actions, and our workflows are in the repository"?

<details>
<summary>Show Answer</summary>

**This achieves approximately SLSA Level 2, but verification is needed:**

**SLSA Level 1** requirements (met):
- ✓ Scripted build (GitHub Actions workflow)
- ✓ Provenance generated (GitHub attestation)

**SLSA Level 2** requirements (partially met):
- ✓ Hosted build service (GitHub)
- ⚠️ Authenticated provenance (needs Sigstore or GitHub Attestations)

**SLSA Level 3** requirements (not met):
- ✗ Isolated, ephemeral build environment (standard runners are shared)
- ✗ Non-falsifiable provenance (workflow can be modified)

**To achieve SLSA Level 3:**
```yaml
# Use SLSA GitHub Generator
uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v1.9.0
```

This generates non-falsifiable provenance attesting that:
- Build happened on GitHub Actions
- From specific source commit
- Using specific workflow
- Cannot be forged by the repository owner

**Key insight:** "Building on GitHub" isn't enough for L3. The provenance must be non-falsifiable, meaning even the repository owner can't forge it.

</details>

### Question 4
You want to prevent dependency confusion attacks. What controls would you implement?

<details>
<summary>Show Answer</summary>

**Multi-layer defense:**

**1. Package naming:**
```json
// Use scoped packages (npm)
{
  "dependencies": {
    "@mycompany/internal-utils": "1.0.0"
  }
}
```
Scopes are globally unique, can't be typosquatted.

**2. Registry configuration:**
```ini
# .npmrc
@mycompany:registry=https://npm.internal.mycompany.com
registry=https://registry.npmjs.org
always-auth=true
```
Scoped packages only from internal registry.

**3. Lockfile enforcement:**
```yaml
# CI/CD
steps:
  - run: npm ci  # Fails if lockfile doesn't match
```

**4. Version pinning in lockfile:**
```json
// package-lock.json includes registry URLs
"node_modules/@mycompany/internal-utils": {
  "version": "1.0.0",
  "resolved": "https://npm.internal.mycompany.com/..."
}
```

**5. Private package reservation:**
Register your internal package names on public registries (even if empty) to prevent squatting.

**6. Dependency review:**
```yaml
# GitHub Actions
- name: Dependency Review
  uses: actions/dependency-review-action@v3
  with:
    fail-on-severity: high
    deny-packages: "pkg:npm/internal-*"  # Block public internal- packages
```

</details>

---

## Hands-On Exercise: Secure Supply Chain Implementation

Implement SBOM generation, signing, and verification.

### Part 1: Generate SBOM

```bash
# Create sample project
mkdir supply-chain-demo && cd supply-chain-demo

cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
EOF

cat > requirements.txt << 'EOF'
flask==2.3.0
requests==2.28.0
EOF

cat > app.py << 'EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
EOF

# Build image
docker build -t supply-chain-demo:v1 .

# Generate SBOM with Syft
syft supply-chain-demo:v1 -o spdx-json > sbom.spdx.json

# View SBOM components
cat sbom.spdx.json | jq '.packages[].name'

# Scan SBOM for vulnerabilities
grype sbom:./sbom.spdx.json
```

### Part 2: Sign Image with Cosign

```bash
# Install cosign
brew install cosign  # or download from GitHub releases

# Login to registry (using Docker Hub for demo)
docker login

# Tag and push
docker tag supply-chain-demo:v1 yourusername/supply-chain-demo:v1
docker push yourusername/supply-chain-demo:v1

# Sign with keyless signing (opens browser)
COSIGN_EXPERIMENTAL=1 cosign sign yourusername/supply-chain-demo:v1

# Verify signature
cosign verify yourusername/supply-chain-demo:v1 \
  --certificate-identity your-email@example.com \
  --certificate-oidc-issuer https://accounts.google.com
```

### Part 3: Attach SBOM as Attestation

```bash
# Attach SBOM to image
cosign attest --predicate sbom.spdx.json \
  --type spdxjson \
  yourusername/supply-chain-demo:v1

# Verify attestation exists
cosign verify-attestation yourusername/supply-chain-demo:v1 \
  --type spdxjson \
  --certificate-identity your-email@example.com \
  --certificate-oidc-issuer https://accounts.google.com

# Download and inspect SBOM
cosign download attestation yourusername/supply-chain-demo:v1 | jq '.payload | @base64d | fromjson'
```

### Success Criteria

- [ ] SBOM generated for container image
- [ ] Vulnerabilities identified from SBOM
- [ ] Image signed with Cosign
- [ ] Signature verified successfully
- [ ] SBOM attached as attestation

---

## Key Takeaways

1. **SBOM is essential** — You can't secure what you can't see
2. **Sign everything** — Prove artifacts come from your build system
3. **Verify at admission** — Don't let unsigned images deploy
4. **SLSA provides a framework** — Progressive levels for supply chain maturity
5. **Defense in depth** — Lockfiles, scopes, signing, verification all work together

---

## Further Reading

**Frameworks:**
- **SLSA** — slsa.dev
- **OpenSSF Scorecard** — securityscorecards.dev
- **CNCF Supply Chain Security** — github.com/cncf/tag-security

**Tools:**
- **Sigstore** — sigstore.dev
- **Syft** — github.com/anchore/syft
- **Cosign** — github.com/sigstore/cosign

**Standards:**
- **SPDX** — spdx.dev
- **CycloneDX** — cyclonedx.org
- **in-toto** — in-toto.io

---

## Summary

Supply chain security protects against attacks on everything except your own code:

- **SBOM** documents what's in your software (know your ingredients)
- **Image signing** proves artifacts come from your build (verify origin)
- **SLSA** provides maturity levels (progressive improvement)
- **Admission control** enforces policies at deploy time (trust but verify)

The goal is end-to-end integrity: from source code to running container, every step is verified and every artifact is traceable.

---

## Next Module

Continue to [Module 4.5: Runtime Security](module-4.5-runtime-security.md) to learn about protecting running applications and detecting threats in production.

---

*"Trust, but verify. Then verify again at deploy time."*
