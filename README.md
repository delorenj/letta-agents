# DeloNET Letta AgentForge

A Python SDK for managing Letta agents with MetaMCP integration, providing a hybrid architecture that combines RAG for semantic search with MCP for direct filesystem interaction.

## Overview

DeloNET Letta AgentForge is a control center for managing Letta AI agents with integrated MetaMCP Hub support. It implements a clean separation of concerns:

- **MCP (Model Context Protocol)**: Handles direct interaction with filesystems, git repositories, and other tools
- **RAG (Retrieval-Augmented Generation)**: Provides semantic search and discovery across your codebase

This architecture ensures agents have both powerful discovery capabilities (RAG) and direct read/write access (MCP) without the synchronization issues of treating RAG as a filesystem.

## Key Features

- **Unified Agent Management**: Simple API for creating and configuring Letta agents
- **MetaMCP Hub Integration**: Centralized proxy for aggregating multiple MCP servers
- **RAG Folder Synchronization**: Automatic syncing of local folders for semantic search
- **Tool Filtering**: Selective tool registration based on custom criteria
- **Error Handling**: Robust retry logic and graceful error handling
- **Configuration Management**: Environment-based configuration with sensible defaults

## Architecture

```

                    DeloNET Letta                        
                  (Orchestrator)                         
,,,
                                      
                                      
          
   MCP          Agent           RAG    
 Manager       Manager        Manager  
,     ,     ,
                                     
                                     
          
MetaMCP         Letta          Letta   
  Hub           Agents        Folders  
          
     
     

  MCP Servers (filesystem, git, etc) 

```

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/delonet-letta.git
cd delonet-letta

# Install with uv
uv pip install -e .

# For development
uv pip install -e ".[dev]"
```

### Using pip

```bash
pip install -e .

# For development
pip install -e ".[dev]"
```

## Quick Start

### 1. Environment Configuration

Create a `.env` file in your project root:

```bash
# Letta Configuration
LETTA_BASE_URL=http://localhost:8283/v1
LETTA_TOKEN=your_token_here  # Optional for self-hosted
LETTA_PROJECT=your_project   # Optional for self-hosted

# MetaMCP Hub Configuration
METAMCP_HUB_URL=https://mcp.delo.sh/metamcp
METAMCP_BEARER_TOKEN=your_token  # Optional

# RAG Configuration (optional)
RAG_LOCAL_FOLDER=/path/to/your/codebase
RAG_FOLDER_NAME=default_rag
```

### 2. Basic Usage

```python
from delonet_letta import DeloNETLetta

# Initialize the orchestrator
orchestrator = DeloNETLetta()

# Setup an agent with MCP and RAG
results = orchestrator.setup_agent(
    agent_name="my-devops-agent",
    system_prompt="You are a helpful DevOps assistant.",
    enable_rag=True,
    sync_rag_folder=True
)

print(f"Agent ID: {results['agent_id']}")
print(f"Tools registered: {len(results['tools_registered'])}")
```

### 3. CLI Usage

```bash
# Setup a new agent
delonet-letta setup my-agent

# List available tools for an agent
delonet-letta list-tools my-agent

# Sync RAG folder
delonet-letta sync-rag my-agent
```

## Configuration Guide

### Letta Configuration

The `LettaConfig` class manages Letta client connection settings:

```python
from delonet_letta import LettaConfig

config = LettaConfig(
    base_url="http://localhost:8283/v1",
    token="your_token",  # Required for Letta Cloud
    project="your_project",  # Required for Letta Cloud
    llm_model="openai/gpt-4",
    embedding_model="openai/text-embedding-3-small"
)
```

**Environment Variables:**
- `LETTA_BASE_URL`: Letta API endpoint (default: `http://localhost:8283/v1`)
- `LETTA_TOKEN`: Authentication token (required for Letta Cloud)
- `LETTA_PROJECT`: Project name (required for Letta Cloud)
- `LETTA_LLM_MODEL`: Default LLM model (default: `openai/gpt-4`)
- `LETTA_EMBEDDING_MODEL`: Default embedding model (default: `openai/text-embedding-3-small`)

### MetaMCP Configuration

The `MetaMCPConfig` class manages MetaMCP Hub integration:

```python
from delonet_letta import MetaMCPConfig

config = MetaMCPConfig(
    hub_base_url="https://mcp.delo.sh/metamcp",
    bearer_token="optional_token"
)

# Get agent-specific endpoint
endpoint = config.get_endpoint("my-agent")
# Returns: https://mcp.delo.sh/metamcp/my-agent/mcp
```

**Environment Variables:**
- `METAMCP_HUB_URL`: MetaMCP hub base URL (default: `https://mcp.delo.sh/metamcp`)
- `METAMCP_BEARER_TOKEN`: Optional bearer token for authentication

### RAG Configuration

The `RAGConfig` class manages RAG folder synchronization:

```python
from delonet_letta import RAGConfig
from pathlib import Path

config = RAGConfig(
    local_folder=Path("/path/to/codebase"),
    folder_name="my_rag_folder",
    duplicate_handling="replace",  # or "skip"
    include_patterns=["**/*.py", "**/*.md"],
    exclude_patterns=["**/__pycache__/**", "**/.git/**"]
)
```

