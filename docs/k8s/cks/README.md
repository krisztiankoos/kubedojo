# CKS Curriculum

> **Certified Kubernetes Security Specialist** - Demonstrate your ability to secure container-based applications and Kubernetes platforms

## About CKS

The CKS is a **hands-on, performance-based exam** that validates your skills in securing Kubernetes clusters and workloads. CKA certification is a prerequisite.

| Aspect | Details |
|--------|---------|
| **Format** | Performance-based (hands-on) |
| **Duration** | 2 hours |
| **Questions** | 15-20 tasks |
| **Passing Score** | 67% |
| **Validity** | 2 years |
| **Prerequisite** | Active CKA certification |

## Curriculum Structure

| Part | Topic | Weight | Modules |
|------|-------|--------|---------|
| Part 0 | Environment | - | 4 |
| Part 1 | Cluster Setup | 10% | 5 |
| Part 2 | Cluster Hardening | 15% | 5 |
| Part 3 | System Hardening | 15% | 4 |
| Part 4 | Minimize Microservice Vulnerabilities | 20% | 4 |
| Part 5 | Supply Chain Security | 20% | 4 |
| Part 6 | Monitoring, Logging, Runtime Security | 20% | 4 |
| **Total** | | **100%** | **30** |

## Module Overview

### Part 0: Environment (4 modules)
- 0.1 CKS Overview - Exam format and domains
- 0.2 Security Lab - Setting up a security-focused cluster
- 0.3 Security Tools - Essential tools (trivy, falco, kubesec)
- 0.4 Exam Strategy - Security-focused approach

### Part 1: Cluster Setup (5 modules)
- 1.1 Network Policies - Default deny, egress control
- 1.2 CIS Benchmarks - Cluster hardening standards
- 1.3 Ingress Security - TLS, authentication
- 1.4 Node Metadata Protection - Instance metadata security
- 1.5 GUI Element Security - Dashboard security

### Part 2: Cluster Hardening (5 modules)
- 2.1 RBAC Deep Dive - Least privilege principles
- 2.2 Service Account Security - Token restrictions
- 2.3 API Server Security - Admission control, audit
- 2.4 Kubernetes Upgrades - Secure upgrade procedures
- 2.5 Restricting API Access - Anonymous auth, insecure ports

### Part 3: System Hardening (4 modules)
- 3.1 AppArmor - Application armor profiles
- 3.2 Seccomp - System call filtering
- 3.3 Kernel Hardening - sysctl, kernel parameters
- 3.4 Network Security - Host firewall, port scanning

### Part 4: Minimize Microservice Vulnerabilities (4 modules)
- 4.1 Security Contexts - Pod and container security
- 4.2 Pod Security Admission - Enforcing standards
- 4.3 Secrets Management - Encryption at rest
- 4.4 Runtime Sandboxing - gVisor, Kata containers

### Part 5: Supply Chain Security (4 modules)
- 5.1 Image Security - Base images, minimization
- 5.2 Image Scanning - Vulnerability detection
- 5.3 Static Analysis - YAML/manifest scanning
- 5.4 Admission Controllers - Image policies, OPA

### Part 6: Runtime Security (4 modules)
- 6.1 Audit Logging - API server auditing
- 6.2 Falco - Runtime threat detection
- 6.3 Container Investigation - Forensics
- 6.4 Immutable Infrastructure - Read-only containers

## How to Use This Curriculum

1. **Complete CKA first** - It's a prerequisite
2. **Set up security lab** - Complete Part 0
3. **Practice with tools** - Falco, Trivy, etc.
4. **Understand attack vectors** - Think like an attacker
5. **Apply defense in depth** - Layer your security

## Key Skills

- Network policies (default deny)
- RBAC with least privilege
- Pod Security Standards
- Image scanning and signing
- Runtime threat detection with Falco
- Audit logging configuration

## Start Learning

Begin with Part 0 to set up your security-focused environment and understand the exam format.

Good luck on your CKS journey!
