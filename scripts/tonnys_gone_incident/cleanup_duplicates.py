#!/usr/bin/env python3
"""Clean up duplicate Tonny agents."""

from letta_client import Letta


def cleanup_duplicates():
    """Delete duplicate Tonny agents, keeping only the primary one with identities."""
    client = Letta(base_url="http://localhost:8283")

    print("=" * 80)
    print("CLEANING UP DUPLICATE TONNY AGENTS")
    print("=" * 80)

    agents = client.agents.list()
    tonny_agents = [a for a in agents if "tonny" in a.name.lower()]

    # Find primary agent (has identity_ids)
    primary_agent = None
    duplicates = []

    for agent in tonny_agents:
        details = client.agents.retrieve(agent_id=agent.id)
        has_identities = (
            len(details.identity_ids) > 0 if hasattr(details, "identity_ids") else False
        )

        if "copy" in agent.name:
            duplicates.append(agent)

    print(f"\nFound {len(duplicates)} duplicate agents to delete:")

    for agent in duplicates:
        print(f"  - {agent.name} (ID: {agent.id})")

    response = input("\nDelete these agents? (yes/no): ")

    if response.lower() == "yes":
        deleted = 0
        for agent in duplicates:
            try:
                client.agents.delete(agent_id=agent.id)
                print(f"  ✓ Deleted: {agent.name}")
                deleted += 1
            except Exception as e:
                print(f"  ✗ Error deleting {agent.name}: {e}")

        print(f"\n✓ Deleted {deleted} duplicate agents")
    else:
        print("\nCanceled. No agents deleted.")

    print("=" * 80)


if __name__ == "__main__":
    cleanup_duplicates()
