"""Tests for the channel-based AI agent bridge primitives."""

from __future__ import annotations

import sqlite3
import sys
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from ai_agent_bridge import _channels, _db


@pytest.fixture(autouse=True)
def isolate_db(tmp_path):
    """Ensure every test runs against a clean, isolated SQLite database."""
    db_file = tmp_path / "messages.db"
    with patch("ai_agent_bridge._config.DB_PATH", db_file), \
         patch("ai_agent_bridge._db.DB_PATH", db_file):
        _db.init_db()
        yield db_file


def _iso_at(seconds: int) -> str:
    base = datetime(2026, 1, 1, tzinfo=UTC)
    return (base + timedelta(seconds=seconds)).isoformat()


def _delivery_row(delivery_id: str) -> sqlite3.Row:
    conn = _db.get_db()
    try:
        row = conn.execute(
            """
            SELECT delivery_id, status, lease_until, attempt_count,
                   retry_after, delivered_at, error, last_error_kind
            FROM deliveries
            WHERE delivery_id = ?
            """,
            (delivery_id,),
        ).fetchone()
        assert row is not None
        return row
    finally:
        conn.close()


# 1. Channel CRUD

def test_create_channel_basic():
    """Verify a new channel can be created and retrieved."""
    ch = _channels.create_channel("my-topic", description="A test topic")
    assert ch["name"] == "my-topic"
    assert ch["description"] == "A test topic"

    listed = _channels.list_channels()
    assert len(listed) == 1
    assert listed[0]["name"] == "my-topic"

def test_create_channel_duplicate_exist_ok_returns_existing():
    """Verify idempotent creation returns the existing channel unmodified."""
    _channels.create_channel("topic", description="original")
    ch = _channels.create_channel("topic", description="new", exist_ok=True)
    assert ch["description"] == "original"  # Existing row is returned

def test_create_channel_duplicate_exist_ok_false_raises():
    """Verify duplicate creation raises ValueError if exist_ok=False."""
    _channels.create_channel("topic")
    with pytest.raises(ValueError, match="already exists"):
        _channels.create_channel("topic", exist_ok=False)

def test_create_channel_with_include_and_subscribers():
    """Verify list fields round-trip correctly."""
    ch = _channels.create_channel(
        "topic",
        include=["shared", "other"],
        subscribers=["claude", "gemini"]
    )
    assert ch["include"] == ["shared", "other"]
    assert ch["subscribers"] == ["claude", "gemini"]

    fetched = _channels.get_channel("topic")
    assert fetched["include"] == ["shared", "other"]
    assert fetched["subscribers"] == ["claude", "gemini"]

def test_create_channel_invalid_name_raises():
    """Verify invalid channel names are rejected."""
    for bad_name in ["", "   ", "My Topic", "my topic"]:
        with pytest.raises(ValueError):
            _channels.create_channel(bad_name)

def test_get_channel_nonexistent_returns_none():
    """Verify getting a nonexistent channel returns None."""
    assert _channels.get_channel("nope") is None

def test_list_channels_ordered_by_creation():
    """Verify list_channels sorts by creation time ascending."""
    _channels.create_channel("topic-a")
    _channels.create_channel("topic-b")
    listed = _channels.list_channels()
    assert listed[0]["name"] == "topic-a"
    assert listed[1]["name"] == "topic-b"

# 2. Posting (origin)

def test_post_to_nonexistent_channel_raises_valueerror():
    """Verify posting requires the channel to exist."""
    with pytest.raises(ValueError, match="does not exist"):
        _channels.post("nope", "gemini", "hello")

def test_post_origin_self_references_thread_id():
    """Verify a root post has thread_id equal to its message_id."""
    _channels.create_channel("topic")
    res = _channels.post("topic", "gemini", "hello")
    assert res["thread_id"] == res["message_id"]

def test_post_origin_round_index_is_zero():
    """Verify a root post starts at round_index 0."""
    _channels.create_channel("topic")
    res = _channels.post("topic", "gemini", "hello")
    assert res["round_index"] == 0

def test_post_with_attachments_roundtrip_json():
    """Verify attachments are stored and parsed correctly."""
    _channels.create_channel("topic")
    atts = [{"name": "file.txt", "content": "data"}]
    _channels.post("topic", "gemini", "hello", attachments=atts)

    msg = _channels.read("topic")[0]
    assert msg["attachments"] == atts

