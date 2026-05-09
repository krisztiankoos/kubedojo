#!/usr/bin/env bash
# Overnight chain helper: cleanup stale worktrees + branches from the marathon.
# v3: handle BOTH `merged` (dispatcher-driven, just cleanup) and `merge_held_nits`
#     (orchestrator-driven, do the merge first then cleanup). v2 only handled
#     merge_held_nits, which left 7 worktrees behind from the early happy-path merges.

set -u
LOG_FILE="${1:-logs/388_cka_part2_2026-05-09.jsonl}"
OUT_LOG="${LOG_FILE}.auto-merger.log"
SEEN_FILE="${LOG_FILE}.auto-merger.seen"
touch "$SEEN_FILE"

source ./.envrc 2>/dev/null
unset GITHUB_TOKEN 2>/dev/null

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] auto-merger v3 started, watching $LOG_FILE" >> "$OUT_LOG"

cleanup_pr() {
  local PR="$1"
  local MODULE="$2"
  local SLUG=$(basename "$MODULE" .md | sed 's/\./-/g')
  local WT=".worktrees/codex-388-pilot-${SLUG}"
  local BRANCH="codex/388-pilot-${SLUG}"
  if [ -d "$WT" ]; then
    git worktree remove "$WT" --force >> "$OUT_LOG" 2>&1
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] worktree $WT removed" >> "$OUT_LOG"
  fi
  git branch -D "$BRANCH" >> "$OUT_LOG" 2>&1
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] cleanup done for $SLUG" >> "$OUT_LOG"
}

tail -F -n +1 "$LOG_FILE" 2>/dev/null | while IFS= read -r line; do
  EVENT=$(echo "$line" | python3 -c "import sys, json; print(json.loads(sys.stdin.read()).get('event', ''))" 2>/dev/null)

  case "$EVENT" in
    merge_held_nits)
      PR=$(echo "$line" | python3 -c "import sys, json; print(json.loads(sys.stdin.read()).get('pr', ''))" 2>/dev/null)
      MODULE=$(echo "$line" | python3 -c "import sys, json; print(json.loads(sys.stdin.read()).get('module', ''))" 2>/dev/null)
      KEY="held:$PR"
      if [ -z "$PR" ] || grep -q "^$KEY\$" "$SEEN_FILE"; then continue; fi
      echo "$KEY" >> "$SEEN_FILE"
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] auto-merging held PR #$PR ($MODULE)" >> "$OUT_LOG"
      if gh pr merge "$PR" --squash --admin >> "$OUT_LOG" 2>&1; then
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] PR #$PR remote merged" >> "$OUT_LOG"
      elif gh pr view "$PR" --json state -q .state 2>/dev/null | grep -q MERGED; then
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] PR #$PR already MERGED" >> "$OUT_LOG"
      else
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] PR #$PR merge FAILED" >> "$OUT_LOG"
        continue
      fi
      cleanup_pr "$PR" "$MODULE"
      ;;
    merged)
      PR=$(echo "$line" | python3 -c "import sys, json; print(json.loads(sys.stdin.read()).get('pr', ''))" 2>/dev/null)
      MODULE=$(echo "$line" | python3 -c "import sys, json; print(json.loads(sys.stdin.read()).get('module', ''))" 2>/dev/null)
      KEY="merged:$PR"
      if [ -z "$PR" ] || grep -q "^$KEY\$" "$SEEN_FILE"; then continue; fi
      echo "$KEY" >> "$SEEN_FILE"
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] dispatcher-merged PR #$PR — cleanup only" >> "$OUT_LOG"
      cleanup_pr "$PR" "$MODULE"
      ;;
  esac
done
