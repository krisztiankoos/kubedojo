---
title: "Module 3.14: Azure App Service — Operator Path"
slug: cloud/azure-essentials/module-3.14-app-service
sidebar:
  order: 15
---
**Complexity**: [COMPLEX] | **Time:** 90-120 min | **Prerequisites**: [3.7-aci-aca](../module-3.7-aci-aca/) (Container Apps), [3.8-functions](../module-3.8-functions/), [3.9-key-vault](../module-3.9-key-vault/), [3.10-monitor](../module-3.10-monitor/)
## What You'll Be Able to Do (Debug, Design, Evaluate)
After completing this module, you will be able to:

- **Debug** App Service incidents by separating plan capacity, worker health, deployment slot state, networking path, identity permissions, and application logs.
- **Design** a production Web App pattern with the right App Service Plan tier, deployment slots, managed identity, private networking, autoscale rules, and diagnostics.
- **Evaluate** when App Service is the right default, when Azure Container Apps is a better fit, and when AKS is justified by platform control requirements.

The focus is the operator path. You are not learning App Service as a portal wizard. You are learning it as a production hosting surface with shared compute, slots, warm-up behavior, identity, private access patterns, and scaling boundaries. By the end, you should be able to look at a web workload and answer:

- Which service should host it?
- Which plan tier should run it?
- Which settings must be sticky across swaps?
- Which path does inbound traffic use?
- Which path does outbound traffic use?
- Which logs prove what happened?
- Which rollback takes minutes instead of hours?

## Why This Module Matters

Azure App Service is one of the most useful services in Azure because it handles a boring but hard problem: running web applications without making every team become an operating-system, load-balancer, and patching team. It can host .NET, Java, Node.js, Python, PHP, Ruby, Go, and custom containers. It can terminate HTTPS, bind custom domains, integrate with Entra ID, use managed identity, pull secrets from Key Vault, attach to VNets, receive traffic over Private Link, autoscale, and ship logs to Azure Monitor. That convenience is why many enterprise applications land on App Service first. The risk is that App Service looks simple until the first production incident. A team deploys to the production slot and discovers that the app takes ninety seconds to warm up. A connection string swaps with the slot when the database setting should have stayed attached to production. The app can reach the public internet but cannot reach the private database because VNet integration was misunderstood. An autoscale rule adds workers but the App Service Plan is shared with three other apps, so the noisy app scales everyone and increases cost. A migration from Premium v2 to Premium v3 is planned as a quick scale-up, then the team learns that the existing deployment unit cannot support the desired Premium v3 SKU. App Service is not a toy service. It is a managed application platform with strong operational features and sharp edges. The biggest feature is deployment slots. Slots let you deploy a new release into a parallel environment, warm it up, validate it, and swap it into production with a fast rollback path. For many long-running web applications, that is the killer feature that keeps App Service relevant even when Container Apps and AKS are available. The second biggest decision is whether App Service should be used at all. [Azure Container Apps](../module-3.7-aci-aca/) often beats App Service for new event-driven microservices because it has revision traffic splitting, KEDA scaling, service-to-service patterns, and container-native operations. App Service often beats Container Apps for traditional web apps, enterprise .NET applications, slot-based release workflows, and teams that want a stable PaaS contract without Kubernetes concepts. AKS wins only when the platform needs Kubernetes-level control and is willing to operate Kubernetes-level complexity.

> **Pause and predict:** A team has a public .NET monolith with predictable traffic, a SQL backend, and a strict requirement for pre-production validation plus instant rollback. Should your first candidate be App Service, Container Apps, or AKS? What feature drives that answer?

## When App Service, When Container Apps, When AKS (THE decision mental model)

Start with the shape of the workload, not the feature list. App Service is best when the unit of deployment is a web application. Container Apps is best when the unit of deployment is a containerized service or worker that benefits from revisions, event-driven scaling, and scale-to-zero economics. AKS is best when the unit of operation is a Kubernetes platform. Those are different ownership models.

### The Fast Decision Sequence

Use this sequence before drawing architecture boxes:

1. If the workload is a traditional web app or API with a stable runtime, custom domain, TLS, managed identity, and release-slot workflow, evaluate App Service first.
2. If the workload is a set of containerized microservices, event-driven workers, queue consumers, or services that should scale to zero, evaluate Container Apps first.
3. If the workload needs Kubernetes APIs, custom controllers, service mesh, admission policy, advanced scheduling, or platform team ownership of clusters, evaluate AKS.
4. If the workload is a short event handler, evaluate Azure Functions before all three.
5. If the workload needs full VM control, App Service is probably the wrong abstraction.

### Mental Model Table

| Decision factor | App Service | Container Apps | AKS |
|---|---|---|---|
| Primary abstraction | Web app in an App Service Plan | Container app revision in a managed environment | Kubernetes workload in a cluster |
| Best default for | Long-running web apps and APIs | New containerized services and workers | Platform-heavy systems |
| Release strength | Deployment slots and swap rollback | Revisions and traffic splitting | Rollouts through Kubernetes controllers |
| Scale-to-zero | No for dedicated App Service Plans | Yes for many workloads | No by default; possible with add-ons and careful design |
| Event-driven scaling | Limited compared with KEDA | Strong through KEDA-style rules | Strong if you install and operate KEDA |
| Operations surface | App, plan, slots, settings, diagnostics | App, revisions, environment, ingress, scale rules | Cluster, nodes, CNI, ingress, storage, policies, upgrades |
| Team fit | App teams that want PaaS | App teams comfortable with containers | Platform teams ready to operate Kubernetes |
| Common mistake | Treating the plan as per-app compute | Treating every web app as a microservice | Using Kubernetes because it is familiar |

### App Service Wins When

- You need a managed web-hosting platform with minimal infrastructure ownership.
- Deployment slots are central to your release and rollback strategy.
- The app is a monolith or modular monolith with a conventional HTTP lifecycle.
- The runtime is supported directly by App Service.
- The organization already has App Service runbooks, policies, and cost models.
- App teams need custom domains, TLS, auth integration, and diagnostics without owning ingress controllers.

### Container Apps Wins When

- The workload is already containerized and designed as a service or worker.
- You need revision-based gradual rollout instead of slot swap.
- Queue length, Kafka lag, Service Bus messages, or HTTP concurrency should drive scaling.
- Scale to zero is a real cost requirement.
- Dapr, internal service discovery, and microservice patterns matter.
- You want less Kubernetes than AKS but more container-native behavior than App Service.

