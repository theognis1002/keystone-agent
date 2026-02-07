from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, create_sdk_mcp_server

from .config import SYSTEM_PROMPT, MCP_SERVER_NAME, MCP_SERVER_VERSION, SANDBOX_URL
from .sandbox import sandbox
from .tools import ALL_TOOLS, tool_names


class KeystoneAgent:
    def __init__(self) -> None:
        server = create_sdk_mcp_server(
            name=MCP_SERVER_NAME,
            version=MCP_SERVER_VERSION,
            tools=ALL_TOOLS,
        )
        options = ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            mcp_servers={MCP_SERVER_NAME: server},
            allowed_tools=tool_names(MCP_SERVER_NAME),
            permission_mode="bypassPermissions",
        )
        self.client = ClaudeSDKClient(options=options)

    async def check_sandbox(self) -> None:
        print("Connecting to sandbox...")
        try:
            ctx = await sandbox.sandbox.get_context()
            print(f"Sandbox ready (version {ctx.version}, home: {ctx.home_dir})")
        except Exception as e:
            raise ConnectionError(
                f"Could not reach sandbox at {SANDBOX_URL}: {e}\n"
                "Start it with: docker run --security-opt seccomp=unconfined "
                "--rm -it -p 8081:8080 ghcr.io/agent-infra/sandbox:latest"
            ) from e

    async def connect(self) -> None:
        await self.client.__aenter__()

    async def disconnect(self) -> None:
        await self.client.__aexit__(None, None, None)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
