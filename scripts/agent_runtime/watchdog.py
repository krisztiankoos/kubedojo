"""Subprocess I/O streaming + hard-timeout kill watchdog for the agent runtime.

Originally implemented as two-layer stall detection, but stall
detection was REMOVED from the kill path on 2026-04-10 after a
string of production incidents. The module now does three things:

1. **stdout/stderr drainers** — background threads drain both pipes
   in parallel. CRITICAL for any subprocess that writes significant
   stderr volume (e.g. Codex CLI writes hundreds of KB of
   reasoning trace + tool calls to stderr), because otherwise the
   16KB pipe buffer fills and blocks the subprocess forever on its
   next write. See ``_stderr_streamer`` for the incident chain.

2. **Liveness-file mtime poller** — updates
   ``WatchdogState.last_activity`` for observability (emitted into
   usage records) but never drives kill decisions. Stall detection
   as a kill condition was unreliable because every CLI version
   bump broke a different mtime signal; see ``should_kill`` for
   the full story.

3. **Hard-timeout kill** — the ONLY condition the watchdog kills on.
   Triggers ``AgentTimeoutError`` when ``now - start_time >
   hard_timeout``. Default hard_timeout is 1h.

Issue: #1184
"""
from __future__ import annotations

import contextlib
import os
import subprocess
import threading
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

# Poll interval for the mtime fallback thread. 5s is a good balance — fast
# enough to extend the stall clock promptly, slow enough that the overhead
# is negligible (at most 5 stat calls per 5s = ~1 per second).
_MTIME_POLL_INTERVAL_S = 5.0

# Maximum number of liveness paths to poll. Adapters returning more than
# this many paths will only have the first _MAX_LIVENESS_PATHS polled.
# Arbitrary but bounded — prevents adapter mistakes from causing poll storms.
_MAX_LIVENESS_PATHS = 5


@dataclass
class WatchdogState:
    """Shared state between the main thread and the background watchdog threads.

    Mutable by design. Access is not lock-protected because we only write
    monotonic floats to ``last_activity`` and booleans to ``stop`` — both
    are atomic on CPython due to the GIL.

    Fields:
        start_time: monotonic timestamp when the subprocess was spawned.
        last_activity: monotonic timestamp of the most recent observed
            activity (stdout line or liveness file mtime bump).
        stop: Set to True by the main thread when the watchdog should exit.
        stdout_lines: Accumulated stdout lines captured by the streamer.
            The runner reads this on normal termination to build the final
            response. (Popen.communicate() would block; we need nonblocking.)
        stderr_lines: Accumulated stderr lines captured by a separate
            streamer thread. Before 2026-04-10 we relied on
            ``proc.stderr.read()`` at completion time, but that ONLY
            works if stderr fits in the OS pipe buffer (16KB on macOS)
            — and Codex CLI writes hundreds of KB of banner + echoed
            prompt + reasoning trace + tool calls to stderr during a
            single long call. When the pipe filled up, Codex's next
            stderr write blocked forever, hanging the entire call at
            0% CPU with STAT=S. Verified empirically via a direct-shell
            experiment that stderr backpressure (not a Codex bug) was
            the cause. Fix: mirror stdout_lines with stderr_lines, and
            add an _stderr_streamer thread that drains stderr in
            parallel with stdout. See #1184.
    """
    start_time: float
    last_activity: float
    stop: bool = False
    stdout_lines: list[str] = field(default_factory=list)
    stderr_lines: list[str] = field(default_factory=list)


def _stdout_streamer(proc: subprocess.Popen, state: WatchdogState) -> None:
    """Background thread: read stdout line-by-line, bump last_activity.

    Exits when the pipe closes (subprocess terminates) or state.stop is True.
    """
    assert proc.stdout is not None  # Popen was configured with stdout=PIPE
    try:
        for line in iter(proc.stdout.readline, ""):
            if state.stop:
                break
            state.stdout_lines.append(line)
            state.last_activity = time.monotonic()
    except (ValueError, OSError):
        # Pipe closed or subprocess killed. Normal shutdown path.
        pass
    finally:
        # Ensure the pipe is drained/closed so the subprocess's exit
        # doesn't hang waiting for us to consume.
        try:
            if proc.stdout is not None:
                proc.stdout.close()
        except OSError:
            pass


