---
title: "Networking"
sidebar:
  order: 1
---

On-premises networking is fundamentally different from cloud networking. There is no VPC wizard, no managed load balancer, no automatic DNS. You design the physical topology, configure the switches, and run the protocols that make Kubernetes networking work on bare metal.

## Modules

| Module | Description | Time |
|--------|-------------|------|
| 3.1 Datacenter Network Architecture | Spine-leaf topology, ToR, L2/L3, MTU, VLAN design | 60 min |
| 3.2 BGP & Routing for Kubernetes | BGP peering, Calico BGP, route reflectors, multi-site | 60 min |
| 3.3 Load Balancing Without Cloud | MetalLB, kube-vip, HAProxy/Keepalived | 60 min |
| 3.4 DNS & Certificate Infrastructure | Internal DNS, split-horizon, cert-manager with Vault CA | 45 min |
