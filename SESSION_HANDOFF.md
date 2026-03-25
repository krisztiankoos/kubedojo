# Session Handoff — 2026-03-25 (Session 2)

## What Was Done This Session

### Infrastructure
- **Replaced ai_agent_bridge with dispatch.py** — 1,800+ lines → 230 lines. Direct CLI calls, no SQLite broker. Gemini-reviewed, 3 deadlock bugs fixed.
- **Added dispatch logging** — JSON logs to `.dispatch-logs/` with `python scripts/dispatch.py logs`
- **Consolidated 12 skills → 4** — k8s-cert-expert, platform-expert, curriculum-writer, module-quality-reviewer. Closed #129.
- **Supply chain hardening** — Pinned GH Actions to SHA, generated requirements.lock with hashes, enabled Dependabot. Closed #131.

### Starlight Migration (MkDocs → Astro)
- **Wrote migrate-to-starlight.py** — Converts 648 English + 115 Ukrainian files (frontmatter injection, README→index, .uk.md→uk/ directory, link fixup, sidebar ordering from mkdocs.yml)
- **Scaffolded Astro/Starlight project** — astro.config.mjs, package.json, content.config.ts, custom CSS
- **Fixed critical bugs** found via Chrome browser investigation:
  - 5,323 broken `.md` links → stripped all `.md` extensions from internal links
  - Dots stripped from slugs (module-1.1 → module-11) → explicit `slug:` frontmatter
  - Sidebar showing parent label on all children → only set on index pages
  - 2 corrupted Ukrainian files (watchdog output) → cleaned + added H1 titles
- **Removed old MkDocs** — deleted docs/, mkdocs.yml, requirements.txt, .venv
- **Rewrote health check** for Starlight (frontmatter, link format, module count)
- **Build**: 1,298 pages in ~30-80s (vs MkDocs 60s). Closed #130.

### Content
- **Trivy/LiteLLM supply chain attack** (March 2026) — Added as war story to 3 modules + new "Did You Know" in Trivy module
- **Supply Chain Defense Guide** — New standalone practical guide (CI/CD hardening, dependency management, container security, K8s runtime defense, incident response)
- **Updated STATUS.md** — Accurate 528 module count, current open issues
- **Fixed all build warnings** — 19 missing README nav entries, 10 broken relative links, broken link to renamed module

### Fixes
- Fixed start-docs.sh (mkdocs flags)
- Fixed start-claude.sh (STATUS.md parsing, GitHub URL)
- Renamed uk-glossary.md → glossary.md for i18n handling
- Removed glossary from nav until Starlight per-locale nav

## Open Issues
- #14 — Curriculum monitoring (ongoing)
- #105 — Ukrainian translation (~40% done)

## Not Yet Done
- **Gemini adversary review** of ~100+ unreviewed modules (started, in progress)
- **Ukrainian sidebar translations** (`src/content/i18n/uk.json` for sidebar labels)
- **Start scripts** need updating for Node.js (start-docs.sh still references MkDocs)

## Key Decisions
- Pinned zod@3.25.76 (zod v4 breaks Starlight schema validation)
- Used `defaultLocale: 'root'` (not `'en'`) for Starlight i18n — keeps English content at root URLs
- Starlight sidebar uses `autogenerate` with `sidebar.order` frontmatter — no 700-line manual config
- Removed duplicate @astrojs/sitemap (Starlight includes it automatically)

## Unpushed Commits
None — all pushed.
