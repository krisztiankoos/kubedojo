# GitHub Actions Security

Defensive rules for `.github/workflows/**` and `.github/actions/**`. Enforced by `zizmor.yml`.

## 1. Pin every `uses:` to a full commit SHA

Format: `uses: owner/repo@<40-char SHA>  # vX.Y.Z`

Why: tags are mutable. The 2026-05-19 actions-cool incident moved every tag of two actions to imposter commits in attacker-controlled forks; only SHA-pinned consumers were unaffected. Same attack class hit `tj-actions/changed-files` in 2026-03. Org-agnostic — applies to `actions/*` (GitHub's own org) just as much as third-party.

The version comment matters: it tells Dependabot what tag this SHA tracks, so Dependabot updates can flow.

## 2. Resolve SHAs from the upstream repo, not from a blog post

```bash
curl -s "https://api.github.com/repos/<owner>/<repo>/git/refs/tags/<tag>" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['object']['sha'])"
```

Or with auth: `gh api /repos/<owner>/<repo>/git/refs/tags/<tag> --jq '.object.sha'`.

## 3. `persist-credentials: false` on every `actions/checkout`

Unless the workflow needs to `git push` (almost never the case for this repo's workflows), set `persist-credentials: false` on the checkout step. Prevents the `GITHUB_TOKEN` from sitting in `.git/config` for subsequent steps to exfiltrate.

## 4. Permissions scoped to the job, not the workflow

Workflow-level `permissions:` apply to all jobs. Privileged scopes (`pages: write`, `id-token: write`, `contents: write`, `packages: write`) must live on the specific job that needs them.

## 5. Reviewing a Dependabot github-actions PR

Dependabot maintains the SHA-pinning pattern when the existing entry uses a SHA. But the PR can still be the attack delivery vector if Dependabot is fed a poisoned tag. Before merging:

```bash
# Verify the new SHA actually points to the claimed tag in the upstream repo
gh api /repos/<owner>/<repo>/git/refs/tags/<tag> --jq '.object.sha'
# Should match the SHA in the PR diff. If not, do not merge.
```

**Do not enable auto-merge on `github-actions` Dependabot PRs.** They are the single highest-impact PR class in this repo (CI runs with broad permissions).

## 6. New workflow checklist

When adding a `.github/workflows/*.yml`:

1. Every `uses:` is SHA-pinned with version comment.
2. `permissions:` block is present and starts from `contents: read` minimum.
3. Privileged scopes are job-level, not workflow-level.
4. `actions/checkout` has `persist-credentials: false` unless the workflow pushes commits.
5. Run `uvx zizmor --offline .github/workflows/<new-file>.yml` locally — must be clean.
6. CI's `zizmor` workflow will re-run the scan on the PR and block on findings.

## References

- The Hacker News, 2026-05-19: https://thehackernews.com/2026/05/github-actions-supply-chain-attack.html (actions-cool incident).
- zizmor audits: https://docs.zizmor.sh/audits/
- Memory: `feedback_actions_pin_to_sha.md`
