from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace

import pytest


@pytest.fixture
def mock_sandbox(monkeypatch):
    sb = AsyncMock()
    monkeypatch.setattr("keystone.tools.python.sandbox", sb)
    monkeypatch.setattr("keystone.tools.shell.sandbox", sb)
    monkeypatch.setattr("keystone.tools.files.sandbox", sb)
    return sb


def _make_stream(text):
    return SimpleNamespace(output_type="stream", text=text)


def _make_execute_result(text_plain):
    return SimpleNamespace(output_type="execute_result", data={"text/plain": text_plain})


def _make_display_data(text_plain):
    return SimpleNamespace(output_type="display_data", data={"text/plain": text_plain})


def _make_error(ename="ValueError", evalue="bad value", traceback=None):
    return SimpleNamespace(
        output_type="error",
        ename=ename,
        evalue=evalue,
        traceback=traceback or [],
    )


@pytest.fixture
def jupyter_output_factory():
    return {
        "stream": _make_stream,
        "execute_result": _make_execute_result,
        "display_data": _make_display_data,
        "error": _make_error,
    }


@pytest.fixture
def shell_result_factory():
    def _make(output="", exit_code=0):
        return SimpleNamespace(data=SimpleNamespace(output=output, exit_code=exit_code))
    return _make


@pytest.fixture
def file_write_result_factory():
    def _make(bytes_written=100, file="/home/gem/test.txt"):
        return SimpleNamespace(data=SimpleNamespace(bytes_written=bytes_written, file=file))
    return _make


@pytest.fixture
def file_read_result_factory():
    def _make(content="file content"):
        return SimpleNamespace(data=SimpleNamespace(content=content))
    return _make
