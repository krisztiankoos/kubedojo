# Agent Bridge Setup Guide

The Agent Bridge provides channel-based, multi-agent communication with a leased delivery queue, allowing LLM agents (like Claude, Gemini, Codex) to communicate asynchronously and deterministically across invocations while minimizing token overhead.

This guide explains how to integrate the Agent Bridge into a new project (e.g., `kubedojo`).

## 1. What the Bridge Does

The Agent Bridge replaces 1:1 message passing with **topic-scoped channels**. It provides:
- **Pinned context:** Each channel (e.g., `architecture`, `ops`) automatically injects shared project state into prompts, reducing token waste.
- **Message history:** Truncated thread history is managed in a local SQLite database.
- **Delivery queue:** A leased delivery system ensures messages are routed and processed exactly once by target agents via an inbox worker.

## 2. Prerequisites

- **Python 3.12+**
- **SQLite** (bundled with Python)
- `agent_runtime` (or similar LLM CLI tools) for inbox draining and agent invocation.

## 3. Setup Steps for a New Project

Follow these steps to initialize the bridge in a new repository (e.g., `kubedojo`):

### Step 3.1: Copy or Symlink the Bridge
Copy the `scripts/ai_agent_bridge/` directory from a reference implementation (like `learn-ukrainian`) into your project:
```bash
cp -r /path/to/learn-ukrainian/scripts/ai_agent_bridge scripts/
```

### Step 3.2: Configure Environment Variables
Set the required environment variables in your project's `.envrc` or shell startup script. For example:
```bash
export AB_REPO_ROOT="/path/to/kubedojo"
export AB_DB_PATH="${AB_REPO_ROOT}/.bridge/messages.db"
export AB_CONTEXT_DIR="${AB_REPO_ROOT}/docs/agent-channels"
export AB_WAKE_DIR="${AB_REPO_ROOT}/.agent/wake"
```

### Step 3.3: Create Initial Channels
Create your base channels. It is recommended to create a `shared` channel for global context, and include it in topic-specific channels.
```bash
# Create the global shared channel
ab channel new shared

# Create a topic channel and include shared context
ab channel new ops --include shared
```

### Step 3.4: Test the Setup
Verify the bridge is functioning correctly:
```bash
# List available channels
ab channel list

# Post a test message
ab post ops "Initialization test" --to claude

# Check the inbox queue
ab inbox show
```

## 4. Environment Variable Reference

The bridge is fully configurable via `AB_*` environment variables to support portability across projects.

| Variable | Default Value | Description |
|---|---|---|
| `AB_REPO_ROOT` | `Path(__file__).parent.parent.parent` | The root directory of the repository. |
| `AB_DB_PATH` | `{AB_REPO_ROOT}/.mcp/servers/message-broker/messages.db` | Path to the SQLite database. |
| `AB_PID_DIR` | `{AB_REPO_ROOT}/.mcp/servers/message-broker/pids` | Directory for process ID locks. |
| `AB_CONTEXT_DIR` | `{AB_REPO_ROOT}/docs/agent-channels` | Directory containing channel `context.md` files. |
| `AB_WAKE_DIR` | `{AB_REPO_ROOT}/.agent/wake` | Directory for OS-level wake files for the inbox worker. |
| `AB_MONITOR_URL` | `http://localhost:8765/api/state/summary` | URL for the Monitor API. Set to `""` to disable snapshot injection. |
| `AB_GEMINI_MODEL` | `batch_gemini_config.FLASH_MODEL` / `gemini-2.0-flash` | Default Gemini model to invoke. |
| `AB_PIPELINE_ENV_KEY` | `LEARN_UKRAINIAN_PIPELINE` | Env var key to suppress inbox hooks during pipeline runs. |

## 5. CLI Quick Reference

The bridge is managed via the `ab` command line interface (typically aliased to `python -m ai_agent_bridge`).

- **`ab channel ...`**: Manage channels.
  - `ab channel new <name> [--include <other>]`: Create a new channel.
  - `ab channel list`: List all channels.
  - `ab channel context <name> --edit`: Edit the pinned context for a channel.
- **`ab post <channel> "<message>"`**: Send a message to a channel. Use `--to <agent1,agent2>` to specify recipients, or `--parent <id>` to reply to a thread.
- **`ab discuss <channel> "<topic>"`**: Start a bounded multi-agent debate. Use `--with <agents>` and `--max-rounds <N>`.
- **`ab inbox show`**: View pending messages waiting for agents.
- **`ab inbox run <agent> [--until-idle]`**: Run the inbox worker to process messages for a specific agent.
- **`ab sync <agent>`**: Manually drain the queue and sync messages for an agent (alternative to `inbox run`).

## 6. Architecture Diagram

The flow of a message through the Agent Bridge:

```mermaid
graph TD
    A[Human/Agent Post] -->|ab post| B(Channel)
    B -->|Context + Snapshot + History| C[(SQLite DB: channel_messages)]
    C -->|Generate Routes| D[(SQLite DB: deliveries)]
    D -->|Wake Hint| E[Wake File (.agent/wake/)]
    E -.->|File Event| F[Inbox Worker (ab inbox run)]
    D -->|Poll / Lease| F
    F -->|Assemble Prompt| G[Agent Invoke (Claude/Gemini)]
    G -->|Reply| B
```
