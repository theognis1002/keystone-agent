# The Delegation Layer

A meta-agent that sits between you and all your existing tools (email, calendar, Slack, etc.) and, instead of automating fixed workflows, generates bespoke micro-automations on the fly from natural language. It doesn't use Zapier-style templates — it writes the glue code fresh every time, tailored to the exact request.

**Example prompt:** "When anyone from the Portland team emails me about the Henderson project, draft a reply that loops in Sarah and flag it for my Monday review."

## Tech Stack

- Python 3.12, managed with `uv`
- Claude Agent SDK for the agent loop
- AIO Sandbox (agent-sandbox SDK) for secure code execution

## Project Structure

```
keystone/
├── __init__.py        # Exports KeystoneAgent
├── agent.py           # KeystoneAgent — sets up Claude SDK client with MCP tools
├── cli.py             # async REPL that drives the agent
├── config.py          # SANDBOX_URL, MAX_OUTPUT, SYSTEM_PROMPT, MCP constants
├── sandbox.py         # AsyncSandbox singleton (shared by all tools)
└── tools/
    ├── __init__.py    # ALL_TOOLS list, tool_names() helper
    ├── _helpers.py    # _ok(), _err(), _truncate(), _log_tool()
    ├── files.py       # write_file, read_file tools
    ├── python.py      # execute_python tool
    └── shell.py       # run_shell tool
```

## Key Patterns

- **Tool decorator**: Tools use `@tool(name=..., description=..., input_schema=...)` from `claude_agent_sdk`
- **Return format**: Tools return `_ok(text)` on success, `_err(text)` on failure — both produce MCP-compatible content dicts
- **Output truncation**: `MAX_OUTPUT` (10,000 chars) prevents oversized tool results; `_truncate()` clips with a note
- **Sandbox singleton**: `keystone/sandbox.py` creates one `AsyncSandbox` instance shared across all tools
- **Permission bypass**: The agent runs with `permission_mode="bypassPermissions"` since all execution is sandboxed

## Commands

```bash
# Run the agent
uv run main.py

# Lint
uv run ruff check .

# Lint with auto-fix
uv run ruff check --fix .

# Format
uv run ruff format .

# Run unit tests
uv run pytest

# Run integration tests (requires running sandbox)
uv run pytest -m integration
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | — | API key for Claude |
| `SANDBOX_URL` | No | `http://localhost:8081` | Base URL of the AIO Sandbox |

## AIO Sandbox

[AIO Sandbox](https://github.com/agent-infra/sandbox) is an all-in-one agent sandbox environment combining Browser, Shell, File, MCP, VSCode Server, and Jupyter in a single Docker container.

### Starting the Sandbox

Port 8081 (8080 is often occupied):

```
docker run --security-opt seccomp=unconfined --rm -it -p 8081:8080 ghcr.io/agent-infra/sandbox:latest
```

### Python SDK Quick Reference

```python
from agent_sandbox import AsyncSandbox

client = AsyncSandbox(base_url="http://localhost:8081")
```

**Sub-clients:** `client.sandbox`, `client.shell`, `client.file`, `client.jupyter`, `client.browser`, `client.nodejs`, `client.code`, `client.mcp`, `client.skills`, `client.util`

**Common operations:**

```python
# Context
ctx = client.sandbox.get_context()  # .home_dir, .version

# Shell
result = client.shell.exec_command(command="ls -la")  # .data.output

# Files
client.file.write_file(file="/path", content="...")
content = client.file.read_file(file="/path")  # .data.content

# Jupyter
result = client.jupyter.execute_code(code="print('hello')")  # .data (outputs list)
```

### Core API Endpoints

| Endpoint | Description |
|---|---|
| `GET /v1/sandbox` | Sandbox environment info |
| `POST /v1/shell/exec` | Execute shell commands |
| `POST /v1/file/read` | Read file contents |
| `POST /v1/file/write` | Write file contents |
| `POST /v1/jupyter/execute` | Execute Jupyter code |
| `GET /v1/browser/screenshot` | Browser screenshot |

### MCP Servers (built-in)

| Server | Tools |
|---|---|
| `browser` | `navigate`, `screenshot`, `click`, `type`, `scroll` |
| `file` | `read`, `write`, `list`, `search`, `replace` |
| `shell` | `exec`, `create_session`, `kill` |
| `markitdown` | `convert`, `extract_text`, `extract_images` |
