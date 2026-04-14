from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .control_plane import (
    DEFAULT_BUDGETS_PATH,
    DEFAULT_DB_PATH,
    ControlPlane,
)
from .patch_worker import PatchWorker
from .preflight import run_preflight
from .review_worker import ReviewWorker
from .watchdog import sweep_once, watch_forever


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Week 1 v2 pipeline control plane")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Path to .pipeline/v2.db")
    parser.add_argument(
        "--budgets",
        type=Path,
        default=DEFAULT_BUDGETS_PATH,
        help="Path to .pipeline/budgets.yaml",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    enqueue = subparsers.add_parser("enqueue", help="Enqueue a pending job")
    enqueue.add_argument("module_key")
    enqueue.add_argument("--phase", required=True)
    enqueue.add_argument("--model", required=True)
    enqueue.add_argument("--priority", type=int, default=100)
    enqueue.add_argument("--requested-calls", type=int, default=1)
    enqueue.add_argument("--estimated-usd", type=float, default=0.0)

    lease_next = subparsers.add_parser("lease-next", help="Lease the next pending job")
    lease_next.add_argument("worker_id")
    lease_next.add_argument("--model")
    lease_next.add_argument("--requested-calls", type=int)
    lease_next.add_argument("--estimated-usd", type=float)
    lease_next.add_argument("--lease-seconds", type=int, default=900)
    lease_next.add_argument("--json", action="store_true")

    complete = subparsers.add_parser("complete", help="Record usage and complete a lease")
    complete.add_argument("lease_id")
    complete.add_argument("--actual-calls", type=int, default=1)
    complete.add_argument("--actual-usd", type=float, default=0.0)
    complete.add_argument("--tokens-in", type=int, default=0)
    complete.add_argument("--tokens-out", type=int, default=0)

    show = subparsers.add_parser("show", help="Inspect control-plane state")
    show_subparsers = show.add_subparsers(dest="show_command", required=True)
    show_budget = show_subparsers.add_parser("budget", help="Show current usage vs caps")
    show_budget.add_argument("--json", action="store_true")
    show_needs_human = show_subparsers.add_parser(
        "needs-human",
        help="Show modules dead-lettered for human intervention",
    )
    show_needs_human.add_argument("--json", action="store_true")
    show_flapping = show_subparsers.add_parser(
        "flapping",
        help="Show modules with more than three attempts",
    )
    show_flapping.add_argument("--json", action="store_true")

    budget = subparsers.add_parser("budget", help="Alias for show budget; also supports edits")
    budget.add_argument("--json", action="store_true")
    budget_subparsers = budget.add_subparsers(dest="budget_command")
    budget_set = budget_subparsers.add_parser("set", help="Set a model budget field")
    budget_set.add_argument("model")
    budget_set.add_argument("field")
    budget_set.add_argument("value")

    watchdog = subparsers.add_parser("watchdog", help="Manual watchdog controls")
    watchdog_subparsers = watchdog.add_subparsers(dest="watchdog_command", required=True)
    watchdog_subparsers.add_parser("sweep", help="Release expired leases once")
    watchdog_loop = watchdog_subparsers.add_parser("loop", help="Run the optional watchdog loop")
    watchdog_loop.add_argument("--interval-seconds", type=int, default=30)

    review_worker = subparsers.add_parser("review-worker", help="Run the Week 2 review worker")
    review_worker_subparsers = review_worker.add_subparsers(
        dest="review_worker_command",
        required=True,
    )
    review_worker_run = review_worker_subparsers.add_parser("run", help="Review one queued job")
    review_worker_run.add_argument("--worker-id", default="review-worker")
    review_worker_run.add_argument("--json", action="store_true")
    review_worker_loop = review_worker_subparsers.add_parser("loop", help="Run the review worker loop")
    review_worker_loop.add_argument("--worker-id", default="review-worker")
    review_worker_loop.add_argument("--sleep-seconds", type=float, default=5.0)

    patch_worker = subparsers.add_parser("patch-worker", help="Run the Week 3 patch worker")
    patch_worker_subparsers = patch_worker.add_subparsers(
        dest="patch_worker_command",
        required=True,
    )
    patch_worker_run = patch_worker_subparsers.add_parser("run", help="Patch one queued job")
    patch_worker_run.add_argument("--worker-id", default="patch-worker")
    patch_worker_run.add_argument("--json", action="store_true")
    patch_worker_loop = patch_worker_subparsers.add_parser("loop", help="Run the patch worker loop")
    patch_worker_loop.add_argument("--worker-id", default="patch-worker")
    patch_worker_loop.add_argument("--sleep-seconds", type=float, default=5.0)

    preflight = subparsers.add_parser("preflight", help="Run deterministic pre-flight checks")
    preflight.add_argument("module_path", type=Path)
    preflight.add_argument("--json", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    control_plane = ControlPlane(db_path=args.db, budgets_path=args.budgets)

    if args.command == "enqueue":
        job = control_plane.enqueue(
            args.module_key,
            phase=args.phase,
            model=args.model,
            priority=args.priority,
            requested_calls=args.requested_calls,
            estimated_usd=args.estimated_usd,
        )
        print(
            f"enqueued job {job.job_id} {job.module_key} "
            f"({job.phase}/{job.model}) idempotency_key={job.idempotency_key}"
        )
        return 0

    if args.command == "lease-next":
        lease = control_plane.lease_next_job(
            args.worker_id,
            model=args.model,
            requested_calls=args.requested_calls,
            estimated_usd=args.estimated_usd,
            lease_seconds=args.lease_seconds,
        )
        if args.json:
            print(json.dumps(lease.__dict__ if lease else None, indent=2, sort_keys=True))
        elif lease is None:
            print("no lease granted")
        else:
            print(
                f"leased job {lease.job_id} to {lease.worker_id} "
                f"(lease_id={lease.lease_id}, model={lease.model})"
            )
        return 0

    if args.command == "complete":
        inserted = control_plane.record_usage(
            args.lease_id,
            actual_calls=args.actual_calls,
            actual_usd=args.actual_usd,
            tokens_in=args.tokens_in,
            tokens_out=args.tokens_out,
        )
        print("usage recorded" if inserted else "usage already recorded")
        return 0

    if args.command == "show":
        if args.show_command == "budget":
            return _show_budget(control_plane, json_output=args.json)
        if args.show_command == "needs-human":
            return _show_needs_human(control_plane, json_output=args.json)
        if args.show_command == "flapping":
            return _show_flapping(control_plane, json_output=args.json)
        parser.error(f"Unhandled show command: {args.show_command}")

    if args.command == "budget":
        if args.budget_command == "set":
            control_plane.set_budget(args.model, args.field, _coerce_value(args.value))
            print(f"updated {args.model}.{args.field} -> {args.value}")
            return 0
        return _show_budget(control_plane, json_output=args.json)

    if args.command == "watchdog":
        if args.watchdog_command == "sweep":
            released = sweep_once(control_plane)
            print(f"released {released} expired lease(s)")
            return 0
        watch_forever(control_plane, interval_seconds=args.interval_seconds)
        return 0

    if args.command == "review-worker":
        worker = ReviewWorker(control_plane, worker_id=args.worker_id)
        if args.review_worker_command == "run":
            outcome = worker.run_once()
            if args.json:
                print(
                    json.dumps(
                        {
                            "status": outcome.status,
                            "module_key": outcome.module_key,
                            "lease_id": outcome.lease_id,
                            "details": outcome.details,
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )
            elif outcome.status == "idle":
                print("no review job available")
            else:
                print(f"{outcome.status}: {outcome.module_key}")
            return 0
        worker.loop_forever(sleep_seconds=args.sleep_seconds)
        return 0

    if args.command == "patch-worker":
        worker = PatchWorker(control_plane, worker_id=args.worker_id)
        if args.patch_worker_command == "run":
            outcome = worker.run_once()
            if args.json:
                print(
                    json.dumps(
                        {
                            "status": outcome.status,
                            "module_key": outcome.module_key,
                            "lease_id": outcome.lease_id,
                            "details": outcome.details,
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )
            elif outcome.status == "idle":
                print("no patch job available")
            else:
                print(f"{outcome.status}: {outcome.module_key}")
            return 0
        worker.loop_forever(sleep_seconds=args.sleep_seconds)
        return 0

    if args.command == "preflight":
        result = run_preflight(args.module_path)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        else:
            print(f"Preflight {'PASS' if result.passed else 'FAIL'}: {args.module_path}")
            for finding in result.findings:
                icon = "PASS" if finding.passed else finding.severity
                print(f"[{icon}] {finding.id}: {finding.evidence}")
        return 0 if result.passed else 1

    parser.error(f"Unhandled command: {args.command}")
    return 1


def _show_budget(control_plane: ControlPlane, *, json_output: bool) -> int:
    report = control_plane.budget_report()
    if json_output:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    print(f"Budget report ({report['db_path']})")
    for row in report["rows"]:
        usd_cap = row["weekly_budget_usd_cap"]
        usd_cap_text = "n/a" if usd_cap is None else f"{usd_cap:.2f}"
        print(
            f"{row['model']}: active {row['active_leases']}/{row['max_concurrent']} | "
            f"hourly calls {row['hourly_calls_committed']}/{row['hourly_calls_cap']} | "
            f"weekly calls {row['weekly_calls_committed']}/{row['weekly_calls_cap']} | "
            f"weekly usd {row['weekly_budget_usd_committed']:.2f}/{usd_cap_text}"
        )
    if not report["rows"]:
        print("(no configured or observed models)")
    return 0


def _show_needs_human(control_plane: ControlPlane, *, json_output: bool) -> int:
    rows = []
    for event in control_plane.iter_events("needs_human_intervention"):
        payload = json.loads(event["payload_json"])
        rows.append(
            {
                "module_key": event["module_key"],
                "reason": payload.get("reason"),
                "rewrite_attempts": payload.get("rewrite_attempts"),
                "at": event["at"],
            }
        )
    if json_output:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0
    if not rows:
        print("(no modules need human intervention)")
        return 0
    print("Needs human intervention")
    for row in rows:
        print(
            f"{row['module_key']}: {row['reason']} "
            f"(rewrite_attempts={row['rewrite_attempts']}, at={row['at']})"
        )
    return 0


def _show_flapping(control_plane: ControlPlane, *, json_output: bool) -> int:
    counts: dict[str, int] = {}
    for event in control_plane.iter_events("attempt_started"):
        module_key = str(event["module_key"])
        counts[module_key] = counts.get(module_key, 0) + 1
    rows = [
        {"module_key": module_key, "attempts": attempts}
        for module_key, attempts in sorted(counts.items())
        if attempts > 3
    ]
    if json_output:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0
    if not rows:
        print("(no flapping modules)")
        return 0
    print("Flapping modules")
    for row in rows:
        print(f"{row['module_key']}: {row['attempts']} attempts")
    return 0


def _coerce_value(raw: str) -> Any:
    lowered = raw.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


if __name__ == "__main__":
    raise SystemExit(main())
