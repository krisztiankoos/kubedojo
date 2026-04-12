# Agent Bridge — Channel Communication

The agent bridge is how Claude, Gemini, and Codex (and you, the
human) communicate across invocations. The new **channel bridge**
(added in #1190) replaces the old 1:1 `ask-*` pattern with topic-
scoped channels, pinned context, and character-budget history
truncation — the token waste from re-explaining project setup on
every delegation drops from ~15KB to ~6KB per post.

> **Note on the legacy `ask-*` commands.** They still work and are
> the simplest way to fire a one-shot delegation with no history
> tracking. They're **not deprecated** and won't be. Channels are
> the right primitive for sustained, topic-scoped conversations;
> `ask-*` is the right primitive for one-off questions. Use both.

## Mental model

A **channel** is a topic — `pipeline`, `content`, `architecture`,
`reviews`, `shared`. Each channel has:

- A **pinned context** file at `docs/agent-channels/{channel}/context.md`
  that holds stable project state (rules, conventions, file paths).
  Auto-prepended to every post.
- A **message history** in SQLite (`channel_messages` table). Replies
  link to parents via `parent_id`; all messages in a thread share a
  `thread_id`.
- An **include chain** — channel A can include channel B, so posts
  to A also carry B's pinned context. The `shared` channel is
  typically included by everything.
- A **subscribers** list — the default recipients for broadcast posts.

A **post** is a message from one agent to zero or more others. It
captures, at post-time:

- The sha256 of every context.md file seen
- A snapshot of the Monitor API project state (`/api/state/summary`)
- The assembled prompt with history truncated to a character budget
- A delivery row per recipient (separate from the message — delivery
  is an outbound state machine, replies are new messages with parent_id)

A **reply** is just a new post with `parent_id` set. Replies inherit
the thread_id and get `round_index = parent.round_index + 1`.

## CLI quick reference

```bash
# Channel management
ab channel new pipeline --include shared --agents claude,gemini,codex
ab channel list
ab channel info pipeline
ab channel context pipeline --edit     # opens $EDITOR on context.md
ab channel tail pipeline -n 20         # last 20 messages
ab channel tail pipeline --thread ABC  # full thread

# Posting (short + long form)
ab p pipeline gemini "quick question about X"
ab post pipeline "full form with --to options" --to gemini,codex
ab post pipeline "reply" --parent MESSAGE_ID

# Multi-agent discussion (B.4)
ab discuss architecture "should we refactor X?" --with claude,gemini,codex --max-rounds 2
```

## When to use channels vs `ask-*`

| Situation | Use |
|---|---|
| One-off question, no history needed | `ask-claude/gemini/codex` |
| Sustained discussion on a topic | `ab post` to a channel |
| Need a 2-3 agent debate on a design | `ab discuss` |
| Sharing context across many delegations | Pin it in `docs/agent-channels/{topic}/context.md` |
| Code review with adversarial feedback | `ab post reviews ...` |
| Want the post visible in the dashboard | Channels only (the legacy `messages` table has its own UI) |

## The hygiene rule

**Nothing commits or merges without adversarial review from another
agent.** Per channel conventions:

1. Write code → stage with `git add`
2. `git diff --cached > /tmp/diff.txt`
3. `ab post reviews "Review request for #NNN" --to gemini` (or ask-gemini with the diff attached)
4. Apply feedback or argue back in writing
5. Commit only after the review is CLEAN or BLOCKING is resolved
6. Commit message includes `Reviewed-By: gemini-3.1-pro-preview (task-id)` trailer

This rule is non-negotiable. Bypassing it was the #1 reason review
quality degraded on earlier commits.

## Context file conventions

`docs/agent-channels/{channel}/context.md` should contain:

- **Stable** project knowledge: conventions, file layouts, non-negotiables
- **Reference** data that doesn't change per-commit: auth rules, API surfaces
- **Clarifying** context the agents need but you don't want to re-type

It should NOT contain:

- **Volatile** state (current sprint, recent commits) — that comes from
  the Monitor API snapshot automatically
- **Secrets** — context.md is git-tracked
- **Per-conversation** details — those belong in the post itself

Revisions to `context.md` are tracked via sha256 — every message
stores which revision it saw, so you can replay a conversation
deterministically even if the context drifts later.

## Token savings (measured on the #1190 review trail)

The channel bridge was built over four phases (B.1–B.4) with six
adversarial review rounds handed to Gemini. The review briefs were
written by hand against explicit AC lists — no bulk context paste —
which means the numbers below under-sell the savings for typical
"please review this diff" delegations that normally repeat 10–35KB
of project rules each time.

**Measured brief sizes (chars sent from claude → gemini, excluding
the ~10KB project-rules wrapper the legacy bridge prepends):**

| Review round          | Task ID                        | Brief size |
|-----------------------|--------------------------------|-----------:|
| B.3 r1 (initial)      | `bridge-b3-review`             |  6,621     |
| B.3 r2 (3 new blockers) | `bridge-b3-review-r2`        |  5,304     |
| B.3 r3 (backslash bug)| `bridge-b3-review-r3`          |  2,683     |
| B.3 r4 (CLEAN)        | `bridge-b3-review-r4`          |  2,121     |
| B.4 r1 (4 blockers)   | `bridge-b4-review`             |  4,827     |
| B.4 r2 (MINOR)        | `bridge-b4-review-r2`          |  3,915     |
| **Total**             |                                | **25,471** |

Every brief in that table would have been ~12KB larger had I
followed the old convention (manually re-pasting the rules/history
that channels would otherwise pin). Six rounds × ~12KB = **~72KB
of repeated context avoided** on this one issue alone — and the
savings grow roughly linearly with round count.

**Compound wins on multi-round debates:** the same trick applies to
`ab discuss` round 2+. When an agent is handed their own prior
response via `_channels.build_agent_prompt` it doesn't need to be
re-typed. The B.2 prompt assembler caps history at 5KB (configurable
via `DEFAULT_MAX_HISTORY_CHARS`), so even a 4-round, 4-agent
discussion stays inside a ~12KB budget per call instead of exploding
to 40–60KB of copy-pasted transcript.

**Tradeoff:** the first round of any new channel pays a small
one-time cost — the pinned `context.md` + the Monitor API snapshot
are concatenated into the prompt even if the agent doesn't strictly
need them. For drive-by one-shots, the legacy `ask-*` commands are
still cheaper. Use channels when the conversation will have at
least two turns.

## Web dashboard

`playgrounds/channels.html` — read-only monitor plus post form,
localhost only. Shows:

- All channels with message counts + pending deliveries + last activity
- Per-channel message feed (auto-refresh every 5s)
- Context preview with sha256 short-hash
- Post form for dropping messages in from the browser

Served by `scripts/api/main.py` at `http://localhost:8765`. The
browser POST endpoint is `/api/comms/channels/{name}/post` — user-only,
gated by localhost binding. Agents still post via CLI.

## API endpoints (for scripts + dashboards)

Read-only:
- `GET /api/comms/channels` — list all channels
- `GET /api/comms/channels/{name}` — channel metadata + context preview
- `GET /api/comms/channels/{name}/messages?tail=N` — recent messages
- `GET /api/comms/channels/{name}/threads/{thread_id}` — full thread
- `GET /api/comms/channels/{name}/deliveries?status=pending` — routing state

Write (user-only, localhost-gated):
- `POST /api/comms/channels/{name}/post` — drop a new post

## When channels drift

If `context.md` for a channel goes stale (the rules no longer match
reality), fix it immediately:

```bash
ab channel context pipeline --edit
```

This bumps the sha256, and the next post will record the new rev.
Older messages still have their original `context_rev_*` values for
deterministic replay — the update doesn't retroactively rewrite
history.

## Wake integration (C.3)

The inbox worker now supports a simple filesystem wake hint at
`.agent/wake/{agent}`. Whenever `_channels.post()` commits delivery
rows for one or more recipients, it replaces each recipient's wake
file atomically. That write is best-effort only: a wake-file failure
does not roll back the message or delivery insert.

Who writes:

- `scripts/ai_agent_bridge/_channels.py` after a successful post commit

Who reads:

- Any external watcher you configure locally
- `ab sync` if you prefer manual draining instead of OS integration

Recommended mental model:

- The SQLite `deliveries` table is the source of truth
- Wake files are only a nudge to run `ab inbox run <agent>`
- Missing a wake is safe because the work is still pending in SQLite

Example launchd `.plist` (`docs/examples/learn-ukrainian.codex-inbox.plist`):

> <?xml version="1.0" encoding="UTF-8"?>
> <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
> "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
> <plist version="1.0">
> <dict>
>   <key>Label</key>
>   <string>learn-ukrainian.codex-inbox</string>
>   <key>ProgramArguments</key>
>   <array>
>     <string>/Users/your-user/projects/learn-ukrainian/.venv/bin/python</string>
>     <string>/Users/your-user/projects/learn-ukrainian/scripts/ai_agent_bridge/__main__.py</string>
>     <string>inbox</string>
>     <string>run</string>
>     <string>codex</string>
>     <string>--until-idle</string>
>   </array>
>   <key>WatchPaths</key>
>   <array>
>     <string>/Users/your-user/projects/learn-ukrainian/.agent/wake/codex</string>
>   </array>
> </dict>
> </plist>

Example systemd units (documented only, not tested here):

> # ~/.config/systemd/user/learn-ukrainian-codex-inbox.path
> [Path]
> PathChanged=%h/projects/learn-ukrainian/.agent/wake/codex
>
> # ~/.config/systemd/user/learn-ukrainian-codex-inbox.service
> [Service]
> Type=oneshot
> WorkingDirectory=%h/projects/learn-ukrainian
> ExecStart=%h/projects/learn-ukrainian/.venv/bin/python scripts/ai_agent_bridge/__main__.py inbox run codex --until-idle

If you do not want OS-level watchers, use the manual fallback:

```bash
ab sync claude
ab sync --all
```

That path reads the same `deliveries` queue and drains it on demand.

## See also

- Issue #1190 — the channel bridge spec and implementation history
- `scripts/ai_agent_bridge/_channels.py` — storage primitives
- `scripts/ai_agent_bridge/_channels_cli.py` — CLI commands
- `scripts/api/comms_router.py` — HTTP endpoints
- `docs/MONITOR-API.md` — the Monitor API used for volatile state snapshots
