# Module 7.9: System Initiative - DevOps Automation Reimagined

## Complexity: [COMPLEX]
## Time to Complete: 50-55 minutes

---

## Prerequisites

Before starting this module, you should have completed:
- [Module 7.1: Terraform](module-7.1-terraform.md) - Traditional IaC concepts
- [Platform Engineering Discipline](../../disciplines/platform-engineering/) - IDP principles
- Understanding of reactive programming concepts
- Experience with DevOps tooling and workflows

---

## Why This Module Matters

**What If Your Infrastructure Understood Itself?**

The engineer stared at the Terraform output:

```
Error: creating EC2 Instance: insufficient capacity in availability zone
```

She knew the fix: change the AZ. But Terraform didn't know that. It just failed. She had to:

1. Read the error
2. Research the cause
3. Edit the configuration
4. Run `terraform apply` again
5. Wait 5 minutes
6. Hope it works this time

**What if the system knew?**

What if, when AWS reported insufficient capacity, the infrastructure automatically tried another AZ? What if security groups updated when new services were added? What if the system showed you a live diagram of your infrastructure that updated in real-time?

**System Initiative is that vision.**

Built by Adam Jacob (Chef co-founder) and the team behind some of DevOps' most influential tools, System Initiative reimagines infrastructure automation from the ground up. It's not another Terraform wrapper—it's a fundamentally different approach where infrastructure is reactive, collaborative, and visual.

---

## Did You Know?

- **Adam Jacob co-founded Chef and now leads System Initiative** — After years of seeing the limits of configuration management and IaC, he started over with a clean slate.

- **System Initiative models infrastructure as a reactive graph** — Changes propagate through the system like a spreadsheet. Change a VPC CIDR? All dependent resources update automatically.

- **The UI is the source of truth** — Unlike other tools where the UI is optional, System Initiative's visual canvas is how you work. But it's all code underneath.

- **Functions are the building blocks** — Everything in System Initiative is a function. Create an EC2 instance? Function. Validate a security group? Function. Custom logic? Write a function.

- **Collaboration is built-in** — Multiple engineers can work on the same canvas simultaneously, seeing each other's changes in real-time like Google Docs.

- **System Initiative is open source** — After years of development, it launched as an open-source project in 2024 with a commercial cloud offering.

---

## System Initiative Architecture

```
SYSTEM INITIATIVE ARCHITECTURE
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│                    VISUAL CANVAS                                 │
│                                                                  │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐               │
│  │   VPC    │────▶│  Subnet  │────▶│   EC2    │               │
│  │ 10.0.0.0 │     │ .1.0/24  │     │ Instance │               │
│  └──────────┘     └──────────┘     └──────────┘               │
│       │                                  │                      │
│       │           ┌──────────┐          │                      │
│       └──────────▶│  Security│◀─────────┘                      │
│                   │   Group  │                                  │
│                   └──────────┘                                  │
│                                                                  │
│  COLLABORATIVE: Multiple users editing simultaneously           │
└────────────────────────────────────────────────────────────────┘
                              │
                    REACTIVE ENGINE
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  CHANGE SETS                 QUALIFICATION                      │
│  ┌──────────────────┐       ┌──────────────────┐               │
│  │ Proposed changes │       │ Validation funcs │               │
│  │ before apply     │       │ run automatically│               │
│  │                  │       │                  │               │
│  │ Preview impact   │       │ ✓ CIDR valid    │               │
│  │ Track history    │       │ ✓ Ports allowed │               │
│  │ Approve/reject   │       │ ✗ Name missing  │               │
│  └──────────────────┘       └──────────────────┘               │
│                                                                  │
│  FUNCTIONS (TypeScript)                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • create()     - Provision resource                       │  │
│  │ • delete()     - Destroy resource                         │  │
│  │ • qualify()    - Validate configuration                   │  │
│  │ • codeGen()    - Generate code/docs                       │  │
│  │ • refresh()    - Sync with reality                        │  │
│  │ • action()     - Custom operations                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    CLOUD PROVIDERS
┌─────────────────────────────────────────────────────────────────┐
│  AWS  │  GCP  │  Azure  │  Kubernetes  │  Custom               │
└─────────────────────────────────────────────────────────────────┘
```

### Reactive Model

