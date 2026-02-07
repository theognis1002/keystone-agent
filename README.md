# The Delegation Layer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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

## Features

- **Natural language to code** — describe what you want in plain English; the agent writes and executes the code
- **Secure sandbox execution** — all generated code runs inside an isolated Docker container, never on your host
- **Four built-in tools** — Python execution (Jupyter), shell commands, file read, and file write
- **Multi-turn conversations** — the agent maintains context across turns for iterative workflows
- **Real-time visibility** — see the agent's reasoning, the code it writes, and the results as they happen

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

## Project Structure

```
.
├── main.py                # Entry point — runs the REPL
├── keystone/
│   ├── __init__.py        # Package exports (KeystoneAgent)
│   ├── agent.py           # Agent class — Claude SDK + MCP wiring
│   ├── cli.py             # Interactive REPL
│   ├── config.py          # Configuration constants
│   ├── sandbox.py         # Sandbox client singleton
│   └── tools/
│       ├── __init__.py    # Tool registry (ALL_TOOLS)
│       ├── _helpers.py    # Shared utilities (_ok, _err, _truncate)
│       ├── files.py       # write_file, read_file
│       ├── python.py      # execute_python
│       └── shell.py       # run_shell
├── tests/                 # Unit and integration tests
├── pyproject.toml         # Project metadata and dependencies
├── CLAUDE.md              # Development instructions for AI assistants
└── README.md
```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
