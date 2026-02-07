from claude_agent_sdk import tool

from ..sandbox import sandbox
from ._helpers import _ok, _err, _log_tool


@tool(
    name="write_file",
    description="Write content to a file in the sandbox.",
    input_schema={"path": str, "content": str},
)
async def write_file(args: dict) -> dict:
    path = args["path"]
    content = args["content"]
    preview = content[:200] + "..." if len(content) > 200 else content
    _log_tool("write_file", [f"path: {path}"] + preview.splitlines())
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
    _log_tool("read_file", [f"path: {path}"])
    try:
        result = await sandbox.file.read_file(file=path)
        return _ok(result.data.content)
    except Exception as e:
        return _err(f"read_file failed: {e}")
