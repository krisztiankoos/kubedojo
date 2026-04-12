"""Codex interaction: ask_codex and process_for_codex.

Phase 4 of #1184 migrated the bridge subprocess path onto
scripts.agent_runtime. Codex bridge calls now always start fresh,
consistent with the runtime's resume_policy="never" for Codex.
"""

import json
import os

from agent_runtime import runner as agent_runner
from agent_runtime.errors import (
    AgentStalledError,
    AgentTimeoutError,
    AgentUnavailableError,
    RateLimitedError,
)

from ._config import REPO_ROOT
from ._db import get_db, set_session
from ._messaging import acknowledge, send_message
from ._prompts import build_codex_prompt

_CODEX_MODES = {"safe", "workspace-write", "full-auto", "danger"}


def _codex_bridge_mode() -> str:
    """Resolve Codex sandbox mode for ai_agent_bridge calls."""
    requested = (
        os.environ.get("CODEX_BRIDGE_MODE")
        or os.environ.get("CODEX_CLI_MODE")
        or "safe"
    ).strip().lower()
    if requested in _CODEX_MODES:
        return "workspace-write" if requested == "full-auto" else requested
    print(f"⚠️  Invalid CODEX_BRIDGE_MODE='{requested}' — falling back to safe")
    return "safe"


def _codex_bridge_runtime_mode() -> str:
    """Translate CODEX_BRIDGE_MODE env var to runtime vocabulary.

    Runtime uses {read-only, workspace-write, danger}.
    Bridge legacy uses {safe, workspace-write, full-auto, danger}.
    """
    legacy = _codex_bridge_mode()
    if legacy == "danger":
        return "danger"
    if legacy == "workspace-write":
        return "workspace-write"
    return "read-only"  # "safe" → "read-only"


def ask_codex(content: str, task_id: str | None = None, msg_type: str = "query",
              data: str | None = None, new_session: bool = False,
              from_llm: str = "gemini", from_model: str | None = None,
              to_model: str | None = None):
    """Send message to Codex AND invoke Codex to process it."""
    msg_id = send_message(content, task_id, msg_type, data, from_llm=from_llm,
                          to_llm="codex", from_model=from_model, to_model=to_model)
    print(f"\n🚀 Invoking Codex to process message #{msg_id}...")
    process_for_codex(msg_id, new_session)
    return msg_id


def has_codex_headroom(model: str | None = None) -> tuple[bool, str]:
    """Return whether Codex has quota headroom for a new bridge call."""
    from agent_runtime.usage import has_headroom

    effective_model = model or "gpt-5.4"
    return has_headroom("codex", effective_model)


def process_for_codex(message_id: int, new_session: bool = False, no_timeout: bool = False):
    """Read message addressed to Codex, invoke via agent_runtime, send response.

    Phase 4: routes through scripts.agent_runtime.runner.invoke(). Resume
    is dropped (Codex resume_policy="never" in the registry); new_session
    parameter is accepted for backward compatibility but now always True
    in effect.
    """
    msg = _fetch_codex_message(message_id)
    if not msg:
        return

    _ = new_session  # No-op: Codex always starts fresh (resume_policy="never")
    timeout_val = 1800 if no_timeout else 900  # runner has its own hard_timeout
    model = _extract_target_model(msg)
    has_room, reason = has_codex_headroom(model)
    if not has_room:
        _handle_codex_rate_limited(msg, message_id, reason)
        return

    prompt = build_codex_prompt(msg)

    print(f"📨 Message #{msg['id']}")
    print(f"   From: {msg['from']} → To: {msg['to']}")
    print(f"   Type: {msg['type']}")
    print(f"   Task: {msg['task_id'] or 'N/A'}")
    print("   Session: NEW (Codex runtime always fresh)")

    try:
        result = agent_runner.invoke(
            "codex",
            prompt,
            mode=_codex_bridge_runtime_mode(),
            cwd=REPO_ROOT,
            model=model,
            task_id=msg["task_id"],
            session_id=None,  # Codex resume_policy="never"
            tool_config=None,
            entrypoint="bridge",
            hard_timeout=timeout_val,
            # 600s matches dispatch.py — with the mtime-poller liveness
            # fallback in place (state_5.sqlite, sessions/YYYY/MM/DD/,
            # history.jsonl, output file), the stall ceiling only applies
            # to genuinely dead processes. Raised from 180s 2026-04-10
            # after a real delegated task stalled at 181s on a
            # successfully-running invocation. (#1184)
            stall_timeout=min(600, timeout_val),
        )
    except RateLimitedError as exc:
        _handle_codex_rate_limited(msg, message_id, f"Rate limited: {exc}")
        return
    except AgentStalledError as exc:
        _handle_codex_error(msg, message_id, f"Codex stalled: {exc}")
        return
    except AgentTimeoutError as exc:
        _handle_codex_error(msg, message_id, f"Codex hard timeout: {exc}")
        return
    except AgentUnavailableError as exc:
        _handle_codex_error(msg, message_id, f"Codex unavailable: {exc}")
        return

    if not result.ok:
        _handle_codex_error(
            msg,
            message_id,
            result.stderr_excerpt or "Codex returned no final message",
        )
        return

    # Persist session ID for observability (though we never reuse it).
    if result.session_id and msg["task_id"]:
        set_session(msg["task_id"], "codex", result.session_id)

    response = result.response
    if not response:
        _handle_codex_error(msg, message_id, "Codex returned no final message")
        return

    print(f"\n✅ Codex finished ({len(response)} chars)")
    reply_id = send_message(
        content=response,
        task_id=msg["task_id"],
        msg_type="response",
        from_llm="codex",
        to_llm=msg["from"],
    )
    acknowledge(message_id)
    acknowledge(reply_id)


