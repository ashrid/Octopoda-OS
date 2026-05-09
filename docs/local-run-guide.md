# Local Run Guide

This guide covers the **local-first** Octopoda-OS workflow — no cloud account, no login, no API key required.

The canonical local dashboard runs on **http://localhost:7842**.
The older dashboard on port **7844** is a deprecated legacy path.

## 1. Install

Clone and install from the repo root:

```bash
git clone https://github.com/RyjoxTechnologies/Octopoda-OS
cd Octopoda-OS
pip install -e ".[all]"
```

The `[all]` extra includes everything: runtime server, dashboard, MCP server, semantic search (embeddings), and knowledge graph (spaCy).

If you only need specific components:

```bash
pip install -e ".[server,mcp,ai,nlp]"   # dashboard + MCP + embeddings + KG
pip install -e ".[server]"              # dashboard only (no MCP, no AI)
```

If you are on **Python 3.9**, the `[mcp]` extra requires Python 3.10+. Use:

```bash
pip install -e ".[server,ai,nlp]"       # everything except MCP
```

## 2. Start the local runtime and dashboard

```bash
octopoda
```

Or equivalently:

```bash
python3 -m synrix_runtime.start
```

What this does:

- loads `.env` from the repo root if present
- loads local extraction settings from `~/.octopoda/extraction.json` if present
- starts the runtime daemon (SQLite-backed)
- starts the canonical local dashboard at **http://localhost:7842**
- starts the local FastAPI surface at **http://localhost:8741** (unless `--no-api`)

The browser opens automatically. The dashboard shows system health, agent list, memory stats, and has quick Remember/Recall/Search actions — all local, no cloud.

Useful flags:

```bash
octopoda --no-browser                       # don't open browser
octopoda --no-api                           # skip FastAPI server
octopoda --port 7850 --api-port 8750        # custom ports
octopoda --demo                             # start the 4-agent research demo
```

API docs (Swagger UI) at:

```
http://localhost:8741/docs
```

## 3. MCP Server — Use Octopoda from Claude, OpenCode, Cursor, or any MCP client

### Local mode (default — no cloud account needed)

Start the MCP server without an API key:

```bash
octopoda-mcp
```

Or equivalently:

```bash
python3 -m synrix_runtime.api.mcp_server
```

The MCP server runs over stdio and uses the local SQLite-backed runtime. All 28 tools work locally: remember, recall, search, semantic search, snapshots, restore, shared memory, agent messaging, goals, loop detection, memory health, consolidation, and more.

Unlike `octopoda`, the MCP entrypoint does **not** auto-load a repo-local `.env` file. Export variables explicitly or source the file before launching.

### Register with Claude Code

```bash
claude mcp add octopoda -s user -- python3 -m synrix_runtime.api.mcp_server
```

For cloud sync, add the API key:

```bash
claude mcp add octopoda -s user -e OCTOPODA_API_KEY=sk-octopoda-... -- python3 -m synrix_runtime.api.mcp_server
```

