"""Manager for MCP server and tool registration with Letta."""

import logging
from typing import Optional
from letta_client import Letta

from .config import MetaMCPConfig
from .utils import (
    handle_already_exists,
    retry_on_failure,
    MCPServerError,
    ToolRegistrationError,
)

logger = logging.getLogger(__name__)


class MCPManager:
    """Manages MCP server and tool registration for Letta agents."""

    def __init__(self, client: Letta, config: MetaMCPConfig):
        """
        Initialize the MCP manager.

        Args:
            client: Letta client instance
            config: MetaMCP configuration
        """
        self.client = client
        self.config = config

    @retry_on_failure(max_attempts=3, delay=1.0, exceptions=(Exception,))
    def register_mcp_server(
        self,
        agent_name: str,
        force_recreate: bool = False
    ) -> str:
        """
        Register the MetaMCP hub endpoint as an MCP server in Letta.

        Args:
            agent_name: Name of the agent (used to determine endpoint)
            force_recreate: If True, delete and recreate if server exists

        Returns:
            The server name that was registered

        Raises:
            MCPServerError: If registration fails
        """
        server_name = self.config.get_server_name(agent_name)
        endpoint_url = self.config.get_endpoint(agent_name)

        logger.info(f"Registering MCP server '{server_name}' -> {endpoint_url}")

        # Check if server already exists
        if force_recreate:
            try:
                self.client.tools.delete_mcp_server(server_name=server_name)
                logger.info(f"Deleted existing MCP server '{server_name}'")
            except Exception as e:
                if "not found" not in str(e).lower():
                    logger.warning(f"Could not delete server '{server_name}': {e}")

        try:
            # Build the request payload
            request_payload = {
                "type": "streamable_http",
                "server_name": server_name,
                "server_url": endpoint_url,
            }

            # Add bearer token if configured
            if self.config.bearer_token:
                request_payload["bearerToken"] = self.config.bearer_token

            # Register the server
            self.client.tools.add_mcp_server(request=request_payload)

            logger.info(f"✅ Successfully registered MCP server: '{server_name}'")
            return server_name

        except Exception as e:
            if handle_already_exists(str(e)):
                logger.info(f"🔹 MCP server '{server_name}' already exists")
                return server_name
            else:
                error_msg = f"Failed to register MCP server '{server_name}'"
                logger.error(f"{error_msg}: {e}")
                raise MCPServerError(error_msg) from e

    def list_mcp_tools(self, server_name: str) -> list:
        """
        List all tools available from an MCP server.

        Args:
            server_name: Name of the MCP server

        Returns:
            List of tool objects

        Raises:
            MCPServerError: If listing fails
        """
        try:
            logger.info(f"Fetching tools from MCP server '{server_name}'...")

            available_tools = self.client.tools.list_mcp_tools_by_server(
                mcp_server_name=server_name
            )

            tools = available_tools.tools if hasattr(available_tools, 'tools') else available_tools
            logger.info(f"✅ Found {len(tools)} tools from '{server_name}'")

            return tools

        except Exception as e:
            error_msg = f"Failed to list tools from MCP server '{server_name}'"
            logger.error(f"{error_msg}: {e}")
            raise MCPServerError(error_msg) from e

    def register_mcp_tools(
        self,
        server_name: str,
        tool_filter: Optional[callable] = None,
        skip_existing: bool = True
    ) -> tuple[list[str], list[str]]:
        """
        Register all tools from an MCP server with Letta.

        Args:
            server_name: Name of the MCP server
            tool_filter: Optional function to filter tools (returns True to include)
            skip_existing: If True, skip tools that already exist

        Returns:
            Tuple of (successfully_registered_tools, failed_tools)

        Raises:
            ToolRegistrationError: If critical registration failure occurs
        """
        tools = self.list_mcp_tools(server_name)

        if tool_filter:
            tools = [tool for tool in tools if tool_filter(tool)]
            logger.info(f"Filtered to {len(tools)} tools based on filter criteria")

        registered_tools = []
        failed_tools = []

        for tool in tools:
            tool_name = tool.name if hasattr(tool, 'name') else str(tool)

            try:
                self.client.tools.add_mcp_tool(
                    mcp_server_name=server_name,
                    mcp_tool_name=tool_name,
                )

                registered_tools.append(tool_name)
                logger.debug(f"  ✅ Registered tool: {tool_name}")

            except Exception as e:
                if handle_already_exists(str(e)) and skip_existing:
                    registered_tools.append(tool_name)
                    logger.debug(f"  🔹 Tool already exists: {tool_name}")
                else:
                    failed_tools.append(tool_name)
                    logger.warning(f"  ❌ Failed to register tool '{tool_name}': {e}")

        logger.info(
            f"✅ Tool registration complete: "
            f"{len(registered_tools)} registered, "
            f"{len(failed_tools)} failed"
        )

        return registered_tools, failed_tools

    def setup_agent_mcp_tools(
        self,
        agent_name: str,
        force_recreate_server: bool = False,
        tool_filter: Optional[callable] = None
    ) -> tuple[str, list[str], list[str]]:
        """
        Complete MCP setup for an agent: register server and all tools.

        Args:
            agent_name: Name of the agent
            force_recreate_server: Whether to recreate the MCP server
            tool_filter: Optional filter function for tools

        Returns:
            Tuple of (server_name, registered_tools, failed_tools)
        """
        # Step 1: Register the MCP server
        server_name = self.register_mcp_server(
            agent_name=agent_name,
            force_recreate=force_recreate_server
        )

        # Step 2: Register all tools
        registered_tools, failed_tools = self.register_mcp_tools(
            server_name=server_name,
            tool_filter=tool_filter,
            skip_existing=True
        )

        return server_name, registered_tools, failed_tools
