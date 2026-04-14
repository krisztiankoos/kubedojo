---
title: "Bare Metal Provisioning"
sidebar:
  order: 0
---

How do you go from a rack of blank servers to a running Kubernetes cluster? This section covers the boot process, OS installation, and declarative infrastructure that turns hardware into a platform.

In public cloud environments, provisioning a new node is as simple as making an API call. In an on-premises datacenter, you must manage the physical reality of the hardware. This includes understanding the physical infrastructure like racks, power distribution, and out-of-band management interfaces before any software is even installed.

Once the hardware is physically racked and cabled, the next challenge is automating the operating system installation. We will explore network booting via PXE, immutable operating systems optimized specifically for container workloads, and finally, how to bring cloud-like declarative provisioning to your bare-metal servers using tools like Cluster API.

## Modules

| Module | Description | Time |
|--------|-------------|------|
| [Module 2.1: Datacenter Fundamentals](module-2.1-datacenter-fundamentals/) | Racks, PDUs, UPS, cooling, IPMI/BMC/Redfish, out-of-band management | 45 min |
| [Module 2.2: OS Provisioning & PXE Boot](module-2.2-pxe-provisioning/) | PXE/UEFI boot, DHCP/TFTP, MAAS, Tinkerbell, autoinstall | 60 min |
| [Module 2.3: Immutable OS for Kubernetes](module-2.3-immutable-os/) | Talos Linux, Flatcar Container Linux, RHCOS, why immutable matters | 45 min |
| [Module 2.4: Declarative Bare Metal with Cluster API](module-2.4-declarative-bare-metal/) | Cluster API for bare metal, Metal3, Sidero, machine lifecycle | 60 min |