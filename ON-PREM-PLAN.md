# On-Premises Kubernetes Track — Curriculum Plan

Based on Gemini's initial design (26 modules), refined with additional gaps identified.

## Structure: 8 sections, ~30 modules

### Section 1: Planning & Economics (4 modules)
| # | Module | Time | Key Topics |
|---|--------|------|------------|
| 1.1 | The Case for On-Premises K8s | 45m | Cloud vs on-prem decision framework, data sovereignty, latency, compliance drivers, when NOT to go on-prem |
| 1.2 | Server Sizing & Hardware Selection | 60m | CPU (Intel vs AMD, cores vs clock), RAM (ECC, DIMM slots), NVMe vs SSD vs HDD, NUMA awareness, GPU considerations |
| 1.3 | Cluster Topology Planning | 60m | How many clusters, shared vs dedicated control planes, sizing etcd, control plane HA, worker node pools, rack-aware scheduling |
| 1.4 | TCO & Budget Planning | 45m | CapEx vs OpEx, hardware lifecycle (3-5yr refresh), power/cooling per rack (~8-12kW), staffing (1 engineer per 50-100 nodes), cloud breakeven analysis |

### Section 2: Bare Metal Provisioning (4 modules)
| # | Module | Time | Key Topics |
|---|--------|------|------------|
| 2.1 | Datacenter Fundamentals | 45m | Rack units, PDUs, UPS, cooling, cabling standards, IPMI/BMC/Redfish, out-of-band management |
| 2.2 | OS Provisioning & PXE Boot | 60m | PXE/UEFI boot, DHCP/TFTP, kickstart/preseed/autoinstall, MAAS, Tinkerbell |
| 2.3 | Immutable OS for Kubernetes | 45m | Talos Linux, Flatcar Container Linux, RHCOS, why immutable matters for bare metal security |
| 2.4 | Declarative Bare Metal (Sidero/Metal3) | 60m | Cluster API for bare metal, CAPM3, Sidero, declarative hardware inventory, machine lifecycle |

### Section 3: Networking (4 modules)
| # | Module | Time | Key Topics |
|---|--------|------|------------|
| 3.1 | Datacenter Network Architecture | 60m | Spine-leaf topology, ToR switches, L2 vs L3 boundaries, MTU (jumbo frames), VLAN design for K8s |
| 3.2 | BGP & Routing for Kubernetes | 60m | BGP peering with ToR, Calico BGP mode, route reflectors, advertising service IPs, multi-site routing |
| 3.3 | Load Balancing Without Cloud | 60m | MetalLB (L2 vs BGP), kube-vip, HAProxy/Keepalived for API server, F5/Nginx external LBs |
| 3.4 | DNS & Certificate Infrastructure | 45m | Internal DNS (CoreDNS external, BIND), split-horizon DNS, cert-manager with Vault CA, internal ACME |

### Section 4: Storage (3 modules)
| # | Module | Time | Key Topics |
|---|--------|------|------------|
| 4.1 | Storage Architecture Decisions | 45m | DAS vs NAS vs SAN, NVMe vs SSD vs HDD tiering, iSCSI vs FC, storage for etcd (latency requirements) |
| 4.2 | Software-Defined Storage (Ceph/Rook) | 60m | Ceph architecture (MON/OSD/MDS), Rook operator, storage classes, performance tuning, failure domains |
| 4.3 | Local Storage & Alternatives | 45m | OpenEBS, Longhorn, LVM CSI, TopoLVM, local-path-provisioner, when to use each |

### Section 5: Multi-Cluster & Platform (3 modules)
| # | Module | Time | Key Topics |
|---|--------|------|------------|
| 5.1 | Private Cloud Platforms | 60m | VMware vSphere + Tanzu, OpenStack + Magnum, Harvester, when to virtualize vs bare metal |
| 5.2 | Multi-Cluster Control Planes | 60m | Shared etcd, vCluster, Kamaji, external etcd topology, kubeadm HA, cluster federation |
| 5.3 | Cluster API on Bare Metal | 60m | CAPM3 (Metal3), CAPV (vSphere), declarative lifecycle, machine health checks |

### Section 6: Security & Compliance (4 modules)
| # | Module | Time | Key Topics |
|---|--------|------|------------|
| 6.1 | Physical Security & Air-Gapped Environments | 60m | Datacenter physical controls, disconnected registries (Harbor), image mirroring, sneakernet, air-gapped GitOps |
| 6.2 | Hardware Security (HSM/TPM) | 45m | HSMs for key management, TPM for measured boot, Vault with HSM backend, replacing cloud KMS |
| 6.3 | Enterprise Identity (AD/LDAP/OIDC) | 60m | Active Directory integration, LDAP, Keycloak, Dex, OIDC for K8s API, RBAC mapping to corporate groups |
| 6.4 | Compliance for Regulated Industries | 45m | HIPAA physical controls, SOC2 on-prem, PCI DSS, data sovereignty, audit logging, evidence collection |

### Section 7: Day-2 Operations (5 modules)
| # | Module | Time | Key Topics |
|---|--------|------|------------|
| 7.1 | Kubernetes Upgrades on Bare Metal | 60m | kubeadm upgrade path, drain with limited spare capacity, rolling through heterogeneous hardware, rollback strategies |
| 7.2 | Hardware Lifecycle & Firmware | 45m | BIOS/firmware updates, cordon/drain for maintenance windows, disk replacement procedures, predictive failure |
| 7.3 | Node Failure & Auto-Remediation | 45m | Machine Health Checks, node problem detector, automated reboot/reprovision, spare node pools |
| 7.4 | Observability Without Cloud Services | 60m | Self-hosted Prometheus + Thanos, Grafana at scale, Loki for logs, alerting without PagerDuty (on-prem alternatives) |
| 7.5 | Capacity Expansion & Hardware Refresh | 45m | Adding racks, mixed CPU generations, topology spread constraints, decommissioning old nodes |

### Section 8: Resilience & Migration (3 modules)
| # | Module | Time | Key Topics |
|---|--------|------|------------|
| 8.1 | Multi-Site & Disaster Recovery | 60m | Active-active vs active-passive DCs, stretched clusters (etcd latency limits), RTO/RPO, Velero with MinIO |
| 8.2 | Hybrid Cloud Connectivity | 60m | VPN, Direct Connect/ExpressRoute, Submariner, unified service mesh, consistent policy across environments |
| 8.3 | Cloud Repatriation & Migration | 45m | Moving workloads from cloud to on-prem, translating cloud LBs/storage/IAM, data gravity, cutover planning |

---

## Total: 30 modules, ~27 hours of content

## Prerequisites from existing KubeDojo tracks:
- Fundamentals (Cloud Native 101, K8s Basics)
- Linux Deep Dive (networking, storage, security)
- CKA (cluster architecture, kubeadm)
- CKS (security hardening, runtime security)
- Platform Engineering (SRE, GitOps, FinOps)

## What this track does NOT cover (already in other tracks):
- Container fundamentals (Prerequisites)
- kubectl usage (CKA/CKAD)
- Pod Security Standards (CKS)
- ArgoCD/Flux (GitOps discipline)
- Prometheus/Grafana basics (Toolkits)
- Terraform/Ansible (IaC discipline)
