#!/usr/bin/env python3
"""Link DeLorenzo family identities to Tonny agent."""

from letta_client import Letta

def link_identities():
    """Link all family identities to Tonny."""
    client = Letta(base_url="http://localhost:8283")

    # Get all identities
    identities = client.identities.list()
    identity_ids = [identity.id for identity in identities]

    print("="*80)
    print("LINKING IDENTITIES TO TONNY")
    print("="*80)

    print(f"\nFound {len(identity_ids)} identities to link:")
    for identity in identities:
        print(f"  - {identity.name} ({identity.identifier_key})")

    # Get the primary Tonny agent (non-sleeptime)
    agents = client.agents.list()
    tonny_agents = [a for a in agents if "tonny-CTO-orchestrator" in a.name and "sleeptime" not in a.name]

    if not tonny_agents:
        print("\n✗ No Tonny agent found!")
        return

    # Use the first non-sleeptime Tonny
    tonny = tonny_agents[0]

    print(f"\n\nLinking to agent: {tonny.name}")
    print(f"Agent ID: {tonny.id}")

    try:
        # Update the agent to include all identity_ids
        updated_agent = client.agents.modify(
            agent_id=tonny.id,
            identity_ids=identity_ids
        )

        print(f"\n✓ Successfully linked {len(identity_ids)} identities to Tonny!")

        # Verify
        agent_details = client.agents.retrieve(agent_id=tonny.id)
        print(f"\nVerification - Agent identity_ids: {agent_details.identity_ids}")

    except Exception as e:
        print(f"\n✗ Error linking identities: {e}")
        print(f"Error type: {type(e).__name__}")

    print("\n" + "="*80)

if __name__ == "__main__":
    link_identities()
