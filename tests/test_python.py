from types import SimpleNamespace

import pytest

from keystone.tools.python import execute_python

handler = execute_python.handler


class TestExecutePython:
    async def test_stream_output(self, mock_sandbox, jupyter_output_factory):
        mock_sandbox.jupyter.execute_code.return_value = SimpleNamespace(
            data=SimpleNamespace(outputs=[jupyter_output_factory["stream"]("hello world")])
        )
        result = await handler({"code": "print('hello world')"})
        assert "hello world" in result["content"][0]["text"]
        assert "is_error" not in result

    async def test_execute_result(self, mock_sandbox, jupyter_output_factory):
        mock_sandbox.jupyter.execute_code.return_value = SimpleNamespace(
            data=SimpleNamespace(outputs=[jupyter_output_factory["execute_result"]("42")])
        )
        result = await handler({"code": "40 + 2"})
        assert "42" in result["content"][0]["text"]

    async def test_display_data(self, mock_sandbox, jupyter_output_factory):
        mock_sandbox.jupyter.execute_code.return_value = SimpleNamespace(
            data=SimpleNamespace(outputs=[jupyter_output_factory["display_data"]("chart data")])
        )
        result = await handler({"code": "display(chart)"})
        assert "chart data" in result["content"][0]["text"]

    async def test_error_output(self, mock_sandbox, jupyter_output_factory):
        mock_sandbox.jupyter.execute_code.return_value = SimpleNamespace(
            data=SimpleNamespace(outputs=[
                jupyter_output_factory["error"]("TypeError", "oops", ["frame1", "frame2"])
            ])
        )
        result = await handler({"code": "bad code"})
        text = result["content"][0]["text"]
        assert "TypeError" in text
        assert "oops" in text
        assert "frame1" in text

    async def test_no_output(self, mock_sandbox):
        mock_sandbox.jupyter.execute_code.return_value = SimpleNamespace(
            data=SimpleNamespace(outputs=[])
        )
        result = await handler({"code": "x = 1"})
        assert "(no output)" in result["content"][0]["text"]

    async def test_multiple_outputs(self, mock_sandbox, jupyter_output_factory):
        mock_sandbox.jupyter.execute_code.return_value = SimpleNamespace(
            data=SimpleNamespace(outputs=[
                jupyter_output_factory["stream"]("line1"),
                jupyter_output_factory["execute_result"]("line2"),
            ])
        )
        result = await handler({"code": "print('line1'); 'line2'"})
        text = result["content"][0]["text"]
        assert "line1" in text
        assert "line2" in text

    async def test_sandbox_exception(self, mock_sandbox):
        mock_sandbox.jupyter.execute_code.side_effect = ConnectionError("unreachable")
        result = await handler({"code": "print(1)"})
        assert result["is_error"] is True
        assert "execute_python failed" in result["content"][0]["text"]