```
REACTIVE INFRASTRUCTURE MODEL
─────────────────────────────────────────────────────────────────

TRADITIONAL (TERRAFORM):
─────────────────────────────────────────────────────────────────
You change VPC CIDR → You must update:
├── All subnet CIDRs manually
├── All security group references manually
├── All route table entries manually
├── All NAT gateway references manually
└── terraform plan → apply → wait

SYSTEM INITIATIVE:
─────────────────────────────────────────────────────────────────
You change VPC CIDR → System updates:
├── Subnet CIDRs (function recalculates)
├── Security groups (references resolved)
├── Route tables (dependencies traced)
├── NAT gateways (connections followed)
└── All changes shown in change set → apply

SPREADSHEET ANALOGY:
─────────────────────────────────────────────────────────────────
Traditional IaC is like updating cells manually
System Initiative is like Excel formulas

       A        B        C        D
    ┌────────┬────────┬────────┬────────┐
  1 │ VPC    │ =A1/4  │ =A1/4  │ =A1/4  │
    │ CIDR   │ subnet1│ subnet2│ subnet3│
    ├────────┼────────┼────────┼────────┤
  2 │10.0.0.0│10.0.0.0│10.0.64.│10.0.128│
    │  /16   │  /18   │  /18   │   /18  │
    └────────┴────────┴────────┴────────┘

Change A2 → B2, C2, D2 update automatically
```

---

## Getting Started

### Installation

```bash
# Install SI CLI
curl -fsSL https://raw.githubusercontent.com/systeminit/si/main/install.sh | sh

# Start local System Initiative
si start

# Opens web interface at http://localhost:8080

# Login with:
# Email: admin@example.com
# Password: (shown in terminal output)
```

### Creating Your First Workspace

```
SYSTEM INITIATIVE UI WALKTHROUGH
─────────────────────────────────────────────────────────────────

1. CREATE WORKSPACE
┌─────────────────────────────────────────────────────────────────┐
│  Workspaces                                                      │
│  ─────────────────────────────────────────────────────────────  │
│  [+ New Workspace]                                               │
│                                                                  │
│  Name: my-infrastructure                                        │
│  Description: Production AWS setup                               │
│                                                                  │
│  [Create]                                                        │
└─────────────────────────────────────────────────────────────────┘

2. ADD COMPONENTS (Drag from palette)
┌─────────────────────────────────────────────────────────────────┐
│  PALETTE          │  CANVAS                                     │
│  ─────────────    │  ─────────────────────────────────────────  │
│  AWS              │                                              │
│  ├── VPC          │     ┌──────────┐                            │
│  ├── Subnet       │     │   VPC    │  ← Drag here              │
│  ├── EC2          │     │ 10.0.0.0 │                            │
│  ├── RDS          │     └──────────┘                            │
│  └── S3           │                                              │
│                   │                                              │
│  Kubernetes       │                                              │
│  ├── Deployment   │                                              │
│  └── Service      │                                              │
└─────────────────────────────────────────────────────────────────┘

3. CONNECT COMPONENTS (Draw connections)
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│     ┌──────────┐                      ┌──────────┐             │
│     │   VPC    │─────────────────────▶│  Subnet  │             │
│     │ 10.0.0.0 │                      │ .0.0/24  │             │
│     └──────────┘                      └────┬─────┘             │
│                                            │                    │
│                                            ▼                    │
│                                       ┌──────────┐             │
│                                       │   EC2    │             │
│                                       │ t3.micro │             │
│                                       └──────────┘             │
│                                                                  │
│  Connections create dependencies automatically                   │
└─────────────────────────────────────────────────────────────────┘

4. REVIEW CHANGE SET
┌─────────────────────────────────────────────────────────────────┐
│  CHANGE SET: "Add production VPC"                                │
│  ─────────────────────────────────────────────────────────────  │
│  + AWS VPC (vpc-production)                                     │
│    ├── cidr_block: 10.0.0.0/16                                  │
│    └── enable_dns_support: true                                 │
│                                                                  │
│  + AWS Subnet (subnet-public-1)                                 │
│    ├── cidr_block: 10.0.0.0/24                                  │
│    └── vpc_id: → vpc-production                                 │
│                                                                  │
│  + AWS EC2 Instance (web-server)                                │
│    ├── instance_type: t3.micro                                  │
│    └── subnet_id: → subnet-public-1                             │
│                                                                  │
│  [Apply Change Set]  [Discard]                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Writing Custom Functions

```typescript
// Custom function to validate security groups
async function qualify(
  input: {
    ingress: Array<{ from_port: number; to_port: number; cidr: string }>;
    egress: Array<{ from_port: number; to_port: number; cidr: string }>;
  }
): Promise<Qualification> {
  const warnings: string[] = [];
  const errors: string[] = [];

  // Check for overly permissive rules
  for (const rule of input.ingress) {
    if (rule.cidr === "0.0.0.0/0" && rule.from_port === 22) {
      warnings.push("SSH open to the world - consider restricting");
    }
    if (rule.cidr === "0.0.0.0/0" && rule.from_port === 0 && rule.to_port === 65535) {
      errors.push("All ports open to the world - this is dangerous");
    }
  }

  // Check for missing egress
  if (input.egress.length === 0) {
    warnings.push("No egress rules defined - instance cannot reach internet");
  }

  return {
    result: errors.length > 0 ? "failure" : warnings.length > 0 ? "warning" : "success",
    message: [...errors, ...warnings].join("; ") || "Security group looks good",
  };
}
```

```typescript
// Custom action to restart an EC2 instance
async function action_restart(
  input: { instance_id: string }
): Promise<ActionResult> {
  const ec2 = new EC2Client({});

  // Stop instance
  await ec2.send(new StopInstancesCommand({
    InstanceIds: [input.instance_id]
  }));

  // Wait for stopped
  await waitUntilInstanceStopped(
    { client: ec2, maxWaitTime: 300 },
    { InstanceIds: [input.instance_id] }
  );

  // Start instance
  await ec2.send(new StartInstancesCommand({
    InstanceIds: [input.instance_id]
  }));

  return {
    status: "success",
    message: `Instance ${input.instance_id} restarted`
  };
}
```

---

## Real-Time Collaboration

```
COLLABORATIVE EDITING
─────────────────────────────────────────────────────────────────

