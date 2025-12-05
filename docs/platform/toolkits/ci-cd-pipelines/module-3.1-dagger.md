# Module 3.1: Dagger

> **Toolkit Track** | Complexity: `[COMPLEX]` | Time: 45-50 min

## Prerequisites

Before starting this module:
- [DevSecOps Discipline](../../disciplines/devsecops/) — CI/CD concepts
- Programming experience in Go, Python, or TypeScript
- Docker/container fundamentals
- Basic CI/CD pipeline experience

## Why This Module Matters

Traditional CI/CD pipelines are written in YAML—declarative, hard to test, impossible to debug locally. Dagger flips this: write your pipelines in real programming languages, run them anywhere, and debug locally before pushing.

Dagger is the "Docker for CI/CD"—portable pipelines that work the same on your laptop, in GitHub Actions, and in any CI system. No more "works on CI but not locally" debugging nightmares.

## Did You Know?

- **Dagger was founded by the creators of Docker**—Solomon Hykes, the creator of Docker, started Dagger to solve CI/CD the same way Docker solved environments
- **Dagger pipelines are 100% portable**—the same pipeline runs in GitHub Actions, GitLab CI, Jenkins, CircleCI, or your laptop
- **Dagger caches at the layer level like Docker**—unchanged pipeline steps are skipped, just like Docker layer caching
- **The name "Dagger" comes from the CI acronym**—"Devkit for Application Generation and Execution in Reproducible environments"

## What Makes Dagger Different

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL vs DAGGER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TRADITIONAL CI (YAML)                                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  jobs:                                                    │   │
│  │    build:                                                 │   │
│  │      runs-on: ubuntu-latest  ← Tied to runner            │   │
│  │      steps:                                               │   │
│  │        - run: npm install    ← Can't test locally        │   │
│  │        - run: npm test                                    │   │
│  │        - run: docker build   ← Different behavior local  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Problems:                                                       │
│  • Can't run locally                                            │
│  • Can't debug                                                  │
│  • Vendor lock-in                                               │
│  • YAML isn't a programming language                            │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  DAGGER (Code)                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  func (m *MyApp) Build(ctx context.Context) *Container { │   │
│  │    return dag.Container().                                │   │
│  │      From("node:20").                                     │   │
│  │      WithDirectory("/app", m.Source).                     │   │
│  │      WithExec([]string{"npm", "install"}).               │   │
│  │      WithExec([]string{"npm", "test"})                   │   │
│  │  }                                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Benefits:                                                       │
│  ✓ Run anywhere (laptop, CI, cloud)                             │
│  ✓ Real debugging (breakpoints, logs)                          │
│  ✓ Type safety and IDE support                                 │
│  ✓ Testable as regular code                                    │
│  ✓ Reusable modules                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Dagger Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DAGGER ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  YOUR CODE (Go/Python/TypeScript)                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  func Build() {...}                                       │   │
│  │  func Test() {...}                                        │   │
│  │  func Deploy() {...}                                      │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │ SDK Calls                        │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    DAGGER ENGINE                          │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
│  │  │   GraphQL   │  │   Caching   │  │  Container  │       │   │
│  │  │     API     │  │   Layer     │  │   Runtime   │       │   │
│  │  │             │  │             │  │             │       │   │
│  │  │  Receives   │  │  Skips      │  │  Executes   │       │   │
│  │  │  pipeline   │  │  unchanged  │  │  steps in   │       │   │
│  │  │  as DAG     │  │  steps      │  │  containers │       │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 CONTAINER RUNTIME                         │   │
│  │                 (Docker, Podman, etc.)                    │   │
│  │                                                           │   │
│  │  Each pipeline step runs in an isolated container        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Getting Started

### Installation

```bash
# Install Dagger CLI
curl -L https://dl.dagger.io/dagger/install.sh | sh

# Or with Homebrew
brew install dagger/tap/dagger

# Verify installation
dagger version
```

### Initialize a Project

```bash
# Initialize Dagger module
dagger init --sdk=go myproject
# or
dagger init --sdk=python myproject
# or
dagger init --sdk=typescript myproject

cd myproject
```

### Project Structure

```
myproject/
├── dagger.json          # Module configuration
├── dagger/              # Generated code
│   └── ...
└── main.go              # Your pipeline code (or main.py, index.ts)
```

## Writing Pipelines in Go

### Basic Pipeline

