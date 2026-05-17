---
title: "Module 3.13: Azure Application Gateway — Operator Path"
slug: cloud/azure-essentials/module-3.13-application-gateway
sidebar:
  order: 14
---

> **Complexity:** [COMPLEX]  
> **Time:** 60-90 min  
> **Prereqs:** [3.2-vnet](../module-3.2-vnet/), [3.5-dns](../module-3.5-dns/), [3.10-monitor](../module-3.10-monitor/)

## What You'll Be Able to Do

After completing this module, you will be able to:

- **Debug** Application Gateway failures by following a request through listener, WAF policy, routing rule, backend HTTP settings, probe, and backend pool.
- **Design** a regional ingress pattern that uses the right boundary: Application Gateway, Front Door, AGIC, Application Gateway for Containers, or an in-cluster ingress controller.
- **Evaluate** WAF, TLS, autoscaling, cost, logging, and migration choices before they become production incidents.

The emphasis is operational. You are not only learning which Azure resource to create; you are learning how to keep the resource understandable when many teams depend on it.

## Why This Module Matters

Application Gateway is often described as Azure's Layer 7 load balancer. That description is correct but incomplete. In production, it is a regional traffic appliance that combines HTTP routing, TLS termination, health probing, optional Web Application Firewall protection, autoscaling, and diagnostic logging.

That combination is valuable because it lets platform teams protect and route traffic before it reaches workloads. It is also risky because one gateway can become the shared failure point for many applications.

