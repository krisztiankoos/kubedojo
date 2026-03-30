# Starlight Stack Upgrade — Reusable Prompt

> Battle-tested from Learn Ukrainian (Astro 5→6, React 4→5, Starlight 0.37→0.38, Vitest 3→4).
> Use this prompt when upgrading a Starlight site's core dependencies.

---

## The #1 Rule

**Upgrade all major deps together — don't leave half the stack on old versions.**

Astro, @astrojs/react, and @astrojs/starlight are tightly coupled. Upgrading one without the others causes peer dependency conflicts.

---

## Pre-flight Checks

```bash
# 1. Verify current build passes
npm run build

# 2. Run tests
npm test

# 3. Check current versions
cat package.json | grep -E '"(astro|@astrojs|vitest|@vitest)'

# 4. Check for Dependabot PRs that can be superseded
gh pr list --state open --json number,title | jq '.[] | select(.title | test("deps|Bump"))'
```

---

## Upgrade Strategy

### Option A: Direct upgrade on main (recommended for small teams)

```bash
cd starlight/

# Upgrade all core deps in one command
npm install astro@latest @astrojs/react@latest @astrojs/starlight@latest @astrojs/sitemap@latest

# If you use vitest, upgrade together (vitest + plugins must match versions)
npm install vitest@latest @vitest/coverage-v8@latest @vitest/ui@latest

# Verify
npm run build
npm test
```

### Option B: Via Dependabot PRs (when they exist)

1. Merge the **smallest** PR first (minor bumps before major)
2. Pull to local, run `npm install && npm run build && npm test`
3. If lock file conflicts: `git checkout --theirs package-lock.json && npm install --package-lock-only`
4. Merge the next PR, repeat

---

## Common Issues & Fixes

### Peer dependency conflicts

```
npm error Could not resolve dependency:
npm error peer vitest@"4.x" from @vitest/coverage-v8@4.x
```

**Fix:** Upgrade vitest + all @vitest/* packages together in one `npm install` command.

### Lock file merge conflicts

```
CONFLICT (content): Merge conflict in package-lock.json
```

**Fix:** Don't manually resolve. Regenerate:
```bash
git checkout --theirs package-lock.json
npm install --package-lock-only
```

### Astro major version content changes

Astro major versions sometimes change the content collections API. Watch for:
- `[content] Astro config changed` — normal, auto-handled
- `[content] Clearing content store` — normal, rebuilds on first run
- Import path changes (e.g., `@astrojs/starlight/props` → `Astro.locals.starlightRoute`)

### Starlight component override API changes

Check if your component overrides still work after upgrade:
- **Astro 6 / Starlight 0.38:** Props accessed via `Astro.locals.starlightRoute`, NOT `Astro.props`
- Virtual imports for sub-components (Search, ThemeSelect) remain stable
- `StarlightRouteData` type includes: `sidebar`, `entry`, `headings`, `toc`, `pagination`, `head`

### React integration changes

- `@astrojs/react@5` aligns with Astro 6's rendering pipeline
- `client:load` and `client:visible` directives unchanged
- Check `vite.resolve.dedupe` config still lists `['react', 'react-dom']`

---

## Post-Upgrade Verification

```bash
# 1. Build — must produce same page count, 0 errors
npm run build

# 2. Tests — all must pass
npm test

# 3. Dev server — spot check in browser
npm run dev
# Check: homepage, docs page, search, theme toggle, all component overrides

# 4. TypeScript — no new errors
npx tsc --noEmit
```

---

## Closing Dependabot PRs

After upgrading directly, close superseded Dependabot PRs:

```bash
gh pr close <number> --comment "Upgraded directly on main — <package>@<version> installed and verified."
```

---

## Version Compatibility Matrix (as of 2026-03)

| Package | Compatible Range | Notes |
|---------|-----------------|-------|
| astro | 6.x | Major: content collections API stable |
| @astrojs/react | 5.x | Must match Astro 6 |
| @astrojs/starlight | 0.38.x | Component override API: `Astro.locals.starlightRoute` |
| @astrojs/sitemap | 3.x | No breaking changes |
| vitest | 4.x | All @vitest/* must match exactly |
| @vitest/coverage-v8 | 4.x | Peer dep: must match vitest version |
| @vitest/ui | 4.x | Peer dep: must match vitest version |