def _stderr_streamer(proc: subprocess.Popen, state: WatchdogState) -> None:
    """Background thread: drain stderr line-by-line, bump last_activity.

    Exists specifically to prevent stderr pipe backpressure. If the
    runner pipes both stdout and stderr and only drains stdout, stderr
    accumulates in the OS pipe buffer (16KB on macOS). Once full, the
    subprocess's next stderr write blocks indefinitely, hanging the
    entire call at 0% CPU with STAT=S.

    Codex CLI hit this hard: for tool-heavy reviews it writes hundreds
    of KB of events to stderr, exceeds the buffer, and sits forever
    waiting for a reader that never shows up. Verified empirically
    2026-04-10 via a pair of direct-shell vs runtime experiments:
    direct-shell with stderr → regular file exited cleanly in 2min;
    earlier runtime path with stderr → PIPE hung 10+ minutes on the
    same class of task. See #1184.

    Structure mirrors _stdout_streamer for consistency.
    """
    assert proc.stderr is not None  # Popen was configured with stderr=PIPE
    try:
        for line in iter(proc.stderr.readline, ""):
            if state.stop:
                break
            state.stderr_lines.append(line)
            state.last_activity = time.monotonic()
    except (ValueError, OSError):
        pass
    finally:
        try:
            if proc.stderr is not None:
                proc.stderr.close()
        except OSError:
            pass


def _mtime_poller(paths: Iterable[Path], state: WatchdogState) -> None:
    """Background thread: poll file mtimes, bump last_activity on changes.

    Exits when state.stop is True or after the subprocess terminates.
    """
    # Snapshot initial mtimes so we only react to CHANGES, not mere presence.
    baseline_mtimes: dict[Path, float] = {}
    for p in paths:
        try:
            baseline_mtimes[p] = p.stat().st_mtime
        except OSError:
            baseline_mtimes[p] = 0.0  # file doesn't exist yet; any future mtime counts

    while not state.stop:
        time.sleep(_MTIME_POLL_INTERVAL_S)
        if state.stop:
            break
        for p, baseline in baseline_mtimes.items():
            try:
                current = p.stat().st_mtime
            except OSError:
                continue  # file disappeared or permission denied; skip
            if current > baseline:
                state.last_activity = time.monotonic()
                baseline_mtimes[p] = current


def start_watchdog(
    proc: subprocess.Popen,
    liveness_paths: Iterable[Path],
) -> tuple[WatchdogState, list[threading.Thread]]:
    """Start the stdout streamer + mtime poller threads for a running subprocess.

    Args:
        proc: A Popen object with ``stdout=subprocess.PIPE`` and ``text=True``.
        liveness_paths: Paths to poll for mtime changes (adapter-provided).
            Capped at ``_MAX_LIVENESS_PATHS``.

    Returns:
        (state, threads): The shared state and the list of started threads.
        Callers must call ``stop_watchdog(state, threads)`` to join them
        cleanly after the subprocess terminates.
    """
    now = time.monotonic()
    state = WatchdogState(start_time=now, last_activity=now)

    threads: list[threading.Thread] = []

    # Layer 1a: stdout streamer (always started if stdout is a pipe)
    if proc.stdout is not None:
        t_stdout = threading.Thread(
            target=_stdout_streamer,
            args=(proc, state),
            name=f"watchdog-stdout-{proc.pid}",
            daemon=True,
        )
        t_stdout.start()
        threads.append(t_stdout)

    # Layer 1b: stderr streamer — CRITICAL for any subprocess that
    # writes significant stderr volume (e.g. Codex CLI, which writes
    # banner + echoed prompt + reasoning trace + tool calls all to
    # stderr). Without this the stderr pipe can fill up the 16KB
    # macOS buffer and block the subprocess forever on its next
    # stderr write. Added 2026-04-10 after reproducing a multi-minute
    # hang on tool-heavy Codex tasks. See _stderr_streamer docstring.
    if proc.stderr is not None:
        t_stderr = threading.Thread(
            target=_stderr_streamer,
            args=(proc, state),
            name=f"watchdog-stderr-{proc.pid}",
            daemon=True,
        )
        t_stderr.start()
        threads.append(t_stderr)

    # Layer 2: mtime poller (only if adapter returned any paths)
    capped = list(liveness_paths)[:_MAX_LIVENESS_PATHS]
    if capped:
        t_mtime = threading.Thread(
            target=_mtime_poller,
            args=(capped, state),
            name=f"watchdog-mtime-{proc.pid}",
            daemon=True,
        )
        t_mtime.start()
        threads.append(t_mtime)

    return state, threads