Container Apps is often the better answer for new microservices. That is not a criticism of App Service. It is a sign that the workload's natural unit is a container revision, not a web app slot.

### AKS Wins When

- You need Kubernetes APIs and ecosystem tools as the platform contract.
- Teams require custom controllers, CRDs, admission policy, sidecars, or service mesh.
- You need advanced workload placement, GPUs, DaemonSets, host networking, or node-level control.
- The organization has a real platform team with cluster lifecycle ownership.
- You are standardizing on Kubernetes across clouds or on-prem environments.

AKS is a platform, not just a hosting option. If no one owns cluster upgrades, node images, ingress, CNI, policy, and incident response, AKS is usually the expensive answer to a simpler hosting problem.

### Worked Example: Three Teams, Three Correct Answers

Team A owns a .NET MVC app used by finance. It has predictable business-hours traffic, SQL Database, Key Vault secrets, custom domain, and change windows. App Service on a Standard or Premium v3 plan is a strong first candidate because slots, managed identity, Always On, and App Insights fit the work. Team B owns a set of small containerized fraud-scoring APIs and workers. Traffic is spiky, queues drive background processing, and each service releases independently. Container Apps is a strong first candidate because revisions, KEDA scale rules, and scale-to-zero economics match the system. Team C owns a shared internal developer platform with hundreds of services, network policy, service mesh, custom admission controls, and strong multi-tenant requirements. AKS is justified because the platform itself needs Kubernetes primitives.

> **Stop and think:** If a workload can run on both App Service and Container Apps, which rollback model does the team understand better today: slot swap or revision traffic splitting? That answer often matters more than the feature checklist.

## App Service Plans + SKU Tiers (table; Free/Shared/Basic/Standard/Premium v3/Isolated v2; when each makes sense)

An App Service Plan is the compute boundary. Every Web App runs in a plan. The plan defines operating system, region, VM size, pricing tier, and instance count. Apps in the same plan share the plan's workers. Slots for those apps also share the same workers. Diagnostics, WebJobs, deployment activity, and background tasks consume resources from the same plan. This is the most important cost and capacity fact in App Service: **You scale the plan, not just one app.** If three production apps share one plan, scaling out the plan adds instances for all three. That can be efficient when apps have complementary traffic. It can also hide noisy-neighbor problems inside your own subscription.

### SKU Decision Table

| Tier | Compute model | Scale behavior | Production fit | When it makes sense |
|---|---|---|---|---|
| Free | Shared compute with quotas | No scale-out | No | Learning, tiny demos, throwaway tests. Expect limits and idle unloads. |
| Shared | Shared compute with quota-based billing | No scale-out | No | Legacy dev/test only when cost is the only concern. Avoid for real environments. |
| Basic | Dedicated plan workers | Manual scale-out; limited advanced features | Small internal apps only | Low-risk dev/test, simple internal apps, or private endpoint eligibility at minimum cost. |
| Standard | Dedicated workers with production features | Manual and rule-based autoscale | Yes for many apps | Baseline production tier for slots, autoscale, backups, and Always On. |
| Premium v3 | Dedicated workers with stronger CPU/memory options | Higher scale and performance headroom | Preferred for serious production | High-traffic apps, custom containers, private networking, memory pressure, and better performance per instance. |
| Isolated v2 | Dedicated workers inside App Service Environment v3 | High scale in single-tenant environment | Only when justified | Network-isolated, compliance-heavy, high-scale single-tenant workloads where ASE cost is accepted. |

### Scale Up vs Scale Out

Scale up changes the worker size or tier. Examples:

- Standard S1 to Standard S2
- Standard to Premium v3
- Premium v3 P1v3 to P2v3

Scale up is useful when each instance needs more CPU, memory, disk throughput, or feature support. It is also the move when the current tier lacks a required feature, such as autoscale or deployment slots. Scale out changes the number of workers. Examples:

- two workers to four workers;
- autoscale from two to ten workers;
- schedule-based scale-out during business hours.

Scale out is useful when the app is horizontally scalable and requests can be distributed across instances. The app must be stateless or externalize session state to Redis, SQL, Storage, or another shared service. Local disk is not a durable coordination mechanism.

### Plan Isolation Rules

Use separate App Service Plans when:

- apps have different availability requirements;
- one app has unpredictable CPU or memory spikes;
- one team must own cost independently;
- deployment activity for one app should not affect another;
- production and non-production should not share capacity;
- the app needs a different OS, region, tier, or scale profile.

Share a plan when:

- apps are small and low-risk;
- the same team owns all apps;
- scaling them together is acceptable;
- cost efficiency matters more than isolation;
- the blast radius is understood.

Worked example: a company runs a public catalog API, an internal admin portal, and a nightly report generator. Putting all three in one Premium v3 plan may look efficient. During month-end reporting, the report generator saturates CPU and the catalog slows down. The correct fix is not only "add more workers." It may be to isolate the report generator into its own plan so its background load cannot steal capacity from the customer-facing API.

## Web App Provisioning (one azurerm Terraform + one Bicep snippet)

Provision the plan and app as code. The operator goal is reviewability. You want the plan tier, worker count, runtime, identity, HTTPS setting, health check path, app settings, and diagnostics to be visible before deployment. This section uses a Linux Web App because Linux is common for modern runtimes and containers.

### Terraform: App Service Plan + Linux Web App

This example intentionally stays compact. It shows the production decisions an operator should review before adding domain binding, diagnostics, slots, and private networking.

```hcl
resource "azurerm_resource_group" "rg" {
  name     = "rg-appsvc-prod-eus"
  location = "eastus"
}

resource "azurerm_service_plan" "web" {
  name                = "asp-orders-prod-eus"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "P1v3"
  worker_count        = 2
}

resource "azurerm_linux_web_app" "orders" {
  name                = "app-orders-prod-eus"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.web.id
  https_only          = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on         = true
    health_check_path = "/healthz"

    application_stack {
      node_version = "20-lts"
    }
  }

  app_settings = {
    "APP_ENV"                         = "production"
    "WEBSITE_HEALTHCHECK_MAXPINGFAILURES" = "3"
    "SCM_DO_BUILD_DURING_DEPLOYMENT"  = "true"
  }
}
```

Why these choices? `P1v3` is not a universal default, but it is a realistic production starting point for a serious app. Two workers avoid making one worker the only serving instance. `always_on` reduces idle cold-start behavior. The health check path gives App Service a real readiness signal instead of assuming the root path means the app is healthy. The system-assigned identity removes the need for application credentials when calling Key Vault, Storage, or SQL.

