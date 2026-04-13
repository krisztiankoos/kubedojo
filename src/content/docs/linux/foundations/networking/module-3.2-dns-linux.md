---
title: "Module 3.2: DNS in Linux"
slug: linux/foundations/networking/module-3.2-dns-linux
sidebar:
  order: 3
lab:
  id: "linux-3.2-dns"
  url: "https://killercoda.com/kubedojo/scenario/linux-3.2-dns"
  duration: "30 min"
  difficulty: "intermediate"
  environment: "ubuntu"
---

> **Linux Foundations** | Complexity: `[HIGH]` | Time: 45-60 min

## Prerequisites

Before starting this module:
- **Required**: [Module 3.1: TCP/IP Essentials](../module-3.1-tcp-ip-essentials/)
- **Helpful**: Basic understanding of networking concepts and command-line interfaces.

## What You'll Be Able to Do

After completing this module, you will be able to:
- **Diagnose** common DNS resolution failures in Linux environments, leveraging `/etc/hosts` and `/etc/resolv.conf`.
- **Debug** complex DNS issues within Kubernetes clusters using `kubectl` and specialized tools like `dig` and `nslookup`.
- **Evaluate** the impact of `ndots` and search domains on DNS performance and resolution order in both bare-metal and containerized setups.
- **Implement** effective strategies for DNS caching and cache invalidation to optimize application connectivity and ensure service resilience.

## Why This Module Matters

In October 2021, a configuration update at Facebook (now Meta) led to a global outage of its services, including WhatsApp, Instagram, and Messenger, for nearly six hours. The root cause? A DNS issue. Specifically, a faulty configuration change inadvertently severed connections between Meta's DNS servers and the broader internet. This single point of failure cascaded, rendering billions of users unable to access services and costing the company an estimated $100 million in revenue, alongside a significant blow to its reputation.

This incident, far from unique, dramatically illustrates a fundamental truth in modern computing: DNS is the invisible backbone of nearly all network communication. Whether you're accessing a public website, communicating with a cloud API, or ensuring microservices can discover each other within a Kubernetes cluster, DNS is the silent arbiter. When DNS malfunctions, the internet as we know it effectively grinds to a halt. Understanding DNS is not just about knowing a few commands; it's about mastering the core mechanism that connects applications to their destinations, making it an indispensable skill for any robust system design, troubleshooting, or operational role. This module equips you with the in-depth knowledge and practical tools to dissect, diagnose, and resolve the often-elusive "name or service not known" errors, ensuring your systems remain resilient, performant, and reachable.

## Did You Know?

- **DNS was created in 1983** by Paul Mockapetris to replace the HOSTS.TXT file, a manually distributed flat file that listed every hostname on the ARPANET. This massive architectural change was crucial for the internet to scale beyond a few hundred machines to the global network it is today.
- **Kubernetes' CoreDNS handles millions of queries per hour** in large clusters. Every service lookup, every pod-to-pod communication, and every external DNS query flows through it, making it a critical control point for application connectivity and a prime candidate for performance optimization and debugging.
- **The `search` directive in `/etc/resolv.conf` is a performance optimization and convenience feature** that allows users and applications to type short service names (like `my-service`) instead of fully qualified domain names (like `my-service.default.svc.cluster.local`). This convenience, however, comes with subtle implications for resolution order, latency, and potential security concerns if not managed correctly.
- **DNS primarily uses UDP port 53 for queries**, due to its connectionless and low-overhead nature, making it ideal for quick, single-packet transactions. However, it switches to TCP port 53 for larger responses (like zone transfers) or when UDP packets are truncated, especially in scenarios involving DNSSEC. Blocking TCP port 53 can lead to intermittent and hard-to-diagnose DNS failures, particularly in complex network environments.

## The Pillars of Linux DNS Resolution

At its core, DNS resolution in Linux is handled by the C library's resolver (`glibc` for most distributions, or `musl` in Alpine Linux). When an application needs to resolve a hostname to an IP address, it doesn't directly query a DNS server. Instead, it makes a system call to the resolver library, which then follows a defined, configurable process to find the corresponding IP address. This layered approach ensures flexibility and local control over the resolution flow.

### The Resolution Process: A Step-by-Step Walkthrough

The journey from a hostname to an IP address involves several stages, with local configuration files taking precedence over network queries. Understanding this flow is paramount for effective troubleshooting.