def stop_watchdog(
    state: WatchdogState,
    threads: list[threading.Thread],
    timeout: float = 2.0,
    proc: subprocess.Popen | None = None,
) -> None:
    """Signal the watchdog threads to stop and join them.

    Two mechanisms drive shutdown:

    1. ``state.stop = True`` unblocks the mtime poller (it checks this
       flag between sleeps).

    2. Closing ``proc.stdout`` (if ``proc`` is provided) unblocks the
       stdout streamer. Without this, the streamer sits on
       ``proc.stdout.readline()`` forever because the OS pipe read is
       not interruptible from another thread. Setting state.stop has
       no effect on a blocked read. Closing the pipe from THIS thread
       causes ``readline`` to raise ValueError (closed file) which the
       streamer's try/except catches for a clean exit.

       Pass ``proc`` when you want the streamer to drop IMMEDIATELY
       without waiting for the subprocess to exit on its own. If you
       omit ``proc``, the streamer will still exit when the subprocess
       terminates and its stdout pipe naturally closes — acceptable
       for the normal path where we've already waited for exit.

    Safe to call multiple times. Threads that don't join within
    ``timeout`` are left running as daemons — they'll be cleaned up
    on process exit. Added 2026-04-10 after Gemini review noted the
    streamer was leaking threads on long bridge sessions.
    """
    state.stop = True

    # Close stdout AND stderr to unblock the streamer readlines. Only
    # safe after the subprocess has been killed or has naturally exited
    # — if you close while the subprocess is still writing, the
    # subprocess will get SIGPIPE on its next write. Callers already
    # ensure this ordering: they call proc.kill() + proc.wait() BEFORE
    # stop_watchdog.
    #
    # stderr close is as important as stdout close: the stderr streamer
    # thread (added 2026-04-10) blocks on its own readline the same way
    # the stdout streamer does, and a dangling blocked thread leaks.
    if proc is not None:
        if proc.stdout is not None:
            with contextlib.suppress(OSError, ValueError):
                proc.stdout.close()
        if proc.stderr is not None:
            with contextlib.suppress(OSError, ValueError):
                proc.stderr.close()

    for t in threads:
        t.join(timeout=timeout)


