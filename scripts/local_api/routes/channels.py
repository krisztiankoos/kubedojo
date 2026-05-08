from __future__ import annotations

import html as _html
import json as _json
from pathlib import Path
from typing import Any, Callable
from urllib.parse import unquote


RouteResponse = tuple[int, Any, str]


def build_channel_threads_index(
    repo_root: Path,
    *,
    list_channels_fn: Callable[[], list[dict[str, Any]]],
    resolve_bridge_db_path_fn: Callable[[Path], Path],
    query_sqlite_rows_fn: Callable[..., list[dict[str, Any]]],
) -> dict[str, Any]:
    """Build thread rollups for deliberation channels from ``channel_events``."""
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
          ce.thread_id AS thread_id,
          MIN(ce.ts) AS first_event_ts,
          MAX(ce.ts) AS last_event_ts,
          COUNT(ce.event_id) AS event_count
        FROM channel_events ce
        INNER JOIN channel_messages cm
          ON cm.thread_id = ce.thread_id
        GROUP BY cm.channel, ce.thread_id
        ORDER BY cm.channel, ce.thread_id
        """,
    )

    if thread_rows:
        for row in thread_rows:
            channel = row.get("channel")
            if not isinstance(channel, str):
                continue

            thread_id = row.get("thread_id")
            if not isinstance(thread_id, str):
                continue

            thread_entry = {
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
            }

            entry = channels.setdefault(channel, {"name": channel, "created_at": None, "threads": []})
            entry["threads"].append(thread_entry)

        return {"channels": list(channels.values())}

    # TODO: per-channel grouping when channels↔threads link is added
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
        return {"channels": list(channels.values())}

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

    return {
        "channels": [
            {
                "name": "all-threads",
                "created_at": None,
                "threads": threads,
            }
        ]
    }


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


def render_channels_index_html(*, top_nav_css: str, render_top_nav_fn: Callable[[str], str]) -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Deliberations</title>
  <style>
    :root{--bg:#0a0f1a;--surface-0:#111827;--surface-1:#1a2332;--surface-2:#1f2b3d;--text:#e5e7eb;--text-dim:#6b7280;--accent:#38bdf8;--green:#4ade80;--border:rgba(255,255,255,0.06);--radius:12px;--radius-sm:8px}
    *{box-sizing:border-box;margin:0}
    body{font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;background:var(--bg);color:var(--text);line-height:1.5;-webkit-font-smoothing:antialiased}
""" + top_nav_css + """
    .hdr{background:linear-gradient(180deg,rgba(17,24,39,.95),rgba(10,15,26,.98));border-bottom:1px solid var(--border);padding:20px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:var(--topnav-h, 45px);z-index:50;backdrop-filter:blur(12px)}
    .hdr h1{font-size:18px;font-weight:700;letter-spacing:-.02em}
    .hdr p{font-size:12px;color:var(--text-dim);margin-top:2px}
    .btn{background:var(--surface-1);color:var(--text);border:1px solid var(--border);padding:6px 14px;border-radius:var(--radius-sm);font-size:13px;font-weight:500;cursor:pointer;transition:background .15s}
    .btn:hover{background:var(--surface-2)}
    .main{max-width:1200px;margin:0 auto;padding:24px}
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
    a.card{background:var(--surface-0);border:1px solid var(--border);border-radius:var(--radius);padding:20px;text-decoration:none;color:var(--text);display:block;transition:border-color .15s,background .15s}
    a.card:hover{border-color:var(--accent);background:var(--surface-1)}
    .card-ch{font-size:11px;color:var(--accent);text-transform:uppercase;letter-spacing:.06em;font-weight:600;margin-bottom:6px}
    .card-tid{font-size:12px;color:var(--text-dim);font-family:monospace;margin-bottom:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .card-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
    .badge{display:inline-flex;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600}
    .bc{background:rgba(56,189,248,.1);color:#38bdf8}.bcl{background:rgba(56,189,248,.15);color:#38bdf8}
    .bco{background:rgba(74,222,128,.15);color:#4ade80}.bg{background:rgba(167,139,250,.15);color:#a78bfa}
    .bu{background:rgba(251,191,36,.15);color:#fbbf24}
    .card-ts{font-size:11px;color:var(--text-dim);margin-top:8px}
    .empty{text-align:center;color:var(--text-dim);padding:60px 0;font-size:14px}
    .dot{width:6px;height:6px;border-radius:50%;background:var(--green);display:inline-block;animation:pulse 2s ease-in-out infinite}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
    .status{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--text-dim)}
  </style>
</head>
<body>
""" + render_top_nav_fn("channels") + """
<div class="hdr">
  <div><h1>Agent Deliberations</h1><p>ab discuss live transcripts &#8212; claude / codex / gemini</p></div>
  <div style="display:flex;align-items:center;gap:12px">
    <span class="status"><span class="dot"></span>&nbsp;<span id="st">Loading&#8230;</span></span>
    <button class="btn" onclick="load()">Refresh</button>
  </div>
</div>
<div class="main"><div id="grid" class="grid"></div></div>
<script>
const BADGE = {claude:"bcl",codex:"bco",gemini:"bg",user:"bu"};
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
function timeAgo(iso){if(!iso)return"";const d=Math.floor((Date.now()-new Date(iso))/1000);if(d<60)return d+"s ago";if(d<3600)return Math.floor(d/60)+"m ago";if(d<86400)return Math.floor(d/3600)+"h ago";return Math.floor(d/86400)+"d ago";}
function agentBadge(a){const c=BADGE[a]||"bc";return`<span class="badge ${c}">${esc(a)}</span>`;}
function render(data){
  const channels=data.channels||[];
  const total=channels.reduce((n,c)=>n+c.threads.length,0);
  document.getElementById("st").textContent=total+" thread"+(total===1?"":"s");
  if(!total){document.getElementById("grid").innerHTML='<p class="empty">No deliberation threads yet.<br>Start one with <code>ab discuss &lt;channel&gt;</code>.</p>';return;}
  const cards=channels.flatMap(c=>c.threads.map(t=>{
    const agents=(t.agents||[]).map(agentBadge).join("");
    return`<a class="card" href="/channels/${encodeURIComponent(t.thread_id)}"><div class="card-ch">${esc(c.name)}</div><div class="card-tid" title="${esc(t.thread_id)}">${esc(t.thread_id)}</div><div class="card-meta"><span class="badge bc">${esc(t.event_count)} events</span>${agents}</div><div class="card-ts">last activity: ${timeAgo(t.last_event_ts)}</div></a>`;
  }));
  document.getElementById("grid").innerHTML=cards.join("");
}
function load(){fetch("/api/channels").then(r=>r.json()).then(render).catch(()=>{document.getElementById("st").textContent="API unavailable";});}
load();setInterval(load,30000);
</script>
</body></html>"""