def test_post_with_monitor_snapshot_roundtrip():
    """Verify monitor_state_snapshot is stored and parsed correctly."""
    _channels.create_channel("topic")
    snap = {"state": "good", "count": 42}
    _channels.post("topic", "gemini", "hello", monitor_state_snapshot=snap)

    msg = _channels.read("topic")[0]
    assert msg["monitor_state_snapshot"] == snap

def test_post_creates_delivery_row_per_recipient():
    """Verify posting creates one delivery row per specified recipient."""
    _channels.create_channel("topic")
    res = _channels.post("topic", "gemini", "hello", to_agents=["claude", "codex", "user"])
    assert len(res["delivery_ids"]) == 3

    dlvs = _channels.deliveries_for_message(res["message_id"])
    assert len(dlvs) == 3
    assert {d["to_agent"] for d in dlvs} == {"claude", "codex", "user"}
    assert all(d["status"] == "pending" for d in dlvs)


def test_post_touches_recipient_wake_file(tmp_path, monkeypatch):
    """Posting to a recipient updates `.agent/wake/{agent}` after commit."""
    wake_root = tmp_path / ".agent" / "wake"
    wake_root.mkdir(parents=True)
    wake_file = wake_root / "claude"
    wake_file.write_text("old", encoding="utf-8")
    wake_file.touch()
    old_ns = 1_000_000_000
    wake_file_stat = wake_file.stat()
    assert wake_file_stat.st_mtime_ns > 0
    import os
    os.utime(wake_file, ns=(old_ns, old_ns))

    monkeypatch.setattr(_channels, "WAKE_ROOT", wake_root)
    _channels.create_channel("topic")

    _channels.post("topic", "gemini", "hello", to_agents=["claude"], auto_snapshot=False)

    assert wake_file.exists()
    assert wake_file.stat().st_mtime_ns != old_ns
    assert wake_file.read_text(encoding="utf-8").strip()

def test_post_with_zero_recipients_no_deliveries():
    """Verify posting without recipients creates no delivery rows."""
    _channels.create_channel("topic")
    res = _channels.post("topic", "gemini", "hello")
    assert res["delivery_ids"] == []

    dlvs = _channels.deliveries_for_message(res["message_id"])
    assert len(dlvs) == 0

def test_post_invalid_from_agent_raises():
    """Verify posting requires a valid from_agent."""
    _channels.create_channel("topic")
    with pytest.raises(ValueError, match="Unknown agent"):
        _channels.post("topic", "invalid", "hello")

def test_post_invalid_kind_raises():
    """Verify posting requires a valid kind."""
    _channels.create_channel("topic")
    with pytest.raises(ValueError, match="Unknown kind"):
        _channels.post("topic", "gemini", "hello", kind="invalid")

# 3. Replies (threading)

def test_reply_inherits_parent_thread_id():
    """Verify a reply shares the thread_id of its parent."""
    _channels.create_channel("topic")
    parent = _channels.post("topic", "gemini", "hello")
    reply = _channels.post("topic", "claude", "hi", parent_id=parent["message_id"])
    assert reply["thread_id"] == parent["thread_id"]

def test_reply_increments_round_index():
    """Verify a reply has a round_index one greater than its parent."""
    _channels.create_channel("topic")
    parent = _channels.post("topic", "gemini", "hello")
    reply = _channels.post("topic", "claude", "hi", parent_id=parent["message_id"])
    assert reply["round_index"] == 1

def test_reply_nonexistent_parent_raises():
    """Verify replying to an unknown message raises ValueError."""
    _channels.create_channel("topic")
    with pytest.raises(ValueError, match="not found"):
        _channels.post("topic", "claude", "hi", parent_id="nope")

def test_nested_reply_round_index_chain():
    """Verify nested replies correctly increment round_index."""
    _channels.create_channel("topic")
    p0 = _channels.post("topic", "gemini", "p0")
    p1 = _channels.post("topic", "claude", "p1", parent_id=p0["message_id"])
    p2 = _channels.post("topic", "gemini", "p2", parent_id=p1["message_id"])
    assert p0["round_index"] == 0
    assert p1["round_index"] == 1
    assert p2["round_index"] == 2
    assert p0["thread_id"] == p1["thread_id"] == p2["thread_id"]