def should_kill(state: WatchdogState, stall_timeout: int, hard_timeout: int) -> str | None:
    """Check if the subprocess should be killed. Returns the kill reason or None.

    Returns:
        None if the process should continue running.
        "hard_timeout" if total runtime exceeded hard_timeout.

    ``stall_timeout`` is accepted for backward compatibility with callers but
    is NOT used as a kill condition. Deleting stall detection from the kill
    path on 2026-04-10 after a string of production incidents proved it
    unreliable:

    1. Gemini block-buffers stdout when not a TTY; stdout streamer goes
       silent for 5+ min during reasoning bursts — looks identical to a
       hang but is actually successful work.
    2. Codex 0.118 moved its primary log from ``logs_1.sqlite`` to
       ``state_5.sqlite`` to ``sessions/YYYY/MM/DD/rollout-*.jsonl``.
       Each CLI version bump breaks a different mtime signal.
    3. Directory mtime on ``sessions/YYYY/MM/DD/`` bumps only on child
       creation, not on child content writes — so the signal fires ONCE
       at startup and goes silent during the actual run even though the
       child rollout file is actively growing.
    4. Every CLI (Claude, Codex, Gemini) stores live state in a different
       place with a different convention, and tracking each one
       individually is whack-a-mole with no ground truth.

    The mtime poller still runs for observability (via the WatchdogState
    last_activity field, which the runner reads for usage records), but
    the kill decision now relies solely on hard_timeout as the safety net.
    A legitimately long-running task will be allowed to complete; a truly
    runaway process still gets killed by hard_timeout.

    See #1184 for the full incident chain.
    """
    _ = stall_timeout  # accepted but unused; kept in signature for compat.
    now = time.monotonic()
    if (now - state.start_time) > hard_timeout:
        return "hard_timeout"
    return None


# Binary file extensions that MUST NOT be tailed into a UTF-8
# stderr_excerpt on failure. SQLite DBs, shelve DBs, and packed
# state files produce garbage Unicode-replacement chars when
# decoded. Adapters pass state_5.sqlite / logs_1.sqlite as
# liveness paths for mtime-polling purposes, and those can be
# the newest path at failure time.
#
# WAL mode note: SQLite in WAL mode writes to sibling files with
# '-wal' and '-shm' suffixes. These often have the FRESHEST mtime
# during active writes (newer than the main .sqlite file), so
# filtering only the main .sqlite extension isn't enough.
# Gemini 2026-04-10 review finding.
_BINARY_LIVENESS_EXTS = frozenset({
    ".sqlite", ".sqlite3", ".sqlite-wal", ".sqlite-shm",
    ".sqlite-journal", ".sqlite3-wal", ".sqlite3-shm",
    ".sqlite3-journal",
    ".db", ".db-wal", ".db-shm", ".db-journal",
    ".wal", ".shm",
    ".dbm", ".pack", ".idx",
    ".bin", ".pyc", ".pyo",
})


def _is_tailable_text(path: Path) -> bool:
    """Return True if `path` is a regular file suitable for UTF-8 tailing.

    Excludes:
    * Directories (they're passed as liveness paths for Codex's
      sessions/YYYY/MM/DD/ dir, but you can't tail a directory).
    * Known-binary extensions — SQLite, packed indexes, etc.
    * Symlinks to nonexistent targets.
    """
    try:
        if not path.is_file():  # excludes directories and nonexistent
            return False
    except OSError:
        return False
    return path.suffix.lower() not in _BINARY_LIVENESS_EXTS


def tail_liveness_file_for_debug(
    paths: Iterable[Path],
    max_bytes: int = 4096,
) -> str:
    """Tail the newest text-format liveness file for error diagnostics.

    Called by the runner on failure to capture the agent's "last known
    thoughts" from its session file, since stderr may be empty or useless.
    Returns the concatenated tails or an empty string if nothing found.

    Filters out directories and known-binary files (SQLite, etc.) before
    picking the newest candidate — otherwise we'd write replacement-char
    garbage into stderr_excerpt when Codex's state_5.sqlite happens to be
    the newest liveness path at failure time.

    Safe against all filesystem errors; returns "" on any problem.
    """
    candidates: list[tuple[float, Path]] = []
    for p in paths:
        if not _is_tailable_text(p):
            continue
        try:
            mtime = p.stat().st_mtime
            candidates.append((mtime, p))
        except OSError:
            continue

    if not candidates:
        return ""

    # Pick the most recently modified file
    candidates.sort(reverse=True)
    _, newest = candidates[0]

    try:
        size = newest.stat().st_size
        if size == 0:
            return ""
        with open(newest, "rb") as f:
            if size > max_bytes:
                f.seek(-max_bytes, os.SEEK_END)
            tail_bytes = f.read()
        return tail_bytes.decode("utf-8", errors="replace")
    except OSError:
        return ""
