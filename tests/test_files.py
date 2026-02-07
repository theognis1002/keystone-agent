import pytest

from keystone.tools.files import write_file, read_file

write_handler = write_file.handler
read_handler = read_file.handler


class TestWriteFile:
    async def test_success(self, mock_sandbox, file_write_result_factory):
        mock_sandbox.file.write_file.return_value = file_write_result_factory(
            bytes_written=42, file="/home/gem/out.txt"
        )
        result = await write_handler({"path": "/home/gem/out.txt", "content": "hello"})
        text = result["content"][0]["text"]
        assert "42" in text
        assert "/home/gem/out.txt" in text
        assert "is_error" not in result

    async def test_exception(self, mock_sandbox):
        mock_sandbox.file.write_file.side_effect = PermissionError("denied")
        result = await write_handler({"path": "/root/secret", "content": "x"})
        assert result["is_error"] is True
        assert "write_file failed" in result["content"][0]["text"]


class TestReadFile:
    async def test_success(self, mock_sandbox, file_read_result_factory):
        mock_sandbox.file.read_file.return_value = file_read_result_factory(
            content="line1\nline2"
        )
        result = await read_handler({"path": "/home/gem/test.txt"})
        text = result["content"][0]["text"]
        assert "line1" in text
        assert "line2" in text
        assert "is_error" not in result

    async def test_exception(self, mock_sandbox):
        mock_sandbox.file.read_file.side_effect = FileNotFoundError("nope")
        result = await read_handler({"path": "/missing/file.txt"})
        assert result["is_error"] is True
        assert "read_file failed" in result["content"][0]["text"]