```mermaid
graph TD
    A[Application: "Connect to api.example.com"] --> B{1. Check /etc/hosts};
    B -- Not found --> C{2. Check /etc/resolv.conf for DNS server};
    B -- Found --> E[Application connects to 192.168.1.10];
    C --> D[3. Query DNS server (10.96.0.10)];
    D --> F[4. DNS server returns: 93.184.216.34];
    F --> E[5. Application connects to 93.184.216.34];

    subgraph etc_hosts_lookup [/etc/hosts content]
        H1["127.0.0.1 localhost"]
        H2["192.168.1.10 api.example.com"]
    end
    subgraph resolv_conf_content [/etc/resolv.conf content]
        R1["nameserver 10.96.0.10"]
        R2["search default.svc.cluster.local ..."]
    end
    B -- Check --> H1;
    B -- Check --> H2;
    C -- Read --> R1;
    C -- Read --> R2;
```
1.  **Application Request**: An application requests to connect to a hostname, e.g., `api.example.com`.
2.  **`/etc/hosts` Check**: The resolver first checks the local `/etc/hosts` file for a static mapping. This file acts as a simple, high-priority local DNS cache and override mechanism.
3.  **`/etc/resolv.conf` Consult**: If the hostname is not found in `/etc/hosts`, the resolver reads `/etc/resolv.conf` to determine which external DNS servers to query and which domain suffixes to try for unqualified names.
4.  **DNS Server Query**: The resolver sends a DNS query to the configured DNS server(s), typically using UDP port 53.
5.  **DNS Server Response**: The DNS server responds with the corresponding IP address, along with other information like the Time To Live (TTL).
6.  **Application Connects**: The application uses the resolved IP address to establish a connection, bypassing the need for further name resolution until the cached entry expires.

### `/etc/nsswitch.conf`: The Resolver's Order of Operations

The `/etc/nsswitch.conf` file (Name Service Switch configuration) is the master control for how a Linux system performs lookups for various databases, including `hosts`, `passwd`, and `groups`. For DNS resolution, it dictates the exact order in which sources are consulted.

```bash
cat /etc/nsswitch.conf | grep hosts

# Output: hosts: files dns
# Meaning: Check files (/etc/hosts) first, then DNS
```
In this typical configuration, `files` (referring to `/etc/hosts`) are consulted first. If a match is found, the lookup stops. If not, the system proceeds to `dns` (querying the servers specified in `/etc/resolv.conf`). If `dns` were listed first, or `files` omitted, the resolution behavior would change significantly, potentially leading to performance issues or unexpected overrides.

### `/etc/hosts`: The Local Override

The `/etc/hosts` file provides a simple, static mapping of IP addresses to hostnames. It's the first place the resolver looks (if `nsswitch.conf` is configured to do so) and offers a powerful, fast way to override DNS resolution locally without involving network traffic.

```bash
# /etc/hosts
127.0.0.1       localhost
::1             localhost
192.168.1.100   myserver.local myserver
10.0.0.50       database.internal db
```
This file is incredibly useful for:
-   **Local Development**: Mapping internal service names to `localhost` or specific development IP addresses, speeding up iteration.
-   **Testing**: Temporarily redirecting traffic for a production domain to a staging environment without changing global DNS records.
-   **Blocking Sites**: Mapping undesirable domains to `127.0.0.1` or `0.0.0.0` to prevent access at the operating system level.

#### Kubernetes and `/etc/hosts`
Even in Kubernetes, `/etc/hosts` plays a role within each pod. It primarily maps `localhost` and the pod's own IP address to its hostname, ensuring basic network functionality.

```bash
# In a Kubernetes pod
cat /etc/hosts

# Output:
127.0.0.1       localhost
10.244.1.5      my-pod-name
```

> **Pause and predict**: Imagine your application needs to connect to a legacy internal service at `legacy-api.example.com`. To ensure high availability during a migration, you've added an entry to `/etc/hosts` on your application server: `10.0.0.150 legacy-api.example.com`. However, the production DNS record for `legacy-api.example.com` unexpectedly changes to `10.0.0.151`. What IP address will your application attempt to connect to, and why? What's the immediate impact if `10.0.0.150` becomes unresponsive?

## Mastering `/etc/resolv.conf`: The DNS Configuration Hub

