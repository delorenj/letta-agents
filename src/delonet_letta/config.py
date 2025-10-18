"""Configuration management for DeloNET Letta integration."""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class LettaConfig:
    """Configuration for Letta client connection."""

    # Letta connection settings
    base_url: str = field(default_factory=lambda: os.getenv("LETTA_BASE_URL", "http://localhost:8283"))
    token: Optional[str] = field(default_factory=lambda: os.getenv("LETTA_TOKEN"))
    project: Optional[str] = field(default_factory=lambda: os.getenv("LETTA_PROJECT"))

    # Default model configuration
    llm_model: str = field(default_factory=lambda: os.getenv("LETTA_LLM_MODEL", "openai/gpt-4"))
    embedding_model: str = field(default_factory=lambda: os.getenv("LETTA_EMBEDDING_MODEL", "openai/text-embedding-3-small"))

    def __post_init__(self):
        """Validate configuration."""
        # For self-hosted Letta, token and project are optional
        # For Letta Cloud, they are required
        if "letta.com" in self.base_url.lower() or "api.letta" in self.base_url.lower():
            if not self.token:
                raise ValueError("LETTA_TOKEN is required for Letta Cloud")
            if not self.project:
                raise ValueError("LETTA_PROJECT is required for Letta Cloud")

    @property
    def is_cloud(self) -> bool:
        """Check if using Letta Cloud."""
        return "letta.com" in self.base_url.lower() or "api.letta" in self.base_url.lower()


@dataclass
class MetaMCPConfig:
    """Configuration for MetaMCP hub integration."""

    # MetaMCP hub base URL
    hub_base_url: str = field(default_factory=lambda: os.getenv("METAMCP_HUB_URL", "https://mcp.delo.sh/metamcp"))

    # Optional bearer token for MetaMCP hub authentication
    bearer_token: Optional[str] = field(default_factory=lambda: os.getenv("METAMCP_BEARER_TOKEN"))

    def get_endpoint(self, agent_name: str) -> str:
        """Generate the MetaMCP endpoint URL for a specific agent."""
        return f"{self.hub_base_url}/{agent_name}/mcp"

    def get_server_name(self, agent_name: str) -> str:
        """Generate a consistent MCP server name for Letta registration."""
        return f"metamcp_{agent_name}_proxy"


@dataclass
class RAGConfig:
    """Configuration for RAG folder synchronization."""

    # Local folder to sync
    local_folder: Optional[Path] = None

    # Letta folder name
    folder_name: str = "default_rag"

    # Duplicate handling strategy
    duplicate_handling: str = "replace"  # or "skip"

    # File patterns to include (glob patterns)
    include_patterns: list[str] = field(default_factory=lambda: ["**/*.py", "**/*.md", "**/*.txt", "**/*.json"])

    # File patterns to exclude
    exclude_patterns: list[str] = field(default_factory=lambda: [
        "**/__pycache__/**",
        "**/.git/**",
        "**/node_modules/**",
        "**/.venv/**",
        "**/venv/**",
        "**/*.pyc",
    ])

    def __post_init__(self):
        """Convert string path to Path object if needed."""
        if isinstance(self.local_folder, str):
            self.local_folder = Path(self.local_folder)


def load_config() -> tuple[LettaConfig, MetaMCPConfig, RAGConfig]:
    """
    Load all configuration from environment variables.

    Returns:
        Tuple of (LettaConfig, MetaMCPConfig, RAGConfig)

    Raises:
        ValueError: If required configuration is missing
    """
    # Try to load from .env file if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    letta_config = LettaConfig()
    metamcp_config = MetaMCPConfig()

    # RAG config from environment
    rag_folder = os.getenv("RAG_LOCAL_FOLDER")
    rag_config = RAGConfig(
        local_folder=Path(rag_folder) if rag_folder else None,
        folder_name=os.getenv("RAG_FOLDER_NAME", "default_rag"),
    )

    return letta_config, metamcp_config, rag_config