```go
// main.go
package main

import (
    "context"
)

type MyApp struct{}

// Build compiles the application
func (m *MyApp) Build(ctx context.Context, source *Directory) *Container {
    return dag.Container().
        From("golang:1.21").
        WithDirectory("/src", source).
        WithWorkdir("/src").
        WithExec([]string{"go", "build", "-o", "app", "."})
}

// Test runs the test suite
func (m *MyApp) Test(ctx context.Context, source *Directory) (string, error) {
    return dag.Container().
        From("golang:1.21").
        WithDirectory("/src", source).
        WithWorkdir("/src").
        WithExec([]string{"go", "test", "-v", "./..."}).
        Stdout(ctx)
}

// Lint checks code quality
func (m *MyApp) Lint(ctx context.Context, source *Directory) (string, error) {
    return dag.Container().
        From("golangci/golangci-lint:latest").
        WithDirectory("/src", source).
        WithWorkdir("/src").
        WithExec([]string{"golangci-lint", "run"}).
        Stdout(ctx)
}
```

### Running Pipelines

```bash
# Run build function
dagger call build --source=.

# Run test function
dagger call test --source=.

# Run lint function
dagger call lint --source=.
```

### Publishing Container Images

```go
func (m *MyApp) Publish(
    ctx context.Context,
    source *Directory,
    registry string,  // e.g., "ghcr.io/org/myapp"
    tag string,       // e.g., "v1.0.0"
    username string,
    password *Secret,
) (string, error) {
    // Build the container
    container := dag.Container().
        From("golang:1.21-alpine").
        WithDirectory("/src", source).
        WithWorkdir("/src").
        WithExec([]string{"go", "build", "-o", "app", "."}).
        WithEntrypoint([]string{"/src/app"})

    // Push to registry
    ref := fmt.Sprintf("%s:%s", registry, tag)
    return container.
        WithRegistryAuth(registry, username, password).
        Publish(ctx, ref)
}
```

```bash
# Publish with secret
dagger call publish \
  --source=. \
  --registry=ghcr.io/org/myapp \
  --tag=v1.0.0 \
  --username=myuser \
  --password=env:GITHUB_TOKEN
```

### Caching

```go
func (m *MyApp) BuildWithCache(ctx context.Context, source *Directory) *Container {
    // Create a cache volume for Go modules
    goModCache := dag.CacheVolume("go-mod-cache")
    goBuildCache := dag.CacheVolume("go-build-cache")

    return dag.Container().
        From("golang:1.21").
        WithDirectory("/src", source).
        WithWorkdir("/src").
        // Mount cache volumes
        WithMountedCache("/go/pkg/mod", goModCache).
        WithMountedCache("/root/.cache/go-build", goBuildCache).
        // Build with cache
        WithExec([]string{"go", "build", "-o", "app", "."})
}
```

### Parallel Execution

```go
func (m *MyApp) CI(ctx context.Context, source *Directory) error {
    // Run lint, test, and security scan in parallel
    eg, ctx := errgroup.WithContext(ctx)

    eg.Go(func() error {
        _, err := m.Lint(ctx, source)
        return err
    })

    eg.Go(func() error {
        _, err := m.Test(ctx, source)
        return err
    })

    eg.Go(func() error {
        _, err := m.SecurityScan(ctx, source)
        return err
    })

    return eg.Wait()
}
```

## Writing Pipelines in Python

### Basic Pipeline

```python
# main.py
import dagger
from dagger import dag, function, object_type

@object_type
class MyApp:
    @function
    async def build(self, source: dagger.Directory) -> dagger.Container:
        """Build the Python application."""
        return (
            dag.container()
            .from_("python:3.11-slim")
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_exec(["python", "-m", "py_compile", "app.py"])
        )

    @function
    async def test(self, source: dagger.Directory) -> str:
        """Run pytest."""
        return await (
            dag.container()
            .from_("python:3.11-slim")
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_exec(["pip", "install", "pytest"])
            .with_exec(["pytest", "-v"])
            .stdout()
        )

    @function
    async def lint(self, source: dagger.Directory) -> str:
        """Run ruff linter."""
        return await (
            dag.container()
            .from_("python:3.11-slim")
            .with_exec(["pip", "install", "ruff"])
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["ruff", "check", "."])
            .stdout()
        )
```

### Python with UV (Fast Package Manager)

```python
@function
async def build_with_uv(self, source: dagger.Directory) -> dagger.Container:
    """Build with UV package manager for faster installs."""
    return (
        dag.container()
        .from_("python:3.11-slim")
        .with_exec(["pip", "install", "uv"])
        .with_directory("/app", source)
        .with_workdir("/app")
        .with_exec(["uv", "pip", "install", "-r", "requirements.txt"])
    )
```