USER A (Platform Engineer)         USER B (Security Engineer)
┌───────────────────────────────┐ ┌───────────────────────────────┐
│                               │ │                               │
│ Working on: VPC layout        │ │ Working on: Security groups   │
│                               │ │                               │
│  ┌──────────┐                 │ │         ┌──────────┐         │
│  │   VPC    │ ← A editing     │ │         │    SG    │ ← B     │
│  │ (orange) │                 │ │         │ (green)  │         │
│  └──────────┘                 │ │         └──────────┘         │
│        │                      │ │              │                │
│        ▼                      │ │              │                │
│  ┌──────────┐                 │ │              │                │
│  │  Subnet  │                 │ │              │                │
│  └──────────┘                 │ │              │                │
│                               │ │              │                │
│ Cursor: [A] visible to B      │ │ Cursor: [B] visible to A      │
│                               │ │                               │
└───────────────────────────────┘ └───────────────────────────────┘

SHARED CHANGE SET:
┌─────────────────────────────────────────────────────────────────┐
│ Changes by Alice (A):                                           │
│ + VPC (10.0.0.0/16)                                             │
│ + Subnet (10.0.1.0/24)                                          │
│                                                                  │
│ Changes by Bob (B):                                             │
│ + Security Group (web-sg)                                       │
│   └── Ingress: 443/tcp from 0.0.0.0/0                          │
│                                                                  │
│ [Apply All] [Apply Alice's] [Apply Bob's]                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## War Story: From Tickets to Self-Service

*How a platform team eliminated 80% of infrastructure requests*

### The Problem

A 50-person engineering org had:
- **3 platform engineers** handling infrastructure requests
- **Ticket queue**: 2-3 day average wait time
- **Process**: Developer requests → Ticket → Platform review → Terraform PR → Review → Merge → Apply
- **Pain point**: Simple changes took days, complex ones took weeks

### The Old Way

```
INFRASTRUCTURE REQUEST FLOW (BEFORE):
─────────────────────────────────────────────────────────────────

Day 1:
├── 09:00 Developer needs new RDS instance
├── 09:15 Creates JIRA ticket with requirements
├── 10:00 Ticket enters backlog
└── 17:00 Platform team triages (low priority)

Day 2:
├── 14:00 Platform engineer picks up ticket
├── 15:00 Clarifying questions asked
└── 16:00 Developer responds

Day 3:
├── 09:00 Platform engineer writes Terraform
├── 11:00 Opens PR
├── 14:00 Another engineer reviews
├── 16:00 Changes requested
└── 17:00 Updates made

Day 4:
├── 09:00 PR approved
├── 10:00 Merged to main
├── 10:30 CI/CD applies to staging
├── 11:00 Developer tests
├── 14:00 Approved for production
└── 15:00 Applied to production

TOTAL TIME: 4 days for an RDS instance
```

### The System Initiative Way

