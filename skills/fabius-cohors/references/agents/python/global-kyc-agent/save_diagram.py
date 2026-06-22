import asyncio

from dotenv import load_dotenv
from google.adk.cli.agent_graph import get_agent_graph

from global_kyc_agent.agent import root_agent

load_dotenv()


async def main():
    png_bytes = await get_agent_graph(root_agent, None, image=True)
    with open("agent_pattern.png", "wb") as f:
        f.write(png_bytes)
    print("Graph saved to agent_pattern.png")


if __name__ == "__main__":
    asyncio.run(main())
