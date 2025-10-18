#!/usr/bin/env python3
"""
Basic Setup Example for DeloNET Letta

This example demonstrates the simplest possible agent setup with MetaMCP integration.
It shows how to:
1. Initialize the orchestrator
2. Create an agent with MCP tools
3. Verify the setup

Prerequisites:
- Letta instance running (self-hosted or cloud)
- MetaMCP Hub accessible
- Environment variables configured (or .env file)

Environment Variables:
    LETTA_BASE_URL: Letta API endpoint (default: http://localhost:8283/v1)
    METAMCP_HUB_URL: MetaMCP hub URL (default: https://mcp.delo.sh/metamcp)

Optional:
    LETTA_TOKEN: Authentication token for Letta Cloud
    LETTA_PROJECT: Project name for Letta Cloud
"""

from delonet_letta import DeloNETLetta


def main():
    """Run basic agent setup example."""

    print("=" * 60)
    print("DeloNET Letta - Basic Setup Example")
    print("=" * 60)
    print()

    # Step 1: Initialize the orchestrator
    print("Step 1: Initializing DeloNET Letta orchestrator...")
    orchestrator = DeloNETLetta()
    print("✅ Orchestrator initialized")
    print()

    # Step 2: Setup a basic agent
    print("Step 2: Setting up agent 'basic-assistant'...")

    agent_name = "basic-assistant"
    system_prompt = """You are a helpful assistant with access to filesystem and git tools.

Your role is to help users with:
- Reading and analyzing files
- Checking git repository status
- Providing code insights

Always be precise and helpful in your responses."""

    results = orchestrator.setup_agent(
        agent_name=agent_name,
        system_prompt=system_prompt,
        enable_rag=False,  # No RAG for basic example
        sync_rag_folder=False
    )

    print("✅ Agent setup complete!")
    print()

    # Step 3: Display results
    print("=" * 60)
    print("Setup Results")
    print("=" * 60)
    print(f"Agent Name:    {results['agent_name']}")
    print(f"Agent ID:      {results['agent_id']}")
    print(f"MCP Server:    {results['mcp_server']}")
    print(f"Tools:         {len(results['tools_registered'])} registered, "
          f"{len(results['tools_failed'])} failed")
    print()

    # Step 4: List registered tools
    if results['tools_registered']:
        print("Registered Tools:")
        for i, tool_name in enumerate(results['tools_registered'][:10], 1):
            print(f"  {i}. {tool_name}")

        if len(results['tools_registered']) > 10:
            remaining = len(results['tools_registered']) - 10
            print(f"  ... and {remaining} more")
        print()

    # Step 5: Display failed tools if any
    if results['tools_failed']:
        print("⚠️  Failed Tools:")
        for tool_name in results['tools_failed']:
            print(f"  - {tool_name}")
        print()

    # Step 6: Next steps
    print("=" * 60)
    print("Next Steps")
    print("=" * 60)
    print()
    print("Your agent is now ready to use! You can:")
    print()
    print("1. Interact with the agent via the Letta API:")
    print(f"   agent_id = '{results['agent_id']}'")
    print()
    print("2. Send messages using the Letta client:")
    print("   from letta_client import Letta")
    print("   client = Letta(base_url='...')")
    print(f"   response = client.agents.send_message(")
    print(f"       agent_id='{results['agent_id']}',")
    print("       message='Hello! Can you help me?'")
    print("   )")
    print()
    print("3. View available tools:")
    print(f"   server_name = '{results['mcp_server']}'")
    print("   tools = orchestrator.mcp.list_mcp_tools(server_name)")
    print()
    print("4. Check out the advanced setup example for:")
    print("   - RAG integration")
    print("   - Tool filtering")
    print("   - Custom configurations")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print("\nTroubleshooting:")
        print("1. Verify Letta instance is running:")
        print("   curl http://localhost:8283/v1/health")
        print()
        print("2. Check environment variables:")
        print("   - LETTA_BASE_URL")
        print("   - METAMCP_HUB_URL")
        print()
        print("3. For Letta Cloud, ensure you have:")
        print("   - LETTA_TOKEN")
        print("   - LETTA_PROJECT")
        print()
        raise