# 4. Reading

def test_read_empty_channel_returns_empty_list():
    """Verify reading an empty channel returns [] rather than None/error."""
    _channels.create_channel("topic")
    assert _channels.read("topic") == []

def test_read_tail_respects_limit():
    """Verify read(tail=N) returns at most N messages in chronological order."""
    _channels.create_channel("topic")
    for i in range(5):
        _channels.post("topic", "gemini", f"msg{i}")

    msgs = _channels.read("topic", tail=3)
    assert len(msgs) == 3
    assert msgs[0]["body"] == "msg2"
    assert msgs[2]["body"] == "msg4"

def test_read_thread_returns_all_messages_in_order():
    """Verify reading a thread returns all messages sorted by round_index."""
    _channels.create_channel("topic")
    p0 = _channels.post("topic", "gemini", "p0")
    p1 = _channels.post("topic", "claude", "p1", parent_id=p0["message_id"])
    p2 = _channels.post("topic", "gemini", "p2", parent_id=p1["message_id"])

    msgs = _channels.read("topic", thread_id=p0["thread_id"])
    assert len(msgs) == 3
    assert msgs[0]["message_id"] == p0["message_id"]
    assert msgs[1]["message_id"] == p1["message_id"]
    assert msgs[2]["message_id"] == p2["message_id"]

def test_read_thread_filters_by_channel():
    """Verify thread reads don't leak across channels if IDs accidentally match."""
    _channels.create_channel("topic1")
    _channels.create_channel("topic2")
    p0 = _channels.post("topic1", "gemini", "p0")
    # Manually insert a matching thread_id in another channel
    conn = _db.get_db()
    conn.execute(
        "INSERT INTO channel_messages (message_id, channel, thread_id, round_index, from_agent, body, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("fake", "topic2", p0["thread_id"], 0, "claude", "fake", "2000-01-01")
    )
    conn.commit()
    conn.close()

    msgs = _channels.read("topic1", thread_id=p0["thread_id"])
    assert len(msgs) == 1
    assert msgs[0]["message_id"] == p0["message_id"]

# 5. Deliveries (outbound state machine)

def test_mark_delivery_dispatched_sets_timestamp():
    """Verify marking as dispatched updates status and dispatched_at."""
    _channels.create_channel("topic")
    res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
    dlv_id = res["delivery_ids"][0]

    _channels.mark_delivery(dlv_id, "dispatched")
    dlvs = _channels.deliveries_for_message(res["message_id"])
    assert dlvs[0]["status"] == "dispatched"
    assert dlvs[0]["dispatched_at"] is not None

def test_mark_delivery_delivered_sets_delivered_at():
    """Verify marking as delivered updates status and delivered_at."""
    _channels.create_channel("topic")
    res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
    dlv_id = res["delivery_ids"][0]

    _channels.mark_delivery(dlv_id, "delivered")
    dlvs = _channels.deliveries_for_message(res["message_id"])
    assert dlvs[0]["status"] == "delivered"
    assert dlvs[0]["delivered_at"] is not None

def test_mark_delivery_failed_stores_error():
    """Verify marking as failed updates status and error message."""
    _channels.create_channel("topic")
    res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
    dlv_id = res["delivery_ids"][0]

    _channels.mark_delivery(dlv_id, "failed", error="timeout")
    dlvs = _channels.deliveries_for_message(res["message_id"])
    assert dlvs[0]["status"] == "failed"
    assert dlvs[0]["error"] == "timeout"

def test_mark_delivery_invalid_status_raises():
    """Verify updating to an unknown status raises ValueError."""
    _channels.create_channel("topic")
    res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
    with pytest.raises(ValueError, match="invalid delivery status"):
        _channels.mark_delivery(res["delivery_ids"][0], "magic")

def test_deliveries_for_message_returns_all_recipients():
    """Verify deliveries_for_message lists all intended recipients."""
    _channels.create_channel("topic")
    res = _channels.post("topic", "gemini", "hello", to_agents=["claude", "codex"])
    dlvs = _channels.deliveries_for_message(res["message_id"])
    assert len(dlvs) == 2
    assert {d["to_agent"] for d in dlvs} == {"claude", "codex"}

