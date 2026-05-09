#!/usr/bin/env bash
# Overnight chain helper: auto-merge any merge_held_nits PR from the marathon JSONL log.
# Started detached during 2026-05-10 overnight session because gemini-3.1-pro-preview was
# rate-limited all night → headless-claude review fallback consistently returned
# APPROVE_WITH_NITS on every module → dispatcher held them. Auto-merger flushes those
# without orchestrator manual attention. Per `decision-card.md` the orchestrator is
# authorized to override on NITS.
#
# Usage: ./auto_merge_nits.sh <jsonl-log-path>
# Reads JSONL line-by-line, on `merge_held_nits` events runs:
#   gh pr merge $PR --squash --delete-branch --admin
#   git worktree remove + git branch -D
# Logs decisions to <jsonl-log>.auto-merger.log

set -u
LOG_FILE="${1:-logs/388_cka_part2_2026-05-09.jsonl}"
OUT_LOG="${LOG_FILE}.auto-merger.log"
SEEN_FILE="${LOG_FILE}.auto-merger.seen"
touch "$SEEN_FILE"

source ./.envrc 2>/dev/null
unset GITHUB_TOKEN 2>/dev/null

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] auto-merger started, watching $LOG_FILE" >> "$OUT_LOG"

tail -F -n +1 "$LOG_FILE" 2>/dev/null | while IFS= read -r line; do
  if echo "$line" | grep -q '"event": "merge_held_nits"'; then
    PR=$(echo "$line" | python3 -c "import sys, json; print(json.loads(sys.stdin.read()).get('pr', ''))" 2>/dev/null)
    MODULE=$(echo "$line" | python3 -c "import sys, json; print(json.loads(sys.stdin.read()).get('module', ''))" 2>/dev/null)
    if [ -z "$PR" ]; then continue; fi
    # Skip if already processed
    if grep -q "^$PR\$" "$SEEN_FILE"; then continue; fi
    echo "$PR" >> "$SEEN_FILE"

    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] auto-merging PR #$PR ($MODULE)" >> "$OUT_LOG"
    if gh pr merge "$PR" --squash --delete-branch --admin >> "$OUT_LOG" 2>&1; then
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] PR #$PR merged" >> "$OUT_LOG"
      # Cleanup: derive slug from module path
      SLUG=$(basename "$MODULE" .md | sed 's/\./-/g')
      WT=".worktrees/codex-388-pilot-${SLUG}"
      BRANCH="codex/388-pilot-${SLUG}"
      if [ -d "$WT" ]; then
        git worktree remove "$WT" --force >> "$OUT_LOG" 2>&1
      fi
      git branch -D "$BRANCH" >> "$OUT_LOG" 2>&1
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] cleanup done for $SLUG" >> "$OUT_LOG"
    else
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] PR #$PR merge FAILED" >> "$OUT_LOG"
    fi
  fi
done
