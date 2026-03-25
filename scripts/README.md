# KubeDojo Scripts

## check_site_health.py

Validates site integrity — run before every push.

```bash
# Run the health check
python scripts/check_site_health.py
```

**What it checks:**
1. All `mkdocs.yml` nav entries point to existing files
2. No orphaned `.md` files missing from navigation
3. All internal markdown links resolve (`[text](path.md)`)
4. Changelog has links for every mentioned module
5. No duplicate nav entries
6. Module count in STATUS.md matches actual files
7. README files reference their child modules

**Exit codes:** 0 = pass, 1 = errors found

**When to run:**
- Before every `git push`
- After adding new modules
- After updating navigation or changelog

---

## dispatch.py

Direct CLI dispatch for Gemini and Claude — calls CLIs as subprocesses with no broker or database.

### Quick Usage

```bash
# Review a module (--review adds KubeDojo review context)
python scripts/dispatch.py gemini \
  "Review docs/k8s/cka/part3-services-networking/module-3.5-gateway-api.md for technical accuracy" \
  --review

# Review a GitHub issue and post result as comment
python scripts/dispatch.py gemini \
  "Review issue #66: $(gh issue view 66 --json body --jq .body)" \
  --review --github 66

# Review a diff
python scripts/dispatch.py gemini \
  "Review this diff for accuracy: $(git diff HEAD~3..HEAD -- docs/)" \
  --review

# Read prompt from stdin
cat prompt.txt | python scripts/dispatch.py gemini - --review

# Use Claude for expansion
python scripts/dispatch.py claude "Expand this draft to full depth..."
```

### Programmatic Usage

```python
from scripts.dispatch import dispatch_gemini_with_retry, post_to_github

ok, output = dispatch_gemini_with_retry("Review this module...", review=True)
if ok:
    post_to_github(66, output, "gemini-3.1-pro-preview")
```

### Review Criteria

Gemini reviews KubeDojo content against these criteria (auto-injected with `--review`):
- **Technical accuracy**: K8s commands correct and runnable, version numbers accurate
- **Exam alignment**: Content matches current CNCF exam curriculum
- **Completeness**: Acceptance criteria thorough, edge cases covered
- **Junior-friendly**: Beginner-accessible, "why" explained not just "what"

### Architecture

- **No broker** — direct `subprocess.Popen` / `subprocess.run` calls to `gemini` and `claude` CLIs
- **Streaming** — Gemini output streams to stdout in real-time
- **Retry** — exponential backoff on rate limits (default 3 retries)
- **GitHub integration** — posts reviews as issue comments via `gh` CLI (with chunking for long reviews)
