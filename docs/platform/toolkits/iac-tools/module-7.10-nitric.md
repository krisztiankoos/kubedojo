# Module 7.10: Nitric - Cloud-Native Application Framework

## Complexity: [MEDIUM]
## Time to Complete: 45-50 minutes

---

## Prerequisites

Before starting this module, you should have completed:
- [Module 7.3: Pulumi](module-7.3-pulumi.md) - Infrastructure with programming languages
- [Module 7.7: Wing](module-7.7-winglang.md) - Unified infrastructure and code
- Programming fundamentals (TypeScript, Python, Go, or Dart)
- Understanding of cloud services (functions, buckets, queues)

---

## Why This Module Matters

**What If You Could Swap Clouds Without Rewriting Code?**

The CTO got the news: their biggest customer required Azure deployment, but everything was built on AWS. The engineering estimate:

- **Rewrite Lambda handlers** → Azure Functions: 3 weeks
- **Replace S3 API calls** → Azure Blob Storage: 2 weeks
- **Convert SQS** → Azure Service Bus: 2 weeks
- **Update DynamoDB** → Cosmos DB: 4 weeks
- **New Terraform** → Bicep: 3 weeks
- **Testing** → 2 weeks

**Total: 16 weeks of engineering time.**

With Nitric, the change would be:

```yaml
# Change deployment target
provider: azure
# Done.
```

**Nitric provides cloud-agnostic APIs.** Write your application once, deploy to AWS, Azure, GCP, or your own infrastructure. The Nitric SDK abstracts cloud services behind consistent interfaces. The Nitric CLI generates the infrastructure for your target platform.

It's not about avoiding vendor lock-in—it's about choosing where to run without rewriting your application.

---

## Did You Know?

- **Nitric was built for multi-cloud from day one** — Unlike tools that add portability later, Nitric's architecture assumes you might deploy anywhere. Every API is designed to work across providers.

- **Infrastructure is derived from code** — Nitric analyzes your application to understand what resources you need, then generates the infrastructure. You don't write separate IaC.

- **Nitric supports TypeScript, Python, Go, and Dart** — Use your preferred language with the same cloud abstractions.

- **The local development server runs your entire app** — `nitric start` runs your application locally with simulated cloud services. No external dependencies needed.

- **Nitric is open source with a commercial cloud offering** — The framework is free, with Nitric Cloud providing managed deployment pipelines and dashboards.

- **Nitric generates Pulumi code** — Under the hood, Nitric produces Pulumi infrastructure. You can eject to pure Pulumi if needed.

---

## Nitric Architecture

```
NITRIC ARCHITECTURE
─────────────────────────────────────────────────────────────────

YOUR APPLICATION CODE
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  import { api, bucket, queue } from "@nitric/sdk";              │
│                                                                  │
│  const photos = bucket("photos").allow("write", "read");        │
│  const uploads = queue("uploads").allow("send", "receive");     │
│  const imageApi = api("images");                                │
│                                                                  │
│  imageApi.post("/upload", async (ctx) => {                      │
│    await photos.write(ctx.req.params.name, ctx.req.body);       │
│    await uploads.send({ name: ctx.req.params.name });           │
│    return ctx.res.json({ success: true });                      │
│  });                                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    NITRIC CLI ANALYSIS
                              │
         "What cloud resources does this app need?"
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  DISCOVERED RESOURCES:                                          │
│  ├── API: images (1 route)                                      │
│  ├── Bucket: photos (read, write permissions)                   │
│  └── Queue: uploads (send, receive permissions)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                    NITRIC PROVIDERS
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  AWS PROVIDER   │   │  AZURE PROVIDER │   │  GCP PROVIDER   │
│                 │   │                 │   │                 │
│  API Gateway    │   │  APIM           │   │  Cloud Run      │
│  Lambda         │   │  Functions      │   │  Cloud Functions│
│  S3             │   │  Blob Storage   │   │  Cloud Storage  │
│  SQS            │   │  Service Bus    │   │  Pub/Sub        │
│                 │   │                 │   │                 │
│  Pulumi code    │   │  Pulumi code    │   │  Pulumi code    │
│  generated      │   │  generated      │   │  generated      │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

### Resource Abstraction

```
NITRIC RESOURCE MAPPING
─────────────────────────────────────────────────────────────────

