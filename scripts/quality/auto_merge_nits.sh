#!/usr/bin/env bash
# Overnight chain helper: auto-merge any merge_held_nits PR from the marathon JSONL log.
# v2: order is (a) remote merge without --delete-branch, (b) worktree remove --force,
# (c) local branch delete. v1 used --delete-branch which always fails the local delete
# when the worktree still exists, even though the remote merge succeeded.

set -u
LOG_FILE="${1:-logs/388_cka_part2_2026-05-09.jsonl}"
OUT_LOG="${LOG_FILE}.auto-merger.log"
SEEN_FILE="${LOG_FILE}.auto-merger.seen"
touch "$SEEN_FILE"

source ./.envrc 2>/dev/null
unset GITHUB_TOKEN 2>/dev/null

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] auto-merger v2 started, watching $LOG_FILE" >> "$OUT_LOG"

tail -F -n +1 "$LOG_FILE" 2>/dev/null | while IFS= read -r line; do
  if echo "$line" | grep -q '"event": "merge_held_nits"'; then
    PR=$(echo "$line" | python3 -c "import sys, json; print(json.loads(sys.stdin.read()).get('pr', ''))" 2>/dev/null)
    MODULE=$(echo "$line" | python3 -c "import sys, json; print(json.loads(sys.stdin.read()).get('module', ''))" 2>/dev/null)
    if [ -z "$PR" ]; then continue; fi
    if grep -q "^$PR\$" "$SEEN_FILE"; then continue; fi
    echo "$PR" >> "$SEEN_FILE"

    SLUG=$(basename "$MODULE" .md | sed 's/\./-/g')
    WT=".worktrees/codex-388-pilot-${SLUG}"
    BRANCH="codex/388-pilot-${SLUG}"

    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] auto-merging PR #$PR ($MODULE)" >> "$OUT_LOG"
    if gh pr merge "$PR" --squash --admin >> "$OUT_LOG" 2>&1; then
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] PR #$PR remote merged" >> "$OUT_LOG"
    else
      # Check if it merged anyway (e.g., if --delete-branch failed but merge succeeded)
      if gh pr view "$PR" --json state -q .state 2>/dev/null | grep -q MERGED; then
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] PR #$PR already MERGED on origin" >> "$OUT_LOG"
      else
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] PR #$PR merge FAILED" >> "$OUT_LOG"
        continue
      fi
    fi

    if [ -d "$WT" ]; then
      git worktree remove "$WT" --force >> "$OUT_LOG" 2>&1
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] worktree $WT removed" >> "$OUT_LOG"
    fi
    git branch -D "$BRANCH" >> "$OUT_LOG" 2>&1
    git push origin --delete "$BRANCH" >> "$OUT_LOG" 2>&1 || true
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] cleanup done for $SLUG" >> "$OUT_LOG"
  fi
done
