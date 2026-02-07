from claude_agent_sdk import tool

from ..sandbox import sandbox
from ._helpers import _ok, _err, _log_tool


@tool(
    name="run_shell",
    description="Run a shell command inside the sandbox and return its output.",
    input_schema={"command": str},
)
async def run_shell(args: dict) -> dict:
    command = args["command"]
    _log_tool("run_shell", [f"$ {command}"])
    try:
        result = await sandbox.shell.exec_command(command=command)
        output = result.data.output or ""
        exit_code = result.data.exit_code
        return _ok(f"{output}\n[exit code: {exit_code}]")
    except Exception as e:
        return _err(f"run_shell failed: {e}")
