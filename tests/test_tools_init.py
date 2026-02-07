from keystone.tools import ALL_TOOLS, tool_names


class TestAllTools:
    def test_has_four_tools(self):
        assert len(ALL_TOOLS) == 4

    def test_expected_names(self):
        names = {t.name for t in ALL_TOOLS}
        assert names == {"execute_python", "run_shell", "write_file", "read_file"}


class TestToolNames:
    def test_sandbox_server_name(self):
        result = tool_names("sandbox")
        assert result == [
            "mcp__sandbox__execute_python",
            "mcp__sandbox__run_shell",
            "mcp__sandbox__write_file",
            "mcp__sandbox__read_file",
        ]

    def test_different_server_name(self):
        result = tool_names("myserver")
        assert all(n.startswith("mcp__myserver__") for n in result)
        assert len(result) == 4
