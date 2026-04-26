---
revision_pending: true
title: "Module 15.3: Neon & PlanetScale - Serverless Databases That Branch Like Git"
slug: platform/toolkits/data-ai-platforms/cloud-native-databases/module-15.3-serverless-databases
sidebar:
  order: 4
---
## Complexity: [MEDIUM]
## Time to Complete: 40-45 minutes

---

## Prerequisites

Before starting this module, you should have completed:
- [Module 15.1: CockroachDB](../module-15.1-cockroachdb/) - Distributed database concepts
- [Module 15.2: CloudNativePG](../module-15.2-cloudnativepg/) - PostgreSQL fundamentals
- Basic Git workflow (branches, merges)
- Understanding of development environments and CI/CD

---

## What You'll Be Able to Do

After completing this module, you will be able to:

- **Deploy serverless database solutions (Neon, PlanetScale, CockroachDB Serverless) for Kubernetes applications**
- **Configure connection pooling and autoscaling database access patterns for serverless workloads**
- **Implement database branching workflows for development and testing with instant schema cloning**
- **Evaluate serverless database pricing models and latency trade-offs for different application patterns**


## Why This Module Matters

**"Can I Get a Copy of Production?"**

The incident post-mortem was brutal. A Series C e-commerce company had deployed a schema migration that looked perfect in staging. A schema change that looks fine on a small staging dataset can behave very differently on production-sized data, including taking much longer and causing disruptive locking.

A failed migration during peak traffic can create serious business impact and a painful incident for the team handling it.

"Why didn't we test on production-sized data?" the CTO demanded.

The database lead explained the economics: Production was 500GB. Creating a copy meant:
1. **Dump and restore**: can take hours and add meaningful storage and transfer cost per copy
2. **Anonymized subset**: can require substantial engineering time to build and maintain
3. **Just test on staging**: a much smaller staging dataset can hide problems that only appear at production scale

Then the VP of Engineering shared a link to Neon: "What if we could branch the database like Git?"

With database branching, teams can test schema changes against production-like data earlier and catch migration problems before they reach production.

**Serverless databases with branching aren't just convenient—they fundamentally change how teams develop.** Preview environments get real data. Schema migrations get tested at scale. Developers stop guessing and start knowing.

---

## Did You Know?

- **Neon positions branching as a way to avoid paying for multiple full development copies of a production database** — copy-on-write branching can reduce development and test costs because teams store changes instead of cloning an entire database for every environment.

- **PlanetScale and Vitess are used for very high-scale MySQL workloads** — teams adopt them when they need database branching, safer schema changes, and horizontal sharding beyond a single MySQL instance.

- **Point-in-time recovery and branching can reduce recovery time after operator mistakes** — when supported by the platform, teams can restore to an earlier state or bring up a recovery branch much faster than a traditional backup restore.

- **Neon integrates well with preview-style deployment workflows** — serverless Postgres plus branch-based environments can be a good fit for rapid iteration and ephemeral environments.

---

## The Serverless Database Model

