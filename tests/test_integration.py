import pytest

from agent_sandbox import AsyncSandbox

SANDBOX_URL = "http://localhost:8081"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
async def sandbox():
    client = AsyncSandbox(base_url=SANDBOX_URL)
    try:
        await client.sandbox.get_context()
    except Exception:
        pytest.skip(f"Sandbox not reachable at {SANDBOX_URL}")
    return client


async def test_execute_python(sandbox):
    result = await sandbox.jupyter.execute_code(code="print('hello')")
    texts = [
        out.text for out in result.data.outputs
        if out.output_type == "stream" and out.text
    ]
    assert any("hello" in t for t in texts)


async def test_run_shell(sandbox):
    result = await sandbox.shell.exec_command(command="echo hi")
    assert "hi" in result.data.output
    assert result.data.exit_code == 0


async def test_file_round_trip(sandbox):
    path = "/home/gem/test_round_trip.txt"
    content = "round trip content"
    await sandbox.file.write_file(file=path, content=content)
    read_result = await sandbox.file.read_file(file=path)
    assert read_result.data.content == content
