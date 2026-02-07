# The Delegation Layer

A meta-agent that generates bespoke micro-automations on the fly from natural language. Instead of Zapier-style templates or fixed workflows, it writes fresh glue code every time — tailored to the exact request — and executes it in a secure sandboxed environment.

## How It Works

You type a natural language request into the CLI. A Claude agent interprets your intent, writes Python (or shell commands) to accomplish it, and executes that code inside an isolated Docker sandbox. You see the agent's reasoning, the code it writes, and the results — all in your terminal.

```
you> what python version is in the sandbox?

  ┌─ execute_python ─────────────────────
  │ import sys
  │ print(sys.version)
  └──────────────────────────────────────

agent> The sandbox is running Python 3.11.2
```

## Quickstart

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [Docker](https://www.docker.com/)
- An `ANTHROPIC_API_KEY` set in your environment (or `.env` file)

### 1. Start the sandbox

```bash
docker run --security-opt seccomp=unconfined --rm -it -p 8081:8080 ghcr.io/agent-infra/sandbox:latest
```

Verify it's running at http://localhost:8081/v1/docs.

### 2. Install dependencies

```bash
uv sync
```

### 3. Run

```bash
uv run main.py
```

Type requests at the `you>` prompt. Type `quit` or `exit` (or Ctrl+C) to stop.

## Example Prompts

| Prompt                                  | What happens                                                |
| --------------------------------------- | ----------------------------------------------------------- |
| `check my ip address`                   | Writes a script using `urllib` to hit httpbin.org/ip        |
| `list files in the home directory`      | Runs `ls -la` via shell                                     |
| `create a simple flask app and run it`  | Writes the app to a file, installs Flask, starts the server |
| `download and parse the top HN stories` | Fetches the Hacker News API, formats the results            |

## Architecture

```
┌──────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  You     │────▶│  Claude Agent    │────▶│  AIO Sandbox        │
│  (CLI)   │◀────│  (Claude SDK)    │◀────│  (Docker container) │
└──────────┘     └──────────────────┘     └─────────────────────┘
```

The agent has four tools, all executed inside the sandbox:

| Tool             | Description                             |
| ---------------- | --------------------------------------- |
| `execute_python` | Run Python code in a Jupyter kernel     |
| `run_shell`      | Run a shell command                     |
| `write_file`     | Write a file to the sandbox filesystem  |
| `read_file`      | Read a file from the sandbox filesystem |

## Tech Stack

- **Python 3.12** — managed with [uv](https://docs.astral.sh/uv/)
- **[Claude Agent SDK](https://docs.anthropic.com/en/docs/agents)** — multi-turn agent loop with MCP tool support
- **[AIO Sandbox](https://github.com/agent-infra/sandbox)** — all-in-one Docker sandbox with Shell, Jupyter, File, Browser, and VSCode Server

## Sandbox Services

Once the sandbox container is running, these are available:

| Service       | URL                                                   |
| ------------- | ----------------------------------------------------- |
| API docs      | http://localhost:8081/v1/docs                         |
| VNC browser   | http://localhost:8081/vnc/index.html?autoconnect=true |
| VSCode Server | http://localhost:8081/code-server/                    |
| MCP services  | http://localhost:8081/mcp                             |

## Docker Compose

For a persistent sandbox setup:

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

```bash
docker compose up -d
```

## Project Structure

```
.
├── main.py           # Single-file CLI agent
├── pyproject.toml    # Project metadata and dependencies
├── CLAUDE.md         # Development instructions for AI assistants
└── README.md
```