## Writing Pipelines in TypeScript

### Basic Pipeline

```typescript
// index.ts
import { dag, Container, Directory, object, func } from "@dagger.io/dagger"

@object()
class MyApp {
  @func()
  async build(source: Directory): Promise<Container> {
    return dag
      .container()
      .from("node:20-slim")
      .withDirectory("/app", source)
      .withWorkdir("/app")
      .withExec(["npm", "install"])
      .withExec(["npm", "run", "build"])
  }

  @func()
  async test(source: Directory): Promise<string> {
    return dag
      .container()
      .from("node:20-slim")
      .withDirectory("/app", source)
      .withWorkdir("/app")
      .withExec(["npm", "install"])
      .withExec(["npm", "test"])
      .stdout()
  }

  @func()
  async lint(source: Directory): Promise<string> {
    return dag
      .container()
      .from("node:20-slim")
      .withDirectory("/app", source)
      .withWorkdir("/app")
      .withExec(["npm", "install"])
      .withExec(["npm", "run", "lint"])
      .stdout()
  }
}
```

## Dagger Modules

### Using Community Modules

```go
// Use a community module for Kubernetes deployment
func (m *MyApp) Deploy(ctx context.Context, kubeconfig *Secret) error {
    // Install the kubectl module
    kubectl := dag.Kubectl()

    return kubectl.
        WithKubeconfig(kubeconfig).
        Apply(ctx, "./k8s/deployment.yaml")
}
```

```bash
# Install a module
dagger install github.com/dagger/dagger/modules/kubectl

# List available modules
dagger modules
```

### Creating Reusable Modules

```go
// Create a reusable Go builder module
// dagger/go-builder/main.go

package main

type GoBuilder struct{}

// Build compiles a Go application
func (m *GoBuilder) Build(
    source *Directory,
    goVersion Optional[string],
) *Container {
    version := goVersion.GetOr("1.21")

    return dag.Container().
        From(fmt.Sprintf("golang:%s", version)).
        WithDirectory("/src", source).
        WithWorkdir("/src").
        WithMountedCache("/go/pkg/mod", dag.CacheVolume("go-mod")).
        WithExec([]string{"go", "build", "-o", "app", "."})
}

// Test runs Go tests
func (m *GoBuilder) Test(source *Directory) (string, error) {
    return dag.Container().
        From("golang:1.21").
        WithDirectory("/src", source).
        WithWorkdir("/src").
        WithExec([]string{"go", "test", "-v", "./..."}).
        Stdout(context.Background())
}
```

## Integration with CI Systems

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Dagger
        uses: dagger/dagger-for-github@v5

      - name: Run tests
        run: dagger call test --source=.

      - name: Build and publish
        if: github.ref == 'refs/heads/main'
        run: |
          dagger call publish \
            --source=. \
            --registry=ghcr.io/${{ github.repository }} \
            --tag=${{ github.sha }} \
            --username=${{ github.actor }} \
            --password=env:GITHUB_TOKEN
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

variables:
  DAGGER_VERSION: "0.9.0"

.dagger:
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - apk add curl
    - curl -L https://dl.dagger.io/dagger/install.sh | sh
    - export PATH=$PATH:/root/.local/bin

test:
  extends: .dagger
  stage: test
  script:
    - dagger call test --source=.

build:
  extends: .dagger
  stage: build
  script:
    - dagger call build --source=.

deploy:
  extends: .dagger
  stage: deploy
  only:
    - main
  script:
    - dagger call publish --source=. --registry=$CI_REGISTRY_IMAGE --tag=$CI_COMMIT_SHA
```

### Local Development

```bash
# Run the same pipeline locally
dagger call test --source=.
dagger call build --source=.

# Debug with verbose output
dagger call test --source=. --debug

