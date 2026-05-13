#!/bin/bash
# shellcheck source=.claude/hooks/_lib.sh
source "${BASH_SOURCE[0]%/*}/_lib.sh"
set -euo pipefail

# Hook: PreToolUse (Bash) — Block direct commits to main unless the subject is pipeline-owned or PR-backed.

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

if ! echo "$COMMAND" | grep -Eq '(^|[;&|[:space:]])git[[:space:]]+commit([[:space:]]|$)'; then
  exit 0
fi

BRANCH=$(git -C "$CWD" rev-parse --abbrev-ref HEAD 2>/dev/null || true)
if [ "$BRANCH" != "main" ]; then
  exit 0
fi

PARSE_RESULT=$(python3 -c '
import shlex
import sys

command = sys.argv[1]

try:
    tokens = shlex.split(command)
except ValueError as exc:
    print(f"UNKNOWN\tcould not parse shell command ({exc})")
    raise SystemExit

args = None
for index, token in enumerate(tokens[:-1]):
    if token == "git" and tokens[index + 1] == "commit":
        args = tokens[index + 2 :]
        break

if args is None:
    print("UNKNOWN\tmatched git commit text, but could not locate argv")
    raise SystemExit

for index, token in enumerate(args):
    if token in {"-F", "--file"}:
        print("UNKNOWN\tcommit message comes from a file")
        raise SystemExit
    if token.startswith("-F") and token != "-F":
        print("UNKNOWN\tcommit message comes from a file")
        raise SystemExit
    if token.startswith("--file="):
        print("UNKNOWN\tcommit message comes from a file")
        raise SystemExit

subject = None
for index, token in enumerate(args):
    if token in {"-m", "--message"}:
        if index + 1 >= len(args):
            print("UNKNOWN\t-m was present without a statically visible message")
            raise SystemExit
        subject = args[index + 1]
        break
    if token.startswith("-m") and token != "-m":
        subject = token[2:]
        break
    if token.startswith("--message="):
        subject = token.split("=", 1)[1]
        break

if subject is None:
    if "--amend" in args and "--no-edit" in args:
        print("UNKNOWN\tcommit amend keeps the existing message")
    else:
        print("UNKNOWN\tno statically visible -m commit subject")
    raise SystemExit

if subject.startswith("$("):
    print("UNKNOWN\tcommit subject is dynamically built with command substitution")
    raise SystemExit

print("SUBJECT\t" + (subject.splitlines()[0] if subject else ""))
' "$COMMAND" || true)

PARSE_KIND=${PARSE_RESULT%%$'\t'*}
PARSE_VALUE=${PARSE_RESULT#*$'\t'}

if [ "$PARSE_KIND" != "SUBJECT" ]; then
  printf '[hook note] direct commit to main not introspected: %s; allowing.\n' "$PARSE_VALUE" >&2
  exit 0
fi

SUBJECT=$PARSE_VALUE

case "$SUBJECT" in
  backfill* | handoff* | docs\(status\):*)
    exit 0
    ;;
esac

if printf '%s\n' "$SUBJECT" | grep -Eq '\(#[0-9]+\)'; then
  exit 0
fi

deny \
  "direct commit to main without PR ref is blocked." \
  "subject must start with one of [backfill, handoff, docs(status):] OR contain (#N)." \
  "feedback_no_direct_push_to_main.md"
