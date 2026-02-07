from claude_agent_sdk import tool

from ..sandbox import sandbox
from ._helpers import _ok, _err, _log_tool


@tool(
    name="execute_python",
    description="Execute Python code in a Jupyter kernel inside the sandbox.",
    input_schema={"code": str},
)
async def execute_python(args: dict) -> dict:
    code = args["code"]
    _log_tool("execute_python", code.splitlines())
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
