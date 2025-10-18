#!/usr/bin/env python3
"""Verify Tonny's memory blocks are intact."""

from letta_client import Letta

def verify_tonny():
    """Check Tonny's memory blocks."""
    client = Letta(base_url="http://localhost:8283")

    # Get the most recent Tonny agent (not the _copy versions)
    agents = client.agents.list()

    # Find a Tonny agent
    tonny_agent = None
    for agent in agents:
        if "tonny-CTO-orchestrator" in agent.name and "sleeptime" not in agent.name:
            tonny_agent = agent
            break

    if not tonny_agent:
        print("ERROR: Could not find Tonny agent")
        return

    print(f"Found Tonny: {tonny_agent.name} (ID: {tonny_agent.id})")
    print("\n" + "="*80)

    # Get full agent details
    agent_details = client.agents.retrieve(agent_id=tonny_agent.id)

    print("\n📝 AGENT INFORMATION:")
    print("="*80)
    print(f"Name: {agent_details.name}")
    print(f"Description: {agent_details.description}")

    # Get memory blocks using the blocks accessor
    print("\n📝 MEMORY BLOCKS:")
    print("="*80)

    try:
        blocks = client.agents.blocks.list(agent_id=tonny_agent.id)
        for block in blocks:
            print(f"\n🔹 {block.label.upper()}")
            print(f"   Description: {block.description if hasattr(block, 'description') else 'N/A'}")
            print(f"   Size: {len(block.value)} chars / {block.limit} limit")
            print(f"   Content preview:")
            # Show first 300 chars
            preview = block.value[:300].replace('\n', '\n     ')
            print(f"     {preview}...")

            # Check for family member names
            if block.label == "persona" and "Tonny" in block.value:
                print("     ✓ Tonny persona found!")
            elif block.label == "human" and "DeLorenzo" in block.value:
                print("     ✓ DeLorenzo family information found!")
            elif block.label == "goals" and "DeLorenzo" in block.value:
                print("     ✓ Family goals found!")
    except Exception as e:
        print(f"  ⚠ Error accessing blocks: {e}")
        print(f"  Agent details: {agent_details}")

    print("\n" + "="*80)
    print("\n✓ Verification complete!")

if __name__ == "__main__":
    verify_tonny()
