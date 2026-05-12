#!/usr/bin/env bash
# kill_chain_at_boundary.sh — watch chain log; SIGTERM chain when current
# module is fully done (verdict logged) AND next module hasn't started yet.
#
# Usage:
#   ./scripts/quality/kill_chain_at_boundary.sh <chain_pid> <log_file> <current_module_slug>
#
# Exits 0 after sending SIGTERM, 1 on timeout (default 30 min cap).

set -uo pipefail

CHAIN_PID="$1"
LOG="$2"
CURRENT_SLUG="$3"
TIMEOUT_S="${4:-1800}"

mark_log() {
    printf '[%s] kill-watcher: %s\n' "$(date '+%H:%M:%S')" "$*" | tee -a logs/388_chain_2026-05-12.log
}

mark_log "watching log=$LOG current_slug=$CURRENT_SLUG chain_pid=$CHAIN_PID timeout=${TIMEOUT_S}s"

start_ts=$(date +%s)
INITIAL_LINES=$(wc -l < "$LOG")

while true; do
    now=$(date +%s)
    if [ $((now - start_ts)) -gt "$TIMEOUT_S" ]; then
        mark_log "TIMEOUT after ${TIMEOUT_S}s — NOT killing. Investigate manually."
        exit 1
    fi

    # Look for any event AFTER initial line count that indicates the
    # current module FINISHED. Verdict events: merge_held_nits, merge_held,
    # merge_failed, module_skip. Also a NEW module_start with different slug.
    NEW_LINES=$(tail -n +$((INITIAL_LINES + 1)) "$LOG" 2>/dev/null)

    if [ -n "$NEW_LINES" ]; then
        # check for verdict on current module
        if echo "$NEW_LINES" | grep -qE "\"slug\":\s*\"${CURRENT_SLUG}\".*\"event\":\s*\"(merge_held_nits|merge_held|merge_failed|module_skip)\""; then
            mark_log "verdict logged for ${CURRENT_SLUG} — killing chain PID $CHAIN_PID"
            kill -TERM "$CHAIN_PID"
            sleep 2
            if kill -0 "$CHAIN_PID" 2>/dev/null; then
                mark_log "SIGTERM didn't take, sending SIGKILL"
                kill -KILL "$CHAIN_PID"
            fi
            mark_log "chain killed cleanly at module boundary (after ${CURRENT_SLUG})"
            exit 0
        fi

        # also check for next module_start with different slug
        NEXT_SLUG=$(echo "$NEW_LINES" | grep -oE '"event":\s*"module_start".*"slug":\s*"[^"]+"' | grep -oE '"slug":\s*"[^"]+"' | head -1 | sed 's/.*"\([^"]*\)"/\1/')
        if [ -n "$NEXT_SLUG" ] && [ "$NEXT_SLUG" != "$CURRENT_SLUG" ]; then
            mark_log "next module_start detected: $NEXT_SLUG — killing chain PID $CHAIN_PID"
            kill -TERM "$CHAIN_PID"
            sleep 2
            if kill -0 "$CHAIN_PID" 2>/dev/null; then
                kill -KILL "$CHAIN_PID"
            fi
            mark_log "chain killed at module boundary (before $NEXT_SLUG started its codex run)"
            exit 0
        fi
    fi

    sleep 5
done