def test_pending_deliveries_for_agent_filters_by_agent():
    """Verify agent queues only return their own pending deliveries."""
    _channels.create_channel("topic")
    _channels.post("topic", "gemini", "msg", to_agents=["claude", "codex"])

    claude_q = _channels.pending_deliveries_for("claude")
    codex_q = _channels.pending_deliveries_for("codex")
    gemini_q = _channels.pending_deliveries_for("gemini")

    assert len(claude_q) == 1
    assert len(codex_q) == 1
    assert len(gemini_q) == 0

def test_pending_deliveries_for_agent_ordered_oldest_first():
    """Verify the pending queue orders by oldest message first."""
    _channels.create_channel("topic")
    _channels.post("topic", "gemini", "msg1", to_agents=["claude"])
    _channels.post("topic", "gemini", "msg2", to_agents=["claude"])

    q = _channels.pending_deliveries_for("claude")
    assert len(q) == 2
    assert q[0]["body"] == "msg1"
    assert q[1]["body"] == "msg2"

# 6. Concurrency

def test_concurrent_post_no_data_loss(isolate_db):
    """Verify multiple threads can post simultaneously without locking errors."""
    _channels.create_channel("topic")

    threads = []
    barrier = threading.Barrier(5)

    def worker(i):
        barrier.wait()
        _channels.post("topic", "gemini", f"body{i}", to_agents=["claude", "codex", "user"])

    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # Verify via direct sqlite3 connection
    conn = sqlite3.connect(isolate_db)
    cursor = conn.cursor()
    msgs = cursor.execute("SELECT message_id FROM channel_messages WHERE channel='topic'").fetchall()
    dlvs = cursor.execute("SELECT delivery_id FROM deliveries").fetchall()
    conn.close()

    assert len(msgs) == 5
    assert len(set(msgs)) == 5  # No duplicates
    assert len(dlvs) == 15      # 5 messages * 3 recipients

def test_concurrent_reply_to_same_parent():
    """Verify multiple threads can reply to the same parent safely."""
    _channels.create_channel("topic")
    parent = _channels.post("topic", "gemini", "parent")

    threads = []
    barrier = threading.Barrier(3)

    def worker(i):
        barrier.wait()
        _channels.post("topic", "claude", f"reply{i}", parent_id=parent["message_id"])

    for i in range(3):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    msgs = _channels.read("topic", thread_id=parent["thread_id"])
    assert len(msgs) == 4
    # The parent is 0, the replies should all be round_index 1
    round_indices = [m["round_index"] for m in msgs]
    assert round_indices == [0, 1, 1, 1]

# 7. context_sha256 helper

def test_context_sha256_existing_file(tmp_path):
    """Verify sha256 computes correctly for an existing file."""
    f = tmp_path / "context.md"
    f.write_text("hello world")
    import hashlib
    expected = hashlib.sha256(b"hello world").hexdigest()
    assert _channels.context_sha256(f) == expected

def test_context_sha256_missing_file_returns_empty_string(tmp_path):
    """Verify missing files return empty string rather than raising."""
    f = tmp_path / "nope.md"
    assert _channels.context_sha256(f) == ""


# ════════════════════════════════════════════════════════════════════
# B.2: Context injection + Monitor API fetch + prompt assembly (#1190)
# ════════════════════════════════════════════════════════════════════

@pytest.fixture
def isolated_context_root(tmp_path, monkeypatch):
    """Point CONTEXT_ROOT at a tmp dir so tests don't read real docs/."""
    root = tmp_path / "agent-channels"
    root.mkdir()
    monkeypatch.setattr(_channels, "CONTEXT_ROOT", root)
    return root


def test_channel_context_path_returns_expected_location(isolated_context_root):
    """Verify channel_context_path resolves to {CONTEXT_ROOT}/{channel}/context.md."""
    p = _channels.channel_context_path("pipeline")
    assert p == isolated_context_root / "pipeline" / "context.md"


def test_load_channel_context_missing_returns_empty_body(isolated_context_root):
    """Loading a channel with no context.md returns empty body + missing list."""
    _channels.create_channel("pipeline")
    result = _channels.load_channel_context("pipeline")
    assert result["body"] == ""
    assert "pipeline" in result["missing"]
    assert "pipeline" in result["revs"]
    assert result["revs"]["pipeline"] == ""