```
INFRASTRUCTURE REQUEST FLOW (AFTER):
─────────────────────────────────────────────────────────────────

Day 1:
├── 09:00 Developer needs new RDS instance
├── 09:05 Opens System Initiative workspace
├── 09:10 Drags RDS component to canvas
├── 09:12 Configures: instance type, storage, credentials
├── 09:15 Qualification functions run automatically:
│         ├── ✓ Instance type valid
│         ├── ✓ Storage within quota
│         ├── ✓ Backup retention set
│         ├── ✓ Encryption enabled (enforced)
│         └── ✗ No private subnet selected (must fix)
├── 09:18 Developer selects private subnet
├── 09:20 Qualification passes
├── 09:22 Change set created, auto-assigned to platform team
├── 09:30 Platform engineer reviews in UI (sees full context)
├── 09:35 One-click approve
└── 09:40 Applied, developer notified

TOTAL TIME: 40 minutes
```

### What Made It Work

```
SYSTEM INITIATIVE GUARDRAILS
─────────────────────────────────────────────────────────────────

QUALIFICATION FUNCTIONS (Automatic validation):
┌─────────────────────────────────────────────────────────────────┐
│ Security:                                                        │
│ ├── RDS must be in private subnet                               │
│ ├── Encryption at rest required                                 │
│ ├── IAM authentication required                                 │
│ └── Security group must not be 0.0.0.0/0                       │
│                                                                  │
│ Cost:                                                            │
│ ├── Instance type must be from approved list                    │
│ ├── Storage cannot exceed 500GB without approval                │
│ └── Multi-AZ must be justified for dev environments            │
│                                                                  │
│ Operations:                                                      │
│ ├── Backup retention minimum 7 days                             │
│ ├── Maintenance window must be defined                          │
│ └── Monitoring must be enabled                                  │
└─────────────────────────────────────────────────────────────────┘

RESULT: Developers can self-serve SAFELY
```

### Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Avg request time | 4 days | 40 min | -99% |
| Platform tickets/week | 35 | 7 | -80% |
| Infrastructure errors | 8/month | 1/month | -87% |
| Developer satisfaction | 3.2/5 | 4.6/5 | +44% |
| Platform team capacity | "Drowning" | "Strategic projects" | ∞ |

---

## Common Mistakes

| Mistake | Why It's Bad | Better Approach |
|---------|--------------|-----------------|
| Treating it like Terraform | Miss reactive benefits | Embrace connections and propagation |
| Skipping qualification | Lose guardrails | Write validations for safety |
| Ignoring change sets | No review process | Always review before apply |
| Working alone | Miss collaboration | Invite team to workspace |
| Complex functions | Hard to maintain | Keep functions focused |
| No component reuse | Duplicate effort | Build component libraries |
| Forgetting refresh | Drift from reality | Regular refresh cycles |
| Manual documentation | Gets stale | Use codeGen functions |

---

## Hands-On Exercise

### Task: Build a VPC with Automatic Subnet Calculation

**Objective**: Create a VPC where subnet CIDRs automatically calculate based on VPC CIDR.

**Success Criteria**:
1. VPC component with configurable CIDR
2. Subnets that auto-calculate CIDRs
3. Qualification ensuring no CIDR overlap
4. Change set preview showing all resources

### Steps

```bash
# 1. Start System Initiative
si start

# 2. Open browser to http://localhost:8080
```

```
CANVAS SETUP:
─────────────────────────────────────────────────────────────────

3. Create workspace "vpc-demo"

4. Add AWS VPC component
   - Name: main-vpc
   - CIDR: 10.0.0.0/16

5. Add connection formula for subnets:
```

```typescript
// Custom function: calculateSubnetCidr
function calculateSubnetCidr(
  vpcCidr: string,
  subnetIndex: number,
  subnetBits: number
): string {
  // Parse VPC CIDR
  const [ip, prefix] = vpcCidr.split("/");
  const vpcPrefix = parseInt(prefix);
  const newPrefix = vpcPrefix + subnetBits;

  // Calculate subnet CIDR
  const ipNum = ip.split(".").reduce((acc, octet) => (acc << 8) + parseInt(octet), 0);
  const subnetSize = Math.pow(2, 32 - newPrefix);
  const subnetStart = ipNum + (subnetIndex * subnetSize);

  // Convert back to IP
  const newIp = [
    (subnetStart >> 24) & 255,
    (subnetStart >> 16) & 255,
    (subnetStart >> 8) & 255,
    subnetStart & 255,
  ].join(".");

  return `${newIp}/${newPrefix}`;
}
```

