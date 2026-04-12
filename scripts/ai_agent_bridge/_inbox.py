"""Thread-coalesced inbox draining for the channel bridge.

Why this exists: Phase C.1 added leased deliveries, but draining them
one row at a time would fragment thread context, duplicate replies, and
throw away Claude's bridge-session cache warmth. Phase C.2 instead
claims one whole thread-group per invocation so the worker can emit one
reply, update one delivery cohort, and reuse the same Claude session for
that thread on the next wake. See #1192.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

try:
    from agent_runtime.errors import (
        AgentStalledError,
        AgentTimeoutError,
        AgentUnavailableError,
        RateLimitedError,
    )
    from agent_runtime.runner import invoke as runtime_invoke

    _HAS_RUNTIME = True
except ImportError:
    class RateLimitedError(Exception):
        """Fallback used when agent_runtime is not importable."""


    class AgentStalledError(Exception):
        """Fallback used when agent_runtime is not importable."""


    class AgentTimeoutError(Exception):
        """Fallback used when agent_runtime is not importable."""


    class AgentUnavailableError(Exception):
        """Fallback used when agent_runtime is not importable."""


    runtime_invoke = None
    _HAS_RUNTIME = False

from . import _channels
from ._config import CLAUDE_CMD, REPO_ROOT
from ._db import get_db

_DEFAULT_HARD_TIMEOUT_SECONDS = 900
_DEFAULT_STALL_TIMEOUT_SECONDS = 600
_DEFAULT_GLOBAL_RETRY_SECONDS = 120
_SESSION_COLUMNS = {
    "claude": "claude_session_id",
    "gemini": "gemini_session_id",
    "codex": "codex_session_id",
}


@dataclass(frozen=True)
class InboxRunSummary:
    """Compact counters so callers can verify drain behavior in tests.

    The worker is intentionally retry-heavy and non-interactive. A small,
    immutable summary makes it obvious whether a wake delivered work,
    terminal-failed a thread, or aborted early because the provider was
    unavailable and the lease was released for a later retry.
    """

    agent: str
    threads_processed: int = 0
    deliveries_claimed: int = 0
    deliveries_delivered: int = 0
    deliveries_failed: int = 0
    deliveries_released: int = 0
    replies_posted: int = 0
    aborted: bool = False
    abort_reason: str | None = None


@dataclass(frozen=True)
class _ClaimedDelivery:
    delivery_id: str
    message_id: str
    thread_id: str
    channel: str
    to_agent: str
    to_model: str | None
    from_agent: str
    body: str
    round_index: int
    created_at: str


@dataclass(frozen=True)
class _ClaimedThread:
    channel: str
    thread_id: str
    deliveries: tuple[_ClaimedDelivery, ...]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _iso_after(value: str, *, seconds: int) -> str:
    return (datetime.fromisoformat(value) + timedelta(seconds=seconds)).isoformat()


def _validate_agent(agent: str) -> None:
    if agent not in _channels.VALID_AGENTS:
        raise ValueError(
            f"Unknown agent '{agent}'. Expected one of {_channels.VALID_AGENTS}."
        )


def _thread_session_key(channel: str, thread_id: str) -> str:
    return f"bridge:{channel}:{thread_id}"


def _get_session_id(task_id: str, agent: str) -> str | None:
    column = _SESSION_COLUMNS[agent]
    conn = get_db()
    try:
        row = conn.execute(
            f"SELECT {column} FROM sessions WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        return str(row[column]) if row and row[column] else None
    finally:
        conn.close()


def _set_session_id(task_id: str, agent: str, session_id: str) -> None:
    column = _SESSION_COLUMNS[agent]
    now = _now_iso()
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute(
            "SELECT task_id FROM sessions WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if existing:
            conn.execute(
                f"UPDATE sessions SET {column} = ?, updated_at = ? WHERE task_id = ?",
                (session_id, now, task_id),
            )
        else:
            conn.execute(
                f"INSERT INTO sessions (task_id, {column}, created_at, updated_at) "
                f"VALUES (?, ?, ?, ?)",
                (task_id, session_id, now, now),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _claim_next_thread(
    agent: str,
    *,
    max_attempts: int,
    lease_seconds: int,
    delivery_budget: int | None,
    now: str,
) -> tuple[_ClaimedThread | None, bool]:
    """Claim one whole thread so #1192 never invokes per delivery row."""

    lease_until = _iso_after(now, seconds=lease_seconds)
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        candidate = conn.execute(
            """
            SELECT cm.thread_id, cm.channel
            FROM deliveries d
            JOIN channel_messages cm ON cm.message_id = d.message_id
            WHERE d.to_agent = ?
              AND d.attempt_count < ?
              AND (d.retry_after IS NULL OR d.retry_after <= ?)
              AND (
                    d.status = 'pending'
                    OR (d.status = 'processing' AND d.lease_until <= ?)
              )
              AND NOT EXISTS (
                    SELECT 1
                    FROM deliveries d2
                    JOIN channel_messages cm2 ON cm2.message_id = d2.message_id
                    WHERE d2.to_agent = d.to_agent
                      AND cm2.thread_id = cm.thread_id
                      AND d2.status = 'processing'
                      AND d2.lease_until > ?
              )
            ORDER BY cm.created_at ASC, d.delivery_id ASC
            LIMIT 1
            """,
            (agent, max_attempts, now, now, now),
        ).fetchone()
        if not candidate:
            conn.commit()
            return None, False

        thread_id = str(candidate["thread_id"])
        channel = str(candidate["channel"])
        count_row = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM deliveries d
            JOIN channel_messages cm ON cm.message_id = d.message_id
            WHERE d.to_agent = ?
              AND cm.thread_id = ?
              AND d.attempt_count < ?
              AND (d.retry_after IS NULL OR d.retry_after <= ?)
              AND (
                    d.status = 'pending'
                    OR (d.status = 'processing' AND d.lease_until <= ?)
              )
            """,
            (agent, thread_id, max_attempts, now, now),
        ).fetchone()
        claim_count = int(count_row["count"]) if count_row else 0
        if claim_count == 0:
            conn.commit()
            return None, False
        if delivery_budget is not None and claim_count > delivery_budget:
            conn.commit()
            return None, True

        conn.execute(
            """
            UPDATE deliveries
            SET status = 'processing',
                lease_until = ?,
                attempt_count = attempt_count + 1
            WHERE delivery_id IN (
                SELECT d.delivery_id
                FROM deliveries d
                JOIN channel_messages cm ON cm.message_id = d.message_id
                WHERE d.to_agent = ?
                  AND cm.thread_id = ?
                  AND d.attempt_count < ?
                  AND (d.retry_after IS NULL OR d.retry_after <= ?)
                  AND (
                        d.status = 'pending'
                        OR (d.status = 'processing' AND d.lease_until <= ?)
                  )
            )
            """,
            (lease_until, agent, thread_id, max_attempts, now, now),
        )

        rows = conn.execute(
            """
            SELECT d.delivery_id, d.message_id, d.to_agent, d.to_model,
                   cm.thread_id, cm.channel, cm.from_agent, cm.body,
                   cm.round_index, cm.created_at
            FROM deliveries d
            JOIN channel_messages cm ON cm.message_id = d.message_id
            WHERE d.to_agent = ?
              AND cm.thread_id = ?
              AND d.status = 'processing'
              AND d.lease_until = ?
            ORDER BY cm.created_at ASC, d.delivery_id ASC
            """,
            (agent, thread_id, lease_until),
        ).fetchall()
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    deliveries = tuple(
        _ClaimedDelivery(
            delivery_id=str(row["delivery_id"]),
            message_id=str(row["message_id"]),
            thread_id=str(row["thread_id"]),
            channel=str(row["channel"]),
            to_agent=str(row["to_agent"]),
            to_model=str(row["to_model"]) if row["to_model"] else None,
            from_agent=str(row["from_agent"]),
            body=str(row["body"]),
            round_index=int(row["round_index"]),
            created_at=str(row["created_at"]),
        )
        for row in rows
    )
    if not deliveries:
        return None, False
    return _ClaimedThread(channel=channel, thread_id=thread_id, deliveries=deliveries), False


def _update_claimed_status(
    claimed: _ClaimedThread,
    *,
    status: str,
    error_text: str | None = None,
    error_kind: str | None = None,
    retry_after: str | None = None,
    delivered_at: str | None = None,
) -> None:
    delivery_ids = [delivery.delivery_id for delivery in claimed.deliveries]
    placeholders = ", ".join("?" for _ in delivery_ids)
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        if status == "delivered":
            conn.execute(
                f"""
                UPDATE deliveries
                SET status = 'delivered',
                    delivered_at = ?,
                    error = NULL,
                    lease_until = NULL,
                    retry_after = NULL,
                    last_error_kind = NULL
                WHERE delivery_id IN ({placeholders})
                """,
                (delivered_at or _now_iso(), *delivery_ids),
            )
        elif status == "failed":
            conn.execute(
                f"""
                UPDATE deliveries
                SET status = 'failed',
                    error = ?,
                    lease_until = NULL,
                    retry_after = NULL,
                    last_error_kind = ?
                WHERE delivery_id IN ({placeholders})
                """,
                (error_text or "", error_kind, *delivery_ids),
            )
        else:
            conn.execute(
                f"""
                UPDATE deliveries
                SET status = 'pending',
                    error = ?,
                    lease_until = NULL,
                    retry_after = ?,
                    last_error_kind = ?
                WHERE delivery_id IN ({placeholders})
                """,
                (error_text or "", retry_after, error_kind, *delivery_ids),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _render_messages(messages: list[dict[str, object]]) -> str:
    return "\n".join(
        (
            f"[{str(message['created_at'])[:19]}] "
            f"{message['from_agent']} (round {message['round_index']}): "
            f"{message['body']}"
        )
        for message in messages
    )


def _build_thread_prompt(
    agent: str,
    claimed: _ClaimedThread,
    *,
    has_session: bool,
) -> str:
    thread_messages = _channels.read(claimed.channel, thread_id=claimed.thread_id)
    if not thread_messages:
        raise ValueError(
            f"thread '{claimed.thread_id}' in channel '{claimed.channel}' has no messages"
        )

    claimed_ids = {delivery.message_id for delivery in claimed.deliveries}
    unseen = [message for message in thread_messages if message["message_id"] in claimed_ids]
    if not unseen:
        raise ValueError(
            f"claimed deliveries for thread '{claimed.thread_id}' did not map to messages"
        )

    latest_message = unseen[-1]
    if agent == "claude" and has_session:
        sections = [
            f"Continue the existing bridge session for channel #{claimed.channel}.",
            "Respond with one plain-text reply as the target agent.",
            "Address the latest unseen message directly.",
            "--- unseen messages ---",
            _render_messages(unseen),
        ]
        return "\n\n".join(section for section in sections if section.strip())

    context = _channels.load_channel_context(claimed.channel)["body"].strip()
    root = thread_messages[0]
    # NIT from Gemini c2-review r1: when a thread JUST started, the root
    # message is also in unseen[]. Don't render it twice in the cold prompt.
    root_in_unseen = root["message_id"] in claimed_ids
    prior_messages = [
        message
        for message in thread_messages[1:]
        if message["message_id"] not in claimed_ids
    ]
    sections = [
        context,
        f"You are {agent} replying on the #{claimed.channel} channel bridge.",
        # Skip the root section entirely if root is also in unseen — the
        # unseen block below will render it once and only once.
        ("--- root question ---\n" + _render_messages([root])) if not root_in_unseen else "",
        (
            "--- thread so far ---\n" + _render_messages(prior_messages)
            if prior_messages
            else ""
        ),
        "--- unseen messages to answer now ---",
        _render_messages(unseen),
        (
            "Reply once, in plain text, with the message you want posted as a "
            f"channel reply to {latest_message['message_id']}."
        ),
    ]
    return "\n\n".join(section for section in sections if section.strip())


def _resolve_model(claimed: _ClaimedThread) -> str | None:
    models = {delivery.to_model for delivery in claimed.deliveries if delivery.to_model}
    if len(models) > 1:
        raise ValueError(
            f"thread '{claimed.thread_id}' has conflicting to_model values: {sorted(models)}"
        )
    return next(iter(models), None)


def _invoke_thread(agent: str, claimed: _ClaimedThread) -> Any:
    task_id = _thread_session_key(claimed.channel, claimed.thread_id)
    existing_session = _get_session_id(task_id, agent) if agent == "claude" else None
    has_session = existing_session is not None
    prompt = _build_thread_prompt(agent, claimed, has_session=has_session)
    session_id = existing_session
    session_to_store: str | None = None
    tool_config: dict[str, object] | None = None

    if agent == "claude":
        tool_config = {"cmd_prefix": CLAUDE_CMD, "is_new_session": False}
        if session_id is None:
            session_id = str(uuid.uuid4())
            session_to_store = session_id
            tool_config["is_new_session"] = True

    result = runtime_invoke(
        agent,
        prompt,
        mode="read-only",
        cwd=REPO_ROOT,
        model=_resolve_model(claimed),
        task_id=task_id,
        session_id=session_id if agent == "claude" else None,
        tool_config=tool_config,
        entrypoint="bridge",
        hard_timeout=_DEFAULT_HARD_TIMEOUT_SECONDS,
        stall_timeout=_DEFAULT_STALL_TIMEOUT_SECONDS,
    )

    if agent == "claude" and result.ok:
        persisted_session = result.session_id or session_to_store or existing_session
        if persisted_session:
            _set_session_id(task_id, agent, persisted_session)

    return result


def run_inbox(
    agent: str,
    *,
    max_messages: int | None = None,
    until_idle: bool = True,
    stop_after_seconds: int | None = None,
) -> InboxRunSummary:
    """Drain one agent inbox without splitting a live thread across calls.

    The worker stops on global provider failures because those are not
    specific to one delivery row; releasing the current lease with a
    retry_after preserves the thread cohort for the next wake instead of
    falsely terminal-failing work that would likely succeed once the
    provider recovers. See #1192.
    """
    if not _HAS_RUNTIME or runtime_invoke is None:
        raise RuntimeError(
            "agent_runtime is required for inbox draining. "
            "Install it or add scripts/ to PYTHONPATH."
        )

    _validate_agent(agent)
    if max_messages is not None and max_messages <= 0:
        raise ValueError("max_messages must be > 0 when provided")
    if stop_after_seconds is not None and stop_after_seconds <= 0:
        raise ValueError("stop_after_seconds must be > 0 when provided")

    claimed_total = 0
    delivered_total = 0
    failed_total = 0
    released_total = 0
    replies_total = 0
    threads_total = 0
    abort_reason: str | None = None
    start_time = time.monotonic()

    while True:
        if (
            stop_after_seconds is not None
            and threads_total > 0
            and time.monotonic() - start_time >= stop_after_seconds
        ):
            break

        remaining_budget = (
            None if max_messages is None else max_messages - claimed_total
        )
        if remaining_budget is not None and remaining_budget <= 0:
            break

        # Soft-cap: never enforce delivery_budget on the FIRST claim of
        # a run. Otherwise an oldest-thread larger than max_messages
        # would permanently deadlock the queue — every wake would bail
        # without processing anything. Subsequent claims still enforce
        # the budget so a single run can't blow past max_messages by
        # multiple threads. (Gemini issue-1192-c2-review r1 BLOCKER.)
        hard_budget = remaining_budget if claimed_total > 0 else None

        claimed, _blocked_by_budget = _claim_next_thread(
            agent,
            max_attempts=_channels.DEFAULT_MAX_DELIVERY_ATTEMPTS,
            lease_seconds=_channels.DEFAULT_DELIVERY_LEASE_SECONDS,
            delivery_budget=hard_budget,
            now=_now_iso(),
        )
        if claimed is None:
            break

        claimed_total += len(claimed.deliveries)
        try:
            result = _invoke_thread(agent, claimed)
        # Note: transient global failures (rate limit, timeout, unavailable)
        # release the lease back to pending with a retry_after, but DO NOT
        # decrement attempt_count. The agent WAS attempted (it just hit a
        # provider-side fault), so the attempt is real. Eventually a
        # genuinely-down provider will exhaust DEFAULT_MAX_DELIVERY_ATTEMPTS
        # and the deliveries will reach terminal `failed` — that's the
        # right behavior, not infinite retry.
        # (Gemini issue-1192-c2-review r1 BLOCKER caught the original
        # decrement_attempts=True path which net-zero'd attempts.)
        except RateLimitedError as exc:
            _update_claimed_status(
                claimed,
                status="pending",
                error_text=str(exc),
                error_kind="rate_limited",
                retry_after=_iso_after(
                    _now_iso(),
                    seconds=_channels.DEFAULT_RATE_LIMIT_RETRY_SECONDS,
                ),
            )
            released_total += len(claimed.deliveries)
            abort_reason = str(exc)
            break
        except (AgentStalledError, AgentTimeoutError) as exc:
            _update_claimed_status(
                claimed,
                status="pending",
                error_text=str(exc),
                error_kind="timeout",
                retry_after=_iso_after(
                    _now_iso(),
                    seconds=_DEFAULT_GLOBAL_RETRY_SECONDS,
                ),
            )
            released_total += len(claimed.deliveries)
            abort_reason = str(exc)
            break
        except AgentUnavailableError as exc:
            _update_claimed_status(
                claimed,
                status="pending",
                error_text=str(exc),
                error_kind="unavailable",
                retry_after=_iso_after(
                    _now_iso(),
                    seconds=_DEFAULT_GLOBAL_RETRY_SECONDS,
                ),
            )
            released_total += len(claimed.deliveries)
            abort_reason = str(exc)
            break
        except Exception as exc:
            _update_claimed_status(
                claimed,
                status="failed",
                error_text=f"{type(exc).__name__}: {exc}",
                error_kind="tool_error",
            )
            failed_total += len(claimed.deliveries)
            threads_total += 1
            if not until_idle:
                break
            continue

        reply_body = result.response.strip()
        if not result.ok or not reply_body:
            _update_claimed_status(
                claimed,
                status="failed",
                error_text=result.stderr_excerpt or "agent returned no reply",
                error_kind="parse_error",
            )
            failed_total += len(claimed.deliveries)
            threads_total += 1
            if not until_idle:
                break
            continue

        try:
            # Reply linkage lives in channel_messages.parent_id, not the
            # deliveries table — we don't need the returned message_id.
            _channels.post(
                claimed.channel,
                agent,
                reply_body,
                parent_id=claimed.deliveries[-1].message_id,
                from_model=result.model,
                auto_snapshot=False,
            )
        except Exception as exc:
            _update_claimed_status(
                claimed,
                status="failed",
                error_text=f"reply post failed: {type(exc).__name__}: {exc}",
                error_kind="tool_error",
            )
            failed_total += len(claimed.deliveries)
            threads_total += 1
            if not until_idle:
                break
            continue

        # Reply linkage lives in channel_messages.parent_id, not in the
        # deliveries table — no separate linkage step needed here.
        _update_claimed_status(
            claimed,
            status="delivered",
            delivered_at=_now_iso(),
        )
        delivered_total += len(claimed.deliveries)
        replies_total += 1
        threads_total += 1

        if not until_idle:
            break

    return InboxRunSummary(
        agent=agent,
        threads_processed=threads_total,
        deliveries_claimed=claimed_total,
        deliveries_delivered=delivered_total,
        deliveries_failed=failed_total,
        deliveries_released=released_total,
        replies_posted=replies_total,
        aborted=abort_reason is not None,
        abort_reason=abort_reason,
    )
