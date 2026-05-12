#!/usr/bin/env bash
# run_388_chain.sh — sequentially run dispatch_388_pilot.py over 3 queues.
# Started 2026-05-12 overnight to lift prereqs → ai → ai/ml-engineering.
#
# Usage:
#   ./scripts/quality/run_388_chain.sh
#
# Each track writes its own JSONL log under logs/. The chain marker log
# captures phase transitions for the morning briefing.

set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO"

CHAIN_LOG="$REPO/logs/388_chain_2026-05-12.log"
mkdir -p "$REPO/logs"

note() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$CHAIN_LOG"
}

note "chain_start pid=$$ tracks=prereqs,ai,ai-ml-engineering total=168"

for phase in prereqs ai ai-ml; do
    queue="$REPO/scripts/quality/queue-${phase}.txt"
    log="$REPO/logs/388_chain_2026-05-12_${phase}.jsonl"
    n=$(wc -l < "$queue")
    note "phase_start phase=${phase} count=${n} queue=${queue}"
    "$REPO/.venv/bin/python" "$REPO/scripts/quality/dispatch_388_pilot.py" \
        --input "$queue" \
        --log "$log"
    rc=$?
    note "phase_end phase=${phase} rc=${rc}"
done

note "chain_end"
