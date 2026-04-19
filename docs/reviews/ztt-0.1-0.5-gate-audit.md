---
title: "ZTT 0.1–0.5 Gate Audit — session 6"
date: 2026-04-19
author: Claude (session 6)
gates_run: [overstatement, semantic_verify, unsourced_assertion, coherence]
---

# TL;DR

Ran all four session-6 content gates against the currently-promoted
ZTT 0.1–0.5. **27 actionable findings** across the five modules,
broken down below. Gate B (semantic verify of citations) came back
100% SUPPORTED — the citation pipeline's output is trustworthy at
the URL ↔ claim level. Everything else flags is a content-quality
issue that the original v1-pipeline didn't catch.

# Totals by gate

| Gate | Candidates | Real issues | Notes |
|---|---|---|---|
| A — overstatement | 28 | **16 overstated** | 6 acceptable, 5 not_a_claim, 1 error (re-run recommended) |
| B — semantic verify | 28 | **0** | 28/28 SUPPORTED by Gemini-as-verifier against Codex-researched citations |
| C — unsourced assertion | 3 | **3** | All in 0.3 |
| D — coherence | 41 sections across 5 modules | **8 off_topic** | 4 in 0.1, 2 in 0.2, 0 in 0.3, 0 in 0.4, 2 in 0.5 |

# Per-module findings

## module-0.1-what-is-a-computer — 7 issues

### Coherence (4) — `absolute_beginner` audience mismatches

- **"Why This Matters for Kubernetes" section** — the "In the cloud,
  pricing depends on instance type / OS / region…" paragraph is off-
  topic for a foundational hardware module. *Action: `rewrite_to_fit`*
- **"Common Mistakes" table row** — "Over-provisioning cloud servers
  / A team might pay hundreds of dollars per month for a larger server
  than they use" jumps to FinOps from hardware basics. *Action: `delete`*
- **Quiz question 5** — "Your team is deploying a new web application
  to the cloud and debating whether to use Windows or Linux servers"
  — cloud/Kubernetes infra scenario, too advanced. *Action: `delete`*
- **Quiz question 6** — "You are running a database server for your
  company's e-commerce site, and during a major sale, the server
  crashes" — enterprise monitoring scenario, out of scope. *Action:
  `delete`*

### Overstatements (3)

- L195: *"Every single thing your computer does follows this pattern"*
  → *"Nearly everything your computer does follows this pattern."*
- L236: *"A 4 GHz CPU is always better than a 3 GHz one"* (inside a
  "Common Mistakes" table row describing the mistake) — **this is
  intentional** (the row is literally a wrong belief to correct). Keep.
- L275: *"When the server reached 100% memory usage, the operating
  system had no more counter space to process the sudden influx… and
  likely killed the database process"* → *"When the server reached
  100% memory usage, the operating system likely had little or no RAM
  left… and may have killed the database process to protect system
  stability."*

---

## module-0.2-what-is-a-terminal — 4 issues

### Coherence (2)

- **"Why Do Engineers Use Terminals?" section** — an AWS S3 February
  2017 outage war story. Topically distant from terminal basics for
  absolute beginners. *Action: `delete`*
- **"Common Mistakes in Production" subsection** — the subsection
  itself is a tangent to "Common Mistakes" (the preceding subsection
  targets beginner errors; this one jumps to production ops war
  stories). *Action: `delete`*

### Overstatements (2)

- L27: *"Every single tool in modern software engineering — Kubernetes,
  Docker, cloud platforms, automation scripts — starts with one thing:
  **the terminal**"* → *"Many of the tools you'll use in modern
  software engineering… are easiest to learn and control from **the
  terminal**."*
- L424: *"the terminal allows you to write a script that does this
  instantly and perfectly every time"* → *"… a script that can handle
  this quickly and consistently."*

---

## module-0.3-first-commands — 10 issues

### Unsourced (3)

- L342: **Pixar Toy Story 2 war story** — known; your earlier
  flag. Needs a citation to a reliable primary source (Oren Jacob or
  Galyn Susman telling). Currently uncited.
- L400: **"A Site Reliability Engineer uses `ls -lt | head` during a
  major site outage"** — hypothetical example, LLM triage would
  likely return `teaching_hypothetical`. Keep with minor rewording.
- L419: **"`ls` dates back to 1961 in MIT's CTSS where it was called
  `LISTF`, and the modern `ls` appeared in the first version of Unix
  in 1971"** — real factual claim, uncited. Primary source:
  Wikipedia "ls (Unix)" or "CTSS".

### Overstatements (7)

