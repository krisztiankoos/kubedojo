from __future__ import annotations

import html as _html
import json as _json
import re as _re
import threading as _threading
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, unquote


RouteResponse = tuple[int, Any, str]
_POST_DB_LOCK = _threading.Lock()


def _json_response(status: int, payload: dict[str, Any]) -> RouteResponse:
    return status, payload, "application/json; charset=utf-8"


def _safe_json_for_script(value: Any) -> str:
    return (
        _json.dumps(value)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def _channel_event_sort_key(channel: dict[str, Any]) -> str:
    value = channel.get("last_event_ts") or channel.get("created_at") or ""
    return str(value)


def _finalize_channel_rollup(
    channels: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    for channel in channels.values():
        threads = channel.get("threads")
        if not isinstance(threads, list):
            threads = []
            channel["threads"] = threads
        channel["thread_count"] = len(threads)
        channel["message_count"] = sum(
            int(thread.get("message_count") or 0)
            for thread in threads
            if isinstance(thread, dict)
        )
        channel["event_count"] = sum(
            int(thread.get("event_count") or 0)
            for thread in threads
            if isinstance(thread, dict)
        )
        channel["last_event_ts"] = max(
            (
                str(thread.get("last_event_ts") or "")
                for thread in threads
                if isinstance(thread, dict)
            ),
            default=channel.get("created_at") or "",
        )
    return {
        "channels": sorted(
            channels.values(),
            key=_channel_event_sort_key,
            reverse=True,
        )
    }


def build_channel_threads_index(
    repo_root: Path,
    *,
    list_channels_fn: Callable[[], list[dict[str, Any]]],
    resolve_bridge_db_path_fn: Callable[[Path], Path],
    query_sqlite_rows_fn: Callable[..., list[dict[str, Any]]],
) -> dict[str, Any]:
    """Build deliberation thread rollups from ``channel_messages``.

    ``channel_messages`` is the transcript source of truth. ``channel_events``
    is optional metadata for progress state and visualization hints.
    """
    db_path = resolve_bridge_db_path_fn(repo_root)
    channels_raw = list_channels_fn()

    channels: dict[str, dict[str, Any]] = {
        channel["name"]: {
            "name": channel["name"],
            "created_at": channel.get("created_at"),
            "threads": [],
        }
        for channel in channels_raw
        if isinstance(channel, dict)
    }

    thread_rows = query_sqlite_rows_fn(
        db_path,
        """
        SELECT
          cm.channel AS channel,
          cm.thread_id AS thread_id,
          MIN(cm.created_at) AS thread_started_at,
          MAX(cm.created_at) AS thread_last_at,
          COUNT(*) AS message_count,
          (
            SELECT substr(cm2.body, 1, 80)
            FROM channel_messages cm2
            WHERE cm2.channel = cm.channel
              AND cm2.thread_id = cm.thread_id
            ORDER BY cm2.rowid ASC
            LIMIT 1
          ) AS subject
        FROM channel_messages cm
        GROUP BY cm.channel, cm.thread_id
        ORDER BY cm.channel ASC, MAX(cm.created_at) DESC
        """,
    )

    thread_index: dict[tuple[str, str], dict[str, Any]] = {}
    thread_keys_by_id: dict[str, list[tuple[str, str]]] = {}
    for row in thread_rows:
        channel = row.get("channel")
        thread_id = row.get("thread_id")
        if not isinstance(channel, str) or not isinstance(thread_id, str):
            continue
        thread_started_at = row.get("thread_started_at")
        thread_last_at = row.get("thread_last_at")
        thread_entry = {
            "thread_id": thread_id,
            "subject": (row.get("subject") or "").strip(),
            "thread_started_at": thread_started_at,
            "thread_last_at": thread_last_at,
            "message_count": int(row.get("message_count") or 0),
            "first_event_ts": None,
            "last_event_ts": thread_last_at,
            "event_count": 0,
            "agents": [],
            "model_cascades": [],
            "reply_state": None,
            "vote_counts": {
                "agree": 0,
                "defer": 0,
                "options": {},
            },
        }
        thread_key = (channel, thread_id)
        thread_index[thread_key] = thread_entry
        thread_keys_by_id.setdefault(thread_id, []).append(thread_key)
        entry = channels.setdefault(
            channel,
            {"name": channel, "created_at": None, "threads": []},
        )
        entry["threads"].append(thread_entry)

    if thread_index:
        event_rows = query_sqlite_rows_fn(
            db_path,
            """
            SELECT event_id, thread_id, event, payload_json, ts
            FROM channel_events
            ORDER BY event_id ASC
            """,
            limit=10000,
        )
        agents_by_thread: dict[str, set[str]] = {}
        latest_reply_state: dict[str, tuple[int, dict[str, Any]]] = {}
        for event_row in event_rows:
            thread_id = event_row.get("thread_id")
            if not isinstance(thread_id, str) or thread_id not in thread_keys_by_id:
                continue
            entries = [
                thread_index[thread_key]
                for thread_key in thread_keys_by_id[thread_id]
            ]
            ts = event_row.get("ts")
            for entry in entries:
                entry["first_event_ts"] = entry["first_event_ts"] or ts
                entry["last_event_ts"] = ts or entry["last_event_ts"]
                entry["event_count"] += 1

            payload_raw = event_row.get("payload_json")
            try:
                payload = _json.loads(payload_raw) if payload_raw else {}
            except _json.JSONDecodeError:
                payload = {}
            event = event_row.get("event")
            event_id = int(event_row.get("event_id") or 0)

            if event == "reply_started":
                agent = payload.get("agent")
                if isinstance(agent, str):
                    agents_by_thread.setdefault(thread_id, set()).add(agent)
                latest_reply_state[thread_id] = (
                    event_id,
                    {"event": event, "ts": ts, **payload},
                )
            elif event == "reply_complete":
                agent = payload.get("agent")
                if isinstance(agent, str):
                    agents_by_thread.setdefault(thread_id, set()).add(agent)
                latest_reply_state[thread_id] = (
                    event_id,
                    {"event": event, "ts": ts, **payload},
                )
                body = payload.get("body")
                if isinstance(body, str):
                    for entry in entries:
                        entry["vote_counts"]["agree"] += len(
                            _re.findall(r"\[AGREE\]", body)
                        )
                        entry["vote_counts"]["defer"] += len(
                            _re.findall(r"\[DEFER\]", body)
                        )
                        options = entry["vote_counts"]["options"]
                        for match in _re.findall(r"\[OPTION ([A-Z0-9]+)\]", body):
                            options[match] = int(options.get(match, 0)) + 1
            elif event == "model_cascade":
                for entry in entries:
                    entry["model_cascades"].append({"ts": ts, **payload})

        for thread_id, agents in agents_by_thread.items():
            for thread_key in thread_keys_by_id.get(thread_id, []):
                thread_index[thread_key]["agents"] = sorted(agents)
        for thread_id, (_, state) in latest_reply_state.items():
            for thread_key in thread_keys_by_id.get(thread_id, []):
                thread_index[thread_key]["reply_state"] = state
        return _finalize_channel_rollup(channels)

    # Legacy fallback for event-only databases created before channel_messages
    # existed. New rollups never depend on this path.
    fallback_threads = query_sqlite_rows_fn(
        db_path,
        """
        SELECT
          thread_id,
          MIN(ts) AS first_event_ts,
          MAX(ts) AS last_event_ts,
          COUNT(event_id) AS event_count
        FROM channel_events
        GROUP BY thread_id
        ORDER BY thread_id
        """,
    )
    if not fallback_threads:
        return _finalize_channel_rollup(channels)

    threads: list[dict[str, Any]] = []
    for row in fallback_threads:
        thread_id = row.get("thread_id")
        if not isinstance(thread_id, str):
            continue
        threads.append({
            "thread_id": thread_id,
            "first_event_ts": row.get("first_event_ts"),
            "last_event_ts": row.get("last_event_ts"),
            "event_count": int(row.get("event_count") or 0),
            "agents": [
                agent_row["agent"]
                for agent_row in query_sqlite_rows_fn(
                    db_path,
                    """
                    SELECT DISTINCT json_extract(payload_json, '$.agent') AS agent
                    FROM channel_events
                    WHERE thread_id = ?
                      AND event = 'reply_started'
                      AND json_extract(payload_json, '$.agent') IS NOT NULL
                    ORDER BY agent ASC
                    """,
                    (thread_id,),
                )
                if isinstance(agent_row.get("agent"), str)
            ],
        })

    return _finalize_channel_rollup(
        {
            "all-threads": {
                "name": "all-threads",
                "created_at": None,
                "threads": threads,
            }
        }
    )


def build_channel_events_payload(
    thread_id: str,
    read_channel_events_fn: Callable[..., list[dict[str, Any]]],
    since_event_id: int = 0,
) -> dict[str, Any]:
    events_raw = read_channel_events_fn(thread_id, after_event_id=since_event_id)
    events: list[dict[str, Any]] = []
    next_since_event_id = since_event_id

    for event in events_raw:
        event_id = int(event.get("_event_id", 0))
        payload = dict(event)
        payload.pop("_event_id", None)
        payload.pop("thread_id", None)
        payload["event_id"] = event_id
        events.append(payload)
        next_since_event_id = max(next_since_event_id, event_id)

    return {
        "thread_id": thread_id,
        "events": events,
        "next_since_event_id": next_since_event_id,
    }


def build_channel_timeline_payload(
    repo_root: Path,
    channel_name: str,
    *,
    resolve_bridge_db_path_fn: Callable[[Path], Path],
    query_sqlite_rows_fn: Callable[..., list[dict[str, Any]]],
    since_event_id: int = 0,
    since_ts: str | None = None,
) -> dict[str, Any]:
    """Return channel events enriched with posted message bodies.

    ``channel_events`` stores event metadata while ``channel_messages`` stores
    prose. The browser timeline needs both, but writes must still flow through
    the bridge primitive, so this read path joins them at render time.
    """
    db_path = resolve_bridge_db_path_fn(repo_root)
    params: list[Any] = [channel_name, since_event_id]
    since_clause = ""
    if since_ts:
        since_clause = "AND ce.ts > ?"
        params.append(since_ts)

    rows = query_sqlite_rows_fn(
        db_path,
        f"""
        SELECT
          ce.event_id,
          ce.delivery_id,
          ce.thread_id,
          ce.event,
          ce.payload_json,
          ce.ts,
          posted.message_id AS message_id,
          posted.from_agent AS message_from_agent,
          posted.from_model AS message_from_model,
          posted.kind AS message_kind,
          posted.body AS message_body,
          posted.created_at AS message_created_at
        FROM channel_events ce
        LEFT JOIN channel_messages posted
          ON posted.message_id = json_extract(ce.payload_json, '$.message_id')
        WHERE EXISTS (
          SELECT 1
          FROM channel_messages cm
          WHERE cm.channel = ?
            AND cm.thread_id = ce.thread_id
        )
          AND ce.event_id > ?
          {since_clause}
        ORDER BY ce.event_id ASC
        """,
        tuple(params),
        limit=10000,
    )

    events: list[dict[str, Any]] = []
    next_since_event_id = since_event_id
    for row in rows:
        event_id = int(row.get("event_id") or 0)
        payload_raw = row.get("payload_json")
        try:
            payload = _json.loads(payload_raw) if payload_raw else {}
        except _json.JSONDecodeError:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}

        event = {
            "event_id": event_id,
            "delivery_id": row.get("delivery_id"),
            "thread_id": row.get("thread_id"),
            "event": row.get("event"),
            "ts": row.get("ts"),
            **payload,
        }
        if row.get("message_id"):
            event.update(
                {
                    "message_id": row.get("message_id"),
                    "from_agent": row.get("message_from_agent"),
                    "from_model": row.get("message_from_model"),
                    "kind": row.get("message_kind"),
                    "body": row.get("message_body"),
                    "created_at": row.get("message_created_at"),
                }
            )
        events.append(event)
        next_since_event_id = max(next_since_event_id, event_id)

    return {
        "channel": channel_name,
        "events": events,
        "count": len(events),
        "next_since_event_id": next_since_event_id,
    }


def channel_exists_in_db(
    repo_root: Path,
    channel_name: str,
    *,
    resolve_bridge_db_path_fn: Callable[[Path], Path],
    query_sqlite_rows_fn: Callable[..., list[dict[str, Any]]],
) -> bool:
    rows = query_sqlite_rows_fn(
        resolve_bridge_db_path_fn(repo_root),
        "SELECT 1 AS found FROM channels WHERE name = ? LIMIT 1",
        (channel_name,),
    )
    return bool(rows)


def render_channels_chat_html(
    selected_channel: str | None,
    *,
    top_nav_css: str,
    render_top_nav_fn: Callable[[str], str],
) -> str:
    selected_js = _safe_json_for_script(selected_channel)
    title_channel = selected_channel or "Channels"
    escaped_title = _html.escape(title_channel, quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title} - Agent Deliberations</title>
  <style>
    :root{{--bg:#101112;--panel:#17191b;--panel-2:#202326;--line:#30343a;--text:#f3f4f2;--muted:#9ca3a3;--teal:#3dd6c6;--orange:#f59e0b;--blue:#69a7ff;--green:#55d17f;--violet:#b99cff;--red:#fb7185;--topnav-h:45px}}
    *{{box-sizing:border-box;margin:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--text);line-height:1.45;-webkit-font-smoothing:antialiased}}
{top_nav_css}
    .channels-app{{height:calc(100vh - var(--topnav-h, 45px));display:grid;grid-template-columns:240px minmax(0,1fr);border-top:1px solid var(--line)}}
    .channels-sidebar{{background:#121416;border-right:1px solid var(--line);padding:14px 10px;overflow:auto}}
    .sidebar-title{{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);padding:4px 10px 10px}}
    .channel-link{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;color:var(--text);text-decoration:none;border-radius:6px;padding:7px 10px;font-size:13px;min-height:34px}}
    .channel-link:hover,.channel-link.active{{background:var(--panel-2)}}
    .channel-name{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
    .unread-badge{{display:none;min-width:18px;padding:1px 6px;border-radius:999px;background:var(--orange);color:#16120a;font-size:11px;font-weight:800;text-align:center}}
    .unread-badge.visible{{display:inline-block}}
    .sidebar-meta{{font-size:11px;color:var(--muted);padding:10px}}
    .channel-main{{min-width:0;display:grid;grid-template-rows:auto minmax(0,1fr) auto;background:var(--bg)}}
    .channel-header{{border-bottom:1px solid var(--line);background:rgba(23,25,27,.96);padding:14px 18px}}
    .channel-header h1{{font-size:18px;font-weight:750;letter-spacing:0}}
    .channel-header p{{font-size:12px;color:var(--muted);margin-top:2px}}
    .messages{{overflow:auto;padding:16px 18px 28px;scrollbar-gutter:stable}}
    .empty{{color:var(--muted);font-size:13px;padding:28px 4px}}
    .event-row{{max-width:900px;margin:0 0 12px;border-left:3px solid var(--line);padding-left:10px}}
    .event-row.claude{{border-left-color:var(--blue)}}.event-row.codex{{border-left-color:var(--green)}}.event-row.gemini{{border-left-color:var(--violet)}}
    .event-row.user{{border-left-color:var(--orange);background:rgba(245,158,11,.08);padding:10px 12px;border-radius:0 6px 6px 0}}
    .message-meta{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;color:var(--muted);font-size:11px;margin-bottom:4px}}
    .agent-name{{font-weight:800}}.agent-name.claude{{color:var(--blue)}}.agent-name.codex{{color:var(--green)}}.agent-name.gemini{{color:var(--violet)}}.agent-name.user{{color:var(--orange)}}
    .model-tag,.event-pill{{background:var(--panel-2);border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:10px;color:var(--muted)}}
    .message-body{{font-size:13px;white-space:pre-wrap;word-break:break-word;color:var(--text)}}
    .event-note{{color:var(--muted);font-size:12px;padding:2px 0}}
    .post-form{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;border-top:1px solid var(--line);background:var(--panel);padding:12px 18px}}
    .post-input{{width:100%;min-height:44px;max-height:150px;resize:vertical;border:1px solid var(--line);border-radius:6px;background:#0f1011;color:var(--text);padding:10px 12px;font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace}}
    .post-input:focus{{outline:2px solid rgba(61,214,198,.35);border-color:var(--teal)}}
    .post-button{{border:1px solid rgba(245,158,11,.6);background:var(--orange);color:#171207;border-radius:6px;padding:0 16px;font-size:13px;font-weight:800;cursor:pointer}}
    .post-button:disabled{{opacity:.55;cursor:not-allowed}}
    .form-status{{grid-column:1 / -1;color:var(--muted);font-size:12px;min-height:16px}}
    @media(max-width:760px){{.channels-app{{grid-template-columns:1fr;height:auto;min-height:calc(100vh - var(--topnav-h, 45px))}}.channels-sidebar{{max-height:210px;border-right:0;border-bottom:1px solid var(--line)}}.channel-main{{min-height:70vh}}}}
  </style>
</head>
<body>
{render_top_nav_fn("channels")}
<div class="channels-app" data-selected-channel="{_html.escape(selected_channel or "", quote=True)}">
  <nav class="channels-sidebar" aria-label="Channels">
    <div class="sidebar-title">Channels</div>
    <div id="channelList"></div>
    <div class="sidebar-meta" id="sidebarMeta">Loading...</div>
  </nav>
  <main class="channel-main">
    <header class="channel-header">
      <h1 id="channelTitle">Agent Deliberations</h1>
      <p><span id="channelMeta">Select a channel</span> · <span id="pollState">idle</span></p>
    </header>
    <!-- delta-render: message nodes use data-message-id and renderedMsgIds; existing nodes are never overwritten -->
    <section class="messages" id="messageList" aria-live="polite">
      <div class="empty" id="emptyState">Waiting for channel activity...</div>
    </section>
    <form class="post-form" id="postForm">
      <textarea class="post-input" id="postBody" name="body" maxlength="8000" placeholder="Post to the selected channel"></textarea>
      <button class="post-button" id="postButton" type="submit">Post</button>
      <div class="form-status" id="formStatus"></div>
    </form>
  </main>
</div>
<script>
const INITIAL_CHANNEL = {selected_js};
const DEFAULT_POLL_MS = 5000;
const TIGHT_POLL_MS = 1000;
const QUIET_RESET_MS = 30000;
let selectedChannel = INITIAL_CHANNEL;
let sinceId = 0;
let currentFetchId = 0;
let pollTimer = null;
let lastEventType = "";
let lastNewEventAt = 0;
let channels = [];
let hasBooted = false;
const renderedMsgIds = new Set();
const channelList = document.getElementById("channelList");
const messageList = document.getElementById("messageList");
const emptyState = document.getElementById("emptyState");
const postForm = document.getElementById("postForm");
const postBody = document.getElementById("postBody");
const postButton = document.getElementById("postButton");
const formStatus = document.getElementById("formStatus");
function lastVisitedKey(name){{return "kdjo_channel_lastvisited_"+name;}}
function timeAgo(iso){{if(!iso)return"no activity";const d=Math.floor((Date.now()-new Date(iso))/1000);if(d<60)return d+"s ago";if(d<3600)return Math.floor(d/60)+"m ago";if(d<86400)return Math.floor(d/3600)+"h ago";return Math.floor(d/86400)+"d ago";}}
function setText(el,value){{el.textContent=value == null ? "" : String(value);}}
function rememberVisited(name){{if(name)localStorage.setItem(lastVisitedKey(name),new Date().toISOString());}}
function computePollDelayMs(now=Date.now()){{if((lastEventType==="reply_started"||lastEventType==="heartbeat")&&lastNewEventAt&&now-lastNewEventAt<QUIET_RESET_MS)return TIGHT_POLL_MS;return DEFAULT_POLL_MS;}}
function isNearBottom(){{return messageList.scrollHeight-messageList.scrollTop-messageList.clientHeight<48;}}
function resetMessages(){{renderedMsgIds.clear();sinceId=0;lastEventType="";lastNewEventAt=0;messageList.replaceChildren(emptyState);emptyState.style.display="block";}}
function renderSidebar(){{channelList.replaceChildren();channels.forEach(ch=>{{const a=document.createElement("a");a.className="channel-link"+(ch.name===selectedChannel?" active":"");a.href="/channels/"+encodeURIComponent(ch.name);a.dataset.channelName=ch.name;const name=document.createElement("span");name.className="channel-name";name.textContent="# "+ch.name;const badge=document.createElement("span");badge.className="unread-badge";badge.dataset.unreadFor=ch.name;a.append(name,badge);a.addEventListener("click",()=>rememberVisited(ch.name));channelList.appendChild(a);}});document.getElementById("sidebarMeta").textContent=channels.length+" channel"+(channels.length===1?"":"s");updateUnreadBadges();}}
function updateUnreadBadges(){{channels.forEach(ch=>{{const badge=channelList.querySelector(`[data-unread-for="${{CSS.escape(ch.name)}}"]`);if(!badge)return;const last=localStorage.getItem(lastVisitedKey(ch.name));if(ch.name===selectedChannel||!ch.last_event_ts||last&&new Date(ch.last_event_ts)<=new Date(last)){{badge.classList.remove("visible");badge.textContent="";return;}}if(!last){{badge.textContent=String(ch.event_count||1);badge.classList.add("visible");return;}}fetch("/api/channel/"+encodeURIComponent(ch.name)+"/events?since_ts="+encodeURIComponent(last)).then(r=>r.json()).then(data=>{{const n=(data.events||[]).length;if(n>0){{badge.textContent=String(n);badge.classList.add("visible");}}else{{badge.classList.remove("visible");badge.textContent="";}}}}).catch(()=>{{badge.textContent="!";badge.classList.add("visible");}});}});}}
function appendMeta(parent,ev,agent){{const meta=document.createElement("div");meta.className="message-meta";const name=document.createElement("span");name.className="agent-name "+agent;name.textContent=agent==="user"?"👤 user":agent;meta.appendChild(name);if(ev.from_model||ev.model){{const model=document.createElement("span");model.className="model-tag";model.textContent=ev.from_model||ev.model;meta.appendChild(model);}}const stamp=document.createElement("span");stamp.textContent=(ev.ts||ev.created_at||"").slice(0,19).replace("T"," ");meta.appendChild(stamp);parent.appendChild(meta);}}
function appendBody(parent,body){{const div=document.createElement("div");div.className="message-body";div.textContent=body||"";parent.appendChild(div);}}
function appendNote(ev,text,cls=""){{const key=String(ev.event_id||"")+"-"+String(ev.ts||"");if(renderedMsgIds.has(key))return;renderedMsgIds.add(key);const row=document.createElement("div");row.className="event-row "+cls;row.dataset.eventId=String(ev.event_id||"");const note=document.createElement("div");note.className="event-note";note.textContent=text;row.appendChild(note);messageList.appendChild(row);}}
function appendMessage(ev){{const key=ev.message_id||String(ev.event_id||"")+"-"+String(ev.ts||"");if(renderedMsgIds.has(key))return;renderedMsgIds.add(key);const agent=(ev.from_agent||ev.agent||"unknown").toLowerCase();const cls=["claude","codex","gemini","user"].includes(agent)?agent:"";const row=document.createElement("article");row.className="event-row "+cls;row.dataset.messageId=key;row.dataset.eventId=String(ev.event_id||"");appendMeta(row,ev,agent);appendBody(row,ev.body||"");messageList.appendChild(row);}}
function renderEvent(ev){{if(emptyState)emptyState.style.display="none";if(ev.event==="message_posted"&&ev.body!==undefined)appendMessage(ev);else if(ev.event==="reply_complete")appendMessage(ev);else if(ev.event==="reply_started")appendNote(ev,(ev.agent||"agent")+" started replying","");else if(ev.event==="heartbeat")appendNote(ev,"heartbeat elapsed="+(ev.elapsed_s||"?")+"s","");else if(ev.event==="delivery_failed")appendNote(ev,"delivery failed "+(ev.error_kind||""),"");else if(ev.event==="delivery_delivered")appendNote(ev,"delivered "+(ev.delivery_id||""),"");else if(ev.event==="model_cascade")appendNote(ev,"cascade "+(ev.from||"")+" -> "+(ev.to||""),"");}}
function applyEvents(events,nextSince){{if(!events.length)return;const stick=isNearBottom();events.forEach(renderEvent);sinceId=Math.max(sinceId,nextSince||sinceId);lastEventType=events[events.length-1].event||"";lastNewEventAt=Date.now();document.getElementById("channelMeta").textContent=events.length+" new event"+(events.length===1?"":"s")+" · last "+timeAgo(events[events.length-1].ts);if(stick)messageList.scrollTop=messageList.scrollHeight;rememberVisited(selectedChannel);updateUnreadBadges();}}
function schedulePoll(){{clearTimeout(pollTimer);pollTimer=setTimeout(poll,computePollDelayMs());document.getElementById("pollState").textContent="next poll "+computePollDelayMs()/1000+"s";}}
function poll(){{if(!selectedChannel){{schedulePoll();return;}}const myFetchId=++currentFetchId;fetch("/api/channel/"+encodeURIComponent(selectedChannel)+"/events?since_event_id="+sinceId).then(r=>r.json()).then(data=>{{if(myFetchId!==currentFetchId)return;applyEvents(data.events||[],data.next_since_event_id);}}).catch(()=>{{if(myFetchId===currentFetchId)document.getElementById("pollState").textContent="API unavailable";}}).finally(()=>{{if(myFetchId===currentFetchId)schedulePoll();}});}}
function chooseChannel(name){{selectedChannel=name;if(!selectedChannel&&channels.length)selectedChannel=channels[0].name;document.getElementById("channelTitle").textContent=selectedChannel?"# "+selectedChannel:"Agent Deliberations";postButton.disabled=!selectedChannel;resetMessages();rememberVisited(selectedChannel);renderSidebar();poll();}}
function loadChannels(){{fetch("/api/channels").then(r=>r.json()).then(data=>{{channels=data.channels||[];if(selectedChannel&&!channels.some(ch=>ch.name===selectedChannel))channels.unshift({{name:selectedChannel,event_count:0,last_event_ts:null,threads:[]}});renderSidebar();if(!hasBooted){{hasBooted=true;chooseChannel(selectedChannel);}}}}).catch(()=>{{document.getElementById("sidebarMeta").textContent="API unavailable";}});}}
postForm.addEventListener("submit",ev=>{{ev.preventDefault();if(!selectedChannel)return;const body=postBody.value;if(!body.trim()){{formStatus.textContent="Body is required.";return;}}postButton.disabled=true;formStatus.textContent="Posting...";fetch("/api/channel/"+encodeURIComponent(selectedChannel)+"/post",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{body,from_agent:"user"}})}}).then(async r=>{{const data=await r.json();if(!r.ok)throw new Error(data.error||"post failed");postBody.value="";formStatus.textContent="Posted.";rememberVisited(selectedChannel);poll();loadChannels();}}).catch(err=>{{formStatus.textContent=err.message;}}).finally(()=>{{postButton.disabled=false;postBody.focus();}});}});
loadChannels();
</script>
</body></html>"""


def render_channels_index_html(
    *,
    top_nav_css: str,
    render_top_nav_fn: Callable[[str], str],
) -> str:
    return render_channels_chat_html(
        None,
        top_nav_css=top_nav_css,
        render_top_nav_fn=render_top_nav_fn,
    )


def render_channel_thread_html(
    channel_name: str,
    *,
    top_nav_css: str,
    render_top_nav_fn: Callable[[str], str],
) -> str:
    return render_channels_chat_html(
        channel_name,
        top_nav_css=top_nav_css,
        render_top_nav_fn=render_top_nav_fn,
    )


def _parse_post_body(body_bytes: bytes | None, content_type: str) -> dict[str, Any]:
    raw = (body_bytes or b"").decode("utf-8", errors="replace")
    if "application/json" in content_type:
        try:
            payload = _json.loads(raw or "{}")
        except _json.JSONDecodeError as exc:
            raise ValueError("invalid_json") from exc
        if not isinstance(payload, dict):
            raise ValueError("invalid_json")
        return payload

    parsed = parse_qs(raw, keep_blank_values=True)
    payload: dict[str, Any] = {}
    for key, values in parsed.items():
        if key == "to":
            payload[key] = values
        else:
            payload[key] = values[-1] if values else ""
    return payload


def _parse_to_agents(value: Any) -> list[str] | None:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        return [agent.strip() for agent in value.split(",") if agent.strip()]
    if isinstance(value, list):
        agents: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                agents.append(item.strip())
        return agents
    raise ValueError("invalid_to")


def route_channel_post_request(
    path: str,
    *,
    body_bytes: bytes | None,
    content_type: str,
    bridge_db_path: Path | None = None,
) -> RouteResponse | None:
    if not (path.startswith("/api/channel/") and path.endswith("/post")):
        return None

    raw_channel = path[len("/api/channel/") : -len("/post")]
    channel_name = unquote(raw_channel).strip("/")
    if not channel_name:
        return _json_response(400, {"ok": False, "error": "missing_channel"})

    try:
        payload = _parse_post_body(body_bytes, content_type)
        body_value = payload.get("body")
        body = body_value if isinstance(body_value, str) else ""
        if not body.strip():
            return _json_response(400, {"ok": False, "error": "body_required"})
        if len(body) > 8000:
            return _json_response(400, {"ok": False, "error": "body_too_long"})
        from_agent = payload.get("from_agent", "user")
        if from_agent != "user":
            return _json_response(400, {"ok": False, "error": "invalid_from_agent"})
        to_agents = _parse_to_agents(payload.get("to"))
    except ValueError as exc:
        return _json_response(400, {"ok": False, "error": str(exc)})

    try:
        from ai_agent_bridge import _db as bridge_db
        from ai_agent_bridge._channels import get_channel, post

        with _POST_DB_LOCK:
            old_db_path = bridge_db.DB_PATH
            if bridge_db_path is not None:
                bridge_db.DB_PATH = bridge_db_path
            try:
                if get_channel(channel_name) is None:
                    return _json_response(404, {"ok": False, "error": "channel_not_found"})
                result = post(
                    channel=channel_name,
                    from_agent="user",
                    body=body,
                    to_agents=to_agents,
                    auto_snapshot=False,
                    context_rev_shared="",
                    context_rev_channel="",
                    monitor_state_snapshot=None,
                )
            finally:
                bridge_db.DB_PATH = old_db_path
    except Exception as exc:  # noqa: BLE001 - endpoint contract requires JSON 500
        return _json_response(
            500,
            {
                "ok": False,
                "error": "internal_error",
                "exception": type(exc).__name__,
                "message": str(exc),
            },
        )

    return _json_response(
        200,
        {
            "ok": True,
            "message_id": result.get("message_id"),
            "thread_id": result.get("thread_id"),
            "ts": result.get("created_at"),
        },
    )


def route_channel_page_request(
    path: str,
    *,
    top_nav_css: str,
    render_top_nav_fn: Callable[[str], str],
) -> RouteResponse | None:
    if path == "/channels":
        return 200, render_channels_index_html(
            top_nav_css=top_nav_css,
            render_top_nav_fn=render_top_nav_fn,
        ), "text/html; charset=utf-8"
    if path.startswith("/channels/"):
        raw_tid = unquote(path[len("/channels/"):]).strip("/")
        return 200, render_channel_thread_html(
            raw_tid,
            top_nav_css=top_nav_css,
            render_top_nav_fn=render_top_nav_fn,
        ), "text/html; charset=utf-8"
    return None


def route_channel_api_request(
    repo_root: Path,
    path: str,
    query: dict[str, list[str]],
    *,
    resolve_bridge_db_path_fn: Callable[[Path], Path],
    query_sqlite_rows_fn: Callable[..., list[dict[str, Any]]],
) -> RouteResponse | None:
    if path == "/api/channels":
        from ai_agent_bridge._channels import list_channels
        return (
            200,
            build_channel_threads_index(
                repo_root,
                list_channels_fn=list_channels,
                resolve_bridge_db_path_fn=resolve_bridge_db_path_fn,
                query_sqlite_rows_fn=query_sqlite_rows_fn,
            ),
            "application/json; charset=utf-8",
        )
    if path.startswith("/api/channel/") and path.endswith("/events"):
        raw_name = path[len("/api/channel/") : -len("/events")]
        name = unquote(raw_name).strip("/")
        if not name:
            return 400, {"error": "missing_channel_or_thread"}, "application/json; charset=utf-8"
        try:
            since_raw = query.get("since_event_id", ["0"])[0]
            if since_raw is None:
                raise TypeError
            since_event_id = int(since_raw)
        except (TypeError, ValueError):
            return 400, {"error": "invalid_since_event_id"}, "application/json; charset=utf-8"
        since_ts = query.get("since_ts", [None])[0]
        if channel_exists_in_db(
            repo_root,
            name,
            resolve_bridge_db_path_fn=resolve_bridge_db_path_fn,
            query_sqlite_rows_fn=query_sqlite_rows_fn,
        ):
            return (
                200,
                build_channel_timeline_payload(
                    repo_root,
                    name,
                    resolve_bridge_db_path_fn=resolve_bridge_db_path_fn,
                    query_sqlite_rows_fn=query_sqlite_rows_fn,
                    since_event_id=since_event_id,
                    since_ts=since_ts,
                ),
                "application/json; charset=utf-8",
            )
        from ai_agent_bridge._channels_watch import read_channel_events
        return (
            200,
            build_channel_events_payload(
                name,
                read_channel_events_fn=read_channel_events,
                since_event_id=since_event_id,
            ),
            "application/json; charset=utf-8",
        )
    return None
