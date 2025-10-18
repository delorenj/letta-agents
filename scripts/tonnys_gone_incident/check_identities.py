#!/usr/bin/env python3
"""Check and restore Letta identities."""

from letta_client import Letta
import json

def check_identities():
    """Check current identities in the system."""
    client = Letta(base_url="http://localhost:8283")

    print("="*80)
    print("IDENTITIES IN SYSTEM")
    print("="*80)

    try:
        identities = client.identities.list()

        if isinstance(identities, list):
            print(f"Found {len(identities)} identities:")
            for identity in identities:
                print(f"\n  ID: {identity.id if hasattr(identity, 'id') else 'N/A'}")
                print(f"  Name: {identity.name if hasattr(identity, 'name') else 'N/A'}")
                if hasattr(identity, 'metadata'):
                    print(f"  Metadata: {identity.metadata}")
        else:
            print(f"Identities object: {identities}")
            print(f"Type: {type(identities)}")

    except Exception as e:
        print(f"Error listing identities: {e}")
        print(f"Error type: {type(e).__name__}")

    # Check what an identity object looks like
    print("\n" + "="*80)
    print("IDENTITY METHODS")
    print("="*80)
    print([m for m in dir(client.identities) if not m.startswith('_')])

    # Check agents' identity_ids
    print("\n" + "="*80)
    print("AGENT IDENTITY LINKS")
    print("="*80)

    agents = client.agents.list()
    for agent in [a for a in agents if "tonny" in a.name.lower()][:1]:  # Just check one
        details = client.agents.retrieve(agent_id=agent.id)
        print(f"\nAgent: {agent.name}")
        print(f"  identity_ids: {details.identity_ids if hasattr(details, 'identity_ids') else 'N/A'}")

if __name__ == "__main__":
    check_identities()