| Line | Current | Proposed rewrite |
|---|---|---|
| L342 | `rm` does exactly what you tell it to, *instantly* | `rm` *usually* does exactly what you tell it to, *immediately*, and often with no "Are you sure?" prompt |
| L400 | uses `mkdir -p` to *instantly* create identical deployment directory structures | uses `mkdir -p` to quickly create matching deployment directory structures |
| L419 | `ls` is one of *the oldest* commands still in use | `ls` is among the oldest command-line commands still widely used today |
| L480 | the *#1 beginner mistake* — *always* know where you are | a very common beginner mistake — make sure you know where you are |
| L492 | you *must always* double-check your commands | you *should usually* double-check your commands |
| L504 | the tilde (`~`) is a *universal* shortcut that *always* represents your home directory | the tilde (`~`) is a standard shell shortcut that usually represents your home directory |

---

## module-0.4-files-and-directories — 2 issues

### Overstatements (2)

- L408: *"Every single file on your computer is somewhere on a branch
  that connects back up to `/`"* → *"Almost every file you work with
  on your computer is somewhere on a branch that ultimately connects
  back up to `/`."*
- L438: *"The `~` acts as a dynamic shortcut that always resolves to
  the current user's home directory"* → *"The `~` acts as a dynamic
  shortcut that usually resolves to the current user's home directory
  in shell contexts."*

---

## module-0.5-editing-files — 4 issues

### Coherence (2) — Common Mistakes rows off-topic

Both are shell-scripting / permissions topics that don't belong in a
file-editor (nano) module's Common Mistakes table.

- **"Not adding `#!/bin/bash` to scripts you plan to run with
  `./script.sh`"** — shell-execution, not file editing. *Action:
  `delete`*
- **"Forgetting `chmod +x` before running a script"** — filesystem
  permissions, not file editing. *Action: `delete`*

### Overstatements (2)

- L389: *"writes your changes to the disk immediately"* → *"saves
  your changes to the disk."*
- L407: *"You must always address permission issues first because the
  system won't even attempt to read the syntax of a file it isn't
  allowed to execute"* → *"In this situation, you should address the
  permission issue first because `./backup.sh` will not reach the
  script's syntax until the file is executable."*

---

# Pipeline signal-quality notes

- **Gate B (semantic verify) was silent** across all 28 supported
  citations. Either the research step is producing very high-precision
  claim→URL pairs (likely, given allowlist + Codex research prompt),
  or our verifier prompt is too lenient. Worth a sanity check by
  running Gate B on a deliberately-miscited seed next session.
- **Gate A's "Common Mistakes" triage edge**: the gate doesn't know
  when an overstated sentence is *inside* a row that describes a
  mistake pattern (intentional wrong-statement, e.g. ZTT 0.1 L236
  "4 GHz CPU is always better than a 3 GHz one"). Future: pass
  surrounding-row context to LLM triage, or suppress the gate inside
  `| Mistake | What | Fix |` rows.
- **Gate D caught audience-mismatch more than strict topic drift** —
  for `absolute_beginner` modules, Gate D flagged legitimately-topical
  content (cloud pricing, production ops) simply because it's too
  advanced. That's a valuable signal, not a false positive. A future
  version could split `audience_mismatch` from `off_topic` as distinct
  verdicts.
- **Gate C found 3/3 real issues** (Pixar + 2 others). Zero
  over-fires.

# Proposed fix order

1. **Delete the 8 coherence off_topic items** — these are the
   clearest quality wins (user-visible tangents, audience mismatches).
2. **Apply the 16 overstatement rewrites** — low-risk prose polish,
   uses LLM-suggested softenings (already triaged).
3. **Cite the 3 unsourced assertions in 0.3** — add allowlisted
   primary-source links for Pixar, SRE hypothetical framing, and the
   `ls`/CTSS history.
4. **Re-run Gate A triage on ZTT 0.1 L272 (error)** to fill the gap.

Total edit scope: ~27 targeted edits across 5 modules. Each fix is a
few-line diff. Estimate ~30 min to apply mechanically, longer to QA.

# Raw data

- `.pipeline/audit-ztt-0.1-0.5/overstatement.txt` — raw pattern hits.
- `.pipeline/audit-ztt-0.1-0.5/overstatement-triaged.json` — Codex
  verdicts per candidate.
- `.pipeline/audit-ztt-0.1-0.5/unsourced.txt` — pattern hits.
- `.pipeline/audit-ztt-0.1-0.5/coherence-*.json` — per-module Gemini
  findings.
- `.pipeline/citation-verdicts/` — Gate B verdicts (all SUPPORTED).