def test_load_channel_context_with_file_loads_and_hashes(isolated_context_root):
    """Loading a channel with a context.md reads it and computes sha256."""
    _channels.create_channel("pipeline")
    ctx_dir = isolated_context_root / "pipeline"
    ctx_dir.mkdir()
    (ctx_dir / "context.md").write_text("# pipeline rules\nUse BEGIN IMMEDIATE")
    result = _channels.load_channel_context("pipeline")
    assert "pipeline rules" in result["body"]
    assert "BEGIN IMMEDIATE" in result["body"]
    assert result["revs"]["pipeline"]  # nonempty sha256
    assert result["missing"] == []


def test_load_channel_context_recursive_includes(isolated_context_root):
    """Includes are resolved depth-first, shared comes first in body."""
    _channels.create_channel("shared")
    _channels.create_channel("pipeline", include=["shared"])
    (isolated_context_root / "shared").mkdir()
    (isolated_context_root / "shared" / "context.md").write_text("PROJECT RULES")
    (isolated_context_root / "pipeline").mkdir()
    (isolated_context_root / "pipeline" / "context.md").write_text("PIPELINE RULES")
    result = _channels.load_channel_context("pipeline")
    # Shared must appear before pipeline in the combined body
    assert result["body"].index("PROJECT RULES") < result["body"].index("PIPELINE RULES")
    assert set(result["revs"].keys()) == {"shared", "pipeline"}
    assert result["missing"] == []


def test_load_channel_context_cycle_detection(isolated_context_root):
    """Circular includes don't infinite-loop."""
    _channels.create_channel("a", include=["b"])
    _channels.create_channel("b", include=["a"])
    (isolated_context_root / "a").mkdir()
    (isolated_context_root / "a" / "context.md").write_text("A")
    (isolated_context_root / "b").mkdir()
    (isolated_context_root / "b" / "context.md").write_text("B")
    # Should terminate without RecursionError
    result = _channels.load_channel_context("a")
    assert "A" in result["body"]
    assert "B" in result["body"]


def test_fetch_monitor_state_returns_none_on_connection_error(monkeypatch):
    """Monitor API down → returns None, doesn't raise."""
    import urllib.error
    def boom(*a, **kw):
        raise urllib.error.URLError("connection refused")
    monkeypatch.setattr("urllib.request.urlopen", boom)
    assert _channels.fetch_monitor_state(timeout=0.1) is None


def test_fetch_monitor_state_returns_none_on_timeout(monkeypatch):
    """Timeout also returns None, not raise."""
    def boom(*a, **kw):
        raise TimeoutError("slow")
    monkeypatch.setattr("urllib.request.urlopen", boom)
    assert _channels.fetch_monitor_state(timeout=0.1) is None


def test_truncate_history_by_budget_empty():
    """Empty list → empty result, zero dropped."""
    kept, dropped = _channels.truncate_history_by_budget([])
    assert kept == []
    assert dropped == 0


def test_truncate_history_by_budget_all_fit():
    """If everything fits, nothing is dropped."""
    messages = [{"body": "short", "round_index": 0}] * 3
    kept, dropped = _channels.truncate_history_by_budget(messages, max_chars=10000)
    assert len(kept) == 3
    assert dropped == 0


def test_truncate_history_by_budget_drops_oldest_first():
    """Oldest messages are dropped first when over budget."""
    messages = [
        {"body": "a" * 100, "round_index": 0},
        {"body": "b" * 100, "round_index": 1},
        {"body": "c" * 100, "round_index": 2},
    ]
    # Budget fits roughly 1-2 messages (100 body + 80 envelope each)
    kept, dropped = _channels.truncate_history_by_budget(messages, max_chars=200)
    assert dropped >= 1
    # Newest (c) should survive, oldest (a) dropped
    kept_bodies = [m["body"] for m in kept]
    assert "c" * 100 in kept_bodies
    assert "a" * 100 not in kept_bodies


