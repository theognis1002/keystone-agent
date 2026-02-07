from types import SimpleNamespace
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from keystone.agent import KeystoneAgent


class TestKeystoneAgentInit:
    @patch("keystone.agent.ClaudeSDKClient")
    @patch("keystone.agent.create_sdk_mcp_server")
    def test_creates_client_with_correct_config(self, mock_create_server, mock_client_cls):
        mock_create_server.return_value = MagicMock(name="mock_server")
        agent = KeystoneAgent()
        mock_create_server.assert_called_once()
        call_kwargs = mock_create_server.call_args
        assert call_kwargs.kwargs["name"] == "sandbox"
        assert call_kwargs.kwargs["version"] == "1.0.0"
        mock_client_cls.assert_called_once()


class TestCheckSandbox:
    @patch("keystone.agent.ClaudeSDKClient")
    @patch("keystone.agent.create_sdk_mcp_server")
    async def test_success(self, mock_create_server, mock_client_cls, monkeypatch):
        mock_ctx = SimpleNamespace(version="1.2.3", home_dir="/home/gem")
        mock_sb = AsyncMock()
        mock_sb.sandbox.get_context.return_value = mock_ctx
        monkeypatch.setattr("keystone.agent.sandbox", mock_sb)

        agent = KeystoneAgent()
        await agent.check_sandbox()
        mock_sb.sandbox.get_context.assert_awaited_once()

    @patch("keystone.agent.ClaudeSDKClient")
    @patch("keystone.agent.create_sdk_mcp_server")
    async def test_failure_raises_connection_error(self, mock_create_server, mock_client_cls, monkeypatch):
        mock_sb = AsyncMock()
        mock_sb.sandbox.get_context.side_effect = ConnectionError("refused")
        monkeypatch.setattr("keystone.agent.sandbox", mock_sb)

        agent = KeystoneAgent()
        with pytest.raises(ConnectionError, match="Could not reach sandbox"):
            await agent.check_sandbox()


class TestContextManager:
    @patch("keystone.agent.ClaudeSDKClient")
    @patch("keystone.agent.create_sdk_mcp_server")
    async def test_aenter_aexit(self, mock_create_server, mock_client_cls):
        mock_client = AsyncMock()
        mock_client_cls.return_value = mock_client

        agent = KeystoneAgent()
        returned = await agent.__aenter__()
        assert returned is agent
        mock_client.__aenter__.assert_awaited_once()

        await agent.__aexit__(None, None, None)
        mock_client.__aexit__.assert_awaited_once()