NITRIC API         AWS               AZURE              GCP
─────────────────────────────────────────────────────────────────
api()              API Gateway       API Management     API Gateway/
                   + Lambda          + Functions        Cloud Run

bucket()           S3                Blob Storage       Cloud Storage

queue()            SQS               Service Bus        Pub/Sub
                                     Queues

topic()            SNS               Service Bus        Pub/Sub
                                     Topics

schedule()         EventBridge       Timer Trigger      Cloud Scheduler
                   + Lambda          + Functions        + Cloud Functions

secret()           Secrets           Key Vault          Secret Manager
                   Manager

websocket()        API Gateway       SignalR            -
                   WebSocket

kv()               DynamoDB          Cosmos DB          Firestore
                   (on-demand)       (serverless)


PERMISSIONS TRANSLATE AUTOMATICALLY:
─────────────────────────────────────────────────────────────────
bucket("photos").allow("write")

AWS:  s3:PutObject on bucket ARN
Azure: Storage Blob Data Contributor role
GCP:   storage.objects.create permission
```

---

## Getting Started with Nitric

### Installation

```bash
# Install Nitric CLI
# macOS/Linux
curl -L https://nitric.io/install | bash

# Or with Homebrew
brew install nitrictech/tap/nitric

# Verify installation
nitric version

# Create new project
nitric new my-app ts-starter
cd my-app

# Install dependencies
npm install
```

### Project Structure

```
my-app/
├── nitric.yaml        # Project configuration
├── services/          # Your application code
│   └── hello.ts       # Service entry point
├── package.json
└── tsconfig.json
```

### Basic API Example

```typescript
// services/hello.ts
import { api } from "@nitric/sdk";

const helloApi = api("main");

helloApi.get("/hello/:name", async (ctx) => {
  const { name } = ctx.req.params;
  ctx.res.body = `Hello ${name}!`;
  return ctx;
});

helloApi.post("/echo", async (ctx) => {
  ctx.res.body = ctx.req.text();
  return ctx;
});
```

```bash
# Run locally
nitric start

# Output:
# API: main - http://localhost:4001
#   GET  /hello/:name
#   POST /echo

# Test
curl http://localhost:4001/hello/world
# Hello world!
```

### Storage and Queues

```typescript
// services/images.ts
import { api, bucket, queue } from "@nitric/sdk";

// Declare resources with permissions
const photos = bucket("photos").allow("read", "write", "delete");
const thumbnailQueue = queue("thumbnail-jobs").allow("send", "receive");
const imageApi = api("images");

// Upload endpoint
imageApi.post("/upload/:name", async (ctx) => {
  const { name } = ctx.req.params;
  const imageData = ctx.req.data;

  // Write to bucket (works on any cloud)
  await photos.file(name).write(imageData);

  // Queue for thumbnail generation
  await thumbnailQueue.send({
    filename: name,
    timestamp: Date.now(),
  });

  return ctx.res.json({
    message: `Uploaded ${name}`,
    queued: true,
  });
});

// Download endpoint
imageApi.get("/download/:name", async (ctx) => {
  const { name } = ctx.req.params;

  try {
    const data = await photos.file(name).read();
    ctx.res.body = data;
    ctx.res.headers["Content-Type"] = "image/jpeg";
  } catch {
    ctx.res.status = 404;
    ctx.res.body = "Not found";
  }

  return ctx;
});

// Background worker for thumbnails
thumbnailQueue.receive(async (ctx) => {
  const { filename } = ctx.req.json();
  console.log(`Processing thumbnail for: ${filename}`);

  // Read original
  const original = await photos.file(filename).read();

  // Generate thumbnail (placeholder - use sharp/imagemagick in real app)
  const thumbnail = await generateThumbnail(original);

  // Write thumbnail
  await photos.file(`thumbnails/${filename}`).write(thumbnail);

  console.log(`Thumbnail created: thumbnails/${filename}`);
});

async function generateThumbnail(data: Uint8Array): Promise<Uint8Array> {
  // Real implementation would use image processing library
  return data;
}
```

### Scheduled Tasks

```typescript
// services/tasks.ts
import { schedule, bucket } from "@nitric/sdk";

const reports = bucket("reports").allow("write");

// Run every hour
schedule("hourly-report").every("1 hour", async (ctx) => {
  const report = generateReport();
  const filename = `report-${Date.now()}.json`;

  await reports.file(filename).write(JSON.stringify(report));

  console.log(`Report generated: ${filename}`);
});