While `/etc/hosts` provides static overrides, `/etc/resolv.conf` is where the dynamic world of DNS resolution is configured. It explicitly tells your system which DNS servers to query and how to construct queries for unqualified hostnames. A well-configured `resolv.conf` is essential for both performance and correct service discovery.

### Format and Key Directives

The `resolv.conf` file is typically generated automatically by network management tools, but its contents are straightforward, primarily containing `nameserver`, `search`, `domain`, and `options` directives.

```bash
# /etc/resolv.conf

# DNS servers to query (up to 3)
nameserver 10.96.0.10    # Primary DNS
nameserver 8.8.8.8       # Secondary DNS

# Domain search list
search default.svc.cluster.local svc.cluster.local cluster.local

# Options
options ndots:5 timeout:2 attempts:2
```

| Directive  | Purpose                                           | Example                     |
|------------|---------------------------------------------------|-----------------------------|
| `nameserver` | IP address of a DNS server to query. Up to 3 can be listed. | `nameserver 8.8.8.8`        |
| `search`   | List of domain suffixes to append to unqualified hostnames. | `search example.com corp.internal` |
| `domain`   | Default domain name; overridden by `search` if both are present. | `domain example.com`        |
| `options`  | Various resolver options, like `ndots`, `timeout`, `attempts`. | `options ndots:5`           |

### The Nuance of `ndots`

The `ndots` option is often overlooked but profoundly impacts DNS query behavior, especially in environments like Kubernetes where short hostnames are common. It determines when an unqualified hostname (one without a dot) or a partially qualified hostname is considered "absolute" and when search domains should be appended.

```
ndots:5 means:
- If hostname has < 5 dots → try search domains first
- If hostname has >= 5 dots → try as absolute first

Example with ndots:5 and search: default.svc.cluster.local

Query: "api" (0 dots < 5)
  Try: api.default.svc.cluster.local  ← First!
  Try: api.svc.cluster.local
  Try: api.cluster.local
  Try: api  (absolute)

Query: "api.example.com" (2 dots < 5)
  Try: api.example.com.default.svc.cluster.local  ← Wastes time!
  Try: api.example.com.svc.cluster.local
  Try: api.example.com.cluster.local
  Try: api.example.com  ← What we wanted

Query: "a.b.c.d.example.com" (4 dots < 5)
  Still tries search domains first! (need 5+ dots)
```