def test_truncate_history_by_budget_keeps_at_least_one():
    """Even with an absurdly small budget, the newest message is kept."""
    messages = [
        {"body": "a" * 10_000, "round_index": 0},
        {"body": "b" * 10_000, "round_index": 1},
    ]
    kept, _dropped = _channels.truncate_history_by_budget(messages, max_chars=50)
    # At least one (the newest) survives — the "and kept_rev" guard
    assert len(kept) >= 1
    assert kept[-1]["body"] == "b" * 10_000


def test_post_auto_snapshot_captures_context_sha256(isolated_context_root):
    """post() with auto_snapshot=True records file hashes into the message row."""
    _channels.create_channel("shared")
    _channels.create_channel("pipeline", include=["shared"])
    (isolated_context_root / "shared").mkdir()
    (isolated_context_root / "shared" / "context.md").write_text("shared-content")
    (isolated_context_root / "pipeline").mkdir()
    (isolated_context_root / "pipeline" / "context.md").write_text("pipeline-content")

    # Prevent network call in test
    with patch.object(_channels, "fetch_monitor_state", return_value=None):
        result = _channels.post("pipeline", "user", "test body", auto_snapshot=True)

    msgs = _channels.read("pipeline", tail=1)
    assert len(msgs) == 1
    import hashlib
    shared_sha = hashlib.sha256(b"shared-content").hexdigest()
    pipeline_sha = hashlib.sha256(b"pipeline-content").hexdigest()
    assert msgs[0]["context_rev_shared"] == shared_sha
    assert msgs[0]["context_rev_channel"] == pipeline_sha


def test_post_auto_snapshot_with_missing_shared_warns(isolated_context_root, capsys):
    """Missing shared context emits a loud stderr warning per review feedback."""
    _channels.create_channel("shared")  # no context file
    _channels.create_channel("pipeline")  # no context file either
    with patch.object(_channels, "fetch_monitor_state", return_value=None):
        _channels.post("pipeline", "user", "body", auto_snapshot=True)
    captured = capsys.readouterr()
    assert "shared context file is missing" in captured.err


def test_post_auto_snapshot_false_skips_io(isolated_context_root):
    """auto_snapshot=False leaves context_rev_* as empty strings."""
    _channels.create_channel("pipeline")
    _channels.post("pipeline", "user", "body", auto_snapshot=False)
    msgs = _channels.read("pipeline", tail=1)
    assert msgs[0]["context_rev_shared"] == ""
    assert msgs[0]["context_rev_channel"] == ""
    assert msgs[0]["monitor_state_snapshot"] is None


def test_build_agent_prompt_assembles_sections(isolated_context_root):
    """build_agent_prompt produces context + history + body in order."""
    _channels.create_channel("pipeline")
    (isolated_context_root / "pipeline").mkdir()
    (isolated_context_root / "pipeline" / "context.md").write_text("RULES: always test")

    # Post one historical message
    _channels.post("pipeline", "user", "earlier message", auto_snapshot=False)

    with patch.object(_channels, "fetch_monitor_state", return_value=None):
        info = _channels.build_agent_prompt(
            "pipeline", "new post body", include_monitor_state=False
        )

    assert "RULES: always test" in info["prompt"]
    assert "earlier message" in info["prompt"]
    assert "new post body" in info["prompt"]
    # Context must come before history, history before body (order matters
    # for attention — newest/most-important content at the END)
    idx_rules = info["prompt"].index("RULES")
    idx_earlier = info["prompt"].index("earlier message")
    idx_body = info["prompt"].index("new post body")
    assert idx_rules < idx_earlier < idx_body


def test_build_agent_prompt_raises_if_body_alone_exceeds_budget(isolated_context_root):
    """A too-large post body raises ValueError instead of silently truncating."""
    _channels.create_channel("pipeline")
    huge = "x" * 100_000
    with pytest.raises(ValueError, match="post body alone"):
        _channels.build_agent_prompt(
            "pipeline", huge,
            include_monitor_state=False,
            max_prompt_chars=1000,
        )


