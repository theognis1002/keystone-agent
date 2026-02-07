# The Delegation Layer

A meta-agent that sits between you and all your existing tools (email, calendar, Slack, etc.) and, instead of automating fixed workflows, generates bespoke micro-automations on the fly from natural language. It doesn't use Zapier-style templates — it writes the glue code fresh every time, tailored to the exact request.

**Example prompt:** "When anyone from the Portland team emails me about the Henderson project, draft a reply that loops in Sarah and flag it for my Monday review."

## Tech Stack

- Python 3.12, managed with `uv`
- AIO Sandbox (agent-sandbox SDK) for secure code execution

## AIO Sandbox

[AIO Sandbox](https://github.com/agent-infra/sandbox) is an all-in-one agent sandbox environment combining Browser, Shell, File, MCP, VSCode Server, and Jupyter in a single Docker container.

### Starting the Sandbox

Port 8081 (8080 is occupied by adminer):

```
docker run --security-opt seccomp=unconfined --rm -it -p 8081:8080 ghcr.io/agent-infra/sandbox:latest
```

Once running:
- API docs: http://localhost:8081/v1/docs
- VNC browser: http://localhost:8081/vnc/index.html?autoconnect=true
- VSCode Server: http://localhost:8081/code-server/
- MCP services: http://localhost:8081/mcp

### Python SDK Quick Reference

```python
from agent_sandbox import Sandbox       # sync
from agent_sandbox import AsyncSandbox  # async

client = Sandbox(base_url="http://localhost:8081")
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

# Browser
screenshot = client.browser.screenshot()
info = client.browser.get_info()  # .data.cdp_url for Playwright
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

### Docker Compose

```yaml
services:
  sandbox:
    image: ghcr.io/agent-infra/sandbox:latest
    security_opt:
      - seccomp:unconfined
    ports:
      - "8081:8080"
    shm_size: "2gb"
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      WORKSPACE: "/home/gem"
```

## Running

```
uv run main.py
```