```
6. Add Subnet components that reference VPC:
   - Public Subnet 1: CIDR = calculateSubnetCidr(vpc.cidr, 0, 8)
   - Public Subnet 2: CIDR = calculateSubnetCidr(vpc.cidr, 1, 8)
   - Private Subnet 1: CIDR = calculateSubnetCidr(vpc.cidr, 2, 8)
   - Private Subnet 2: CIDR = calculateSubnetCidr(vpc.cidr, 3, 8)

7. Test reactivity:
   - Change VPC CIDR to 172.16.0.0/16
   - Watch all subnet CIDRs update automatically!

8. Add qualification function:
```

```typescript
// Qualification: no overlapping CIDRs
async function qualifySubnets(
  subnets: Array<{ name: string; cidr: string }>
): Promise<Qualification> {
  const cidrs = subnets.map(s => s.cidr);

  // Check for overlaps (simplified)
  for (let i = 0; i < cidrs.length; i++) {
    for (let j = i + 1; j < cidrs.length; j++) {
      if (cidrsOverlap(cidrs[i], cidrs[j])) {
        return {
          result: "failure",
          message: `Subnets ${subnets[i].name} and ${subnets[j].name} overlap`,
        };
      }
    }
  }

  return { result: "success", message: "No CIDR overlaps" };
}
```

```
9. Review change set:
   - See all components to be created
   - See all connections
   - See qualification results

10. Apply change set

11. Verify in AWS Console that resources match canvas
```

---

## Quiz

### Question 1
What makes System Initiative different from Terraform?

<details>
<summary>Show Answer</summary>

**Reactive model with visual collaboration**

Key differences:
- **Reactive**: Changes propagate through connections
- **Visual**: Canvas is the primary interface
- **Collaborative**: Multiple users edit simultaneously
- **Functions**: Everything is extensible TypeScript
- **Change sets**: Staging area before apply
- **Qualification**: Validation runs automatically
</details>

### Question 2
What are qualification functions?

<details>
<summary>Show Answer</summary>

**Automatic validation that runs as you configure**

Qualification functions:
- Run whenever component inputs change
- Return success, warning, or failure
- Block apply if critical failures exist
- Enable self-service with guardrails

Example: "RDS must be in private subnet" qualification prevents misconfiguration before it happens.
</details>

### Question 3
How does the reactive model work?

<details>
<summary>Show Answer</summary>

**Changes propagate through connections automatically**

When you change a component's property:
1. System detects which other components depend on it
2. Those components' formulas are recalculated
3. Their dependents are then recalculated
4. All changes appear in the change set

Like a spreadsheet where formulas update when cells change.
</details>

### Question 4
What are change sets?

<details>
<summary>Show Answer</summary>

**A staging area for infrastructure changes**

Change sets:
- Accumulate all pending changes
- Show before/after diff
- Allow review before apply
- Can be split by author
- Provide audit trail
- Enable approval workflows
</details>

### Question 5
Who created System Initiative?

<details>
<summary>Show Answer</summary>

**Adam Jacob, co-founder of Chef**

Adam created Chef in 2008, one of the foundational configuration management tools. After 15+ years of observing DevOps tooling limitations, he started System Initiative to address fundamental problems with IaC.
</details>

---

## Key Takeaways

1. **Reactive model** — Changes propagate like spreadsheet formulas
2. **Visual-first** — Canvas is the interface, code underneath
3. **Qualification** — Automatic validation enables self-service
4. **Change sets** — Stage and review before applying
5. **Collaboration** — Real-time multi-user editing
6. **Functions** — Everything is extensible TypeScript
7. **Open source** — Built transparently, community-driven
8. **Different mental model** — Not another Terraform wrapper
9. **Guardrails** — Enable self-service safely
10. **Future of DevOps** — Reimagining infrastructure automation

---

## Next Steps

- **Next Module**: [Module 7.10: Nitric](module-7.10-nitric.md) — Cloud-native framework
- **Related**: [Platform Engineering](../../disciplines/platform-engineering/) — IDP concepts
- **Related**: [Platforms Toolkit](../platforms/) — Backstage, Crossplane

---

## Further Reading

- [System Initiative Documentation](https://docs.systeminit.com/)
- [System Initiative GitHub](https://github.com/systeminit/si)
- [Adam Jacob on System Initiative](https://www.youtube.com/watch?v=) (search for talks)
- [System Initiative Discord](https://discord.gg/system-initiative)
- [System Initiative Blog](https://www.systeminit.com/blog)

---

*"System Initiative asks: What if your infrastructure understood itself? What if changes propagated automatically? What if DevOps was visual and collaborative? The answer is a platform that feels like the future."*
