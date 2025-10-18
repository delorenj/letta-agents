"""DeloNET Letta - Control center for the DeLoNET Letta AgentForge."""

import logging
from typing import Optional
from letta_client import Letta

from .config import load_config, LettaConfig, MetaMCPConfig, RAGConfig
from .mcp_manager import MCPManager
from .agent_manager import AgentManager
from .rag_manager import RAGManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class DeloNETLetta:
    """Main orchestrator for DeloNET Letta integration."""

    def __init__(
        self,
        letta_config: Optional[LettaConfig] = None,
        metamcp_config: Optional[MetaMCPConfig] = None,
        rag_config: Optional[RAGConfig] = None
    ):
        """
        Initialize DeloNET Letta orchestrator.

        Args:
            letta_config: Letta configuration (loads from env if None)
            metamcp_config: MetaMCP configuration (loads from env if None)
            rag_config: RAG configuration (loads from env if None)
        """
        # Load config if not provided
        if not all([letta_config, metamcp_config, rag_config]):
            loaded_letta, loaded_metamcp, loaded_rag = load_config()
            letta_config = letta_config or loaded_letta
            metamcp_config = metamcp_config or loaded_metamcp
            rag_config = rag_config or loaded_rag

        self.letta_config = letta_config
        self.metamcp_config = metamcp_config
        self.rag_config = rag_config

        # Initialize Letta client
        client_kwargs = {"base_url": letta_config.base_url}

        if letta_config.token:
            client_kwargs["token"] = letta_config.token

        if letta_config.project:
            client_kwargs["project"] = letta_config.project

        self.client = Letta(**client_kwargs)

        # Initialize managers
        self.mcp = MCPManager(self.client, metamcp_config)
        self.agents = AgentManager(self.client, letta_config)
        self.rag = RAGManager(self.client, rag_config)

        logger.info("✅ DeloNET Letta initialized successfully")

    def setup_agent(
        self,
        agent_name: str,
        system_prompt: Optional[str] = None,
        enable_rag: bool = False,
        sync_rag_folder: bool = False,
        tool_filter: Optional[callable] = None,
        **agent_kwargs
    ) -> dict:
        """
        Complete setup for a Letta agent with MetaMCP integration.

        Args:
            agent_name: Name of the agent
            system_prompt: System prompt for the agent
            enable_rag: Whether to create/attach a RAG folder
            sync_rag_folder: Whether to sync local folder to RAG
            tool_filter: Optional filter for MCP tools
            **agent_kwargs: Additional agent configuration

        Returns:
            Dictionary with setup results
        """
        logger.info(f"🚀 Setting up agent '{agent_name}'...")

        results = {
            "agent_name": agent_name,
            "agent_id": None,
            "mcp_server": None,
            "tools_registered": [],
            "tools_failed": [],
            "rag_folder": None,
            "rag_sync_stats": None,
        }

        # Step 1: Setup MCP server and tools
        logger.info("Step 1/3: Registering MCP server and tools...")
        server_name, registered_tools, failed_tools = self.mcp.setup_agent_mcp_tools(
            agent_name=agent_name,
            tool_filter=tool_filter
        )

        results["mcp_server"] = server_name
        results["tools_registered"] = registered_tools
        results["tools_failed"] = failed_tools

        # Step 2: Setup RAG folder if requested
        folder_name = None
        if enable_rag:
            logger.info("Step 2/3: Setting up RAG folder...")
            folder_name = f"{agent_name}_rag"
            folder_id = self.rag.get_or_create_folder(folder_name)
            results["rag_folder"] = folder_name

            # Sync folder if requested
            if sync_rag_folder and self.rag_config.local_folder:
                successful, failed = self.rag.sync_folder(folder_name=folder_name)
                results["rag_sync_stats"] = {
                    "successful": successful,
                    "failed": failed
                }
        else:
            logger.info("Step 2/3: Skipping RAG setup (not requested)")

        # Step 3: Create or get agent
        logger.info("Step 3/3: Creating/updating agent...")
        agent_id = self.agents.get_or_create_agent(
            agent_name=agent_name,
            system_prompt=system_prompt,
            tool_names=registered_tools,
            folder_name=folder_name,
            **agent_kwargs
        )

        results["agent_id"] = agent_id

        logger.info(f"🎉 Agent '{agent_name}' setup complete!")
        return results


def main() -> None:
    """CLI entry point for delonet-letta."""
    import sys

    if len(sys.argv) < 2:
        print("DeloNET Letta - Control center for the DeLoNET Letta AgentForge")
        print("\nUsage: delonet-letta <command> [args]")
        print("\nCommands:")
        print("  setup <agent_name>     - Setup a new agent with MCP integration")
        print("  list-tools <agent>     - List available MCP tools for an agent")
        print("  sync-rag <agent>       - Sync RAG folder for an agent")
        return

    command = sys.argv[1]

    try:
        orchestrator = DeloNETLetta()

        if command == "setup":
            if len(sys.argv) < 3:
                print("Error: agent_name required")
                return

            agent_name = sys.argv[2]
            results = orchestrator.setup_agent(
                agent_name=agent_name,
                enable_rag=True,
                sync_rag_folder=True
            )

            print(f"\n✅ Agent setup complete!")
            print(f"  Agent ID: {results['agent_id']}")
            print(f"  MCP Server: {results['mcp_server']}")
            print(f"  Tools: {len(results['tools_registered'])} registered")

        elif command == "list-tools":
            if len(sys.argv) < 3:
                print("Error: agent_name required")
                return

            agent_name = sys.argv[2]
            server_name = orchestrator.metamcp_config.get_server_name(agent_name)
            tools = orchestrator.mcp.list_mcp_tools(server_name)

            print(f"\n📋 Available tools from '{server_name}':")
            for tool in tools:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                print(f"  - {tool_name}")

        elif command == "sync-rag":
            if len(sys.argv) < 3:
                print("Error: agent_name required")
                return

            agent_name = sys.argv[2]
            folder_name = f"{agent_name}_rag"

            successful, failed = orchestrator.rag.sync_folder(folder_name=folder_name)
            print(f"\n✅ RAG sync complete: {successful} uploaded, {failed} failed")

        else:
            print(f"Unknown command: {command}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


# Public API
__all__ = [
    'DeloNETLetta',
    'LettaConfig',
    'MetaMCPConfig',
    'RAGConfig',
    'MCPManager',
    'AgentManager',
    'RAGManager',
]
