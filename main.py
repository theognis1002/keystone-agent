import anyio
from agent_sandbox import AsyncSandbox
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)

SANDBOX_URL = "http://localhost:8081"
MAX_OUTPUT = 10_000

SYSTEM_PROMPT = """\
You are a delegation agent with access to a sandboxed execution environment.
When the user asks you to do something, ALWAYS write and execute code to accomplish it
rather than just explaining how. You have four tools:

- execute_python: Run Python code in a Jupyter kernel inside the sandbox.
- run_shell: Run a shell command inside the sandbox.
- write_file: Write a file to the sandbox filesystem.
- read_file: Read a file from the sandbox filesystem.

Bias heavily toward action. If the user asks a question that can be answered by
running code, run the code. If they ask you to create something, create it.
Show the results, not just the plan.
"""

sandbox = AsyncSandbox(base_url=SANDBOX_URL)


def _truncate(text: str) -> str:
    if len(text) > MAX_OUTPUT:
        return text[:MAX_OUTPUT] + f"\n... (truncated, {len(text)} chars total)"
    return text


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": _truncate(text)}]}


def _err(text: str) -> dict:
    return {"content": [{"type": "text", "text": _truncate(text)}], "is_error": True}


@tool(
    name="execute_python",
    description="Execute Python code in a Jupyter kernel inside the sandbox.",
    input_schema={"code": str},
)
async def execute_python(args: dict) -> dict:
    code = args["code"]
    print(f"\n  ┌─ execute_python ─────────────────────")
    for line in code.splitlines():
        print(f"  │ {line}")
    print(f"  └──────────────────────────────────────")
    try:
        result = await sandbox.jupyter.execute_code(code=code)
        parts = []
        for out in result.data.outputs:
            if out.output_type == "stream" and out.text:
                parts.append(out.text)
            elif out.output_type in ("execute_result", "display_data") and out.data:
                parts.append(out.data.get("text/plain", str(out.data)))
            elif out.output_type == "error":
                parts.append(f"{out.ename}: {out.evalue}")
                if out.traceback:
                    parts.append("\n".join(out.traceback))
        return _ok("\n".join(parts) if parts else "(no output)")
    except Exception as e:
        return _err(f"execute_python failed: {e}")


@tool(
    name="run_shell",
    description="Run a shell command inside the sandbox and return its output.",
    input_schema={"command": str},
)
async def run_shell(args: dict) -> dict:
    command = args["command"]
    print(f"\n  ┌─ run_shell ────────────────────────── ")
    print(f"  │ $ {command}")
    print(f"  └──────────────────────────────────────")
    try:
        result = await sandbox.shell.exec_command(command=command)
        output = result.data.output or ""
        exit_code = result.data.exit_code
        return _ok(f"{output}\n[exit code: {exit_code}]")
    except Exception as e:
        return _err(f"run_shell failed: {e}")


@tool(
    name="write_file",
    description="Write content to a file in the sandbox.",
    input_schema={"path": str, "content": str},
)
async def write_file(args: dict) -> dict:
    path = args["path"]
    content = args["content"]
    preview = content[:200] + "..." if len(content) > 200 else content
    print(f"\n  ┌─ write_file ───────────────────────── ")
    print(f"  │ path: {path}")
    for line in preview.splitlines():
        print(f"  │ {line}")
    print(f"  └──────────────────────────────────────")
    try:
        result = await sandbox.file.write_file(file=path, content=content)
        return _ok(f"Wrote {result.data.bytes_written} bytes to {result.data.file}")
    except Exception as e:
        return _err(f"write_file failed: {e}")


@tool(
    name="read_file",
    description="Read the contents of a file in the sandbox.",
    input_schema={"path": str},
)
async def read_file(args: dict) -> dict:
    path = args["path"]
    print(f"\n  ┌─ read_file ────────────────────────── ")
    print(f"  │ path: {path}")
    print(f"  └──────────────────────────────────────")
    try:
        result = await sandbox.file.read_file(file=path)
        return _ok(result.data.content)
    except Exception as e:
        return _err(f"read_file failed: {e}")


server = create_sdk_mcp_server(
    name="sandbox",
    version="1.0.0",
    tools=[execute_python, run_shell, write_file, read_file],
)

options = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={"sandbox": server},
    allowed_tools=[
        "mcp__sandbox__execute_python",
        "mcp__sandbox__run_shell",
        "mcp__sandbox__write_file",
        "mcp__sandbox__read_file",
    ],
    permission_mode="bypassPermissions",
)


async def main():
    print("Connecting to sandbox...")
    try:
        ctx = await sandbox.sandbox.get_context()
        print(f"Sandbox ready (version {ctx.version}, home: {ctx.home_dir})")
    except Exception as e:
        print(f"Could not reach sandbox at {SANDBOX_URL}: {e}")
        print("Start it with: docker run --security-opt seccomp=unconfined --rm -it -p 8081:8080 ghcr.io/agent-infra/sandbox:latest")
        return

    async with ClaudeSDKClient(options=options) as client:
        print("\nThe Delegation Layer — type your request (quit to exit)\n")
        while True:
            try:
                prompt = await anyio.to_thread.run_sync(lambda: input("you> "))
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if prompt.strip().lower() in ("quit", "exit"):
                print("Goodbye!")
                break

            if not prompt.strip():
                continue

            await client.query(prompt)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"\nagent> {block.text}")
                        elif isinstance(block, ToolUseBlock):
                            print(f"\n[{block.name}]")
                elif isinstance(message, ResultMessage):
                    pass


anyio.run(main)