**Real-world implication**: A high `ndots` value (like Kubernetes' default of 5) means that even a seemingly fully qualified external domain name like `www.google.com` (2 dots) will first have all search domains appended to it. This results in multiple failed queries before the resolver eventually tries `www.google.com` as an absolute name, introducing significant latency and unnecessary DNS traffic. To mitigate this, always prefer using fully qualified domain names (FQDNs) with a trailing dot (e.g., `www.google.com.`) for external services to explicitly bypass the search path.

### Kubernetes and `resolv.conf`

Every pod in Kubernetes is assigned its own `/etc/resolv.conf` file, which is meticulously managed by the Kubelet. This configuration is critical as it points to the cluster's CoreDNS service and includes search paths specific to the pod's namespace and the overall cluster domain.

```bash
# In a Kubernetes pod
cat /etc/resolv.conf

# Output:
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

This configuration implies:
-   The primary DNS server for the pod is the ClusterIP of the `kube-dns` service (which CoreDNS implements). This IP is internal to the cluster.
-   Short hostnames (e.g., `my-service`) will automatically try to resolve within the pod's current namespace, then the broader cluster, thanks to the `search` directive.
-   `ndots:5` is specifically set to optimize for Kubernetes internal service discovery. Service FQDNs (e.g., `my-service.default.svc.cluster.local`) typically have 4 dots, meaning they'll be treated as "absolute" names and queried directly. However, as noted above, this can introduce performance penalties for external DNS lookups.

> **Stop and think**: You're debugging a `web-app` pod in the `staging` namespace that is failing to connect to `db-service`. The `web-app` is attempting to connect using the short name `db-service`. Given a typical Kubernetes pod's `/etc/resolv.conf` with `ndots:5` and `search staging.svc.cluster.local svc.cluster.local cluster.local`, outline the precise sequence of DNS queries the `web-app` pod's resolver will attempt. Why is understanding this sequence crucial for effective debugging?

## The DNS Debugger's Toolkit: `dig`, `nslookup`, `host`, `getent`

When DNS issues strike, knowing your tools is half the battle. Linux provides several command-line utilities, each with its unique strengths, to query DNS servers and inspect resolution paths. Mastering these tools will significantly accelerate your troubleshooting process.

### `dig` (Domain Information Groper)

`dig` is the most powerful and flexible command-line tool for querying DNS name servers. It's indispensable for detailed diagnostics, offering fine-grained control over query types, servers, and output format.

```bash
# Basic query: Resolves A record for example.com using default DNS server
dig example.com

# Query specific record type: Fetch only IPv4 address
dig example.com A

# Query specific record type: Fetch only IPv6 address
dig example.com AAAA

# Query specific record type: Fetch Mail Exchanger records
dig example.com MX

# Query specific record type: Fetch Name Server records
dig example.com NS

# Query specific record type: Fetch Text records (often used for SPF, DKIM, DMARC)
dig example.com TXT

# Query specific record type: Fetch Canonical Name record
dig example.com CNAME

# Short output: Displays only the answer section (useful for scripting)
dig +short example.com

# Use specific DNS server: Query Google's public DNS (8.8.8.8)
dig @8.8.8.8 example.com

# Trace full resolution path: Shows iterative queries from root servers down
dig +trace example.com

# Reverse lookup: Resolves IP address to hostname (PTR record)
dig -x 8.8.8.8
```

#### Example `dig` Output
A typical `dig` query provides extensive information about the resolution process, including request/response headers, question, answer, authority, and additional sections. This level of detail is invaluable for advanced debugging.

```bash
dig example.com

; <<>> DiG 9.16.1 <<>> example.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 12345
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; QUESTION SECTION:
;example.com.                   IN      A

;; ANSWER SECTION:
example.com.            3600    IN      A       93.184.216.34

;; Query time: 25 msec
;; SERVER: 10.96.0.10#53(10.96.0.10)
;; WHEN: Mon Dec 01 10:00:00 UTC 2024
;; MSG SIZE  rcvd: 56
```
The `ANSWER SECTION` clearly shows the resolved IP address (93.184.216.34) and its TTL (3600 seconds). The `SERVER` line indicates precisely which DNS server processed and provided the answer, which is crucial for identifying misconfigurations or problematic upstream resolvers.

#### `dig` vs `dig +short`
The `+short` option is incredibly useful for quickly extracting just the IP address or relevant record, making it ideal for scripting or quick command-line checks where verbose output is unnecessary.

```bash
dig example.com
# ... lots of output ...
# example.com.  3600  IN  A  93.184.216.34
# ... query time, server, etc ...

dig +short example.com
# 93.184.216.34
```

### `nslookup`

`nslookup` is a simpler, interactive tool for querying DNS. While `dig` is generally preferred for advanced diagnostics due to its richer features and more standardized output, `nslookup` is often pre-installed and serves as an easier entry point for basic lookups. It can operate in interactive or non-interactive modes.

```bash
# Basic lookup: Resolves example.com using default DNS server
nslookup example.com

# Use specific server: Query Google's public DNS (8.8.8.8)
nslookup example.com 8.8.8.8

# Reverse lookup: Resolves IP address to hostname
nslookup 8.8.8.8
```

### `host`

The `host` command offers an even simpler and more concise output compared to `nslookup`, making it an excellent choice for quick, human-readable lookups. It provides a good balance between brevity and utility.

```bash
# Basic lookup: Resolves example.com
host example.com

# Reverse lookup: Resolves IP address to hostname
host 8.8.8.8

# Find mail servers: Queries MX records
host -t MX example.com
```

### `getent`

The `getent` (get entries) command is unique because it queries the Name Service Switch (NSS) libraries, which means it respects the entire resolution order defined in `/etc/nsswitch.conf`. This includes checking `/etc/hosts` before querying DNS servers. This makes `getent` a particularly valuable tool for understanding how applications *actually* perform name resolution on your system, as it mimics the system calls applications make.

```bash
# Resolve like applications do: Checks /etc/hosts, then DNS, respecting nsswitch.conf
getent hosts example.com

# This command is crucial because it mimics the behavior of system calls that applications make.
# If 'getent' succeeds where 'dig' fails, it often points to an issue with /etc/hosts or search domains.
```

## Kubernetes DNS: The Heart of Service Discovery

Kubernetes relies heavily on DNS for its internal service discovery mechanism. Every service and pod within a cluster is automatically assigned a DNS name, enabling applications to communicate by logical names rather than ephemeral IP addresses. This abstraction is a cornerstone of microservices architecture in Kubernetes.

### CoreDNS: The Cluster Resolver

CoreDNS is the default DNS server for Kubernetes. It runs as a set of pods (typically in the `kube-system` namespace) and is responsible for handling all internal and external DNS queries originating from pods within the cluster.

```mermaid
graph TD
    P[Pod Query: "my-service.default.svc.cluster.local"] --> C(CoreDNS);
    C -- Cluster queries: *.cluster.local --> K[Answer from Kubernetes API];
    C -- External queries: *.* --> U[Forward to upstream DNS];
    K --> R[Returns: 10.96.45.123 (Service ClusterIP)];
    U --> R;

    subgraph CoreDNS_Server [CoreDNS (10.96.0.10)]
        C
    end
```
CoreDNS is configured through its `Corefile` to perform two primary functions:
-   **Resolve cluster names**: Any query ending with `.cluster.local` (or your configured cluster domain) is intercepted and resolved by looking up Services and Pods via the Kubernetes API, which maintains an authoritative list of cluster resources.
-   **Forward external names**: Queries for external domains (e.g., `google.com`) are forwarded to upstream DNS servers, which are typically configured in CoreDNS's `Corefile` to point to public DNS resolvers.

### Kubernetes DNS Naming Conventions

Kubernetes enforces a consistent and predictable naming scheme for services and pods, making service discovery straightforward.

```mermaid
graph TD
    A[Service Fully Qualified Domain Name (FQDN)] --> B("my-service.namespace.svc.cluster.local")
    B --> C{Components of the FQDN}
    C --> D[Service Name: my-service]
    C --> E[Namespace: namespace]
    C --> F[Service Type Indicator: svc]
    C --> G[Cluster Domain: cluster.local]
```
-   **Service FQDN**: `my-service.namespace.svc.cluster.local`
    -   `my-service`: The name of the Kubernetes Service.
    -   `namespace`: The namespace the Service resides in (e.g., `default`, `staging`, `production`).
    -   `svc`: A static indicator denoting this is a Service record.
    -   `cluster.local`: The cluster domain, configurable during cluster setup.
-   **Pod FQDN (with hostname)**: `pod-name.subdomain.namespace.svc.cluster.local` (e.g., for headless services)

The ability to use short names (e.g., `my-service` instead of `my-service.default.svc.cluster.local`) within a pod's namespace is a direct result of the `search` directive in the pod's `/etc/resolv.conf`, which automatically appends appropriate suffixes.

### Testing DNS in Kubernetes

When troubleshooting, it's crucial to test DNS resolution directly from within a pod. This replicates the application's exact network environment and configuration, providing the most accurate debugging context.

```bash
# Run a temporary busybox pod to test DNS resolution
kubectl run dnstest --image=busybox --rm -it --restart=Never -- sh

# Inside the pod:
# 1. Resolve the Kubernetes API service (short name)
nslookup kubernetes

# 2. Resolve the Kubernetes API service (fully qualified name)
nslookup kubernetes.default.svc.cluster.local

# 3. Inspect the pod's resolv.conf
cat /etc/resolv.conf

# 4. Test external DNS resolution
nslookup google.com

# 5. Exit the busybox pod
exit
```
This sequence allows you to quickly verify internal service discovery, external connectivity, and inspect the pod's specific DNS configuration.

### Troubleshooting Common Kubernetes DNS Issues

The error message "nslookup: can't resolve 'kubernetes'" or similar "name or service not known" is a classic Kubernetes DNS debugging scenario. A systematic approach is key:

```bash
# Issue: "nslookup: can't resolve 'kubernetes'"

# Debug steps:
# 1. Check if CoreDNS pods are running and healthy
kubectl get pods -n kube-system -l k8s-app=kube-dns

# 2. Check CoreDNS pod logs for any errors or configuration issues
kubectl logs -n kube-system -l k8s-app=kube-dns

# 3. Verify the kube-dns service exists and has a ClusterIP
kubectl get svc -n kube-system kube-dns

# 4. Verify that the pod can reach the CoreDNS service IP (typically 10.96.0.10) on port 53 (UDP/TCP)
# This uses netcat (nc) from a busybox pod to test connectivity
kubectl run test --image=busybox --rm -it -- \
  nc -zv 10.96.0.10 53
```
These steps help isolate the problem: Is CoreDNS running? Is it misconfigured? Is there a network connectivity issue preventing pods from reaching CoreDNS?

#### Finding a Kubernetes Pod's DNS Server
To definitively confirm what DNS server a Kubernetes pod is actually configured to use:

```bash
# Option 1: Exec into the pod and check its resolv.conf
kubectl exec pod-name -- cat /etc/resolv.conf

# Option 2: Get the ClusterIP of the kube-dns service
kubectl get svc -n kube-system kube-dns -o wide

# The 'nameserver' entry in the pod's resolv.conf should match the 'ClusterIP' of the kube-dns service.
```
This comparison helps verify if the pod's DNS configuration correctly points to the cluster's CoreDNS service.

#### `dig kubernetes` vs `getent hosts kubernetes` in a Pod
Understanding the subtle differences between these commands is paramount in a Kubernetes context:

```bash
dig kubernetes.default.svc.cluster.local  # Works by directly querying the FQDN
dig +search kubernetes                      # Explicitly tells dig to use search domains
getent hosts kubernetes                     # Uses the system resolver, respecting /etc/hosts and search domains
```
`dig` performs a direct DNS query, bypassing local files (`/etc/hosts`) and search paths unless explicitly directed (`+search`). `getent hosts`, however, is a more holistic tool that mimics how applications resolve names, adhering to the NSS configuration (`/etc/nsswitch.conf`). If `getent` succeeds where `dig` fails, it strongly suggests the issue lies with `/etc/hosts` entries or the `search` domain configuration rather than CoreDNS itself.

## DNS Caching: Speed vs. Freshness

DNS queries, especially those traversing the internet, can introduce significant latency. To mitigate this, DNS responses are frequently cached at various levels: client-side (applications, browsers), operating system, and intermediate DNS servers (e.g., CoreDNS, ISP resolvers). While caching dramatically improves performance, it can also lead to issues with stale records if updates are not propagated promptly.

> **Stop and think**: If an application caches a DNS response indefinitely (ignoring the TTL), what happens when the external service it relies on undergoes a blue/green deployment that changes its underlying IP address? How does this local caching behavior impact the application's perceived availability and what is the required operational response?

### `systemd-resolved` (Modern Linux Caching)

Many modern Linux distributions (like Ubuntu and Debian) utilize `systemd-resolved` as a sophisticated system service for network name resolution. It provides a caching DNS resolver and acts as a local stub resolver for applications, centralizing DNS management.

```bash
# Check the current status of systemd-resolved
systemd-resolve --status

# Flush the DNS cache maintained by systemd-resolved
systemd-resolve --flush-caches

# Display statistics about systemd-resolved operations
systemd-resolve --statistics
```
Alternatively, the `resolvectl` command provides a more comprehensive and user-friendly interface for interacting with `systemd-resolved`:

```bash
# Check if systemd-resolved is active
systemctl status systemd-resolved

# View statistics (cache hits, misses, current cache size)
resolvectl statistics

# Flush cache (clears all cached entries)
sudo resolvectl flush-caches

# View current DNS servers and domains configured
resolvectl status
```

### Diagnosing and Flushing Cache Issues

A common and frustrating scenario is when a DNS record for a service has been updated (e.g., an IP address change), but your application or system continues to use an old, cached IP address, leading to connectivity failures.

```bash
# Symptom: An application connects to an old IP address for a domain, even after DNS records have been updated.

# Solutions:
# 1. Flush the local DNS cache (if systemd-resolved is in use)
sudo systemd-resolve --flush-caches
# Or using resolvectl
sudo resolvectl flush-caches

# 2. Check the Time To Live (TTL) of the DNS record to understand how long it's designed to be cached
dig example.com | grep -E "^example.*IN.*A"
# The number after 'IN' in the ANSWER SECTION is the TTL in seconds. A low TTL means changes propagate faster.

# 3. In Kubernetes, if CoreDNS is caching stale external records, you might need to restart its pods to force a refresh
kubectl rollout restart deployment coredns -n kube-system
```
Understanding TTLs is critical for setting expectations on DNS propagation. A short TTL (e.g., 60 seconds) means changes will be reflected quickly, while a long TTL (e.g., 24 hours) will cause delays.

## Common Mistakes

DNS troubleshooting can be tricky and often involves sifting through layers of configuration. Here are some frequent pitfalls and their practical solutions