**Environment Variables:**
- `RAG_LOCAL_FOLDER`: Local folder to sync
- `RAG_FOLDER_NAME`: Name of the Letta folder (default: `default_rag`)

## Usage Examples

### Setup Agent with Custom System Prompt

```python
from delonet_letta import DeloNETLetta

orchestrator = DeloNETLetta()

results = orchestrator.setup_agent(
    agent_name="code-reviewer",
    system_prompt="""You are an expert code reviewer. Your role is to:
    1. Review code for best practices
    2. Identify potential bugs and security issues
    3. Suggest improvements and optimizations
    """,
    enable_rag=True
)
```

### Setup Agent with Tool Filtering

```python
def filesystem_tools_only(tool):
    """Only include filesystem-related tools."""
    tool_name = tool.name if hasattr(tool, 'name') else str(tool)
    return tool_name.startswith('filesystem_')

results = orchestrator.setup_agent(
    agent_name="file-manager",
    tool_filter=filesystem_tools_only,
    enable_rag=False
)
```

### Manual RAG Synchronization

```python
from delonet_letta import DeloNETLetta
from pathlib import Path

orchestrator = DeloNETLetta()

# Sync a specific folder
successful, failed = orchestrator.rag.sync_folder(
    local_folder=Path("/path/to/docs"),
    folder_name="documentation_rag"
)

print(f"Synced {successful} files, {failed} failed")
```

### Register Additional Tools

```python
from delonet_letta import DeloNETLetta

orchestrator = DeloNETLetta()

# Get the MCP server name for an agent
server_name = orchestrator.metamcp_config.get_server_name("my-agent")

# List available tools
tools = orchestrator.mcp.list_mcp_tools(server_name)

# Register specific tools
registered, failed = orchestrator.mcp.register_mcp_tools(
    server_name=server_name,
    tool_filter=lambda tool: tool.name in ['filesystem_read', 'git_status']
)
```

## Understanding the Hybrid Architecture

### Why Not Use RAG as a Filesystem?

Letta Folders implement a RAG pipeline that:
1. Chunks file content
2. Creates vector embeddings
3. Stores for semantic search

This is a **one-way sync** for discovery, not a bidirectional filesystem. Attempting to use RAG for file editing creates synchronization nightmares.

### The Correct Workflow

1. **Discovery (RAG)**: Use `semantic_search_files` to find relevant files
   - "Where is the database connection logic?"
   - "Find all authentication-related code"

2. **Interaction (MCP)**: Use MCP tools for actual file operations
   - `filesystem_read_file` - Read the actual source file
   - `filesystem_write_file` - Modify the real file
   - `git_commit` - Commit changes

This separation ensures:
- No data drift between RAG index and actual files
- Semantic search for discovery
- Direct filesystem access for modifications
- Real-time operations on the source of truth

## CLI Reference

The `delonet-letta` CLI provides convenient commands for common operations:

```bash
# Setup a new agent with MCP and RAG
delonet-letta setup <agent_name>

# List all available MCP tools for an agent
delonet-letta list-tools <agent_name>

# Synchronize RAG folder for an agent
delonet-letta sync-rag <agent_name>
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format with black
black src/

# Lint with ruff
ruff check src/
```

### Project Structure

```
delonet-letta/
 src/delonet_letta/
    __init__.py          # Main orchestrator class
    config.py            # Configuration management
    utils.py             # Error handling and retries
    mcp_manager.py       # MCP server and tool registration
    agent_manager.py     # Agent lifecycle management
    rag_manager.py       # RAG folder synchronization
 docs/
    ARCHITECTURE.md      # Detailed architecture documentation
    API.md               # Complete API reference
 examples/
    basic_setup.py       # Simple usage example
    advanced_setup.py    # Advanced configuration
 pyproject.toml           # Project metadata and dependencies
 README.md                # This file
```

## Troubleshooting

### Connection Issues

If you encounter connection errors to Letta:

```python
# Verify your Letta instance is running
curl http://localhost:8283/v1/health

# Check your configuration
from delonet_letta import load_config
letta_config, _, _ = load_config()
print(f"Connecting to: {letta_config.base_url}")
```

### Tool Registration Failures

If tools fail to register:

```python
# List tools to verify they're available
tools = orchestrator.mcp.list_mcp_tools(server_name)
for tool in tools:
    print(tool.name)

# Check for specific error messages
results = orchestrator.setup_agent(
    agent_name="debug-agent",
    enable_rag=False
)
print(f"Failed tools: {results['tools_failed']}")
```

### RAG Sync Issues

If RAG sync fails:

```python
# Verify local folder exists
from pathlib import Path
local_folder = Path("/path/to/folder")
print(f"Exists: {local_folder.exists()}")
print(f"Is directory: {local_folder.is_dir()}")

# Check file patterns
from delonet_letta import RAGConfig
config = RAGConfig(local_folder=local_folder)
for file in local_folder.rglob("*"):
    if file.is_file():
        print(f"{file}: {config.should_include_file(file)}")
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

[Add your license here]

## Related Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - Detailed architecture and design decisions
- [API Reference](docs/API.md) - Complete API documentation
- [Examples](examples/) - Working code examples

## Credits

Built with:
- [Letta](https://letta.com) - Stateful AI agent framework
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) - Tool integration standard
- MetaMCP Hub - Centralized MCP server aggregation
