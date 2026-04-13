---
title: "Module 1.3: Backstage Catalog & Infrastructure"
slug: k8s/cba/module-1.3-backstage-catalog-infrastructure
sidebar:
  order: 4
---
> **Complexity**: `[COMPLEX]` - Covers two exam domains (44% of CBA combined)
>
> **Time to Complete**: 60-75 minutes
>
> **Prerequisites**: Module 1 (Backstage Overview), Module 2 (Plugins & Extensibility)

## What You'll Be Able to Do

After completing this module, you will be able to:

1. **Design** a catalog taxonomy that models your organization's ownership, dependencies, and API contracts accurately.
2. **Implement** entity providers and processors that auto-discover services from external VCS systems into the catalog.
3. **Evaluate** the architectural components of Backstage to separate frontend static assets from backend Node.js processing.
4. **Diagnose** catalog ingestion failures and orphaned entities by understanding the processing loop and database state.
5. **Compare** manual registration locations against automated discovery mechanisms to architect the optimal ingestion pipeline.

## Why This Module Matters

In the early hours of a major shopping event, a premier e-commerce platform suffered a cascading failure in its payment processing pipeline. The initial trigger was a minor misconfiguration in a secondary fraud-detection microservice, but the true catastrophe was organizational. When alarms began to fire, the incident response team spent precious minutes simply trying to figure out which team owned the service, where the source code lived, and what upstream dependencies were affected. The financial impact was estimated at over four million dollars in lost revenue—all because the organization lacked a centralized, trustworthy directory of software ownership.

This is the exact problem the software catalog solves. The software catalog is the beating heart of Backstage. Without it, Backstage is just a plugin framework with a pretty UI. With it, you have a single pane of glass over every service, API, team, and piece of infrastructure your organization owns. When an incident occurs, you immediately know who to page, where the documentation resides, and what other services might be impacted by a degradation.

The Certified Backstage Associate (CBA) exam, offered by the Linux Foundation / CNCF, is a 90-minute, proctored, multiple-choice exam costing $250 with one free retake. The exam dedicates 22% of its content to the Software Catalog (Domain 3) and another 22% to Infrastructure (Domain 2)—together, that is 44% of your score. Get these two domains right and you are nearly halfway to passing before you even touch plugins or TechDocs.

> **The Library Analogy**
>
> Think of the Backstage catalog as a library's card catalog system. Every book (Component) has a card describing it—author, genre, location. Some books reference other books (API relationships). The librarian (entity processor) receives new books, catalogs them, and shelves them. The building itself—shelves, lighting, HVAC—is the infrastructure. You need both: a great catalog system is useless if the building has no electricity, and a beautiful building with empty shelves helps nobody.

## Did You Know?

1. Backstage was open sourced by Spotify on March 16, 2020.
2. Backstage was accepted into the CNCF Sandbox on September 8, 2020.
3. Backstage moved from CNCF Sandbox to CNCF Incubating on March 15, 2022.
4. As of April 2026, Backstage remains at CNCF Incubating level and has not yet graduated.

## Core Architecture and Entity Kinds

Everything in the Backstage catalog is an **entity**. Each entity has a `kind`, an `apiVersion`, `metadata`, and a `spec`. 

The eight core built-in entity kinds in the Backstage Software Catalog are: Component, API, Resource, System, Domain, User, Group, and Location. Additionally, a Template is an additional kind used by the Scaffolder feature. Backstage Software Templates (Scaffolder) use a Template entity kind and are defined in YAML stored in a Git repository.

A Resource entity describes infrastructure a Component needs to operate at runtime (e.g., databases, storage buckets, CDNs).

Here is the historical ASCII visualization of how these kinds relate:

```text
┌─────────────────────────────────────────────────────────────────┐
│                    BACKSTAGE ENTITY KINDS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  OWNERSHIP          ORGANIZATIONAL        CATALOG MACHINERY      │
│  ┌───────────┐      ┌──────────┐          ┌──────────┐          │
│  │ Component │      │  Group   │          │ Location │          │
│  │ (service, │      │  (team,  │          │ (points  │          │
│  │  library) │      │  dept)   │          │  to YAML)│          │
│  └───────────┘      └──────────┘          └──────────┘          │
│  ┌───────────┐      ┌──────────┐          ┌──────────┐          │
│  │    API    │      │   User   │          │ Template │          │
│  │ (REST,   │      │  (person)│          │ (scaffol-│          │
│  │  gRPC)   │      └──────────┘          │  ding)   │          │
│  └───────────┘                            └──────────┘          │
│  ┌───────────┐      GROUPING                                    │
│  │ Resource  │      ┌──────────┐                                │
│  │ (DB, S3, │      │  System  │                                │
│  │  queue)  │      │  (group  │                                │
│  └───────────┘      │  of comp)│                                │
│                     └──────────┘                                │
│                     ┌──────────┐                                │
│                     │  Domain  │                                │
│                     │ (business│                                │
│                     │  area)   │                                │
│                     └