### Bicep: Same Shape, Native Azure Resource Model

```bicep
param location string = resourceGroup().location
param appName string = 'app-orders-prod-eus'
param planName string = 'asp-orders-prod-eus'

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  kind: 'linux'
  sku: {
    name: 'P1v3'
    tier: 'PremiumV3'
    capacity: 2
  }
  properties: {
    reserved: true
  }
}

resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      alwaysOn: true
      healthCheckPath: '/healthz'
      linuxFxVersion: 'NODE|20-lts'
      appSettings: [
        {
          name: 'APP_ENV'
          value: 'production'
        }
        {
          name: 'WEBSITE_HEALTHCHECK_MAXPINGFAILURES'
          value: '3'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}
```

The important part is that the app, plan, and identity are described together. If a pull request changes `capacity`, `sku`, `alwaysOn`, runtime, or health check behavior, the reviewer can see the operational impact before the release.

### Provisioning Review Checklist

Before applying an App Service change, review:

- plan tier and worker count;
- whether the plan is shared with other apps;
- runtime and OS;
- custom container image source if used;
- `always_on` or `alwaysOn`;
- health check path;
- managed identity type;
- app settings and slot settings;
- VNet integration and private endpoint requirements;
- diagnostic settings;
- slot creation and swap plan;
- rollback owner.

## Deployment Slots + Slot Swap (concrete worked example: green→blue swap; config sync gotchas; pre-warming)

Deployment slots are separate deployment targets for the same Web App. Each slot has its own hostname. Each slot can have its own app settings, connection strings, identity behavior, and deployed code. Slots run on the same App Service Plan as the production slot, so they consume the same plan capacity. That shared capacity is a feature and a cost. It means a staging slot can behave like production because it runs on the same worker class. It also means a staging load test can harm production if the plan is undersized.

### Why Slots Matter

Without slots, deployment rollback usually means redeploying an older artifact. That can be slow, brittle, and hard to perform during an incident. With slots, a release can follow this sequence:

1. Deploy version N+1 to a non-production slot.
2. Warm the slot.
3. Validate health checks and smoke tests.
4. Swap the warmed slot into production.
5. Keep the previous production version in the old slot for rollback.

This is why slots are the killer App Service feature. The rollback can be another swap, not a rebuild.

### Worked Example: Green to Blue Swap

Assume the production slot currently serves the blue version. The `green` slot will receive the new release. The intended flow is:

```text
before release:
  production slot -> blue code -> users
  green slot      -> old or empty code -> no users

after deploy:
  production slot -> blue code -> users
  green slot      -> green code -> validation

after swap:
  production slot -> green code -> users
  green slot      -> blue code -> rollback target
```

Create a slot:

```bash
az webapp deployment slot create \
  --resource-group rg-appsvc-prod-eus \
  --name app-orders-prod-eus \
  --slot green
```

Deploy the new artifact to the `green` slot using your normal deployment system. For example, GitHub Actions, Azure DevOps, Zip Deploy, container image update, or an IaC-driven release. Then validate the slot hostname:

```bash
curl -fsS https://app-orders-prod-eus-green.azurewebsites.net/healthz
curl -fsS https://app-orders-prod-eus-green.azurewebsites.net/version
```

Swap the slot into production:

```bash
az webapp deployment slot swap \
  --resource-group rg-appsvc-prod-eus \
  --name app-orders-prod-eus \
  --slot green \
  --target-slot production
```

If the release fails after swap, swap back:

```bash
az webapp deployment slot swap \
  --resource-group rg-appsvc-prod-eus \
  --name app-orders-prod-eus \
  --slot green \
  --target-slot production
```

The command looks the same because the slot now contains the previous production code. The rollback operation swaps the old code back into production.

### Swap with Preview

For high-risk changes, use a two-phase swap with preview. The preview phase applies destination slot settings to the source slot before completing the swap. That lets you validate the source slot under the configuration it will have after swap. The decision point is simple:

- use a normal swap for routine releases with low configuration risk;
- use swap with preview when configuration and warm-up behavior are the main risk;
- do not use slots as a substitute for real staging environments when external dependencies differ.

### Pre-Warming

Warm-up is not cosmetic. Many frameworks load dependencies, compile views, open connection pools, initialize caches, or perform migrations on first request. If the first real user request pays that cost, the swap looks successful but the user experience fails. Use a dedicated warm-up path. Set:

```text
WEBSITE_SWAP_WARMUP_PING_PATH=/healthz/ready
WEBSITE_SWAP_WARMUP_PING_STATUSES=200,202
```

The warm-up path should exercise the parts of the app that must be ready to accept traffic. It should not perform destructive work. It should not depend on optional downstream systems that can be degraded while the app still serves a useful response.

### Slot Setting Gotchas

Some settings should move with code. Some settings should stay with the slot. Production database connection strings, production Key Vault references, monitoring connection strings, and public callback URLs often need to stay attached to the production slot. Feature flags, runtime settings, and version-specific toggles may need to move with the release. This is the configuration-sync problem. App Service lets you mark app settings and connection strings as slot settings. A slot setting stays with the slot during swap. A non-slot setting swaps with the code. That sentence is worth repeating: **Sticky settings stay with the slot; non-sticky settings move with the release.** The operational danger is that teams often set this once in the portal and forget it. Review slot stickiness in code or in a release checklist.

### Settings That Deserve Extra Review

Review these before every slot-based release:

- database connection strings;
- Key Vault reference settings;
- storage account names and queues;
- `APP_ENV` or environment-name flags;
- telemetry connection strings;
- external callback URLs;
- payment provider keys;
- OAuth redirect URIs;
- `WEBSITE_SWAP_WARMUP_PING_PATH`;
- framework environment variables such as `ASPNETCORE_ENVIRONMENT` or `NODE_ENV`.

> **Pause and predict:** If the staging slot points to a staging database, and that connection string is not marked as a slot setting, what database might production use immediately after the swap?

### Slot Runbook

A usable slot runbook includes:

1. Confirm the slot exists and is not serving production traffic.
2. Deploy the release artifact to the slot.
3. Confirm the slot has the expected code version.
4. Confirm slot settings and connection strings.
5. Warm the slot through the configured warm-up path.
6. Run smoke tests against the slot hostname.
7. Swap into production.
8. Query production logs and metrics for errors and latency.
9. Keep the previous production version in the old slot until the release is accepted.
10. Swap back if the release violates rollback criteria.