def test_build_agent_prompt_respects_budget_when_body_close_to_limit(
    isolated_context_root,
):
    """Regression for negative-slice bug in context truncation (#1190 B.2 review).

    Gemini found that if ``body_len`` is close to but under
    ``max_prompt_chars``, ``remaining = max_prompt_chars - body_len - 100``
    evaluates NEGATIVE, and ``context_text[:-50]`` slices off only the last
    50 chars instead of truncating to 50 chars. Before the fix the final
    prompt blew past the ceiling.
    """
    _channels.create_channel("pipeline")
    (isolated_context_root / "pipeline").mkdir()
    # Large context — 10,000 chars of real content
    (isolated_context_root / "pipeline" / "context.md").write_text("R" * 10_000)

    # body is 950 chars; budget is 1000; remaining would be 1000-950-100 = -50
    body = "B" * 950
    info = _channels.build_agent_prompt(
        "pipeline", body,
        include_monitor_state=False,
        max_prompt_chars=1000,
    )

    # The final prompt MUST fit the budget, no exceptions
    assert len(info["prompt"]) <= 1000, (
        f"prompt length {len(info['prompt'])} exceeds budget 1000 — "
        f"negative-slice bug regressed"
    )
    # Body must survive intact
    assert body in info["prompt"]


def test_post_parent_fk_enforcement(isolated_context_root):
    """Foreign key on parent_id: reply to non-existent parent raises."""
    _channels.create_channel("pipeline")
    # parent_id references a message that doesn't exist
    with pytest.raises(ValueError, match="parent message"):
        _channels.post(
            "pipeline", "user", "reply body",
            parent_id="deadbeef" * 4,
            auto_snapshot=False,
        )


