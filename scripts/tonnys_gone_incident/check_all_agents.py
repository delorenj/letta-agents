#!/usr/bin/env python3
"""Check all Tonny agent copies for memory blocks."""

from letta_client import Letta

def check_all_agents():
    """Check every Tonny agent."""
    client = Letta(base_url="http://localhost:8283")

    agents = client.agents.list()
    tonny_agents = [a for a in agents if "tonny" in a.name.lower()]

    print(f"Found {len(tonny_agents)} Tonny agents\n")
    print("="*100)

    for agent in tonny_agents:
        print(f"\n🤖 Agent: {agent.name}")
        print(f"   ID: {agent.id}")

        # Get full details
        details = client.agents.retrieve(agent_id=agent.id)
        print(f"   Description: {details.description}")

        # Check blocks
        try:
            blocks = client.agents.blocks.list(agent_id=agent.id)
            print(f"   Memory Blocks: {len(blocks)} blocks found")

            for block in blocks:
                has_content = len(block.value.strip()) > 0
                status = "✓" if has_content else "✗ EMPTY"
                print(f"     {status} {block.label}: {len(block.value)} chars")

                # Check for key content
                if block.label == "persona" and "Tonny" in block.value:
                    print(f"        → Contains Tonny identity")
                if "DeLorenzo" in block.value:
                    print(f"        → Contains DeLorenzo family info")

        except Exception as e:
            print(f"   ✗ Error accessing blocks: {e}")

        print("-"*100)

if __name__ == "__main__":
    check_all_agents()