# Interactive shell in container
dagger call build --source=. terminal
```

## Multi-Stage Pipelines

```go
func (m *MyApp) CICD(
    ctx context.Context,
    source *Directory,
    registry string,
    tag string,
    kubeconfig *Secret,
    password *Secret,
) error {
    // Stage 1: Lint
    fmt.Println("🔍 Running lint...")
    if _, err := m.Lint(ctx, source); err != nil {
        return fmt.Errorf("lint failed: %w", err)
    }

    // Stage 2: Test
    fmt.Println("🧪 Running tests...")
    if _, err := m.Test(ctx, source); err != nil {
        return fmt.Errorf("tests failed: %w", err)
    }

    // Stage 3: Security scan
    fmt.Println("🔒 Running security scan...")
    if _, err := m.SecurityScan(ctx, source); err != nil {
        return fmt.Errorf("security scan failed: %w", err)
    }

    // Stage 4: Build and publish
    fmt.Println("📦 Building and publishing...")
    ref, err := m.Publish(ctx, source, registry, tag, password)
    if err != nil {
        return fmt.Errorf("publish failed: %w", err)
    }
    fmt.Printf("Published: %s\n", ref)

    // Stage 5: Deploy
    fmt.Println("🚀 Deploying...")
    if err := m.Deploy(ctx, kubeconfig, ref); err != nil {
        return fmt.Errorf("deploy failed: %w", err)
    }

    fmt.Println("✅ CICD complete!")
    return nil
}
```

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| No caching | Slow builds, repeated downloads | Use `CacheVolume` for package managers |
| Not using secrets | Exposed credentials in logs | Pass secrets via `*Secret` type |
| Large base images | Slow pulls, big attack surface | Use slim/alpine variants |
| Sequential when parallel is possible | Slow pipelines | Use `errgroup` for parallel execution |
| Ignoring exit codes | Silent failures | Check errors explicitly |
| Hardcoding versions | Reproducibility issues | Parameterize versions |

## War Story: The 45-Minute Pipeline

A team had a Jenkins pipeline that took 45 minutes. Each step installed dependencies from scratch—no caching. Debugging required pushing commits and waiting.

They migrated to Dagger. With proper caching and parallel test execution, the pipeline dropped to 8 minutes. Better yet, developers could run the same pipeline locally, catching issues before pushing.

**The transformation**:
```go
// Before: Sequential, no cache
npm install  // 5 min every time
npm test     // 10 min
npm build    // 10 min
docker build // 10 min
docker push  // 10 min

// After: Parallel + cached
eg.Go(func() { m.Lint(ctx, source) })       // 2 min (cached deps)
eg.Go(func() { m.Test(ctx, source) })       // 4 min (cached deps)
eg.Go(func() { m.SecurityScan(ctx, source)}) // 2 min (parallel)
m.Build(ctx, source)                         // 2 min (cached layers)
m.Publish(ctx, ...)                          // 1 min
// Total: ~8 min
```

**The lesson**: Caching and parallelism matter. Dagger makes both easy.

## Quiz

### Question 1
What makes Dagger pipelines portable across CI systems?

<details>
<summary>Show Answer</summary>

Dagger pipelines run inside containers managed by the Dagger Engine. The CI system (GitHub Actions, GitLab, Jenkins) only needs to:
1. Install the Dagger CLI
2. Have Docker (or a compatible container runtime)
3. Run `dagger call <function>`

The pipeline logic is in your code, not in CI-specific YAML. The same code runs identically in any environment with Docker, including your laptop.
</details>

### Question 2
How does Dagger caching work?

<details>
<summary>Show Answer</summary>

Dagger caching works at two levels:

1. **Layer caching**: Like Docker, unchanged pipeline steps are cached. If you run the same container operations with the same inputs, Dagger reuses the cached result.

2. **Volume caching**: `CacheVolume` creates persistent volumes that survive across pipeline runs. Use these for package manager caches (npm, pip, go mod).

```go
goCache := dag.CacheVolume("go-mod")
container.WithMountedCache("/go/pkg/mod", goCache)
```

The cache persists locally and on CI (with proper CI cache configuration). Unchanged steps are skipped entirely.
</details>

### Question 3
You need to run lint, test, and security scan in parallel. Write the Go code.

<details>
<summary>Show Answer</summary>

```go
import "golang.org/x/sync/errgroup"

func (m *MyApp) CI(ctx context.Context, source *Directory) error {
    eg, ctx := errgroup.WithContext(ctx)

    eg.Go(func() error {
        _, err := m.Lint(ctx, source)
        if err != nil {
            return fmt.Errorf("lint: %w", err)
        }
        return nil
    })

    eg.Go(func() error {
        _, err := m.Test(ctx, source)
        if err != nil {
            return fmt.Errorf("test: %w", err)
        }
        return nil
    })

    eg.Go(func() error {
        _, err := m.SecurityScan(ctx, source)
        if err != nil {
            return fmt.Errorf("security: %w", err)
        }
        return nil
    })

    return eg.Wait()  // Returns first error if any
}
```

The `errgroup` package runs goroutines concurrently and returns the first error encountered.
</details>

### Question 4
How do you securely pass a registry password to Dagger?

<details>
<summary>Show Answer</summary>

Use the `*Secret` type, which Dagger handles securely (never logged, encrypted in transit):

```go
func (m *MyApp) Publish(
    ctx context.Context,
    source *Directory,
    password *Secret,  // Secret type
) (string, error) {
    return dag.Container().
        From("golang:1.21").
        WithRegistryAuth("ghcr.io", "user", password).
        Publish(ctx, "ghcr.io/org/app:latest")
}
```

Pass secrets via CLI:
```bash
# From environment variable
dagger call publish --password=env:GITHUB_TOKEN