class TestDeliveryLeasing:
    def test_claim_single_delivery(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])

        claimed = _channels.claim_next_delivery("claude", now=_iso_at(0))

        assert claimed is not None
        assert claimed["delivery_id"] == res["delivery_ids"][0]
        assert claimed["status"] == "processing"

        row = _delivery_row(res["delivery_ids"][0])
        assert row["status"] == "processing"
        assert row["lease_until"] is not None
        assert row["attempt_count"] == 1

    def test_claim_returns_none_when_empty(self):
        assert _channels.claim_next_delivery("claude", now=_iso_at(0)) is None

    def test_claim_atomic_under_concurrent_callers(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])

        barrier = threading.Barrier(3)
        results: list[dict[str, str] | None] = []
        lock = threading.Lock()

        def worker():
            barrier.wait()
            claimed = _channels.claim_next_delivery("claude", now=_iso_at(0))
            with lock:
                results.append(claimed)

        threads = [threading.Thread(target=worker) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        claimed = [item for item in results if item is not None]
        assert len(claimed) == 1
        assert claimed[0]["delivery_id"] == res["delivery_ids"][0]
        assert sum(item is None for item in results) == 2

    def test_claim_respects_retry_after(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
        delivery_id = res["delivery_ids"][0]

        conn = _db.get_db()
        conn.execute(
            "UPDATE deliveries SET retry_after = ? WHERE delivery_id = ?",
            (_iso_at(60), delivery_id),
        )
        conn.commit()
        conn.close()

        assert _channels.claim_next_delivery("claude", now=_iso_at(0)) is None

        claimed = _channels.claim_next_delivery("claude", now=_iso_at(61))
        assert claimed is not None
        assert claimed["delivery_id"] == delivery_id

    def test_claim_respects_max_attempts(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
        delivery_id = res["delivery_ids"][0]

        first = _channels.claim_next_delivery("claude", now=_iso_at(0))
        assert first is not None
        _channels.mark_delivery_failed(
            delivery_id,
            "unavailable",
            "try later",
            reschedule_after=_iso_at(1),
            now=_iso_at(0),
        )

        second = _channels.claim_next_delivery("claude", now=_iso_at(1))
        assert second is not None
        _channels.mark_delivery_failed(
            delivery_id,
            "unavailable",
            "try later",
            reschedule_after=_iso_at(2),
            now=_iso_at(1),
        )

        third = _channels.claim_next_delivery("claude", now=_iso_at(2))
        assert third is not None
        _channels.mark_delivery_failed(
            delivery_id,
            "timeout",
            "final timeout",
            reschedule_after=_iso_at(3),
            now=_iso_at(2),
        )

        row = _delivery_row(delivery_id)
        assert row["status"] == "failed"
        assert row["attempt_count"] == 3
        assert _channels.claim_next_delivery("claude", now=_iso_at(3)) is None

    def test_mark_delivered_terminal(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
        delivery_id = res["delivery_ids"][0]

        claimed = _channels.claim_next_delivery("claude", now=_iso_at(0))
        assert claimed is not None
        _channels.mark_delivery_delivered(
            delivery_id,
            "reply-1",
            now=_iso_at(5),
        )

        row = _delivery_row(delivery_id)
        assert row["status"] == "delivered"
        assert row["delivered_at"] == _iso_at(5)
        assert row["lease_until"] is None
        assert _channels.claim_next_delivery("claude", now=_iso_at(6)) is None

    def test_mark_failed_terminal(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
        delivery_id = res["delivery_ids"][0]

        claimed = _channels.claim_next_delivery("claude", now=_iso_at(0))
        assert claimed is not None
        _channels.mark_delivery_failed(
            delivery_id,
            "tool_error",
            "tool exploded",
            now=_iso_at(5),
        )

        row = _delivery_row(delivery_id)
        assert row["status"] == "failed"
        assert row["error"] == "tool exploded"
        assert row["lease_until"] is None
        assert row["retry_after"] is None
        assert _channels.claim_next_delivery("claude", now=_iso_at(6)) is None

    def test_mark_failed_rescheduled(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
        delivery_id = res["delivery_ids"][0]

        claimed = _channels.claim_next_delivery("claude", now=_iso_at(0))
        assert claimed is not None
        _channels.mark_delivery_failed(
            delivery_id,
            "unavailable",
            "busy",
            reschedule_after=_iso_at(60),
            now=_iso_at(0),
        )

        row = _delivery_row(delivery_id)
        assert row["status"] == "pending"
        assert row["retry_after"] == _iso_at(60)
        assert row["lease_until"] is None
        assert _channels.claim_next_delivery("claude", now=_iso_at(59)) is None

        claimed_again = _channels.claim_next_delivery("claude", now=_iso_at(60))
        assert claimed_again is not None
        assert claimed_again["delivery_id"] == delivery_id

    def test_rate_limit_sets_default_retry_after(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
        delivery_id = res["delivery_ids"][0]

        claimed = _channels.claim_next_delivery("claude", now=_iso_at(0))
        assert claimed is not None
        _channels.mark_delivery_failed(
            delivery_id,
            "rate_limited",
            "rate limited",
            now=_iso_at(0),
        )

        row = _delivery_row(delivery_id)
        assert row["status"] == "pending"
        assert row["retry_after"] == _iso_at(300)
        assert row["last_error_kind"] == "rate_limited"

    def test_release_expired_leases(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
        delivery_id = res["delivery_ids"][0]

        claimed = _channels.claim_next_delivery(
            "claude",
            lease_seconds=30,
            now=_iso_at(0),
        )
        assert claimed is not None

        released = _channels.release_expired_leases(now=_iso_at(31))
        assert released == 1

        row = _delivery_row(delivery_id)
        assert row["status"] == "pending"
        assert row["lease_until"] is None
        assert row["attempt_count"] == 1

        claimed_again = _channels.claim_next_delivery("claude", now=_iso_at(32))
        assert claimed_again is not None
        assert claimed_again["delivery_id"] == delivery_id

    def test_release_expired_leases_ignores_fresh_leases(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
        delivery_id = res["delivery_ids"][0]

        claimed = _channels.claim_next_delivery(
            "claude",
            lease_seconds=30,
            now=_iso_at(0),
        )
        assert claimed is not None

        released = _channels.release_expired_leases(now=_iso_at(29))
        assert released == 0

        row = _delivery_row(delivery_id)
        assert row["status"] == "processing"
        assert row["lease_until"] == _iso_at(30)

    def test_attempt_count_increments_on_each_claim(self):
        _channels.create_channel("topic")
        res = _channels.post("topic", "gemini", "hello", to_agents=["claude"])
        delivery_id = res["delivery_ids"][0]

        first = _channels.claim_next_delivery("claude", now=_iso_at(0))
        assert first is not None
        assert _delivery_row(delivery_id)["attempt_count"] == 1

        _channels.mark_delivery_failed(
            delivery_id,
            "unavailable",
            "retry",
            reschedule_after=_iso_at(1),
            now=_iso_at(0),
        )

        second = _channels.claim_next_delivery("claude", now=_iso_at(1))
        assert second is not None
        assert _delivery_row(delivery_id)["attempt_count"] == 2
