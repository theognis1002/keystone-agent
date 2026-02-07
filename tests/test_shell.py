import pytest

from keystone.tools.shell import run_shell

handler = run_shell.handler


class TestRunShell:
    async def test_successful_command(self, mock_sandbox, shell_result_factory):
        mock_sandbox.shell.exec_command.return_value = shell_result_factory(
            output="file1.txt\nfile2.txt", exit_code=0
        )
        result = await handler({"command": "ls"})
        text = result["content"][0]["text"]
        assert "file1.txt" in text
        assert "[exit code: 0]" in text
        assert "is_error" not in result

    async def test_nonzero_exit_code(self, mock_sandbox, shell_result_factory):
        mock_sandbox.shell.exec_command.return_value = shell_result_factory(
            output="not found", exit_code=1
        )
        result = await handler({"command": "grep missing file.txt"})
        text = result["content"][0]["text"]
        assert "not found" in text
        assert "[exit code: 1]" in text

    async def test_empty_output(self, mock_sandbox, shell_result_factory):
        mock_sandbox.shell.exec_command.return_value = shell_result_factory(
            output="", exit_code=0
        )
        result = await handler({"command": "true"})
        text = result["content"][0]["text"]
        assert "[exit code: 0]" in text

    async def test_sandbox_exception(self, mock_sandbox):
        mock_sandbox.shell.exec_command.side_effect = RuntimeError("timeout")
        result = await handler({"command": "sleep 999"})
        assert result["is_error"] is True
        assert "run_shell failed" in result["content"][0]["text"]