def _fetch_codex_message(message_id: int) -> dict | None:
    """Fetch a message addressed to Codex from the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, task_id, from_llm, to_llm, message_type, content, data, timestamp
        FROM messages
        WHERE id = ? AND to_llm = 'codex'
    """, (message_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"❌ Message {message_id} not found or not addressed to Codex")
        return None

    return {
        "id": row[0],
        "task_id": row[1],
        "from": row[2],
        "to": row[3],
        "type": row[4],
        "content": row[5],
        "data": row[6],
        "timestamp": row[7],
    }


def _extract_target_model(msg: dict) -> str | None:
    """Read optional to_model from message metadata JSON."""
    data = msg.get("data")
    if not data:
        return None
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        return None
    return payload.get("to_model")


def _handle_codex_error(msg: dict, message_id: int, error_msg: str) -> None:
    """Send bridge error back to sender."""
    print(f"\n❌ Codex CLI error: {error_msg[:500]}")
    err_id = send_message(
        content=f"[Bridge Error] Codex CLI failed:\n{error_msg[:500]}",
        task_id=msg["task_id"],
        msg_type="error",
        from_llm="codex",
        to_llm=msg["from"],
        from_model="codex-bridge-error",
    )
    acknowledge(message_id)
    acknowledge(err_id)


def _handle_codex_rate_limited(msg: dict, message_id: int, reason: str) -> None:
    """Defer a rate-limited message without acknowledging the inbound row."""
    print(f"\n⛔ Codex rate limited - message {message_id} deferred")
    print(f"   Reason: {reason}")
    err_id = send_message(
        content=(
            "[Codex rate limited] Usage limit hit.\n"
            f"Reason: {reason}\n\n"
            f"The incoming message (id={message_id}) remains in Codex's "
            "inbox and will be retried automatically when headroom returns. "
            "Sender should NOT retry manually."
        ),
        task_id=msg["task_id"],
        msg_type="error",
        from_llm="codex",
        to_llm=msg["from"],
        from_model="codex-bridge-rate-limited",
    )
    acknowledge(err_id)


def process_all_codex(new_session: bool = False):
    """Process ALL unread messages for Codex in batch."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, task_id, from_llm, message_type, substr(content, 1, 50)
        FROM messages
        WHERE to_llm = 'codex' AND acknowledged = 0
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("📭 No unread messages for Codex to process")
        return

    print(f"📬 Processing {len(rows)} unread message(s) for Codex...\n")
    success = 0
    failed = 0

    for row in rows:
        msg_id, _task_id, from_llm, _msg_type, preview = row
        preview = preview.replace("\n", " ")[:40]
        print(f"━━━ Processing [{msg_id}] from {from_llm}: {preview}...")
        try:
            process_for_codex(msg_id, new_session)
            success += 1
            print("    ✅ Done\n")
        except Exception as e:
            failed += 1
            print(f"    ❌ Failed: {e}\n")

    print(f"\n{'═' * 50}")
    print(f"📊 Results: {success} succeeded, {failed} failed out of {len(rows)} total")
