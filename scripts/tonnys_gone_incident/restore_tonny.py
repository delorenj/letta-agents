#!/usr/bin/env python3
"""Restore Tonny agent from .af backup file."""

from letta_client import Letta

def restore_tonny():
    """Import Tonny agent from .af file."""
    # Connect to local Letta server
    client = Letta(base_url="http://localhost:8283")

    # Path to the most recent Tonny backup
    af_file_path = "/home/delorenj/tonny-CTO-orchestrator.af"

    print(f"Restoring Tonny from: {af_file_path}")
    print("This may take a moment...\n")

    try:
        # Import the agent from .af file
        with open(af_file_path, "rb") as f:
            agent_state = client.agents.import_file(file=f)

        print(f"✓ SUCCESS! Tonny has been restored!")

        # The response contains information about imported agents
        print(f"  Import response: {agent_state}")

        # Check what's in the response
        if hasattr(agent_state, 'agents'):
            print(f"  Number of agents imported: {len(agent_state.agents)}")
            for agent in agent_state.agents:
                print(f"    - Agent: {agent}")

        # List all agents to confirm
        print("\nCurrent agents in system:")
        agents = client.agents.list()
        if isinstance(agents, list):
            for agent in agents:
                print(f"  - {agent.name} (ID: {agent.id})")
        else:
            for agent in agents.agents:
                print(f"  - {agent.name} (ID: {agent.id})")

        return agent_state

    except FileNotFoundError:
        print(f"ERROR: Could not find backup file at {af_file_path}")
        print("Available backup locations:")
        print("  - /home/delorenj/tonny-CTO-orchestrator.af")
        print("  - /home/delorenj/DevCloud/tonny-CTO-orchestrator.af")
        return None
    except Exception as e:
        print(f"ERROR during import: {e}")
        print(f"Error type: {type(e).__name__}")
        return None

if __name__ == "__main__":
    restore_tonny()
