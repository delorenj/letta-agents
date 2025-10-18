"""Manager for Letta agent creation and configuration."""

import logging
from typing import Optional
from letta_client import Letta

from .config import LettaConfig
from .utils import handle_already_exists, AgentError

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages Letta agent lifecycle operations."""

    def __init__(self, client: Letta, config: LettaConfig):
        """
        Initialize the agent manager.

        Args:
            client: Letta client instance
            config: Letta configuration
        """
        self.client = client
        self.config = config

    def get_or_create_agent(
        self,
        agent_name: str,
        system_prompt: Optional[str] = None,
        tool_names: Optional[list[str]] = None,
        folder_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Get existing agent by name or create a new one.

        Args:
            agent_name: Name of the agent
            system_prompt: System prompt for the agent
            tool_names: List of tool names to attach
            folder_name: RAG folder to attach (optional)
            **kwargs: Additional agent configuration

        Returns:
            Agent ID

        Raises:
            AgentError: If agent operations fail
        """
        # Try to find existing agent
        try:
            agents = self.client.agents.list()
            for agent in agents:
                if agent.name == agent_name:
                    logger.info(f"Found existing agent '{agent_name}' (ID: {agent.id})")
                    return agent.id
        except Exception as e:
            logger.warning(f"Could not list agents: {e}")

        # Create new agent
        logger.info(f"Creating new agent '{agent_name}'...")

        try:
            # Build agent configuration
            agent_config = {
                "name": agent_name,
                "llm_config": {
                    "model": kwargs.get("llm_model", self.config.llm_model),
                    "model_endpoint_type": "openai",
                    "context_window": 128000,
                    "put_inner_thoughts_in_kwargs": True,
                },
                "embedding_config": {
                    "model": kwargs.get("embedding_model", self.config.embedding_model),
                    "embedding_endpoint_type": "ollama",
                    "embedding_model": kwargs.get("embedding_model", self.config.embedding_model),
                    "embedding_dim": 768,
                }
            }

            # Add system prompt if provided
            if system_prompt:
                agent_config["system"] = system_prompt

            # Add tools if provided
            if tool_names:
                agent_config["tools"] = tool_names

            # Create the agent
            agent = self.client.agents.create(**agent_config)

            logger.info(f"✅ Created agent '{agent_name}' (ID: {agent.id})")

            # Attach folder if specified
            if folder_name:
                try:
                    self.attach_folder_to_agent(agent.id, folder_name)
                except Exception as e:
                    logger.warning(f"Could not attach folder '{folder_name}': {e}")

            return agent.id

        except Exception as e:
            error_msg = f"Failed to create agent '{agent_name}'"
            logger.error(f"{error_msg}: {e}")
            raise AgentError(error_msg) from e

    def attach_folder_to_agent(self, agent_id: str, folder_name: str) -> None:
        """
        Attach a RAG folder to an agent.

        Args:
            agent_id: Agent ID
            folder_name: Name of the folder to attach

        Raises:
            AgentError: If attachment fails
        """
        try:
            logger.info(f"Attaching folder '{folder_name}' to agent {agent_id}...")

            # First, get the folder ID
            folders = self.client.folders.list()
            folder_id = None

            for folder in folders:
                if folder.name == folder_name:
                    folder_id = folder.id
                    break

            if not folder_id:
                raise AgentError(f"Folder '{folder_name}' not found")

            # Attach the folder to the agent
            self.client.agents.folders.attach(
                agent_id=agent_id,
                folder_id=folder_id
            )

            logger.info(f"✅ Attached folder '{folder_name}' to agent")

        except Exception as e:
            error_msg = f"Failed to attach folder to agent"
            logger.error(f"{error_msg}: {e}")
            raise AgentError(error_msg) from e

    def update_agent_tools(self, agent_id: str, tool_names: list[str]) -> None:
        """
        Update the tools available to an agent.

        Args:
            agent_id: Agent ID
            tool_names: List of tool names to attach

        Raises:
            AgentError: If update fails
        """
        try:
            logger.info(f"Updating agent {agent_id} with {len(tool_names)} tools...")

            self.client.agents.update(
                agent_id=agent_id,
                tools=tool_names
            )

            logger.info(f"✅ Updated agent tools")

        except Exception as e:
            error_msg = f"Failed to update agent tools"
            logger.error(f"{error_msg}: {e}")
            raise AgentError(error_msg) from e
