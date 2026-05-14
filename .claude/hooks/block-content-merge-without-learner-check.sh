#!/bin/bash
# shellcheck source=.claude/hooks/_lib.sh
source "${BASH_SOURCE[0]%/*}/_lib.sh"
set -euo pipefail

# Hook: PreToolUse (Bash) — block `gh pr merge` for content PRs that lack a
# verifiable "Learner check" quote. Forces the orchestrator to actually read
# the module before merging instead of trusting verifier output alone.
#
# Pass condition: PR body contains a `## Learner check` section with a
# markdown blockquote (`> ...`) whose text appears verbatim in at least one
# of the `src/content/docs/**` files the PR touches.
#
# Test overrides:
#   KUBEDOJO_HOOK_GH_JSON           Path to JSON file replacing `gh pr view`.
#   KUBEDOJO_HOOK_FILE_FIXTURE_DIR  Directory holding fixture file contents
#                                   keyed by the same relative path the PR
#                                   reports (replaces `git show <oid>:<path>`).

RAW_PAYLOAD=$(cat)

TOOL_NAME=$(jq -r '.tool_name // ""' <<<"$RAW_PAYLOAD")
if [ "$TOOL_NAME" != "Bash" ]; then
  exit 0
fi

PAYLOAD=$(read_tool_payload <<<"$RAW_PAYLOAD")
COMMAND=${PAYLOAD%%$'\t'*}
CWD=${PAYLOAD#*$'\t'}

if [ -z "$COMMAND" ]; then
  exit 0
fi

if ! printf '%s\n' "$COMMAND" | grep -Eq '(^|[;&|[:space:]])gh[[:space:]]+pr[[:space:]]+merge([[:space:]]|$)'; then
  exit 0
fi

PR_REF=$(python3 -c '
import shlex, sys
command = sys.argv[1]
try:
    tokens = shlex.split(command)
except ValueError:
    sys.exit(0)
found = False
for index, token in enumerate(tokens):
    if found:
        if token.startswith("-"):
            continue
        print(token)
        sys.exit(0)
    if token == "gh" and index + 2 < len(tokens) and tokens[index + 1] == "pr" and tokens[index + 2] == "merge":
        found = True
' "$COMMAND" || true)

if [ -n "${KUBEDOJO_HOOK_GH_JSON:-}" ] && [ -f "${KUBEDOJO_HOOK_GH_JSON}" ]; then
  PR_JSON=$(cat "${KUBEDOJO_HOOK_GH_JSON}")
else
  if ! command -v gh >/dev/null 2>&1; then
    exit 0
  fi
  if [ -n "$PR_REF" ]; then
    PR_JSON=$(gh pr view "$PR_REF" --json body,files,headRefOid,title,number 2>/dev/null || true)
  else
    PR_JSON=$(cd "$CWD" 2>/dev/null && gh pr view --json body,files,headRefOid,title,number 2>/dev/null || true)
  fi
  if [ -z "$PR_JSON" ]; then
    exit 0
  fi
fi

HOOK_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
VERDICT=$(KUBEDOJO_HOOK_FILE_FIXTURE_DIR="${KUBEDOJO_HOOK_FILE_FIXTURE_DIR:-}" \
  python3 "$HOOK_DIR/_lib_pr_check.py" learner "$PR_JSON" || true)

VERDICT_KIND=${VERDICT%%$'\t'*}
VERDICT_MSG=${VERDICT#*$'\t'}

if [ "$VERDICT_KIND" = "DENY" ]; then
  deny \
    "content merge blocked: $VERDICT_MSG" \
    "Add a '## Learner check' section with a markdown blockquote (> ...) >= 30 chars copied verbatim from a touched module." \
    "feedback_teaching_not_listicles.md"
fi

exit 0
