import anyio
from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock, ToolUseBlock

from .agent import KeystoneAgent


async def repl() -> None:
    agent = KeystoneAgent()

    try:
        await agent.check_sandbox()
    except ConnectionError as e:
        print(str(e))
        return

    async with agent:
        print("\nThe Delegation Layer — type your request (quit to exit)\n")
        while True:
            try:
                prompt = await anyio.to_thread.run_sync(lambda: input("you> "))
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if prompt.strip().lower() in ("quit", "exit"):
                print("Goodbye!")
                break

            if not prompt.strip():
                continue

            await agent.client.query(prompt)
            async for message in agent.client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"\nagent> {block.text}")
                        elif isinstance(block, ToolUseBlock):
                            print(f"\n[{block.name}]")
                elif isinstance(message, ResultMessage):
                    pass