## Networking: Hybrid Connections vs VNet Integration vs Private Endpoint (decision table + when each)

App Service networking is easier when you separate inbound and outbound paths. Inbound means clients reaching your app. Outbound means your app reaching dependencies. Hybrid Connections and VNet integration are outbound features. Private Endpoint is an inbound feature. Many production designs use both VNet integration and Private Endpoint.

### Three Patterns

| Pattern | Direction | What it solves | Best fit | What it does not solve |
|---|---|---|---|---|
| Hybrid Connections | Outbound from app to one TCP host:port | Reach a specific private or on-prem endpoint without full VNet integration | Quick access to one legacy dependency | It does not make the app private for inbound traffic; no UDP; no dynamic ports. |
| VNet Integration | Outbound from app into a VNet | Reach private Azure resources, private DNS, peered networks, VPN, or ExpressRoute paths | Apps that need many private dependencies | It does not provide private inbound access to the app. |
| Private Endpoint | Inbound from a VNet to the app | Let private clients reach the app over Private Link | Private apps, app-to-app private ingress, internal APIs | It does not route outbound app traffic into the VNet. |

### Hybrid Connections

Hybrid Connections are pragmatic. They let App Service reach a single TCP endpoint through Azure Relay and a Hybrid Connection Manager running where the endpoint is reachable. The App Service app and the on-prem relay agent both make outbound connections to Azure. That is why the pattern is attractive in locked-down networks. Use Hybrid Connections when:

- one or two legacy TCP dependencies are needed;
- the target is identified by host and port;
- the network team will not approve full VPN or ExpressRoute work yet;
- the app needs a bridge while a migration is in progress.

Avoid Hybrid Connections when:

- the app needs many dependencies;
- the dependency uses UDP or dynamic ports;
- DNS and private routing are central to the design;
- the connection needs to look like normal VNet traffic;
- you need inbound private access to the app.

Worked example: an App Service app needs to call an on-prem license server at `license01.corp.example:443`. Hybrid Connection can be a low-friction bridge because the target is one TCP endpoint. It would be a poor fit for a whole estate of databases, file shares, LDAP, and service discovery.

### VNet Integration

VNet integration lets the app send outbound traffic into a delegated subnet. Use it when the app needs to call private Azure services, databases, internal APIs, or on-prem resources reachable through VPN or ExpressRoute. VNet integration is commonly paired with:

- private DNS zones;
- private endpoints for downstream services;
- route tables;
- NAT Gateway for controlled outbound IP;
- network security review;
- Azure Firewall or NVA egress patterns.

VNet integration does not put the app itself inside your VNet for inbound traffic. That distinction prevents a common incident. An operator enables VNet integration and expects internal clients to reach the app privately. Nothing changes for inbound access because VNet integration is outbound. Private Endpoint is the inbound private access pattern.

### Private Endpoint

Private Endpoint gives the app a private IP address in a VNet through Azure Private Link. Clients inside the VNet, peered VNets, or connected on-prem networks can reach the app privately. Public network access can then be restricted or disabled depending on the design. Use Private Endpoint when:

- the app is an internal API;
- public exposure is not acceptable;
- traffic should stay on private Azure networking;
- Application Gateway or another private client should reach the app;
- DNS can be managed correctly.

Private Endpoint requires DNS discipline. The app's public hostname must resolve to the private endpoint IP from private clients. If DNS is wrong, clients may still resolve the public path and the incident will look like an application failure.

### Combining Patterns

A common production pattern:

```text
client in VNet
  -> private DNS
  -> App Service Private Endpoint
  -> Web App
  -> VNet Integration subnet
  -> private endpoint for SQL / Storage / Key Vault
```

Inbound to the app uses Private Endpoint. Outbound from the app uses VNet integration. Private DNS ties the names to private addresses.

### Decision Rules

| Requirement | Pick first | Rationale |
|---|---|---|
| App must call one on-prem TCP service quickly | Hybrid Connection | It avoids full network integration for one host:port. |
| App must call many private Azure services | VNet Integration | Outbound private routing and DNS become the main need. |
| App must be reachable only from private networks | Private Endpoint | Inbound exposure is the main need. |
| App-to-app private call between two Web Apps | Private Endpoint plus VNet Integration | The caller needs outbound private routing; the callee needs private inbound access. |
| Internal App Gateway fronts App Service | Private Endpoint or documented App Gateway integration pattern | The gateway needs a private path to the app. |
| Legacy dependency uses dynamic ports | Not Hybrid Connection | Hybrid Connections map to TCP host:port, not whole network protocols. |

## Managed Identity for Backend Services (Key Vault secret rotation, Storage role assignment, SQL token auth)

Managed identity gives an App Service app an Entra ID identity. The app can use that identity to request tokens for Azure services. That removes stored credentials from application settings. It also gives operators a normal RBAC and audit story. There are two types:

- system-assigned identity, created with the app and deleted with the app;
- user-assigned identity, created as its own resource and attached to one or more apps.

System-assigned identity is simpler for one app. User-assigned identity is useful when identity lifecycle must outlive the app, several slots or apps need the same identity, or deployment ordering is easier with a stable principal.

### Key Vault: Secret References and Rotation

App Service can use Key Vault references in app settings. The app setting value points to a Key Vault secret instead of storing the secret directly. Example:

```bash
az webapp identity assign \
  --resource-group rg-appsvc-prod-eus \
  --name app-orders-prod-eus

az role assignment create \
  --assignee "$APP_PRINCIPAL_ID" \
  --role "Key Vault Secrets User" \
  --scope "$KEY_VAULT_ID"

az webapp config appsettings set \
  --resource-group rg-appsvc-prod-eus \
  --name app-orders-prod-eus \
  --settings "OrdersDbPassword=@Microsoft.KeyVault(SecretUri=https://kv-orders-prod.vault.azure.net/secrets/orders-db-password/)"
```

Why this shape? The app setting name stays stable. The secret value rotates in Key Vault. The managed identity authorizes access. The application does not need a client secret to read the secret. Prefer versionless secret URIs when normal rotation should be picked up automatically. Use versioned secret URIs only when pinning is deliberate. Operational note: Key Vault references are convenient, but they are still secrets. If a downstream service supports Entra authentication directly, prefer token auth over a password stored in Key Vault.

### Storage: Role Assignment Instead of Account Keys

Storage account keys are broad secrets. Managed identity plus Azure RBAC is usually safer. For blob access:

```bash
az role assignment create \
  --assignee "$APP_PRINCIPAL_ID" \
  --role "Storage Blob Data Contributor" \
  --scope "$STORAGE_ACCOUNT_ID"
```

Then app code uses the Azure Identity SDK. For example, a Python app can use `DefaultAzureCredential`. Local developers authenticate with Azure CLI or developer credentials. The deployed app authenticates with managed identity. The code path stays similar. The operator decision is the scope. Assign at the smallest useful scope:

- container scope when one app writes one container;
- storage account scope when the app legitimately uses many containers;
- resource group scope only when ownership is broad and documented.

### SQL: Token Auth Instead of Password Auth

Azure SQL can use Microsoft Entra authentication. For .NET applications, connection strings can use managed identity authentication. Example shape:

```text
Server=tcp:sql-orders-prod.database.windows.net,1433;
Database=orders;
Authentication=Active Directory Managed Identity;
Encrypt=True;
TrustServerCertificate=False;
```

For a user-assigned identity, include the client ID when the driver requires it. The database must also know the identity. That normally means an Entra admin is configured for the SQL server and a database user is created for the managed identity. Then grant only the required database permissions. Do not grant `db_owner` because the app needed to read one table during a deployment crunch.

### Identity Debugging Checklist

When managed identity access fails:

1. Confirm the app or slot has the expected identity enabled.
2. Confirm the target resource has a role assignment or access policy for that identity.
3. Confirm the scope is correct.
4. Confirm the application requests a token for the right resource.
5. Confirm private networking is not blocking the target call.
6. Remember that authorization changes can take time to propagate.
7. Query application logs for the actual token or authorization error class, not just the HTTP status.

> **Stop and think:** If a Web App receives `403` from Key Vault, is the first hypothesis "Key Vault is down" or "the app identity lacks permission or is using the wrong vault URI"? What evidence would distinguish those?

## Autoscaling (per-plan rules; CPU/memory/HTTP queue; schedule-based; cool-down)

Autoscaling happens at the App Service Plan boundary. That means every app in the plan is affected. Before writing rules, list the apps in the plan and decide whether they should scale together. If not, separate them first.

### Scale Rule Types

Use three kinds of rules:

- metric-based rules for real load;
- schedule-based rules for predictable load;
- manual scale changes for planned events and incident response.

Common metric signals:

- CPU percentage;
- memory percentage;
- HTTP queue length;
- request count;
- average response time;
- HTTP 5xx count.

CPU and memory rules are easy to understand. They are also blunt. HTTP queue length is often a better signal that requests are waiting for worker capacity. Response time and 5xx signals are user closer, but they may indicate application failures rather than capacity needs.

### Example Autoscale Shape

For a production API:

| Rule | Direction | Why |
|---|---|---|
| CPU > 70% for 10 minutes | Scale out by 1 | Sustained CPU pressure suggests more workers may help. |
| Memory > 75% for 10 minutes | Scale out by 1 | Memory pressure can cause GC churn, restarts, or slow requests. |
| HTTP queue length > 100 for 5 minutes | Scale out by 2 | Waiting requests are a direct capacity symptom. |
| CPU < 35% for 30 minutes and queue length low | Scale in by 1 | Avoid paying for idle workers after traffic falls. |
| Weekdays 07:30 | Set minimum to 4 | Business traffic is predictable; warm capacity before users arrive. |
| Weekdays 19:00 | Set minimum to 2 | Reduce baseline after peak hours. |

### Cool-Down Matters

Cool-down prevents oscillation. If a rule scales out and the metric drops immediately, scaling back in too quickly can restart the pressure cycle. Use longer scale-in cool-downs than scale-out cool-downs. A common pattern:

- scale out cool-down: 5 to 10 minutes;
- scale in cool-down: 20 to 30 minutes;
- schedule change lead time: before traffic arrives, not after.

### Per-Plan Rule Design

Do not create autoscale rules in isolation from deployment slots. Slots consume plan resources. A staging slot warming up during a release can increase CPU and memory. If autoscale triggers during every release, that may be acceptable. If a staging performance test causes production cost spikes, the plan is too shared or the release process needs a dedicated test plan.

### Automatic Scaling vs Azure Autoscale

Azure has more than one scaling concept. App Service automatic scaling can handle some scaling decisions for supported tiers. Azure Monitor autoscale rules let you define metric and schedule-based scale behavior. The operator decision is whether you want Azure-managed scaling behavior or explicit rules that match your traffic model and change windows. For regulated production workloads, explicit rules are often easier to explain in review. For simpler workloads, automatic scaling may be enough.

### Autoscale Review Checklist

Before enabling autoscale:

- confirm the app is stateless across workers;
- externalize sessions if needed;
- check downstream dependency capacity;
- choose minimum capacity for normal traffic;
- choose maximum capacity for cost and blast radius;
- set alerts before max capacity is reached;
- use cool-downs that avoid flapping;
- load test the same runtime, slot, network path, and auth behavior used in production.

Scaling out a web tier does not scale the database. If the database is the bottleneck, adding more workers can make the outage worse by increasing concurrent pressure.

## Monitoring + Diagnostics (Log Analytics; ≥2 KQL queries on `AppServiceHTTPLogs` / `AppServiceConsoleLogs`; metric alerts)

App Service should not go to production without diagnostics. At minimum, send HTTP logs, console logs, application logs, and relevant platform metrics to Azure Monitor and Log Analytics. Application Insights is also common for distributed tracing and application-level telemetry. The operator view needs both:

- platform evidence from App Service and Azure Monitor;
- application evidence from logs, traces, dependencies, and exceptions.

### What to Enable

Enable diagnostic settings for:

- `AppServiceHTTPLogs`;
- `AppServiceConsoleLogs`;
- application logs where supported;
- audit or platform logs relevant to the app;
- metrics on the app and App Service Plan.

Use Log Analytics retention deliberately. High-volume web apps can generate large log bills. Do not solve that by disabling logs during incidents. Instead, set retention, sampling, and table plans based on incident and compliance requirements.

### KQL: 5xx Trend by App and Path

```kusto
AppServiceHTTPLogs
| where TimeGenerated > ago(2h)
| where ScStatus >= 500
| summarize
    Requests = count(),
    ExampleClient = any(CIp),
    P95DurationMs = percentile(TimeTaken, 95)
  by bin(TimeGenerated, 5m), _ResourceId, CsMethod, CsUriStem, ScStatus
| order by TimeGenerated desc, Requests desc
```

Use this when the symptom is "the app is returning errors." It groups failures by method, path, and status. That helps separate one broken endpoint from an app-wide failure.