```
TRADITIONAL VS SERVERLESS DATABASE
─────────────────────────────────────────────────────────────────

TRADITIONAL (RDS, CloudNativePG, etc.)
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│                    Always Running                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Database Instance                     │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐      │   │
│  │  │   Compute  │  │   Memory   │  │   Storage  │      │   │
│  │  │ (4 vCPUs)  │  │  (16 GB)   │  │  (500 GB)  │      │   │
│  │  └────────────┘  └────────────┘  └────────────┘      │   │
│  │                                                       │   │
│  │  Cost: $500/month (even at 3 AM with 0 queries)      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘

SERVERLESS (Neon, PlanetScale)
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│                    Scales to Demand                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                         │ │
│  │   Compute (scales 0 to N)      Storage (persistent)    │ │
│  │   ┌───────────────────┐        ┌───────────────────┐   │ │
│  │   │                   │        │                   │   │ │
│  │   │  ░░░░████████░░░░ │        │  ████████████████ │   │ │
│  │   │  ░░░░░░████░░░░░░ │        │  (always there)   │   │ │
│  │   │  ░░░░░░░░░░░░░░░░ │        │                   │   │ │
│  │   │  (scales to zero) │        │  500 GB × $0.25   │   │ │
│  │   └───────────────────┘        └───────────────────┘   │ │
│  │                                                         │ │
│  │   Cost: $0/hour idle + $125/month storage              │ │
│  │         + compute usage (bursty)                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Database Branching

```
DATABASE BRANCHING (NEON)
─────────────────────────────────────────────────────────────────

                    main (production)
                    ████████████████████████████████ 500GB
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    feature/auth      staging           feature/perf
    ░░░░░░░░░░        ░░░░░░░░░░        ░░░░░░░░░░
    +5MB changes      +50MB changes     +2MB changes

    Each branch:
    • Instant creation (copy-on-write)
    • Full data access (reads from main's storage)
    • Isolated writes (changes stored separately)
    • Independent compute (own connection string)
    • Pay only for changes (not full copy)

WORKFLOW EXAMPLE
─────────────────────────────────────────────────────────────────

Day 1: Developer starts feature
┌─────────────────────────────────────────────────────────────┐
│ $ neon branch create feature/new-schema --parent main      │
│ Branch 'feature/new-schema' created                         │
│ Connection: postgres://user@feature-new-schema.neon.tech   │
│                                                             │
│ # Test migration on real data                               │
│ $ psql $BRANCH_URL -f migration.sql                        │
│ ALTER TABLE... OK (tested against 500GB)                   │
└─────────────────────────────────────────────────────────────┘

Day 3: PR deployed to preview environment
┌─────────────────────────────────────────────────────────────┐
│ Vercel preview: https://myapp-git-feature-new-schema.vercel│
│ Connected to: feature/new-schema branch                     │
│                                                             │
│ QA tests against real data volumes                         │
│ No separate test data needed                               │
└─────────────────────────────────────────────────────────────┘

Day 5: Merge to main
┌─────────────────────────────────────────────────────────────┐
│ $ neon branch delete feature/new-schema                    │
│ Branch deleted. Storage reclaimed.                         │
│                                                             │
│ # Migration runs on production (already tested!)           │
└─────────────────────────────────────────────────────────────┘
```

---

## Neon: Serverless PostgreSQL

### Getting Started

```bash
# Install Neon CLI
brew install neonctl
# or
npm install -g neonctl

# Login
neonctl auth

# Create a project
neonctl projects create --name my-app

# Get connection string
neonctl connection-string --project-id <project-id>
# postgres://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb
```

### Creating and Managing Branches

```bash
# List branches
neonctl branches list --project-id my-app

# Create a branch from main
neonctl branches create \
  --project-id my-app \
  --name feature/user-auth \
  --parent main

# Create a branch from a specific point in time
neonctl branches create \
  --project-id my-app \
  --name recovery/pre-incident \
  --parent main \
  --at "2024-01-15T14:30:00Z"

# Get branch connection string
neonctl connection-string \
  --project-id my-app \
  --branch feature/user-auth

# Delete a branch
neonctl branches delete \
  --project-id my-app \
  --name feature/user-auth
```

### Neon with CI/CD

```yaml
# .github/workflows/preview.yml
name: Preview Environment

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  deploy-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create Neon branch
        id: neon
        uses: neondatabase/create-branch-action@v4
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          branch_name: preview/pr-${{ github.event.number }}
          api_key: ${{ secrets.NEON_API_KEY }}

      - name: Run migrations
        run: |
          psql "${{ steps.neon.outputs.db_url }}" -f migrations/*.sql

      - name: Deploy preview
        run: |
          vercel deploy --env DATABASE_URL="${{ steps.neon.outputs.db_url }}"

  cleanup:
    runs-on: ubuntu-latest
    if: github.event.action == 'closed'
    steps:
      - name: Delete Neon branch
        uses: neondatabase/delete-branch-action@v3
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          branch: preview/pr-${{ github.event.number }}
          api_key: ${{ secrets.NEON_API_KEY }}
```

### [Neon Architecture](https://github.com/neondatabase/neon)

```
NEON ARCHITECTURE
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│                        Your Application                          │
│                              │                                   │
│                              │ postgres://                       │
│                              ▼                                   │
├─────────────────────────────────────────────────────────────────┤
│                     Neon Proxy (Authn/Routing)                  │
│                              │                                   │
│           ┌──────────────────┼──────────────────┐               │
│           │                  │                  │               │
│           ▼                  ▼                  ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Compute   │    │   Compute   │    │   Compute   │         │
│  │   (main)    │    │ (staging)   │    │ (feature/x) │         │
│  │             │    │             │    │             │         │
│  │ PostgreSQL  │    │ PostgreSQL  │    │ PostgreSQL  │         │
│  │  process    │    │  process    │    │  process    │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     Pageserver                           │   │
│  │  ┌─────────────────────────────────────────────────────┐│   │
│  │  │              Shared Storage Layer                    ││   │
│  │  │                                                      ││   │
│  │  │  main: ████████████████████████████████████████     ││   │
│  │  │  staging: ░░░░░ (copy-on-write from main)           ││   │
│  │  │  feature/x: ░░░ (copy-on-write from main)           ││   │
│  │  │                                                      ││   │
│  │  └─────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Object Storage (S3)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

Key Innovation: Separated compute from storage
• Compute scales independently (even to zero)
• Storage shared between branches (copy-on-write)
• Instant branching regardless of data size
```

---

## PlanetScale: Serverless MySQL with [Vitess](https://github.com/vitessio/vitess)

### Getting Started

```bash
# Install PlanetScale CLI
brew install planetscale/tap/pscale

# Login
pscale auth login

# Create a database
pscale database create my-app --region us-east

# Create a branch
pscale branch create my-app feature/new-schema

# Connect to branch (opens proxy)
pscale connect my-app feature/new-schema --port 3306

# In another terminal:
mysql -h 127.0.0.1 -P 3306 -u root
```

### [Deploy Requests (Schema Changes)](https://github.com/planetscale/cli)

```bash
# Create a deploy request (like a PR for your schema)
pscale deploy-request create my-app feature/new-schema

# View the diff
pscale deploy-request diff my-app 1

# Deploy to production (non-blocking)
pscale deploy-request deploy my-app 1

# View deployment status
pscale deploy-request show my-app 1
```

### PlanetScale Workflow

```
PLANETSCALE DEPLOY REQUESTS
─────────────────────────────────────────────────────────────────

Traditional Schema Migration:
─────────────────────────────────────────────────────────────────
1. ALTER TABLE users ADD COLUMN email VARCHAR(255)
2. Table locked for duration of migration
3. Queries queue up, application slows/errors
4. If migration fails, manual rollback needed
5. 😰 Sweating during deployment

PlanetScale Deploy Request:
─────────────────────────────────────────────────────────────────

Step 1: Create branch and make changes
┌─────────────────────────────────────────────────────────────┐
│ $ pscale branch create my-app add-email-column             │
│ $ pscale connect my-app add-email-column                   │
│                                                             │
│ mysql> ALTER TABLE users ADD COLUMN email VARCHAR(255);    │
│ Query OK (on branch only, production untouched)            │
└─────────────────────────────────────────────────────────────┘

Step 2: Create deploy request
┌─────────────────────────────────────────────────────────────┐
│ $ pscale deploy-request create my-app add-email-column     │
│                                                             │
│ Deploy Request #42 created                                  │
│                                                             │
│ Schema Diff:                                                │
│ + ALTER TABLE `users` ADD COLUMN `email` varchar(255)      │
│                                                             │
│ Analysis:                                                   │
│ ✓ Non-blocking (online DDL)                                │
│ ✓ No data loss                                              │
│ ✓ Backward compatible                                       │
└─────────────────────────────────────────────────────────────┘

Step 3: Review and deploy
┌─────────────────────────────────────────────────────────────┐
│ Teammate reviews deploy request in web UI                   │
│                                                             │
│ $ pscale deploy-request deploy my-app 42                   │
│                                                             │
│ Deploying... ████████████████████░░░░ 80%                  │
│ • Ghost table created                                       │
│ • Data copying (non-blocking)                               │
│ • Cutover (instant)                                         │
│ ✓ Deployment complete                                       │
│                                                             │
│ Zero downtime. No locks. Application unaware.              │
└─────────────────────────────────────────────────────────────┘
```

### PlanetScale Architecture

```
PLANETSCALE ARCHITECTURE (BUILT ON VITESS)
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│                        Your Application                          │
│                              │                                   │
│                              │ mysql://                          │
│                              ▼                                   │
├─────────────────────────────────────────────────────────────────┤
│                       PlanetScale Proxy                         │
│              (Connection pooling, authentication)               │
│                              │                                   │
│                              ▼                                   │
├─────────────────────────────────────────────────────────────────┤
│                         VTGate                                   │
│              (Query routing, planning, aggregation)             │
│                              │                                   │
│           ┌──────────────────┼──────────────────┐               │
│           │                  │                  │               │
│           ▼                  ▼                  ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  VTTablet   │    │  VTTablet   │    │  VTTablet   │         │
│  │  (shard 1)  │    │  (shard 2)  │    │  (shard 3)  │         │
│  │             │    │             │    │             │         │
│  │   MySQL     │    │   MySQL     │    │   MySQL     │         │
│  │  primary +  │    │  primary +  │    │  primary +  │         │
│  │  replicas   │    │  replicas   │    │  replicas   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
│  Sharding is automatic and transparent to application          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Neon vs PlanetScale Comparison

```
SERVERLESS DATABASE COMPARISON
─────────────────────────────────────────────────────────────────

                         Neon            PlanetScale
─────────────────────────────────────────────────────────────────
DATABASE ENGINE
Engine               PostgreSQL       MySQL (Vitess)
Wire protocol        PostgreSQL       MySQL
Extensions           ✓ (most)         ✗ (MySQL plugins)
Stored procedures    ✓                ✓

SERVERLESS FEATURES
Scale to zero        ✓✓               Plan-dependent / verify current docs
Auto-scaling         ✓                ✓
Branching            ✓✓ (instant)     ✓ (branches)
Point-in-time        ✓ (7-30 days)    ✓ (depends on plan)

DEVELOPER EXPERIENCE
Deploy requests      ✗                ✓✓ (schema review)
Schema diff          Manual           ✓✓ (built-in)
CLI                  ✓                ✓✓
Web console          ✓                ✓✓
GitHub integration   ✓                ✓✓

PERFORMANCE
Connection pooling   ✓ (built-in)     ✓ (built-in)
Read replicas        ✓                ✓
Global regions       Limited          ✓✓
Sharding             ✗                ✓✓ (Vitess)

PRICING (Hobby/Free)
Free tier            Check current plans      Paid plans only for PlanetScale
Compute pricing      Usage-based        Usage-based (check current pricing)
Storage pricing      Per GB           Per GB

BEST FOR:
─────────────────────────────────────────────────────────────────
Neon:        PostgreSQL apps, Vercel/Next.js, instant branching
PlanetScale: MySQL apps, high-scale, schema management workflow
```

---

## War Story: Preview Environments That Actually Work

*How a SaaS company transformed their development workflow*

### The Problem

A B2B SaaS company had a familiar problem:
- Production database: production-sized relational dataset
- Staging: stale, trimmed copy
- Local dev: small seed dataset
- PR previews: mocked or simplified database setup

Bugs kept slipping through because the environments didn't match production. Queries that looked fine on small datasets behaved very differently against production-shaped data, and data mismatches surfaced UI bugs late.

### The Before

```
DEVELOPMENT ENVIRONMENT DRIFT
─────────────────────────────────────────────────────────────────

Production (200GB):
┌─────────────────────────────────────────────────────────────┐
│ users: 2,000,000 │ orders: 50,000,000 │ products: 500,000  │
│ Complex relationships, realistic distributions              │
└─────────────────────────────────────────────────────────────┘
         │
         │ Monthly copy, trimmed
         ▼
Staging (50GB):
┌─────────────────────────────────────────────────────────────┐
│ users: 500,000 │ orders: 10,000,000 │ products: 100,000    │
│ 3 months stale, some data inconsistencies from trimming    │
└─────────────────────────────────────────────────────────────┘
         │
         │ Manually maintained
         ▼
Dev seed (1GB):
┌─────────────────────────────────────────────────────────────┐
│ users: 10,000 │ orders: 100,000 │ products: 1,000          │
│ Hand-crafted, doesn't match real usage patterns            │
└─────────────────────────────────────────────────────────────┘
         │
         │ Mocked for PRs
         ▼
PR Preview (SQLite):
┌─────────────────────────────────────────────────────────────┐
│ users: 100 │ orders: 500 │ products: 50                    │
│ Different database engine, fake data                        │
└─────────────────────────────────────────────────────────────┘

Result: Bugs discovered in production 😱
```

### The After (with Neon)

```
NEON BRANCHING WORKFLOW
─────────────────────────────────────────────────────────────────

Production (main branch):
┌─────────────────────────────────────────────────────────────┐
│ users: 2,000,000 │ orders: 50,000,000 │ products: 500,000  │
│ 200GB of real data                                          │
└─────────────────────────────────────────────────────────────┘
    │              │                │
    │ instant      │ instant        │ instant
    │ branch       │ branch         │ branch
    ▼              ▼                ▼
┌─────────┐   ┌─────────┐     ┌─────────┐
│ staging │   │  PR #42 │     │  PR #43 │
│         │   │         │     │         │
│ 200GB*  │   │ 200GB*  │     │ 200GB*  │
│ +10MB   │   │ +50KB   │     │ +2MB    │
│ changes │   │ changes │     │ changes │
└─────────┘   └─────────┘     └─────────┘

* Copy-on-write: Full data available, only changes stored

Cost comparison (monthly):
─────────────────────────────────────────────────────────────────
Before (copying data):
• Staging RDS: $400/month
• 5 dev environments: $1,000/month
• PR previews: $0 (mocked, but caused bugs)
• Bug fixes from escaped bugs: ~$5,000/month
• Total: ~$6,400/month

After (Neon branching):
• Main branch: $200/month (production)
• Staging + dev + PRs: $50/month (only changes stored)
• Bug fixes: ~$500/month (caught earlier)
• Total: ~$750/month

Savings: ~$5,650/month + developer productivity
```

### CI/CD Integration

```yaml
# Automatic branch creation for each PR
name: Preview Environment
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  create-preview:
    runs-on: ubuntu-latest
    steps:
      - name: Create Neon Branch
        id: create-branch
        uses: neondatabase/create-branch-action@v4
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          branch_name: preview/pr-${{ github.event.number }}
          api_key: ${{ secrets.NEON_API_KEY }}

      - name: Run Migrations
        run: |
          DATABASE_URL="${{ steps.create-branch.outputs.db_url }}"
          npx prisma migrate deploy

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-args: >
            --env DATABASE_URL=${{ steps.create-branch.outputs.db_url }}
```

### Results

| Metric | Before | After |
|--------|--------|-------|
| PR preview data | Mocked | Production-like data |
| Time to create env | Hours or manual setup | Faster branch-based setup |
| Bugs found in staging | Fewer | More |
| Production incidents | More frequent | Less frequent |
| Developer satisfaction | 😐 | 😊 |

**Financial Impact (Annual):**

| Category | Before | After | Savings |
|----------|--------|-------|---------|
| Database infrastructure | Higher | Lower | Meaningful savings |
| Production incidents | Higher impact | Lower impact | Reduced incident cost |
| Developer time finding bugs | Higher | Lower | Time savings |
| Environment setup time | Higher | Lower | Time savings |
| **Total Annual Savings** | | | **Meaningful savings** |

The engineering manager summarized it: "Using branch-based preview databases reduced avoidable environment and defect costs, and the team trusted test results more."

---

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| Not deleting branches | Storage costs accumulate | Delete branches when PRs merge |
| Using branches for backups | Not designed for it | Use native backup features |
| Hardcoding connection strings | Breaks branching workflow | Use environment variables |
| Long-running transactions | Block scale-to-zero | Keep transactions short |
| Ignoring cold starts | First query can be slow | Use connection pooling, keep-alive |
| Treating like traditional DB | Missing the benefits | Embrace branching workflow |
| Not testing migrations on branch | Same mistake that causes incidents | Test schema changes on branch against representative production-like data |
| Skipping deploy request review | Schema changes bypass team review | Require approval for production deploys (PlanetScale) |

---

## Hands-On Exercise

### Task: Set Up Database Branching Workflow

**Objective**: Create a Neon project, implement branching for development, and simulate a PR workflow.

**Success Criteria**:
1. Neon project created with main branch
2. Feature branch created with schema change
3. Branch merged back (simulated)
4. Preview workflow demonstrated

### Steps

```bash
# 1. Install and authenticate with Neon CLI
npm install -g neonctl
neonctl auth

# 2. Create a project
neonctl projects create --name branching-demo
# Note the project ID from output

# 3. Get connection string for main branch
neonctl connection-string --project-id <project-id>

# 4. Connect and create sample schema
psql "<connection-string>" << 'EOF'
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com');

SELECT * FROM users;
EOF

# 5. Create a feature branch
neonctl branches create \
  --project-id <project-id> \
  --name feature/add-phone \
  --parent main

# 6. Get connection string for feature branch
FEATURE_URL=$(neonctl connection-string --project-id <project-id> --branch feature/add-phone)

# 7. Make schema changes on feature branch
psql "$FEATURE_URL" << 'EOF'
-- Add phone column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Update some records
UPDATE users SET phone = '+1-555-0101' WHERE name = 'Alice';
UPDATE users SET phone = '+1-555-0102' WHERE name = 'Bob';

-- Verify changes
SELECT * FROM users;
EOF

# 8. Verify main branch is unchanged
MAIN_URL=$(neonctl connection-string --project-id <project-id>)
psql "$MAIN_URL" -c "SELECT * FROM users;"
# Should NOT have phone column

# 9. List branches
neonctl branches list --project-id <project-id>

# 10. Simulate PR merge (delete feature branch, run migration on main)
# In real workflow, migration would be applied via CD pipeline

# Apply migration to main
psql "$MAIN_URL" << 'EOF'
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
SELECT * FROM users;
EOF

# Delete feature branch
neonctl branches delete \
  --project-id <project-id> \
  --name feature/add-phone

# 11. Verify final state
neonctl branches list --project-id <project-id>
psql "$MAIN_URL" -c "\d users"

# Clean up (optional - delete project)
# neonctl projects delete --project-id <project-id>
```

### Verification

```bash
# Verify:
# ✓ Project created
# ✓ Feature branch created instantly
# ✓ Changes on feature branch didn't affect main
# ✓ Migration applied to main
# ✓ Feature branch deleted
```

---

## Quiz

### Question 1
How does Neon achieve instant database branching?

<details>
<summary>Show Answer</summary>

**Copy-on-write storage architecture**

Neon separates compute from storage. When you create a branch, it shares the same underlying storage as the parent (read-only). Only new writes go to branch-specific storage. This means a 500GB database branches in seconds, and you only pay for the changes.
</details>

### Question 2
What is a PlanetScale "deploy request"?

<details>
<summary>Show Answer</summary>

**A pull request for database schema changes**

Deploy requests let you:
1. Make schema changes on a branch
2. Create a request to merge those changes to production
3. Review the schema diff
4. Deploy with non-blocking DDL (no table locks)

It brings code review workflow to database changes.
</details>

### Question 3
Why is "scale to zero" important for development databases?

<details>
<summary>Show Answer</summary>

**Cost savings when databases aren't being used**

Development, staging, and preview environments are often idle. Traditional databases charge 24/7 regardless of usage. Serverless databases only charge when actively processing queries, making it economical to have many environments (one per PR, developer, etc.).
</details>

### Question 4
What technology powers PlanetScale's sharding capabilities?

<details>
<summary>Show Answer</summary>

**Vitess**

PlanetScale is built on Vitess, the database clustering system created at YouTube to scale MySQL. Vitess provides:
- Automatic sharding
- Query routing
- Connection pooling
- Online schema changes

PlanetScale makes Vitess accessible as a managed service.
</details>

### Question 5
How does Neon's branching help with testing database migrations?

<details>
<summary>Show Answer</summary>

**You can test migrations against production-scale data without affecting production**

Create a branch from production, run the migration, observe:
- How long it takes (realistic data volume)
- Whether it causes locks (realistic query patterns)
- If it breaks any queries (realistic relationships)

If something goes wrong, delete the branch. Production is untouched.
</details>

### Question 6
What happens to cold start latency when a serverless database scales from zero?

<details>
<summary>Show Answer</summary>

**First query may take longer (100ms-1s) while compute spins up**

When a database has been idle and scales to zero, the next query needs to:
1. Wake up compute
2. Load metadata
3. Establish connections

Mitigations:
- Connection pooling (keeps connections warm)
- Keep-alive queries from application
- Provisioned capacity for latency-sensitive workloads
</details>

### Question 7
When would you choose PlanetScale over Neon?

<details>
<summary>Show Answer</summary>

**When you need MySQL, horizontal sharding, or structured schema change workflow**

Choose PlanetScale if:
- Your application uses MySQL
- You need to scale beyond single-node (Vitess sharding)
- You want deploy requests for schema governance
- You need global read replicas

Choose Neon if:
- Your application uses PostgreSQL
- Instant branching is critical
- You use PostgreSQL extensions
- You're in the Vercel ecosystem
</details>

### Question 8
How do serverless databases handle connection pooling differently?

<details>
<summary>Show Answer</summary>

**Built-in connection pooling at the proxy layer**

Traditional databases: Your app needs PgBouncer/ProxySQL because each connection uses server memory.

Serverless databases: The proxy layer handles pooling automatically. Thousands of serverless function instances can share a pool of actual database connections. Neon and PlanetScale both include this, solving the "serverless function + database" connection problem.
</details>

---

## Key Takeaways

1. **Instant branching** — Create database copies in seconds, not hours
2. **Copy-on-write** — Pay only for changes, not full copies
3. **Scale to zero** — No charges when idle
4. **Preview environments** — Every PR gets a database with real data
5. **Deploy requests** — PR workflow for schema changes (PlanetScale)
6. **Built-in pooling** — Solves serverless connection problem
7. **PostgreSQL (Neon)** — Full compatibility, extensions support
8. **MySQL (PlanetScale)** — Vitess-powered horizontal scaling
9. **Developer productivity** — Test migrations before production
10. **Cost efficiency** — Many environments without multiplied costs

---

## Next Steps

- **Next Module**: [Module 15.4: Vitess](../module-15.4-vitess/) — Self-hosted MySQL sharding at scale
- **Related**: [Developer Experience Toolkit](/platform/toolkits/developer-experience/devex-tools/) — Preview environments
- **Related**: [GitOps & Deployments](/platform/toolkits/cicd-delivery/gitops-deployments/) — Database GitOps workflows

---

## Further Reading

- [Neon Documentation](https://neon.tech/docs)
- [PlanetScale Documentation](https://docs.planetscale.com/)
- [Neon Architecture](https://neon.tech/docs/introduction/architecture-overview)
- [PlanetScale Deploy Requests](https://docs.planetscale.com/concepts/deploy-requests)
- [Vitess Overview](https://vitess.io/docs/)

---

*"The best database for development is one that mirrors production exactly. Serverless branching makes that economically possible for the first time."*

## Sources

- [github.com: neon](https://github.com/neondatabase/neon) — The Neon upstream repository explicitly describes Neon as serverless Postgres with separated storage and compute.
- [github.com: cli](https://github.com/planetscale/cli) — The official CLI repository explicitly states that `pscale` brings branches and deploy requests to the command line.
- [github.com: vitess](https://github.com/vitessio/vitess) — The upstream Vitess repository directly describes Vitess as a MySQL horizontal-scaling system with sharding.
- [Neon CLI](https://github.com/neondatabase/neonctl) — Shows the supported CLI workflow for projects, branches, auth, and connection strings.