# From file
dagger call publish --password=file:./token.txt
```

Secrets are never exposed in logs or Dagger Cloud traces.
</details>

## Hands-On Exercise

### Scenario: Build a Dagger Pipeline

Create a Dagger pipeline for a Go application with lint, test, build, and publish stages.

### Setup

```bash
# Create project directory
mkdir dagger-lab && cd dagger-lab

# Create a simple Go application
cat > main.go << 'EOF'
package main

import "fmt"

func main() {
    fmt.Println(Greet("World"))
}

func Greet(name string) string {
    return fmt.Sprintf("Hello, %s!", name)
}
EOF

cat > main_test.go << 'EOF'
package main

import "testing"

func TestGreet(t *testing.T) {
    result := Greet("Dagger")
    expected := "Hello, Dagger!"
    if result != expected {
        t.Errorf("got %s, want %s", result, expected)
    }
}
EOF

cat > go.mod << 'EOF'
module dagger-lab

go 1.21
EOF

# Initialize Dagger
dagger init --sdk=go
```

### Write the Pipeline

```go
// Replace main.go in dagger directory with:
// dagger/main.go

package main

import (
    "context"
    "fmt"
)

type DaggerLab struct{}

// Lint runs golangci-lint
func (m *DaggerLab) Lint(ctx context.Context, source *Directory) (string, error) {
    return dag.Container().
        From("golangci/golangci-lint:v1.55").
        WithDirectory("/src", source).
        WithWorkdir("/src").
        WithExec([]string{"golangci-lint", "run", "--timeout", "5m"}).
        Stdout(ctx)
}

// Test runs go test
func (m *DaggerLab) Test(ctx context.Context, source *Directory) (string, error) {
    return dag.Container().
        From("golang:1.21").
        WithDirectory("/src", source).
        WithWorkdir("/src").
        WithExec([]string{"go", "test", "-v", "./..."}).
        Stdout(ctx)
}

// Build compiles the application
func (m *DaggerLab) Build(source *Directory) *Container {
    return dag.Container().
        From("golang:1.21-alpine").
        WithDirectory("/src", source).
        WithWorkdir("/src").
        WithMountedCache("/go/pkg/mod", dag.CacheVolume("go-mod")).
        WithExec([]string{"go", "build", "-o", "app", "."})
}

// BuildImage creates a minimal container image
func (m *DaggerLab) BuildImage(source *Directory) *Container {
    // Build stage
    builder := m.Build(source)

    // Runtime stage (minimal image)
    return dag.Container().
        From("alpine:latest").
        WithFile("/app", builder.File("/src/app")).
        WithEntrypoint([]string{"/app"})
}

// All runs lint, test, and build
func (m *DaggerLab) All(ctx context.Context, source *Directory) error {
    fmt.Println("🔍 Linting...")
    if _, err := m.Lint(ctx, source); err != nil {
        return err
    }

    fmt.Println("🧪 Testing...")
    if _, err := m.Test(ctx, source); err != nil {
        return err
    }

    fmt.Println("🔨 Building...")
    _ = m.Build(source)

    fmt.Println("✅ All checks passed!")
    return nil
}
```

### Run the Pipeline

```bash
# Run individual stages
dagger call lint --source=.
dagger call test --source=.
dagger call build --source=.

# Run all stages
dagger call all --source=.

# Build container image
dagger call build-image --source=.

# Export the image
dagger call build-image --source=. export --path=./image.tar
```

### Add to GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dagger/dagger-for-github@v5
      - run: dagger call all --source=.
```

### Success Criteria

- [ ] Dagger module initialized
- [ ] Lint function works
- [ ] Test function works
- [ ] Build function produces binary
- [ ] All function runs complete pipeline
- [ ] Understand caching with CacheVolume

### Cleanup

```bash
cd .. && rm -rf dagger-lab
```

## Next Module

Continue to [Module 3.2: Tekton](module-3.2-tekton.md) where we'll explore Kubernetes-native pipelines.

---

*"The best CI/CD pipeline is the one you can run on your laptop. Dagger makes every pipeline local-first."*
