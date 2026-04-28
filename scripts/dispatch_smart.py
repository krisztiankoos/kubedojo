"""Smart-routing headless-Claude dispatcher.

Single CLI for dispatching work to a headless Claude that picks an
appropriate model based on the task class — instead of always burning
opus from the orchestrator session.

Why: the orchestrator runs on claude-opus-4-7. Doing search/scan or
small edits inline burns weekly cap on opus when haiku/sonnet would do
fine. This wrapper lets the orchestrator say "do this kind of work,
pick the right Claude" without having to manually choose model + mode +
worktree every time.

Usage:
    # Cheap search (haiku, read-only, no worktree)
    .venv/bin/python scripts/dispatch_smart.py search \
        "Find every place that imports agent_runtime.runner.invoke and
         note the mode argument used in each."

    # Mid-tier edit (sonnet, workspace-write, in a worktree)
    .venv/bin/python scripts/dispatch_smart.py edit \
        --worktree .worktrees/claude-fix-issue-500 \
        --new-branch claude/fix-issue-500 \
        "Fix the off-by-one in scripts/foo.py:142, add a regression
         test, run pytest, commit with message 'fix: ...'."

    # Heavy architecture work (opus, workspace-write)
    .venv/bin/python scripts/dispatch_smart.py architect \
        --worktree .worktrees/claude-redesign-pipeline \
        --new-branch claude/redesign-pipeline \
        "Redesign the quality pipeline so phase ordering is data-driven."

Task classes — model + default mode mapping:

    search    → claude-haiku-4-5-20251001  read-only       (cheap scan)
    edit      → claude-sonnet-4-6          workspace-write (small change)
    draft     → claude-sonnet-4-6          workspace-write (prose/content)
    architect → claude-opus-4-7            workspace-write (deep reasoning)

Each dispatch is recorded to ``logs/smart_dispatch.jsonl`` for usage
auditing. Reuse with --dry-run to print the chosen plan without firing.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO = Path("/Users/krisztiankoos/projects/kubedojo")
LOG_PATH = REPO / "logs" / "smart_dispatch.jsonl"


@dataclass(frozen=True)
class TaskClassConfig:
    model: str
    default_mode: str  # "read-only" | "workspace-write" | "danger"
    default_timeout_s: int
    description: str


TASK_CLASSES: dict[str, TaskClassConfig] = {
    "search": TaskClassConfig(
        model="claude-haiku-4-5-20251001",
        default_mode="read-only",
        default_timeout_s=600,
        description="cheap codebase scans, file lookups, factual Q&A",
    ),
    "edit": TaskClassConfig(
        model="claude-sonnet-4-6",
        default_mode="workspace-write",
        default_timeout_s=1800,
        description="small/medium code edits, single-file fixes",
    ),
    "draft": TaskClassConfig(
        model="claude-sonnet-4-6",
        default_mode="workspace-write",
        default_timeout_s=3600,
        description="prose/content drafting and expansion",
    ),
    "architect": TaskClassConfig(
        model="claude-opus-4-7",
        default_mode="workspace-write",
        default_timeout_s=3600,
        description="deep reasoning, multi-file refactors, design",
    ),
}


def make_task_id(task_class: str) -> str:
    return f"smart-{task_class}-{int(time.time())}"


def ensure_worktree(worktree: Path, new_branch: str | None,
                    base: str = "main") -> None:
    """Create a worktree if it doesn't exist; reuse if it does.

    Caller is responsible for picking a sensible path under .worktrees/.
    """
    if worktree.exists():
        return
    if new_branch is None:
        raise SystemExit(
            f"[smart] worktree {worktree} does not exist and no "
            f"--new-branch was given; refusing to invent a branch name"
        )
    cmd = ["git", "worktree", "add", "-b", new_branch, str(worktree), base]
    subprocess.run(cmd, cwd=REPO, check=True)


def append_log(entry: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as fp:
        fp.write(json.dumps(entry) + "\n")


def fire(*, task_class: str, prompt: str, mode: str, model: str,
         worktree: Path | None, task_id: str, timeout_s: int) -> int:
    sys.path.insert(0, str(REPO / "scripts"))
    from agent_runtime.runner import invoke

    print(f"[smart] task_class={task_class} model={model} mode={mode} "
          f"timeout={timeout_s}s")
    if worktree:
        print(f"[smart] cwd={worktree}")
    print(f"[smart] task_id={task_id}")

    started = time.time()
    try:
        result = invoke(
            "claude",
            prompt,
            mode=mode,
            cwd=worktree,
            model=model,
            task_id=task_id,
            entrypoint="delegate",
            hard_timeout=timeout_s,
        )
        ok = bool(result.ok)
        response = result.response or ""
        session_id = result.session_id
        stderr_excerpt = result.stderr_excerpt or ""
    except Exception as exc:  # surface the failure but still log it
        ok = False
        response = ""
        session_id = None
        stderr_excerpt = f"{type(exc).__name__}: {exc}"

    elapsed = time.time() - started
    append_log({
        "ts": int(started),
        "elapsed_s": round(elapsed, 1),
        "task_id": task_id,
        "task_class": task_class,
        "model": model,
        "mode": mode,
        "cwd": str(worktree) if worktree else None,
        "ok": ok,
        "session_id": session_id,
        "response_chars": len(response),
        "stderr_excerpt": stderr_excerpt[:400] if stderr_excerpt else None,
    })

    print("=" * 70)
    print(f"OK: {ok}  |  elapsed: {elapsed:.0f}s  |  "
          f"resp_chars: {len(response)}")
    print("=" * 70)
    if response:
        print(response)
    if stderr_excerpt:
        print("---- stderr ----")
        print(stderr_excerpt[:400])
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(
        description="Dispatch a headless Claude with a task-class-based "
                    "model choice (haiku/sonnet/opus).",
    )
    p.add_argument("task_class", choices=sorted(TASK_CLASSES),
                   help="Picks the model + default mode.")
    p.add_argument("prompt", nargs="?", default=None,
                   help="Prompt text. Pass `-` to read from stdin.")
    p.add_argument("--worktree",
                   help="Path to a git worktree under .worktrees/. "
                        "Required for write modes.")
    p.add_argument("--new-branch",
                   help="If --worktree doesn't exist, create it on this "
                        "branch off main.")
    p.add_argument("--mode",
                   choices=["read-only", "workspace-write", "danger"],
                   help="Override task-class default mode.")
    p.add_argument("--model",
                   help="Override task-class default model "
                        "(rarely needed — let the class pick).")
    p.add_argument("--timeout", type=int,
                   help="Override task-class default hard timeout (s).")
    p.add_argument("--task-id",
                   help="Override auto-generated task_id.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print the resolved plan and exit without firing.")
    args = p.parse_args()

    cfg = TASK_CLASSES[args.task_class]
    model = args.model or cfg.model
    mode = args.mode or cfg.default_mode
    timeout_s = args.timeout or cfg.default_timeout_s
    task_id = args.task_id or make_task_id(args.task_class)

    if args.prompt is None:
        sys.stderr.write("[smart] no prompt — pass as arg or `-` for stdin\n")
        return 2
    prompt = sys.stdin.read() if args.prompt == "-" else args.prompt
    if not prompt.strip():
        sys.stderr.write("[smart] prompt is empty\n")
        return 2

    worktree: Path | None = None
    if args.worktree:
        worktree = Path(args.worktree)
        if not worktree.is_absolute():
            worktree = REPO / worktree
        if mode != "read-only":
            ensure_worktree(worktree, args.new_branch)
    elif mode != "read-only":
        sys.stderr.write(
            f"[smart] mode={mode} requires --worktree to avoid trampling "
            "the main checkout\n"
        )
        return 2

    if args.dry_run:
        print(f"[dry-run] task_class={args.task_class} model={model} "
              f"mode={mode} timeout={timeout_s}s")
        print(f"[dry-run] worktree={worktree or '(none — read-only)'}")
        print(f"[dry-run] task_id={task_id}")
        print(f"[dry-run] prompt_chars={len(prompt)}")
        return 0

    return fire(
        task_class=args.task_class,
        prompt=prompt,
        mode=mode,
        model=model,
        worktree=worktree,
        task_id=task_id,
        timeout_s=timeout_s,
    )


if __name__ == "__main__":
    raise SystemExit(main())