The [Application Gateway overview](https://learn.microsoft.com/en-us/azure/application-gateway/overview) is the product entry point. Operators need the next layer of understanding: what owns the hostname, where TLS terminates, how health is measured, what WAF rule blocked a request, and which logs prove the answer.

Consider a common incident. A checkout API returns `403` for some customers, `502` for others, and the application team reports that pods are ready. The gateway may be doing exactly what it was configured to do: WAF blocks a suspicious payload, the backend probe checks the wrong path, or backend TLS expects a different host name. Without a request-path model, each team debugs only its own layer.

Use this flow as your mental map:

```text
client
  -> DNS name
  -> frontend listener
  -> WAF policy
  -> routing rule
  -> backend HTTP settings
  -> health probe
  -> backend pool
  -> application
```

The operator goal is not to memorize every property. The goal is to know which property answers which question during a design review or an incident.

> **Pause and predict:** If a backend service is healthy at `https://api.internal.example.com/ready` but the gateway probe checks `/` with the wrong host header, what will the application team see, and what will the gateway see?

## When App Gateway, Front Door, or AKS Ingress

Start with the traffic boundary.

Application Gateway is regional and VNet-integrated. It is a strong fit when a workload needs regional HTTP routing, private backend access, WAF, TLS termination, and Azure Monitor diagnostics inside an Azure network boundary. The [components documentation](https://learn.microsoft.com/en-us/azure/application-gateway/application-gateway-components) is useful because each component is a separate operational lever.

Azure Front Door is global. It is a strong fit when users are distributed across regions, edge latency matters, global failover is required, or the application needs an anycast-style public entry point before traffic reaches regional origins.

AKS ingress is cluster-centered. It is a strong fit when Kubernetes teams need to own routes as Kubernetes objects and the cluster already has an accepted ingress or Gateway API layer.

Application Gateway for Containers sits between the last two ideas. It is Kubernetes-native, uses the ALB controller and Gateway API-style workflows, and is the forward-looking Application Gateway path for many container ingress designs.

Use this decision sequence:

1. If users need a global edge, evaluate Front Door first.
2. If traffic must enter a regional VNet and reach private backends, evaluate Application Gateway.
3. If the route lifecycle is owned by Kubernetes teams, evaluate AGIC or Application Gateway for Containers.
4. If the service is internal to the cluster and does not need Azure-managed WAF, use an in-cluster ingress or Gateway API controller.

Comparison tables should not imply one service wins everywhere:

| Requirement | Better first candidate | Why |
|---|---|---|
| Global public web app with multi-region failover | Front Door | The boundary is global before traffic reaches a region. |
| Regional private API in a hub-and-spoke VNet | Application Gateway | The boundary is regional and close to private backends. |
| Existing App Gateway fronts both VMs and AKS | AGIC plus Application Gateway | Reuses the regional gateway while AKS expresses ingress intent. |
| New AKS ingress platform with Gateway API ownership | Application Gateway for Containers | Separates platform-owned gateways from app-owned routes. |
| Cluster-only internal service | AKS ingress or Gateway API controller | A managed regional edge may add cost without adding value. |

Worked example: a public retail site has users in North America and Europe, but each regional API is private inside its VNet. A reasonable design is Front Door at the global edge and Application Gateway in each region. Front Door handles global entry and failover. Application Gateway handles regional WAF policy, private backend routing, and VNet integration.

The same pattern would be overkill for an internal admin tool used by one operations team in one region. There, a private Application Gateway may be enough, or an internal AKS ingress may be enough if the tool never needs a shared regional edge.

> **Stop and think:** Which team owns each boundary in your organization: public DNS, global edge, regional listener, WAF policy, Kubernetes route, certificate, and incident dashboard? If the answer is "everyone," the design needs clearer ownership.

## Provisioning Patterns

Application Gateway has many nested child resources. Provision it as code so listener, rule, probe, WAF, and certificate changes are reviewable together.

A production-shaped deployment normally includes:

- a dedicated Application Gateway subnet;
- a Standard public IP for public gateways;
- a private frontend when internal ingress is required;
- a v2 SKU for new deployments;
- autoscale bounds;
- a separate WAF policy;
- listener certificates from Key Vault;
- explicit backend probes;
- diagnostic settings to Log Analytics.

Do not share the Application Gateway subnet with other resources. Size the subnet for scale-out and future changes. Many teams reserve at least `/24` for production v2 gateways so capacity and migration work do not become emergency subnet surgery.

### Terraform Example

This snippet is intentionally compact. It shows the relationships an operator must review, not a full reusable module.

```hcl
resource "azurerm_user_assigned_identity" "appgw" {
  name                = "id-appgw-prod-eus"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

resource "azurerm_public_ip" "appgw" {
  name                = "pip-appgw-prod-eus"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = ["1", "2", "3"]
}

resource "azurerm_web_application_firewall_policy" "appgw" {
  name                = "waf-appgw-prod-eus"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  policy_settings {
    enabled                     = true
    mode                        = "Prevention"
    request_body_check          = true
    max_request_body_size_in_kb = 128
  }

  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.2"
    }
  }
}

resource "azurerm_application_gateway" "appgw" {
  name                = "agw-prod-eus"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  zones               = ["1", "2", "3"]
  firewall_policy_id  = azurerm_web_application_firewall_policy.appgw.id

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.appgw.id]
  }

  sku {
    name = "WAF_v2"
    tier = "WAF_v2"
  }

  autoscale_configuration {
    min_capacity = 2
    max_capacity = 10
  }

  gateway_ip_configuration {
    name      = "gw-ipcfg"
    subnet_id = azurerm_subnet.appgw.id
  }

  frontend_ip_configuration {
    name                 = "public-fe"
    public_ip_address_id = azurerm_public_ip.appgw.id
  }

  frontend_port {
    name = "https-443"
    port = 443
  }

  ssl_certificate {
    name                = "cert-api"
    key_vault_secret_id = azurerm_key_vault_certificate.api.secret_id
  }

  backend_address_pool {
    name  = "pool-api"
    fqdns = ["api.internal.contoso.example"]
  }

  probe {
    name                                      = "probe-api"
    protocol                                  = "Https"
    path                                      = "/ready"
    interval                                  = 30
    timeout                                   = 10
    unhealthy_threshold                       = 3
    pick_host_name_from_backend_http_settings = true
  }

  backend_http_settings {
    name                                = "https-api"
    protocol                            = "Https"
    port                                = 443
    probe_name                          = "probe-api"
    request_timeout                     = 30
    pick_host_name_from_backend_address = true
    cookie_based_affinity               = "Disabled"
  }

  http_listener {
    name                           = "lst-api"
    frontend_ip_configuration_name = "public-fe"
    frontend_port_name             = "https-443"
    protocol                       = "Https"
    host_name                      = "api.contoso.example"
    ssl_certificate_name           = "cert-api"
  }

  request_routing_rule {
    name                       = "rule-api"
    rule_type                  = "Basic"
    priority                   = 100
    http_listener_name         = "lst-api"
    backend_address_pool_name  = "pool-api"
    backend_http_settings_name = "https-api"
  }
}
```

The design choice is to keep the WAF policy separate from the gateway. That lets security reviewers focus on WAF behavior while platform reviewers focus on listeners, routes, and backends.

The probe uses `/ready`, not `/`. A root path may redirect, render a marketing page, or depend on optional systems. A readiness endpoint should answer whether this backend should receive traffic now.

### Bicep Example

The Bicep model is also nested. In production, split this into modules only when ownership becomes clearer.

```bicep
param location string = resourceGroup().location
param appGatewayName string = 'agw-prod-eus'
param appGwSubnetId string
param keyVaultSecretId string
param backendFqdn string = 'api.internal.contoso.example'

resource publicIp 'Microsoft.Network/publicIPAddresses@2023-11-01' = {
  name: 'pip-appgw-prod-eus'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
  zones: [
    '1'
    '2'
    '3'
  ]
}

resource wafPolicy 'Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies@2023-11-01' = {
  name: 'waf-appgw-prod-eus'
  location: location
  properties: {
    policySettings: {
      enabledState: 'Enabled'
      mode: 'Prevention'
      requestBodyCheck: true
    }
    managedRules: {
      managedRuleSets: [
        {
          ruleSetType: 'OWASP'
          ruleSetVersion: '3.2'
        }
      ]
    }
  }
}

resource appGateway 'Microsoft.Network/applicationGateways@2023-11-01' = {
  name: appGatewayName
  location: location
  properties: {
    firewallPolicy: {
      id: wafPolicy.id
    }
    sku: {
      name: 'WAF_v2'
      tier: 'WAF_v2'
    }
    autoscaleConfiguration: {
      minCapacity: 2
      maxCapacity: 10
    }
    gatewayIPConfigurations: [
      {
        name: 'gw-ipcfg'
        properties: {
          subnet: {
            id: appGwSubnetId
          }
        }
      }
    ]
    frontendIPConfigurations: [
      {
        name: 'public-fe'
        properties: {
          publicIPAddress: {
            id: publicIp.id
          }
        }
      }
    ]
    frontendPorts: [
      {
        name: 'https-443'
        properties: {
          port: 443
        }
      }
    ]
    sslCertificates: [
      {
        name: 'cert-api'
        properties: {
          keyVaultSecretId: keyVaultSecretId
        }
      }
    ]
    backendAddressPools: [
      {
        name: 'pool-api'
        properties: {
          backendAddresses: [
            {
              fqdn: backendFqdn
            }
          ]
        }
      }
    ]
    probes: [
      {
        name: 'probe-api'
        properties: {
          protocol: 'Https'
          path: '/ready'
          interval: 30
          timeout: 10
          unhealthyThreshold: 3
          pickHostNameFromBackendHttpSettings: true
        }
      }
    ]
    backendHttpSettingsCollection: [
      {
        name: 'https-api'
        properties: {
          protocol: 'Https'
          port: 443
          requestTimeout: 30
          pickHostNameFromBackendAddress: true
          probe: {
            id: resourceId('Microsoft.Network/applicationGateways/probes', appGatewayName, 'probe-api')
          }
        }
      }
    ]
    httpListeners: [
      {
        name: 'lst-api'
        properties: {
          protocol: 'Https'
          hostName: 'api.contoso.example'
          frontendIPConfiguration: {
            id: resourceId('Microsoft.Network/applicationGateways/frontendIPConfigurations', appGatewayName, 'public-fe')
          }
          frontendPort: {
            id: resourceId('Microsoft.Network/applicationGateways/frontendPorts', appGatewayName, 'https-443')
          }
          sslCertificate: {
            id: resourceId('Microsoft.Network/applicationGateways/sslCertificates', appGatewayName, 'cert-api')
          }
        }
      }
    ]
    requestRoutingRules: [
      {
        name: 'rule-api'
        properties: {
          ruleType: 'Basic'
          priority: 100
          httpListener: {
            id: resourceId('Microsoft.Network/applicationGateways/httpListeners', appGatewayName, 'lst-api')
          }
          backendAddressPool: {
            id: resourceId('Microsoft.Network/applicationGateways/backendAddressPools', appGatewayName, 'pool-api')
          }
          backendHttpSettings: {
            id: resourceId('Microsoft.Network/applicationGateways/backendHttpSettingsCollection', appGatewayName, 'https-api')
          }
        }
      }
    ]
  }
}
```

Before merging a provisioning change, review subnet size, SKU, WAF policy attachment, certificate source, probe paths, rule priorities, diagnostics, and rollback plan.

## WAF Policy Design

Application Gateway WAF is a policy system, not a checkbox. The [WAF overview](https://learn.microsoft.com/en-us/azure/web-application-firewall/ag/ag-overview) explains the managed-rule model; operators need to understand how policy changes are tested, scoped, and rolled back.

Start with managed OWASP rules. Use Detection mode while learning a new application's request profile. Move to Prevention mode when the false-positive path is understood. Do not leave production in Detection mode indefinitely unless the risk is explicitly accepted.

A mature WAF workflow has four principles:

- custom rules are used for business-specific controls;
- managed rules are tuned narrowly;
- false positives are investigated with logs, not guesses;
- every exclusion has an owner and review date.

### Custom Rule Example

This custom rule blocks `/admin` unless the source IP is in the operations CIDR. It reduces exposure but does not replace application authentication.

```hcl
resource "azurerm_web_application_firewall_policy" "appgw" {
  name                = "waf-appgw-prod-eus"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  policy_settings {
    enabled = true
    mode    = "Prevention"
  }

  custom_rules {
    name      = "BlockAdminOutsideOps"
    priority  = 10
    rule_type = "MatchRule"
    action    = "Block"

    match_conditions {
      match_variables {
        variable_name = "RequestUri"
      }
      operator     = "BeginsWith"
      match_values = ["/admin"]
    }

    match_conditions {
      match_variables {
        variable_name = "RemoteAddr"
      }
      operator           = "IPMatch"
      negation_condition = true
      match_values       = ["10.20.0.0/16"]
    }
  }

  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.2"
    }
  }
}
```

Why this shape? The URI condition identifies the sensitive surface. The source-IP condition limits exposure to operations networks. The application still owns identity and authorization.

### Tuned Rule and Rate-Limit Example

False positives should be narrowed, not bulldozed. Suppose a legacy search client sends a header named `X-Legacy-Search` that trips one SQL injection rule. A per-rule exclusion keeps the rest of the SQLi group active:

```bash
az network application-gateway waf-policy managed-rule exclusion rule-set add \
  --resource-group rg-edge-prod \
  --policy-name waf-appgw-prod-eus \
  --type OWASP \
  --version 3.2 \
  --group-name "REQUEST-942-APPLICATION-ATTACK-SQLI" \
  --rule-ids 942430 \
  --match-variable "RequestHeaderValues" \
  --match-operator "Equals" \
  --selector "X-Legacy-Search"
```

Rate limiting is a custom-rule problem. This example blocks a login path after 100 matching requests in the configured window, grouping all matching traffic together:

```bash
az network application-gateway waf-policy custom-rule create \
  --resource-group rg-edge-prod \
  --policy-name waf-appgw-prod-eus \
  --name LoginRateLimit \
  --priority 99 \
  --rule-type RateLimitRule \
  --action Block \
  --rate-limit-threshold 100 \
  --group-by-user-session '[{"groupByVariables":[{"variableName":"None"}]}]'

az network application-gateway waf-policy custom-rule match-condition add \
  --resource-group rg-edge-prod \
  --policy-name waf-appgw-prod-eus \
  --name LoginRateLimit \
  --match-variables RequestUri \
  --operator Contains \
  --value "/login"
```

For geo-blocking, use `RemoteAddr` with `GeoMatch` and document the business owner. Country rules are easy to add and easy to forget.

### False-Positive Triage Steps

Use this sequence when valid traffic is blocked:

1. Capture timestamp, URL, method, client IP, user action, and correlation ID.
2. Confirm the gateway returned the response; not every `403` is WAF.
3. Query WAF logs for rule ID, action, message, match variable, and selector.
4. Reproduce safely in staging or Detection mode when possible.
5. Decide whether the request is unsafe, malformed, or legitimately blocked by a broad rule.
6. Apply the narrowest exclusion: rule, variable, selector, path, listener, or policy scope.
7. Return to Prevention mode and document why the exception exists.

The [WAF customization guidance](https://learn.microsoft.com/en-us/azure/web-application-firewall/ag/application-gateway-customize-waf-rules-portal) is useful when translating a portal investigation back into code.

> **Pause and predict:** If a checkout payload trips a SQL injection rule because a product name contains suspicious punctuation, which is safer: disabling the SQLi rule group globally or excluding one selector for one path after log review?

## Backend Pools: AKS Integration — AGIC vs AGfC

AKS integration is a control-plane decision. You are choosing who expresses routing intent and who is allowed to mutate the edge.

AGIC, the Application Gateway Ingress Controller, watches Kubernetes Ingress resources and programs an existing Application Gateway. The [AGIC overview](https://learn.microsoft.com/en-us/azure/application-gateway/ingress-controller-overview) remains important because many production clusters use it today.

Application Gateway for Containers is the successor path for Kubernetes-first Application Gateway designs. The [Application Gateway for Containers overview](https://learn.microsoft.com/en-us/azure/application-gateway/for-containers/overview) describes the newer model built around the ALB controller and Gateway API-style resources.

Backend pools are not only for AKS. Operators commonly mix backend types during migrations:

| Backend pattern | Pool entry | Health probe concern | HTTPS-to-backend concern |
|---|---|---|---|
| AKS with AGIC | Pod IPs from Kubernetes endpoints | Align AGIC annotations with pod readiness. | Backend cert and protocol must match AGIC support. |
| App Service | FQDN or private endpoint path | Pick host name from backend settings for multi-tenant hostnames. | SNI and host header usually need the app hostname. |
| VMs or VMSS | NIC, VMSS, private IP, or FQDN | Probe the real app readiness path, not just `/`. | Upload trusted root certs for private CA chains. |
| Mixed migration | Separate pool per backend class | Do not reuse one probe across unlike apps. | Keep backend settings explicit per pool. |

Pick AGIC when:

- an existing Application Gateway already fronts the environment;
- the platform team accepts ARM-level gateway updates from the controller;
- Ingress resources and AGIC annotations are already standardized;
- the gateway also fronts non-Kubernetes backends.

Pick Application Gateway for Containers when:

- you are designing a new AKS ingress platform;
- Gateway API ownership matters;
- app teams need route objects while platform teams own gateways;
- faster Kubernetes route and backend updates are important;
- you can invest in new runbooks and migration testing.

### AGIC Ingress Example

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: orders
  namespace: apps
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
    appgw.ingress.kubernetes.io/backend-protocol: "https"
    appgw.ingress.kubernetes.io/health-probe-path: "/ready"
    appgw.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - orders.contoso.example
      secretName: orders-tls
  rules:
    - host: orders.contoso.example
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: orders
                port:
                  number: 443
```

The important parts are not the annotations themselves. The important contract is that Kubernetes now declares host, path, backend protocol, and probe behavior that will affect an Azure gateway.

### AGfC Gateway API Example

Your installed GatewayClass name may differ. Confirm it from your cluster before applying.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: shared-edge
  namespace: platform
spec:
  gatewayClassName: azure-alb-external
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      hostname: "*.apps.contoso.example"
      allowedRoutes:
        namespaces:
          from: Selector
          selector:
            matchLabels:
              traffic.kubedojo.io/allowed: "true"
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: orders
  namespace: apps
spec:
  parentRefs:
    - name: shared-edge
      namespace: platform
  hostnames:
    - orders.apps.contoso.example
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: orders
          port: 8080
```

This example separates ownership. The platform namespace owns the Gateway. The app namespace owns the HTTPRoute only if route policy allows it. That is easier to review than a shared Ingress object with many annotations.

> **Stop and think:** In a shared cluster, what outage can happen if any namespace can claim any hostname on the shared gateway?

## TLS Termination + Key Vault Cert Sync

Application Gateway can terminate TLS at the listener and then connect to backends over HTTP or HTTPS. For production, prefer HTTPS to the backend unless there is a documented reason not to.

The [TLS overview](https://learn.microsoft.com/en-us/azure/application-gateway/ssl-overview) explains listener-side TLS. The [backend HTTP settings documentation](https://learn.microsoft.com/en-us/azure/application-gateway/configuration-http-settings) explains backend protocol, host name, timeout, and probe behavior.

Key Vault-backed certificates are the usual production pattern. The [Key Vault certificate integration documentation](https://learn.microsoft.com/en-us/azure/application-gateway/key-vault-certs) covers the managed identity and secret-reference model.

### Rotation Gotchas

Certificate rotation has three timelines: issuance, Key Vault version creation, and Application Gateway sync. Those are not the same event.

Use versionless secret IDs when automatic rotation is intended. Use versioned IDs only when pinning a specific certificate version is deliberate.

Monitor the certificate served by the listener, not just the certificate stored in Key Vault. A renewed Key Vault object does not help users if the gateway cannot read it or has not picked it up.

### Chain Order

Certificate chain problems are painful because some clients cache intermediates and others do not. Test with a clean client and verify the leaf certificate, intermediates, hostname, expiry, and trust chain.

### Backend mTLS

Backend TLS validates the backend to the gateway. Backend mTLS also validates the gateway to the backend. Use mTLS when the backend requires client-certificate authentication or compliance demands it, but only if certificate lifecycle automation is mature enough to operate it.

TLS troubleshooting sequence:

1. DNS resolves to the expected frontend.
2. Listener serves the expected certificate.
3. Certificate includes the hostname and is not expired.
4. Chain is complete.
5. Gateway identity can read the Key Vault secret.
6. Backend setting uses the expected protocol, port, host name, and SNI behavior.
7. Probe status matches application readiness.

## Autoscaling + Cost

Application Gateway v2 supports autoscaling. The [autoscaling documentation](https://learn.microsoft.com/en-us/azure/application-gateway/application-gateway-autoscaling-zone-redundant) is the starting point for how minimum and maximum capacity behave.

Autoscaling does not remove capacity planning. You still choose minimum capacity for baseline reliability and maximum capacity for cost and blast-radius control.

Capacity units represent consumption across compute, persistent connections, and throughput. The [pricing documentation](https://learn.microsoft.com/en-us/azure/application-gateway/understanding-pricing) defines one capacity unit as the highest pressure among one compute unit, 2,500 persistent connections, or 2.22 Mbps throughput. A traffic pattern with many long-lived connections can stress the gateway differently than a burst of small requests.

```text
capacity_units = max(
  current_compute_units,
  current_connections / 2500,
  throughput_mbps / 2.22
)
```

Worked example: if the gateway reports 18 compute units, 50,000 current connections, and 16 Mbps throughput, the estimate is `max(18, 20, 7.2)`, so current capacity pressure is about 20 capacity units. If autoscale minimum is two instances, you are already reserving roughly that baseline because each instance maps to 10 reserved capacity units.

Autoscaling rules of thumb:

- keep production minimum capacity high enough for normal traffic;
- set maximum capacity deliberately and alert before it is reached;
- load test WAF-enabled traffic, not just pass-through traffic;
- isolate noisy or regulated applications when shared capacity is risky;
- treat scale events as signals worth reviewing after incidents.

Cost-lens checklist:

- Does the design need both Front Door and Application Gateway, or only one boundary?
- Are dev and test gateways scaled down with explicit maximums?
- Are zones required for the workload and region?
- Are Log Analytics retention and WAF log volume estimated?
- Are Key Vault, public IP, DNS, data transfer, and monitoring included?
- Is a dedicated gateway justified by isolation, compliance, or ownership?
- Is the WAF policy scoped so inspection work matches real exposure?

Cost decisions should be tied to reliability decisions. A shared gateway may be cheaper, but one noisy tenant can affect many services. Dedicated gateways cost more, but they can make ownership and blast radius clearer.

## Monitoring + Diagnostics

Application Gateway without logs is a black box. Enable diagnostics before sending production traffic.

Send access logs and WAF logs to Log Analytics. Route metrics to Azure Monitor alerts. Use the [monitoring documentation](https://learn.microsoft.com/en-us/azure/application-gateway/monitor-application-gateway) and [diagnostics documentation](https://learn.microsoft.com/en-us/azure/application-gateway/application-gateway-diagnostics) to confirm categories for your SKU and collection mode.

A useful dashboard answers these questions:

- Are requests reaching the gateway?
- Which listeners and backend pools are active?
- Which backends are unhealthy?
- Which status codes changed?
- Which WAF rules are firing?
- Are capacity units, connections, or latency rising?

### KQL: 5xx by Backend Pool

```kusto
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.NETWORK"
| where Category == "ApplicationGatewayAccessLog"
| where httpStatus_d between (500 .. 599)
| summarize Requests=count(), ExampleUri=any(requestUri_s)
  by bin(TimeGenerated, 5m), Resource, backendPoolName_s, httpStatus_d
| order by TimeGenerated desc
```

This query starts from user-visible failure and groups by backend pool. If one pool dominates, the incident is probably not gateway-wide.

### KQL: WAF Blocks by Rule

```kusto
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.NETWORK"
| where Category == "ApplicationGatewayFirewallLog"
| where action_s in ("Blocked", "Block")
| summarize Blocks=count(), ExampleMessage=any(message_s)
  by bin(TimeGenerated, 15m), Resource, ruleId_s, requestUri_s, clientIp_s
| order by Blocks desc
```

This query turns "the WAF broke checkout" into evidence: rule ID, URI, client IP, count, and time window.

### KQL: Latency and Error Trend

```kusto
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.NETWORK"
| where Category == "ApplicationGatewayAccessLog"
| summarize
    Requests=count(),
    P95LatencyMs=percentile(timeTaken_d * 1000, 95),
    Errors=countif(httpStatus_d >= 500)
  by bin(TimeGenerated, 10m), backendPoolName_s
| extend ErrorRate = todouble(Errors) / todouble(Requests)
| order by TimeGenerated desc
```

Metric alerts should cover unhealthy host count, 5xx spikes, WAF blocked request spikes, capacity approaching maximum, current connections, response latency, and certificate expiration inventory.

## Production Gotchas

### Gotcha 1: v1 to v2 Is a Migration

Moving from a legacy v1 gateway to v2 is not a casual SKU toggle. Treat it as a migration with new capacity, copied configuration, certificate validation, WAF review, DNS cutover, rollback, and parallel observability. The [v1/v2 migration guidance](https://learn.microsoft.com/en-us/azure/application-gateway/migrate-v1-v2) exists because the change affects more than a billing label.

### Gotcha 2: WAF Blocks Valid Traffic

During a launch, a form field triggers a managed WAF rule. The fastest action is to disable a rule group globally. The operator action is slower but safer: find the rule ID, confirm the match variable and selector, reproduce safely, scope the exclusion to the affected path or policy, and document the reason.

### Gotcha 3: Certificate Sync Timing

A certificate is renewed in Key Vault, but the gateway still serves the old certificate. The likely causes are identity access, versioned secret IDs, sync timing, or an incomplete certificate object. Always monitor the served listener certificate and rehearse renewal before expiration week.

### Gotcha 4: Probe Contract Drift

An application changes readiness from `/ready` to `/healthz`, or makes readiness depend on a database that is not required for degraded service. Application Gateway marks backends unhealthy because the probe contract changed. Treat probes as release contracts, not incidental URLs.

## Decision Framework

### App Gateway vs Front Door

| Decision factor | Application Gateway | Front Door |
|---|---|---|
| Primary boundary | Regional VNet edge | Global public edge |
| Best fit | Private regional apps, regional APIs, AKS ingress | Global web apps, multi-region failover |
| Backend reachability | Strong for private VNet backends | Strong for origin groups and edge routing |
| WAF placement | Regional | Global edge |
| Latency model | Users reach a regional gateway | Users reach a nearby edge |
| Operational risk | Regional blast radius | Broad edge-config blast radius |
| Use both when | Regional private ingress still matters | Global routing needs protected regional origins |

### SKU v1 vs v2

| Decision factor | v1 | v2 |
|---|---|---|
| New deployments | Avoid for modern production | Preferred default |
| Autoscaling | Legacy behavior | Built-in v2 autoscaling |
| Zone redundancy | Limited compared with v2 | Supported in eligible regions |
| Public IP model | Legacy | Standard public IP model |
| Feature investment | Legacy | Current strategic path |
| Operator action | Stabilize and migrate | Standardize and automate |

## Did You Know?

- Application Gateway is regional even when it has a public frontend.
- Detection mode logs WAF matches without blocking, which is useful during onboarding.
- A backend can be healthy in Kubernetes but unhealthy to Application Gateway because of host header, path, TLS, or probe status mismatch.
- Versionless Key Vault secret IDs are usually preferred when automatic certificate rotation is intended.

## Common Mistakes

| Mistake | Why It Happens | How to Fix It |
|---|---|---|
| Using `/` as a health probe because it is easy to remember | The default path responds during early testing | Probe the app's real readiness endpoint and expected host header. |
| Creating an undersized Application Gateway subnet | Teams size for today's instance count | Reserve subnet space for max autoscale, private frontend IPs, and v2 migration. |
| Leaving WAF in Detection mode forever | Teams fear false positives | Review logs, tune narrow exclusions, then move to Prevention with rollback. |
| Disabling broad WAF rule groups for one false positive | Incident pressure rewards fast unblocks | Use per-rule exclusions tied to a selector, path, and owner. |
| Pinning a Key Vault certificate version accidentally | Scripts copy the full secret ID | Use versionless secret IDs for normal rotation. |
| Letting AGIC and Terraform fight over gateway child resources | Both tools seem authoritative | Give controller-generated listeners, pools, and rules one owner. |
| Choosing Front Door or Application Gateway without naming the traffic boundary first | Feature lists look similar | Decide global edge, regional VNet edge, or cluster ingress before selecting product. |

## Quiz

### Question 1

A private regional API runs in AKS. Users connect through corporate networks. The platform team wants WAF, Key Vault-backed TLS, private backend access, and Azure Monitor diagnostics. Which entry point is the best first candidate?

A. Azure Front Door only
B. Application Gateway with AKS integration
C. Public Kubernetes LoadBalancer service
D. Azure Traffic Manager only

<details>
<summary>Answer</summary>

**Correct: B.** The workload is regional and private-backend oriented. Application Gateway can sit in the VNet, terminate TLS, apply WAF policy, and integrate with AKS.

</details>

### Question 2

Checkout POST requests are blocked after WAF moves to Prevention mode. Logs show one managed rule firing on one request field. What should the operator do first?

A. Disable the whole managed rule group globally
B. Move the policy to Detection forever
C. Apply the narrowest justified exclusion after confirming rule ID, field, selector, and path
D. Remove WAF from the listener

<details>
<summary>Answer</summary>

**Correct: C.** The evidence points to a scoped false positive. Broad disables reduce protection for unrelated traffic.

</details>

### Question 3

A new multi-team AKS platform wants platform engineers to own listeners and application teams to own routes only for allowed namespaces. Which model best expresses that ownership?

A. One public LoadBalancer service per namespace
B. AGIC annotations on arbitrary Ingress objects without admission policy
C. Gateway and HTTPRoute resources through Application Gateway for Containers
D. Manual listener edits in the portal after every release

<details>
<summary>Answer</summary>

**Correct: C.** Gateway API separates infrastructure-owned Gateway configuration from application-owned HTTPRoute configuration, which matches the ownership requirement.

</details>

### Question 4

A listener still serves an old certificate after a renewed certificate appears in Key Vault. What should you check first?

A. Backend replica count
B. Gateway identity access and whether the listener uses a versioned or versionless secret ID
C. DNS MX records
D. WAF CRS version

<details>
<summary>Answer</summary>

**Correct: B.** Certificate sync depends on secret access and the referenced secret ID. Backend replicas, MX records, and WAF rules do not explain the listener certificate.

</details>

## Hands-On Exercise

This exercise is local-first. You can complete the Kubernetes reasoning with `kind` or `minikube`. The Azure CLI section is optional and requires an Azure subscription with approval to create billable resources.

### Setup

Create a local cluster with `kind`:

```bash
kind create cluster --name appgw-operator
```

Fallback with `minikube`:

```bash
minikube start -p appgw-operator
```

Create a sample workload:

```bash
kubectl create namespace apps
kubectl -n apps create deployment orders --image=nginx:1.27
kubectl -n apps expose deployment orders --port=8080 --target-port=80
kubectl -n apps get deploy,svc
```

This does not create Azure resources. It gives you local Kubernetes objects for route-design practice.

### Tasks

1. Draw the request path for `orders.contoso.example`: DNS, listener, WAF policy, routing rule, backend setting, probe, service, pod.
2. Write an AGIC-style Ingress for the local `orders` service with host `orders.contoso.example` and probe path `/ready`.
3. Write a Gateway API HTTPRoute for `orders.apps.contoso.example` that attaches to a platform-owned Gateway named `shared-edge`.
4. Draft a WAF false-positive runbook using the KQL queries from this module.
5. Decide whether AGIC or Application Gateway for Containers is a better starting point for a new multi-team AKS ingress platform, and explain why.

### Azure Subscription Note

Only run these commands if you have an Azure subscription and permission to create billable networking resources:

```bash
az group create \
  --name rg-appgw-operator-lab \
  --location eastus

az network vnet create \
  --resource-group rg-appgw-operator-lab \
  --name vnet-appgw-operator-lab \
  --address-prefixes 10.42.0.0/16 \
  --subnet-name snet-appgw \
  --subnet-prefixes 10.42.0.0/24

az network public-ip create \
  --resource-group rg-appgw-operator-lab \
  --name pip-appgw-operator-lab \
  --sku Standard \
  --allocation-method Static
```

Clean up optional Azure resources when finished:

```bash
az group delete \
  --name rg-appgw-operator-lab \
  --yes
```

### Success Criteria

- Your diagram separates global, regional, and Kubernetes boundaries.
- Your Ingress manifest makes host, service, and probe intent clear.
- Your HTTPRoute answer explains who owns the parent Gateway.
- Your WAF runbook requires logs before exclusions.
- Your AGIC vs AGfC answer explains ownership and rollout behavior, not just product names.

## Sources

- [Azure Application Gateway overview](https://learn.microsoft.com/en-us/azure/application-gateway/overview)
- [Application Gateway autoscaling and zone redundancy](https://learn.microsoft.com/en-us/azure/application-gateway/application-gateway-autoscaling-zone-redundant)
- [Understanding pricing for Azure Application Gateway and Web Application Firewall](https://learn.microsoft.com/en-us/azure/application-gateway/understanding-pricing)
- [Application Gateway TLS overview](https://learn.microsoft.com/en-us/azure/application-gateway/ssl-overview)
- [Use Key Vault certificates with Application Gateway](https://learn.microsoft.com/en-us/azure/application-gateway/key-vault-certs)
- [Application Gateway backend HTTP settings](https://learn.microsoft.com/en-us/azure/application-gateway/configuration-http-settings)
- [Monitor Application Gateway](https://learn.microsoft.com/en-us/azure/application-gateway/monitor-application-gateway)
- [Application Gateway WAF overview](https://learn.microsoft.com/en-us/azure/web-application-firewall/ag/ag-overview)
- [Customize WAF rules for Application Gateway](https://learn.microsoft.com/en-us/azure/web-application-firewall/ag/application-gateway-customize-waf-rules-portal)
- [Application Gateway Ingress Controller overview](https://learn.microsoft.com/en-us/azure/application-gateway/ingress-controller-overview)
- [Application Gateway for Containers overview](https://learn.microsoft.com/en-us/azure/application-gateway/for-containers/overview)
- [Migrate Azure Application Gateway and WAF from v1 to v2](https://learn.microsoft.com/en-us/azure/application-gateway/migrate-v1-v2)

## Next Module

Module 3.14 is not present in this checkout. Continue with the [Enterprise Hybrid Cloud track](../../enterprise-hybrid/).
