from ..config import MAX_OUTPUT


def _truncate(text: str) -> str:
    if len(text) > MAX_OUTPUT:
        return text[:MAX_OUTPUT] + f"\n... (truncated, {len(text)} chars total)"
    return text


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": _truncate(text)}]}


def _err(text: str) -> dict:
    return {"content": [{"type": "text", "text": _truncate(text)}], "is_error": True}


def _log_tool(name: str, lines: list[str]) -> None:
    print(f"\n  ┌─ {name} {'─' * max(1, 38 - len(name))}")
    for line in lines:
        print(f"  │ {line}")
    print(f"  └──────────────────────────────────────")
