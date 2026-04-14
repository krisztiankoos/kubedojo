---
title: "Module 4.2: Multi-Cluster and Multi-Region Architectures"
slug: cloud/architecture-patterns/module-4.2-multi-cluster
sidebar:
  order: 3
---
> **Complexity**: `[COMPLEX]`
>
> **Time to Complete**: 3 hours
>
> **Prerequisites**: [Module 4.1: Managed vs Self-Managed Kubernetes](../module-4.1-managed-vs-selfmanaged/)
>
> **Track**: Cloud Architecture Patterns

## What You'll Be Able to Do

After completing this module, you will be able to:

- **Design multi-cluster architectures for fault isolation, regulatory compliance, and team autonomy across regions**
- **Implement cross-cluster service discovery and traffic routing using service mesh or DNS-based approaches**
- **Configure cluster federation patterns for workload placement, failover, and capacity management**
- **Evaluate single-cluster vs multi-cluster tradeoffs for latency, blast radius, and operational complexity**

---

## Why This Module Matters

**October 25, 2021. Facebook (now Meta).**

At 15:39 UTC, a routine maintenance command issued to Facebook's backbone routers went wrong. The command was intended to assess the capacity of the backbone network. Instead, it disconnected every Facebook data center from the internet simultaneously. Not gradually. Not region by region. All at once.

BGP routes for Facebook, Instagram, WhatsApp, and Oculus were withdrawn from the global routing table. DNS servers, now unreachable, started returning SERVFAIL. Within minutes, 3.5 billion people lost access to the services they used for communication, business, and (in some countries) emergency coordination. Facebook's own engineers couldn't access internal tools to diagnose the problem because those tools ran on the same infrastructure. They had to physically drive to data centers and manually reconfigure routers.

The outage lasted nearly six hours. Revenue impact: approximately $65 million. Market cap loss during the outage: $47 billion. WhatsApp-dependent businesses in India, Brazil, and Southeast Asia lost an entire day of commerce.

The root cause wasn't a hardware failure or a cyberattack. It was a single-cluster, single-plane-of-control architecture where one bad command could reach every region simultaneously. There was no blast radius containment. No regional isolation. No independent failure domain that could keep operating while the rest recovered.

This module teaches you how to design architectures where that can't happen. You'll learn to think in failure domains, route traffic across regions, manage state across distance, and build systems where the worst-case scenario is a regional degradation -- not a global outage.

---

## Failure Domains: The Foundation of Multi-Cluster Design

Before you can design a multi-cluster architecture, you need to understand failure domains -- the boundaries within which a failure is contained.

Think of failure domains like bulkheads on a ship. A breach in one compartment doesn't sink the ship because the bulkheads contain the flooding. In cloud infrastructure, failure domains work the same way: a failure within one domain shouldn't propagate to others.

CLOUD FAILURE DOMAIN HIERARCHY