### Register with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "octopoda": {
      "command": "python3",
      "args": ["-m", "synrix_runtime.api.mcp_server"]
    }
  }
}
```

For local mode, omit `OCTOPODA_API_KEY`. For cloud sync, set it in the `env` block.

### Register with OpenCode / Cursor

Add to your MCP configuration (format varies by client):

```json
{
  "octopoda": {
    "command": "python3",
    "args": ["-m", "synrix_runtime.api.mcp_server"],
    "env": {
      "OCTOPODA_API_KEY": ""
    }
  }
}
```

Leave `OCTOPODA_API_KEY` empty for local mode, or set a real key for cloud sync.

### Available MCP tools (28 total)

| Category | Tools |
|----------|-------|
| Memory | `octopoda_remember`, `octopoda_recall`, `octopoda_search`, `octopoda_recall_similar`, `octopoda_recall_history`, `octopoda_forget`, `octopoda_forget_stale` |
| Snapshots | `octopoda_snapshot`, `octopoda_restore` |
| Shared memory | `octopoda_share`, `octopoda_read_shared` |
| Agent management | `octopoda_list_agents`, `octopoda_agent_stats` |
| Audit | `octopoda_log_decision` |
| Messaging | `octopoda_send_message`, `octopoda_read_messages`, `octopoda_broadcast` |
| Goals | `octopoda_set_goal`, `octopoda_get_goal`, `octopoda_update_progress` |
| Loop detection | `octopoda_loop_status`, `octopoda_loop_history` |
| Health | `octopoda_memory_health`, `octopoda_consolidate`, `octopoda_search_filtered` |
| Context | `octopoda_process_conversation`, `octopoda_get_context`, `octopoda_related` |

In local mode, all tools use the SQLite backend. If you set `OCTOPODA_API_KEY`, the same tools route through the cloud API.

## 4. Configure AI Extraction

Fact extraction runs in the background after every `remember()` call. It sends the stored text to an LLM, decomposes it into self-contained facts, embeds each fact, and stores them for high-quality semantic search.

### Setup

Create `~/.octopoda/extraction.json`:

```json
{
  "provider": "custom",
  "api_key": "your-api-key",
  "model": "gpt-4o-mini",
  "base_url": "https://your-endpoint/v1"
}
```

Supported providers:

| Provider | Description | Required fields |
|----------|-------------|-----------------|
| `custom` | Any OpenAI-compatible endpoint | `api_key`, `model`, `base_url` |
| `openai` | OpenAI API | `api_key`, `model` (optional, default `gpt-4o-mini`) |
| `openrouter` | OpenRouter (uses OpenAI-compatible mode) | `api_key`, `model` |
| `ollama` | Local Ollama | No key required — just have Ollama running |
| `anthropic` | Anthropic Claude | `api_key` |
| `none` | Disable extraction | — |

The `custom` provider is the most flexible — it maps to OpenAI-compatible mode internally and sends requests to `{base_url}/chat/completions` with your key and model.

### Verify extraction is working

```bash
python3 - <<'PY'
import time, sqlite3, os
from octopoda import AgentRuntime

agent = AgentRuntime("extract_test")
agent.remember("bio", "Alice is a vegetarian living in London who prefers dark mode")
agent.flush()
time.sleep(3)

db = os.path.expanduser("~/.synrix/data/synrix.db")
cur = sqlite3.connect(db).cursor()
cur.execute("SELECT fact_text FROM fact_embeddings ORDER BY rowid DESC LIMIT 5")
for r in cur.fetchall():
    print(f"  - {r[0]}")
PY
```

If you see facts like `"User is vegetarian"` and `"User lives in London"`, extraction is working.

### Manage settings from the dashboard

The canonical local dashboard on **7842** exposes:

- `/api/settings` — view current settings
- `/api/settings/extraction` — get/set extraction config
- `/api/settings/test-llm` — test LLM connectivity

Settings are persisted to `~/.octopoda/extraction.json` and loaded automatically on every runtime/MCP startup.

## 5. Legacy dashboard status

This path still exists but is deprecated:

```bash
python3 dashboard/app.py
```

It runs on **http://localhost:7844** and prints a deprecation notice at startup. Use it only for transitional compatibility. For normal local use, prefer **7842**.

## 6. Quick reference

```bash
# Start everything (dashboard + API + daemon)
octopoda

# Start without opening the browser
octopoda --no-browser

# Dashboard only, no API server
octopoda --no-api

# MCP server (local mode)
octopoda-mcp

# Register MCP with Claude Code (local mode)
claude mcp add octopoda -s user -- python3 -m synrix_runtime.api.mcp_server

# Check extraction config
python3 dashboard/load_extraction_config.py

# Quick smoke test
python3 -c "from octopoda import AgentRuntime; a=AgentRuntime('smoke'); a.remember('h','w'); print(a.recall('h').value)"

# API docs (Swagger)
open http://localhost:8741/docs
```

## 7. Troubleshooting

### Dashboard did not start
- check whether port `7842` is already in use
- run with `--port 7850`
- confirm Flask dependencies: `pip install -e ".[server]"`

### API did not start
- run with `--no-api` if you only need the dashboard
- confirm FastAPI/uvicorn: `pip install fastapi uvicorn`

### Extraction is not active
- check `~/.octopoda/extraction.json`
- confirm `OCTOPODA_LLM_PROVIDER` is being set correctly
- restart the runtime or MCP process after changing settings

### MCP is using cloud unexpectedly
- unset `OCTOPODA_API_KEY`
- restart the MCP process

### MCP tools are not appearing in your client
- verify the MCP process starts: `octopoda-mcp` should print "starting in LOCAL mode"
- check your client's MCP configuration points at the correct entrypoint
- the path `python3 -m synrix_runtime.api.mcp_server` must be runnable from the repo root

### You launched the wrong dashboard
- **7842** = canonical runtime-backed local dashboard
- **7844** = deprecated legacy dashboard