def render_channel_thread_html(
    thread_id: str,
    *,
    top_nav_css: str,
    render_top_nav_fn: Callable[[str], str],
) -> str:
    tid_js = _json.dumps(thread_id)
    tid_short = thread_id[:20] + ("…" if len(thread_id) > 20 else "")
    escaped_tid = _html.escape(thread_id, quote=True)
    escaped_tid_short = _html.escape(tid_short, quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Thread {escaped_tid_short}</title>
  <style>
    :root{{--bg:#0a0f1a;--surface-0:#111827;--surface-1:#1a2332;--surface-2:#1f2b3d;--text:#e5e7eb;--text-dim:#6b7280;--border:rgba(255,255,255,0.06);--radius-sm:8px}}
    *{{box-sizing:border-box;margin:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif;background:var(--bg);color:var(--text);line-height:1.5;-webkit-font-smoothing:antialiased}}
{top_nav_css}
    .hdr{{background:linear-gradient(180deg,rgba(17,24,39,.95),rgba(10,15,26,.98));border-bottom:1px solid var(--border);padding:16px 24px;position:sticky;top:var(--topnav-h, 45px);z-index:50;backdrop-filter:blur(12px)}}
    .hdr-row{{display:flex;align-items:center;gap:12px;flex-wrap:wrap}}
    .back{{color:#38bdf8;text-decoration:none;font-size:13px}}.back:hover{{text-decoration:underline}}
    .tid{{font-size:13px;font-weight:600;font-family:monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:420px;color:#e5e7eb}}
    .meta{{font-size:11px;color:var(--text-dim);margin-top:4px}}
    .feed{{max-width:860px;margin:24px auto;padding:0 24px 80px}}
    .bubble{{margin-bottom:16px;max-width:720px}}
    .bubble.claude{{border-left:3px solid #38bdf8}}.bubble.codex{{border-left:3px solid #4ade80}}
    .bubble.gemini{{border-left:3px solid #a78bfa}}.bubble.user{{border-left:3px solid #fbbf24}}
    .bi{{background:var(--surface-0);border:1px solid var(--border);border-left:none;border-radius:0 var(--radius-sm) var(--radius-sm) 0;padding:12px 16px}}
    .bm{{font-size:11px;color:var(--text-dim);margin-bottom:6px;display:flex;align-items:center;gap:8px}}
    .an{{font-weight:700}}.an.claude{{color:#38bdf8}}.an.codex{{color:#4ade80}}.an.gemini{{color:#a78bfa}}.an.user{{color:#fbbf24}}
    .mt{{background:var(--surface-2);padding:1px 6px;border-radius:4px;font-size:10px;font-family:monospace}}
    .bb{{font-size:13px;white-space:pre-wrap;word-break:break-word}}
    .vote-agree{{background:rgba(74,222,128,.2);color:#4ade80;padding:1px 6px;border-radius:4px;font-weight:700}}
    .vote-option{{background:rgba(56,189,248,.2);color:#38bdf8;padding:1px 6px;border-radius:4px;font-weight:700}}
    .vote-defer{{background:rgba(156,163,175,.2);color:#9ca3af;padding:1px 6px;border-radius:4px;font-weight:700}}
    .hb{{font-size:11px;color:var(--text-dim);padding:3px 0 6px 16px}}
    .pill{{display:inline-flex;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:500}}
    .p-ok{{background:rgba(74,222,128,.1);color:#4ade80}}.p-fail{{background:rgba(248,113,113,.1);color:#f87171}}.p-info{{background:rgba(56,189,248,.1);color:#38bdf8}}
    .empty{{text-align:center;color:var(--text-dim);padding:60px 0;font-size:14px}}
  </style>
</head>
<body>
{render_top_nav_fn("channels")}
<div class="hdr">
  <div class="hdr-row"><a class="back" href="/channels">&larr; Channels</a><div class="tid" title="{escaped_tid}">{escaped_tid}</div></div>
  <div class="meta"><span id="ec">0 events</span> &middot; <span id="lu">connecting&#8230;</span></div>
</div>
<div class="feed" id="feed"><div class="empty" id="emp">Waiting for events&#8230;</div></div>
<script>
const TID={tid_js};
let sinceId=0,atBottom=true,hbEl=null,hbN=0,totalEvents=0;
const feed=document.getElementById("feed");
feed.addEventListener("scroll",()=>{{atBottom=(feed.scrollHeight-feed.scrollTop-feed.clientHeight)<40;}});
function esc(s){{return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}}
function timeAgo(iso){{if(!iso)return"";const d=Math.floor((Date.now()-new Date(iso))/1000);if(d<60)return d+"s ago";if(d<3600)return Math.floor(d/60)+"m ago";return Math.floor(d/3600)+"h ago";}}
function hiliteVotes(t){{return t.replace(/\\[(AGREE)\\]/g,'<span class="vote-agree">[$1]</span>').replace(/\\[(OPTION [A-Z0-9]+)\\]/g,'<span class="vote-option">[$1]</span>').replace(/\\[(DEFER)\\]/g,'<span class="vote-defer">[$1]</span>');}}
function pill(cls,html){{return`<div style="padding:2px 0 6px 16px"><span class="pill ${{cls}}">${{html}}</span></div>`;}}
function renderEv(ev){{
  const e=ev.event;
  if(e==="heartbeat"){{
    if(!hbEl){{hbEl=document.createElement("div");hbEl.className="hb";hbN=0;feed.appendChild(hbEl);}}
    hbN++;hbEl.textContent="(♥ "+hbN+" heartbeat"+(hbN>1?"s":"")+" elapsed="+(ev.elapsed_s||"?")+"s)";
    return;
  }}
  hbEl=null;
  const el=document.createElement("div");
  if(e==="delivery_delivered"){{el.innerHTML=pill("p-ok","&#10003; delivered "+esc(ev.delivery_id||""));}}
  else if(e==="delivery_failed"){{el.innerHTML=pill("p-fail","&#10007; failed "+esc(ev.error_kind||""));}}
  else if(e==="model_cascade"){{el.innerHTML=pill("p-info","cascade "+esc(ev.from||"")+" &rarr; "+esc(ev.to||""));}}
  else if(e==="reply_started"){{el.innerHTML=pill("p-info","&#8635; "+esc(ev.agent||"?")+" started");}}
  else if(e==="reply_complete"){{
    const a=ev.agent||"unknown";
    const ac=["claude","codex","gemini","user"].includes(a)?a:"";
    const body=ev.body?hiliteVotes(esc(ev.body)):'<em style="color:var(--text-dim)">no body</em>';
    el.className="bubble "+ac;
    el.innerHTML=`<div class="bi"><div class="bm"><span class="an ${{ac}}">${{esc(a)}}</span>${{ev.model?`<span class="mt">${{esc(ev.model)}}</span>`:""}}
      <span>${{esc((ev.ts||"").slice(0,19).replace("T"," "))}}</span></div><div class="bb">${{body}}</div></div>`;
  }} else {{return;}}
  feed.appendChild(el);
}}
function poll(){{
  fetch("/api/channel/"+encodeURIComponent(TID)+"/events?since_event_id="+sinceId)
    .then(r=>r.json()).then(data=>{{
      const evs=data.events||[];
      if(evs.length){{
        const emp=document.getElementById("emp");if(emp)emp.remove();
        evs.forEach(renderEv);
        sinceId=data.next_since_event_id||sinceId;
        totalEvents+=evs.length;
        document.getElementById("ec").textContent=totalEvents+" event"+(totalEvents===1?"":"s");
        document.getElementById("lu").textContent="updated "+timeAgo(evs[evs.length-1].ts);
        if(atBottom)feed.scrollTop=feed.scrollHeight;
      }}
    }}).catch(()=>{{document.getElementById("lu").textContent="API unavailable";}});
  setTimeout(poll,2000);
}}
poll();
</script>
</body></html>"""


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
        raw_thread_id = path[len("/api/channel/") : -len("/events")]
        thread_id = unquote(raw_thread_id).strip("/")
        if not thread_id:
            return 400, {"error": "missing_thread_id"}, "application/json; charset=utf-8"
        try:
            since_raw = query.get("since_event_id", ["0"])[0]
            if since_raw is None:
                raise TypeError
            since_event_id = int(since_raw)
        except (TypeError, ValueError):
            return 400, {"error": "invalid_since_event_id"}, "application/json; charset=utf-8"
        from ai_agent_bridge._channels_watch import read_channel_events
        return (
            200,
            build_channel_events_payload(
                thread_id,
                read_channel_events_fn=read_channel_events,
                since_event_id=since_event_id,
            ),
            "application/json; charset=utf-8",
        )
    return None