### KQL: Slow Requests Before Errors

```kusto
AppServiceHTTPLogs
| where TimeGenerated > ago(6h)
| summarize
    Requests = count(),
    P50Ms = percentile(TimeTaken, 50),
    P95Ms = percentile(TimeTaken, 95),
    P99Ms = percentile(TimeTaken, 99),
    Errors = countif(ScStatus >= 500)
  by bin(TimeGenerated, 10m), _ResourceId
| extend ErrorRate = todouble(Errors) / todouble(Requests)
| order by TimeGenerated desc
```

Use this when latency increased before the outage. Many incidents begin as saturation, not immediate failure.

### KQL: Console Errors After a Slot Swap

```kusto
AppServiceConsoleLogs
| where TimeGenerated > ago(1h)
| where Level in ("Error", "Warning") or ResultDescription has_any ("Exception", "ERROR", "Traceback")
| project TimeGenerated, _ResourceId, Host, Level, ResultDescription
| order by TimeGenerated desc
```

Use this right after deployment or swap. It finds application startup errors, dependency failures, and container logs that may not appear as clean HTTP status patterns yet.

### KQL: One Client or User Agent Dominates Traffic

```kusto
AppServiceHTTPLogs
| where TimeGenerated > ago(30m)
| summarize Requests = count(), Errors = countif(ScStatus >= 500)
  by CIp, UserAgent, CsUriStem
| top 20 by Requests desc
```

Use this when a sudden traffic spike might be one client, one crawler, or one broken retry loop.

### Metric Alerts

Create alerts for:

- App Service Plan CPU percentage sustained high;
- App Service Plan memory percentage sustained high;
- HTTP queue length above baseline;
- HTTP 5xx rate above baseline;
- average response time or p95 response time above SLO;
- worker restarts or app restarts;
- slot swap failure events;
- plan instance count approaching autoscale maximum;
- Key Vault, SQL, or Storage dependency failures from Application Insights.

Alert thresholds should start from a baseline. If normal CPU is 55% during peak, a 60% alert is noise. If normal HTTP queue length is zero, a small nonzero sustained queue may be meaningful.

### Deployment Dashboard

A release dashboard should show:

- current slot and code version;
- request count;
- 4xx and 5xx;
- latency percentiles;
- CPU and memory;
- HTTP queue length;
- dependency failures;
- console errors;
- active instance count;
- last swap timestamp.

The goal is not to create a beautiful dashboard. The goal is to answer one question quickly: **Should we keep the release, pause, or swap back?**

## App Service Environment v3 (when ASE is justified — single-tenant pattern, IL stamps, cost tradeoff)

App Service Environment v3 is a single-tenant App Service deployment inside your virtual network. It is not the default App Service choice. It is the expensive isolation choice. In multitenant App Service, your App Service Plan workers are dedicated to your plan, but the surrounding platform is shared. In an App Service Environment, the environment itself is dedicated to one customer and deployed into a VNet subnet. Apps run in Isolated v2 plans.

### When ASE v3 Is Justified

ASE v3 is justified when one or more of these are true:

- compliance requires single-tenant App Service hosting;
- inbound and outbound network isolation must be controlled at the environment boundary;
- the app estate needs very high scale in App Service;
- internal line-of-business apps need an internal virtual IP pattern;
- the organization has a platform team ready to own the ASE lifecycle;
- dedicated host isolation is specifically required and budgeted.

ASE v3 is not justified because:

- someone wants "more secure" without defining a requirement;
- a single app needs one private endpoint;
- the app only needs outbound access to SQL;
- the team dislikes public DNS;
- the app could use multitenant App Service with Private Endpoint and VNet integration.

### Internal Load Balancer Pattern

An internal App Service Environment uses an internal VIP. Apps are reachable through private networking instead of public internet exposure. A common pattern:

```text
corporate network / peered VNet
  -> private DNS
  -> internal Application Gateway
  -> internal App Service Environment app
  -> private downstream services
```

This pattern can satisfy enterprise network controls, but it also creates more platform ownership. DNS, certificates, gateway routing, ASE subnet sizing, route tables, and diagnostics all become platform responsibilities.

### Cost Tradeoff

ASE is a cost and commitment decision. Even an empty ASE can have baseline cost behavior. Isolated v2 workers are priced differently from multitenant App Service workers. Dedicated host options add more cost and constraints. Before approving ASE, compare it against:

- Premium v3 App Service with Private Endpoint and VNet integration;
- Container Apps environment with internal ingress;
- AKS with private ingress;
- a regional Application Gateway plus private App Service endpoints.

The question is not "Is ASE powerful?" It is. The question is "Which requirement forces ASE instead of multitenant App Service?"

## Production Gotchas (≥3 war stories: slot warm-up, app settings vs connection strings during swap, Premium v3 vs Premium v2 cold-migration)

### War Story 1: The Swap Was Fast, the App Was Not

A team deployed a new release to a staging slot and swapped immediately after the deployment completed. The swap itself finished quickly. For the next five minutes, users saw slow responses and intermittent `503` errors. The root cause was application warm-up. The app compiled templates, opened database pools, and built an in-memory cache on first request. The slot had passed a shallow `/` check that returned before the real dependencies were ready. The fix:

- configure `WEBSITE_SWAP_WARMUP_PING_PATH` to a real readiness path;
- make the readiness path prove the app can serve core traffic;
- keep expensive cache warm-up bounded and observable;
- run smoke tests against the slot before swap;
- watch `AppServiceConsoleLogs` and p95 latency immediately after swap.

The lesson: Slot swap changes routing. It does not magically make a cold app warm.

### War Story 2: The Connection String Moved With the Code

A staging slot used a staging database. Production used a production database. The team swapped a release and production immediately began writing to the staging database. The app code was fine. The slot setting model was wrong. The connection string was not sticky, so it moved with the release during swap. The fix:

- mark environment-specific settings as slot settings;
- review app settings and connection strings before every swap;
- keep a script or IaC definition for stickiness;
- use swap with preview for risky configuration changes;
- add a startup log line that records the expected database name without leaking secrets.

The lesson: Slots are safe only when configuration ownership is explicit.

### War Story 3: Premium v3 Was Not a Button

A team planned to scale from Premium v2 to Premium v3 during a performance incident. The desired Premium v3 SKU was not available for the existing app's deployment unit. The emergency "scale up" became a cold migration to a new plan and app in a different resource group or deployment stamp. That required DNS, custom domains, certificates, private endpoints, VNet integration, slot setup, diagnostics, and release validation. The fix:

- check Premium v3 availability before the incident;
- create new production plans in deployment units that support the desired v3 SKUs;
- rehearse migration with a non-production app;
- keep DNS TTL and rollback plans documented;
- do not sell a tier migration as a zero-risk scale-up.

The lesson: Scale-up can be a migration when the existing stamp cannot host the target tier.

### War Story 4: The Plan Scaled, the Database Fell Over

An autoscale rule added six workers during a traffic spike. HTTP queue length dropped for a few minutes. Then SQL throttling increased, API latency worsened, and 5xx errors climbed. The web tier was not the only bottleneck. Adding workers increased concurrent database pressure. The fix:

- include dependency capacity in autoscale reviews;
- add database metrics to the release dashboard;
- use connection pool limits and backpressure;
- load test the whole path, not only the web tier;
- scale the database or reduce concurrency before increasing max workers.

The lesson: Autoscale is not capacity planning for the whole system.

### War Story 5: "Consumption-Style" Expectations Caused Cold Starts

A team expected the app to behave like a serverless workload: cheap when idle and instantly fast when traffic returned. They used a low tier, disabled Always On, and accepted idle unload behavior. The first request after idle paid startup cost. Then new scale-out workers also had cold initialization under load. The fix:

- use Basic or higher with Always On for long-running web apps;
- use Premium v3 for serious production latency requirements;
- move true scale-to-zero workloads to Container Apps or Functions;
- warm new slots and new instances before routing critical traffic;
- keep startup work small and observable.

The lesson: App Service is a web app platform. If the requirement is scale-to-zero event economics, evaluate Container Apps or Functions instead of forcing App Service to behave like them.

## Decision Framework (App Service vs Container Apps vs AKS table; SKU vs Plan vs ASE table)

### App Service vs Container Apps vs AKS

| Question | App Service | Container Apps | AKS |
|---|---|---|---|
| What is the deployment unit? | Web app or API | Container app revision | Kubernetes workload |
| What is the strongest release primitive? | Deployment slots and swap | Revisions and traffic splitting | Deployment, StatefulSet, rollout controllers, GitOps |
| What is the scaling model? | Plan workers and autoscale rules | HTTP/event/KEDA-style scaling, often scale-to-zero | Cluster and workload autoscaling |
| Who owns the platform? | App team with light platform support | App team plus environment owners | Platform team |
| What is the main operational risk? | Shared plan capacity and config swaps | Revision, ingress, and scale-rule behavior | Cluster complexity |
| When is it the first pick? | Traditional web apps, enterprise APIs, slot rollback | New microservices, workers, event-driven containers | Kubernetes platform requirements |
| When should you hesitate? | Event-driven scale-to-zero microservices | Classic apps needing slot workflows and simple PaaS | Small apps without platform staff |

### SKU vs Plan vs ASE

| Need | Choose | Why |
|---|---|---|
| Learning or demo | Free or Basic | Keep cost low; do not treat it as production. |
| Small internal production app | Standard plan | Slots, Always On, and autoscale features become available. |
| Serious production web app | Premium v3 plan | Better performance, private networking fit, and production headroom. |
| Multiple low-risk apps with same owner | Shared Standard or Premium v3 plan | Cost-efficient if shared scaling is acceptable. |
| Noisy or critical app | Dedicated plan for that app | Isolates cost, capacity, and deployment effects. |
| Private inbound app | Private Endpoint on multitenant App Service | Usually enough without ASE. |
| Strict single-tenant network-isolated estate | ASE v3 with Isolated v2 plans | Use only when isolation requirement justifies cost. |

### Release Decision Checklist

Before choosing App Service, write the answers:

- What is the rollback mechanism?
- Which settings are sticky?
- What path warms the app?
- What tier supports the required features?
- Which apps share the plan?
- What is the max scale-out and why?
- Is inbound public, private, or both?
- How does outbound traffic reach dependencies?
- Which identity reads Key Vault, Storage, and SQL?
- Which dashboard decides keep, pause, or rollback?

## Did You Know? (3-5 bullets)

- Deployment slots run on the same App Service Plan workers as production, so staging activity can consume production capacity.
- VNet integration is outbound only; Private Endpoint is the usual private inbound pattern.
- Key Vault references reduce secret sprawl, but direct Entra token auth is better when the downstream service supports it.
- Premium v3 availability can depend on the app's existing deployment unit, so a scale-up can become a migration.
- Container Apps often beats App Service for new event-driven microservices, even though App Service is excellent for traditional web apps.

## Common Mistakes (5-7)

| Mistake | Why it happens | Better operator move |
|---|---|---|
| Putting every app in one App Service Plan | Sharing looks cheaper | Separate critical or noisy apps into their own plans. |
| Treating VNet integration as private inbound access | The name sounds bidirectional | Use VNet integration for outbound and Private Endpoint for inbound. |
| Swapping slots without reviewing sticky settings | The release process focuses on code | Review app settings and connection strings as part of the swap runbook. |
| Using `/` as the warm-up path | It is easy to curl | Use a readiness path that proves the app can serve core traffic. |
| Scaling out to fix every incident | More workers feel safe | Check database, storage, dependency, and queue pressure first. |
| Choosing AKS for a normal web app | Kubernetes is familiar to platform teams | Use App Service unless Kubernetes primitives are required. |
| Choosing App Service for every containerized microservice | Existing App Service knowledge is strong | Evaluate Container Apps when revisions, KEDA, and scale-to-zero matter. |

## Quiz (4 scenario questions with `<details>` answers; reasoning, not recall)

### Question 1

A team is building a new set of small containerized services. Each service releases independently. Workers scale from queue length. HTTP services should scale down aggressively outside business hours. The team does not need Kubernetes APIs. Which platform should be the first candidate?

A. App Service  
B. Container Apps  
C. AKS  
D. App Service Environment v3

<details>
<summary>Answer</summary>

**Correct: B.** Container Apps matches container revisions, event-driven scaling, and scale-to-zero economics without requiring the team to operate AKS. App Service can run containers, but the workload shape is microservice and worker oriented rather than slot-oriented web app hosting.

</details>

### Question 2

A production Web App uses a staging slot. The staging slot should use a staging database. Production should always use the production database. What must be true before swapping?

A. The database connection string must be marked as a slot setting.  
B. The staging slot must run on a separate App Service Plan.  
C. The app must use a Free tier plan.  
D. VNet integration must be disabled.

