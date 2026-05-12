#!/bin/bash
# Hook: PreToolUse (Bash) — Block branch creation in the primary repo dir.

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
if [ -z "$COMMAND" ]; then
  exit 0
fi

if ! echo "$COMMAND" | grep -Eq '(^|[;&|[:space:]])git[[:space:]]+checkout([^;&|]*)[[:space:]]+-[bB]([[:space:]]|$)|(^|[;&|[:space:]])git[[:space:]]+switch([^;&|]*)[[:space:]]+-[cC]([[:space:]]|$)'; then
  exit 0
fi

normalize_path() {
  if [ -d "$1" ]; then
    (cd "$1" && pwd -P)
  else
    printf '%s\n' "$1"
  fi
}

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
PRIMARY_DIR=$(git -C "$PROJECT_DIR" worktree list --porcelain 2>/dev/null | awk '/^worktree / {sub(/^worktree /, ""); print; exit}')
if [ -z "$PRIMARY_DIR" ]; then
  PRIMARY_DIR="$PROJECT_DIR"
fi

CWD=$(echo "$INPUT" | jq -r '.tool_input.cwd // .tool_input.workdir // .cwd // empty' 2>/dev/null)
if [ -z "$CWD" ]; then
  CWD="$PWD"
fi

PRIMARY_DIR=$(normalize_path "$PRIMARY_DIR")
CWD=$(normalize_path "$CWD")

case "$CWD/" in
  "$PRIMARY_DIR/.worktrees/"*)
    exit 0
    ;;
esac

case "$CWD/" in
  "$PRIMARY_DIR" | "$PRIMARY_DIR/"*)
    printf '%s\n' \
      "branch creation in the primary repo dir is blocked." \
      "Use a worktree under \`.worktrees/\` instead." \
      "See feedback_never_branch_in_primary_dir.md." >&2
    exit 2
    ;;
esac

exit 0