// Run at specific time (cron)
schedule("daily-cleanup").cron("0 2 * * *", async (ctx) => {
  console.log("Running daily cleanup at 2 AM");
  // Cleanup logic here
});
```

---

## Deploying to Multiple Clouds

### Configuration

```yaml
# nitric.yaml
name: my-app
services:
  - match: services/*.ts
    start: npm run dev:services $SERVICE_PATH

# Stack files define deployment targets
```

```yaml
# nitric.aws.yaml (AWS deployment)
provider: nitric/aws@latest
region: us-east-1

config:
  # AWS-specific settings
  lambda:
    memory: 512
    timeout: 30

  # Optional: specify VPC
  vpc:
    id: vpc-12345
    subnets:
      - subnet-abc
      - subnet-def
```

```yaml
# nitric.azure.yaml (Azure deployment)
provider: nitric/azure@latest
region: eastus

config:
  # Azure-specific settings
  functions:
    memory: 512
    timeout: 30

  # Optional: resource group
  resourceGroup: my-app-rg
```

```yaml
# nitric.gcp.yaml (GCP deployment)
provider: nitric/gcp@latest
region: us-central1
project: my-gcp-project

config:
  # GCP-specific settings
  cloudrun:
    memory: 512Mi
    cpu: 1
```

### Deployment Commands

```bash
# Deploy to AWS
nitric up -s aws

# Deploy to Azure
nitric up -s azure

# Deploy to GCP
nitric up -s gcp

# Tear down
nitric down -s aws
```

---

## War Story: Multi-Cloud in Production

*How a healthcare company met compliance requirements with zero code changes*

### The Requirement

A healthcare SaaS company faced a challenge:
- **Existing infrastructure**: AWS (Lambda, S3, DynamoDB)
- **New customer**: Required Azure deployment (compliance)
- **Timeline**: 6 weeks to production
- **Budget**: Very limited engineering time

### Traditional Approach

```
ESTIMATED WORK (WITHOUT NITRIC):
─────────────────────────────────────────────────────────────────

Application Layer:
├── Rewrite Lambda handlers → Azure Functions    3 weeks
│   ├── Different event formats
│   ├── Different context objects
│   └── Different response structures
│
├── Replace AWS SDK → Azure SDK                  2 weeks
│   ├── S3 → Blob Storage (different API)
│   ├── DynamoDB → Cosmos DB (different model)
│   └── SQS → Service Bus (different patterns)
│
└── Testing and validation                       2 weeks

Infrastructure Layer:
├── Write Azure Bicep/ARM templates              2 weeks
├── CI/CD for Azure                              1 week
└── Security review                              1 week

TOTAL: 11 weeks (they had 6)
```

### Nitric Approach

```typescript
// services/patient-records.ts (UNCHANGED for both clouds)
import { api, bucket, kv, topic } from "@nitric/sdk";

// These resources work identically on AWS and Azure
const records = bucket("patient-records").allow("read", "write");
const patientDb = kv("patients").allow("get", "set", "delete");
const auditTopic = topic("audit-events").allow("publish");
const recordsApi = api("records");

recordsApi.post("/patients/:id/records", async (ctx) => {
  const { id } = ctx.req.params;
  const record = ctx.req.json();

  // Write to bucket
  const filename = `${id}/${Date.now()}.json`;
  await records.file(filename).write(JSON.stringify(record));

  // Update patient metadata
  const patient = await patientDb.get(id);
  await patientDb.set(id, {
    ...patient,
    lastRecord: filename,
    updatedAt: Date.now(),
  });

  // Audit trail
  await auditTopic.publish({
    action: "record_created",
    patientId: id,
    filename,
    timestamp: Date.now(),
  });

  return ctx.res.json({ success: true, filename });
});
```

```yaml
# nitric.azure.yaml (New stack file - only new code needed)
provider: nitric/azure@latest
region: westus2

config:
  containerapps:
    memory: 1Gi
    cpu: 0.5

  # Healthcare compliance settings
  storage:
    encryption: customer-managed
    softDelete: true

  cosmos:
    backupPolicy: continuous
```

### Actual Work Done

```
WORK COMPLETED (WITH NITRIC):
─────────────────────────────────────────────────────────────────

Week 1:
├── Created nitric.azure.yaml stack file          1 day
├── Local testing with `nitric start`             2 days
└── Integration tests (same tests, different cloud) 2 days

Week 2:
├── First Azure deployment (nitric up)            1 day
├── Compliance review of generated infrastructure 2 days
└── Minor adjustments to Azure config             2 days

Week 3:
├── Performance testing                           2 days
├── Security audit                                2 days
└── Documentation                                 1 day

Week 4:
├── Customer acceptance testing                   3 days
└── Production deployment                         2 days

TOTAL: 4 weeks (2 weeks ahead of schedule)
```

### Results

| Metric | Traditional | Nitric | Savings |
|--------|-------------|--------|---------|
| Code changes | 15,000 lines | 50 lines | 99.7% |
| Developer weeks | 11 | 4 | 64% |
| Test rewrite | Complete | Zero | 100% |
| Future clouds | 11 weeks each | 1 week each | 91% |

---

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| Cloud-specific code | Breaks portability | Use only Nitric SDK |
| Ignoring permissions | Runtime errors | Declare `.allow()` explicitly |
| Hardcoding config | Different per cloud | Use environment variables |
| Large services | Slow cold starts | Split into focused services |
| Skipping local dev | Slow iteration | Always use `nitric start` |
| Manual infrastructure | Drift from code | Let Nitric generate infra |
| Not checking generated code | Blind deployment | Review Pulumi output |
| Tight cloud coupling | Vendor lock-in | Abstract through Nitric APIs |

---

## Hands-On Exercise

### Task: Build a Multi-Cloud Notes API

**Objective**: Create a notes API that works on any cloud provider.

**Success Criteria**:
1. CRUD operations for notes
2. Local development working
3. Deploy to at least one cloud
4. Verify cloud-agnostic patterns

### Steps

```bash
# 1. Create project
nitric new notes-api ts-starter
cd notes-api
npm install
```

```typescript
// services/notes.ts
import { api, kv, bucket, topic } from "@nitric/sdk";

// Resources - cloud-agnostic
const notes = kv("notes").allow("get", "set", "delete");
const attachments = bucket("attachments").allow("read", "write");
const events = topic("note-events").allow("publish");
const notesApi = api("notes");

// Create note
notesApi.post("/notes", async (ctx) => {
  const { title, content } = ctx.req.json();
  const id = crypto.randomUUID();

  await notes.set(id, {
    id,
    title,
    content,
    createdAt: Date.now(),
    updatedAt: Date.now(),
  });

  await events.publish({
    type: "note.created",
    noteId: id,
    timestamp: Date.now(),
  });

  return ctx.res.json({ id, title });
});

// Get note
notesApi.get("/notes/:id", async (ctx) => {
  const { id } = ctx.req.params;

  try {
    const note = await notes.get(id);
    return ctx.res.json(note);
  } catch {
    ctx.res.status = 404;
    return ctx.res.json({ error: "Note not found" });
  }
});

// Update note
notesApi.put("/notes/:id", async (ctx) => {
  const { id } = ctx.req.params;
  const updates = ctx.req.json();

  const existing = await notes.get(id);
  if (!existing) {
    ctx.res.status = 404;
    return ctx.res.json({ error: "Note not found" });
  }

  const updated = {
    ...existing,
    ...updates,
    updatedAt: Date.now(),
  };

  await notes.set(id, updated);

  await events.publish({
    type: "note.updated",
    noteId: id,
    timestamp: Date.now(),
  });

  return ctx.res.json(updated);
});

// Delete note
notesApi.delete("/notes/:id", async (ctx) => {
  const { id } = ctx.req.params;

  await notes.delete(id);

  await events.publish({
    type: "note.deleted",
    noteId: id,
    timestamp: Date.now(),
  });

  return ctx.res.json({ deleted: true });
});

// Add attachment
notesApi.post("/notes/:id/attachments/:filename", async (ctx) => {
  const { id, filename } = ctx.req.params;
  const data = ctx.req.data;

  const path = `${id}/${filename}`;
  await attachments.file(path).write(data);

  return ctx.res.json({ path });
});

// Get attachment
notesApi.get("/notes/:id/attachments/:filename", async (ctx) => {
  const { id, filename } = ctx.req.params;

  try {
    const data = await attachments.file(`${id}/${filename}`).read();
    ctx.res.body = data;
    return ctx;
  } catch {
    ctx.res.status = 404;
    return ctx.res.json({ error: "Attachment not found" });
  }
});

// Event subscriber
events.subscribe(async (ctx) => {
  const event = ctx.req.json();
  console.log(`Event received: ${event.type} for note ${event.noteId}`);
});
```

```bash
# 2. Run locally
nitric start

# 3. Test the API
# Create note
curl -X POST http://localhost:4001/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "My Note", "content": "Hello Nitric!"}'

# Get note
curl http://localhost:4001/notes/{id}

# Update note
curl -X PUT http://localhost:4001/notes/{id} \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated content"}'

# Delete note
curl -X DELETE http://localhost:4001/notes/{id}

# 4. Create AWS stack
cat > nitric.aws.yaml << 'EOF'
provider: nitric/aws@latest
region: us-east-1
EOF

# 5. Deploy to AWS
nitric up -s aws

# 6. Test deployed API
curl https://xxx.execute-api.us-east-1.amazonaws.com/notes

# 7. Create Azure stack (same code!)
cat > nitric.azure.yaml << 'EOF'
provider: nitric/azure@latest
region: eastus
EOF

# 8. Deploy to Azure
nitric up -s azure

# Same API, different cloud, zero code changes!
```

---

## Quiz

### Question 1
What makes Nitric different from other IaC tools?

<details>
<summary>Show Answer</summary>

**Infrastructure is derived from application code**

- You write application code using Nitric SDK
- Nitric analyzes what resources you use
- Infrastructure is generated automatically
- No separate IaC files to maintain
- Deploy to any cloud from same code
</details>

### Question 2
How does Nitric handle cloud-specific differences?

<details>
<summary>Show Answer</summary>

**Providers translate Nitric APIs to cloud services**

Each provider (AWS, Azure, GCP) maps Nitric resources:
- `bucket()` → S3 / Blob Storage / Cloud Storage
- `queue()` → SQS / Service Bus / Pub/Sub
- `kv()` → DynamoDB / Cosmos DB / Firestore

The Nitric SDK provides a consistent API regardless of target.
</details>

### Question 3
What does `nitric start` do?

<details>
<summary>Show Answer</summary>

**Runs your entire application locally with simulated services**

`nitric start`:
- Starts local API servers
- Simulates buckets, queues, topics, etc.
- Provides a dashboard at localhost:49152
- Enables hot reload on code changes
- No cloud credentials needed
</details>

### Question 4
What infrastructure format does Nitric generate?

<details>
<summary>Show Answer</summary>

**Pulumi**

Nitric generates Pulumi code for deployment:
- You can inspect the generated code
- You can eject to pure Pulumi if needed
- Pulumi handles state management
- Supports all Pulumi backends
</details>

### Question 5
When should you NOT use Nitric?

<details>
<summary>Show Answer</summary>

**When you need cloud-specific features or fine-grained control**

Nitric excels at:
- Portable serverless apps
- Multi-cloud requirements
- Rapid development

Consider alternatives when:
- You need specific AWS/Azure/GCP features not in Nitric
- You need precise infrastructure control
- You're building non-serverless workloads
- You need Kubernetes-native deployment
</details>

---

## Key Takeaways

1. **Cloud-agnostic APIs** — Write once, deploy anywhere
2. **Infrastructure derived** — No separate IaC to maintain
3. **Local development** — Full simulation without cloud
4. **Permissions declared** — `.allow()` handles IAM
5. **Multiple languages** — TypeScript, Python, Go, Dart
6. **Pulumi under the hood** — Proven deployment engine
7. **Focus on application** — Not cloud plumbing
8. **Multi-cloud ready** — Change stack file, not code
9. **Open source** — Framework is free
10. **Reduce lock-in** — Freedom to choose cloud

---

## Next Steps

- **Complete**: [IaC Tools Toolkit](./README.md) ✓
- **Related**: [Module 7.7: Wing](module-7.7-winglang.md) — Similar philosophy
- **Related**: [Module 7.8: SST](module-7.8-sst.md) — AWS serverless comparison

---

## Further Reading

- [Nitric Documentation](https://nitric.io/docs)
- [Nitric GitHub](https://github.com/nitrictech/nitric)
- [Nitric Examples](https://github.com/nitrictech/examples)
- [Nitric Discord](https://discord.gg/nitric)
- [Nitric vs Serverless Framework](https://nitric.io/docs/guides/comparison/serverless-framework)

---

*"Nitric asks: Why should changing clouds mean rewriting your application? The answer is that it shouldn't—and with cloud-agnostic APIs, it doesn't have to."*