<details>
<summary>Answer</summary>

**Correct: A.** Environment-specific connection strings should stay with the slot. If the setting is not sticky, it can move with the release during swap and production can point to the wrong database.

</details>

### Question 3

An internal API must be reachable only from a hub VNet and on-prem networks connected through ExpressRoute. The same API must call a private SQL endpoint. Which networking combination best matches the requirement?

A. Hybrid Connection only  
B. VNet integration only  
C. Private Endpoint for inbound plus VNet integration for outbound  
D. Public access restriction only

<details>
<summary>Answer</summary>

**Correct: C.** Private Endpoint gives private inbound access to the app. VNet integration gives the app outbound access into the VNet path for private dependencies. Hybrid Connection is useful for one TCP endpoint, but it is not private inbound access.

</details>

### Question 4

During a traffic spike, an autoscale rule adds workers. CPU drops, but latency and 5xx errors increase. SQL metrics show throttling and connection pressure. What is the best reasoning?

A. Autoscale failed because workers cannot be added to App Service.  
B. The bottleneck moved to SQL, and more web workers increased dependency pressure.  
C. The app needs an App Service Environment v3 immediately.  
D. The only fix is to disable HTTPS.

<details>
<summary>Answer</summary>

**Correct: B.** Autoscaling the web tier can increase concurrent calls to downstream services. The operator should review database capacity, connection pooling, backpressure, and dependency metrics before raising max worker count further.

</details>

## Hands-On Exercise (Setup → 4-5 Tasks → Success Criteria; design exercises with Azure-sub note for actual provisioning)

This exercise is design-first. You can complete the architecture and runbook work without an Azure subscription. The optional provisioning steps require an Azure subscription and can create billable resources. Use a sandbox subscription only if you have permission.

### Setup

Create a working folder for your design notes:

```bash
mkdir -p app-service-operator-lab
cd app-service-operator-lab
```

Create these files:

```text
decision.md
slots-runbook.md
networking.md
autoscale.md
monitoring.kql
```

Use this scenario:

```text
Application: orders-api
Runtime: Node.js or .NET
Traffic: steady business traffic, 3x spike at 09:00 and 13:00
Release: weekly, rollback must be under 5 minutes
Dependencies: Azure SQL, Storage account, Key Vault
Inbound: public today, private-only target in six months
Team: app team owns code; platform team owns shared network and policies
```

### Task 1: Choose the Hosting Platform

In `decision.md`, compare App Service, Container Apps, and AKS. Write the decision in one paragraph. Include:

- why App Service is or is not the first candidate;
- what would make Container Apps better;
- what would make AKS justified;
- what rollback primitive the team will use.

### Task 2: Design the Plan and Slot Model

In `slots-runbook.md`, choose:

- plan tier;
- minimum worker count;
- whether the app shares a plan;
- production slot;
- staging slot name;
- warm-up path;
- rollback command;
- sticky settings list.

Then write a ten-step slot swap runbook. Include a stop condition that triggers rollback.

### Task 3: Design Networking

In `networking.md`, draw the inbound and outbound paths in text. Include:

- current public inbound model;
- target private inbound model;
- VNet integration subnet purpose;
- private endpoints for SQL, Storage, or Key Vault;
- DNS responsibility;
- whether Hybrid Connections are needed.

Explain why VNet integration alone is not enough for private inbound access.

### Task 4: Design Autoscale

In `autoscale.md`, write a scale plan with:

- minimum and maximum workers;
- CPU rule;
- memory rule;
- HTTP queue rule;
- weekday schedule rule;
- scale-in and scale-out cool-down;
- dependency capacity warning.

Explain what metric would make you stop increasing web workers and investigate SQL instead.

### Task 5: Write Monitoring Queries

In `monitoring.kql`, write:

- one `AppServiceHTTPLogs` query for 5xx errors by path;
- one `AppServiceHTTPLogs` query for latency percentiles;
- one `AppServiceConsoleLogs` query for startup errors after deployment;
- a short list of metric alerts.

Use the queries in this module as a starting point, but adapt names and time windows to the scenario.

### Optional Azure Provisioning

If you have an approved Azure subscription, provision a small non-production Web App and staging slot. Keep cost low. Delete resources when finished. Do not run production-scale Premium or ASE resources for this lab unless your organization explicitly approved the spend.

### Success Criteria

You are done when:

- `decision.md` explains why App Service, Container Apps, or AKS is the right first choice;
- `slots-runbook.md` can execute a release and rollback without guessing;
- `networking.md` separates inbound and outbound paths correctly;
- `autoscale.md` includes scale-out, scale-in, schedule, and cool-down logic;
- `monitoring.kql` contains at least three usable queries;
- your design names the top two failure modes and the evidence that would prove each one.

## Sources (10-12 citations from learn.microsoft.com/en-us/azure/app-service/* + adjacent paths)

- [Azure App Service overview](https://learn.microsoft.com/en-us/azure/app-service/overview)
- [Azure App Service plans](https://learn.microsoft.com/en-us/azure/app-service/overview-hosting-plans)
- [Set up staging environments in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/deploy-staging-slots)
- [Environment variables and app settings reference for Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/reference-app-settings)
- [Integrate your app with an Azure virtual network](https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration)
- [Use private endpoints for Azure App Service apps](https://learn.microsoft.com/en-us/azure/app-service/overview-private-endpoint)
- [Hybrid Connections in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/app-service-hybrid-connections)
- [Managed identities for Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity)
- [Use Key Vault references as app settings](https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references)
- [How to enable automatic scaling in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/manage-automatic-scaling)
- [Troubleshoot an App Service app with Azure Monitor](https://learn.microsoft.com/en-us/azure/app-service/tutorial-troubleshoot-monitor)
- [App Service Environment overview](https://learn.microsoft.com/en-us/azure/app-service/environment/app-service-app-service-environment-layered-security)

## Next Module (close the Azure Essentials section or link to enterprise-hybrid)

This closes the Azure Essentials sequence with the last major application-hosting decision point: web apps on App Service, containerized services on Container Apps, and Kubernetes platforms on AKS. From here, continue into enterprise and hybrid cloud patterns where these services become part of broader governance, network, identity, and platform operating models. Recommended next step: [Cloud Custodian -- Policy-as-Code Governance Across Multi-Cloud](../../enterprise-hybrid/module-10.11-cloud-custodian/), then revisit the Azure modules when designing policy guardrails for App Service Plans, private endpoints, managed identities, and diagnostic settings.
