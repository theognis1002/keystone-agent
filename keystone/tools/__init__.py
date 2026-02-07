from .python import execute_python
from .shell import run_shell
from .files import write_file, read_file

ALL_TOOLS = [execute_python, run_shell, write_file, read_file]


def tool_names(server_name: str) -> list[str]:
    return [f"mcp__{server_name}__{t.name}" for t in ALL_TOOLS]
