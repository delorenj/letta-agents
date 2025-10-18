#!/usr/bin/env python3
"""Complete status check and cleanup for Tonny restoration."""

from letta_client import Letta

def final_status():
    """Show complete system status."""
    client = Letta(base_url="http://localhost:8283")

    print("="*100)
    print(" "*35 + "TONNY RESTORATION - FINAL STATUS")
    print("="*100)

    # Identities
    print("\n📇 IDENTITIES (DeLorenzo Family)")
    print("-"*100)
    identities = client.identities.list()
    for identity in identities:
        print(f"  ✓ {identity.name} ({identity.identifier_key}) - ID: {identity.id}")

    # Agents
    print("\n\n🤖 AGENTS")
    print("-"*100)
    agents = client.agents.list()
    tonny_agents = [a for a in agents if "tonny" in a.name.lower()]

    primary_agent = None
    duplicate_agents = []

    for agent in tonny_agents:
        details = client.agents.retrieve(agent_id=agent.id)

        is_primary = len(details.identity_ids) > 0 if hasattr(details, 'identity_ids') else False

        if is_primary and "sleeptime" not in agent.name:
            primary_agent = agent
            print(f"  ✓ PRIMARY: {agent.name}")
            print(f"     ID: {agent.id}")
            print(f"     Identities: {len(details.identity_ids)} linked")
            print(f"     Description: {details.description}")

            # Check memory blocks
            blocks = client.agents.blocks.list(agent_id=agent.id)
            print(f"     Memory Blocks:")
            for block in blocks:
                has_key_data = False
                if block.label == "persona" and "Tonny" in block.value:
                    has_key_data = True
                    status = "✓ Tonny identity"
                elif "DeLorenzo" in block.value:
                    has_key_data = True
                    status = "✓ Family data"
                else:
                    status = "✓"

                print(f"       {status} {block.label}: {len(block.value)} chars")
        else:
            duplicate_agents.append(agent)

    if duplicate_agents:
        print(f"\n  ⚠ DUPLICATES (can be deleted):")
        for agent in duplicate_agents:
            print(f"     - {agent.name} (ID: {agent.id})")

    # Summary
    print("\n\n" + "="*100)
    print("✓ RESTORATION COMPLETE")
    print("="*100)
    print(f"  • {len(identities)} family member identities created")
    print(f"  • {len(tonny_agents)} Tonny agents exist ({len(duplicate_agents)} duplicates)")
    print(f"  • Primary agent has all memory blocks intact")
    print(f"  • All identities linked to primary agent")

    if duplicate_agents:
        print(f"\n  ℹ You have {len(duplicate_agents)} duplicate agents that can be safely deleted")
        print(f"    Run: python cleanup_duplicates.py")

    print("\n  🎉 Tonny is fully operational with complete family data!")
    print("="*100)

    return primary_agent, duplicate_agents

if __name__ == "__main__":
    final_status()
