# API Reference

Complete API reference for DeloNET Letta AgentForge.

## Table of Contents

- [DeloNETLetta](#delonetletta)
- [MCPManager](#mcpmanager)
- [AgentManager](#agentmanager)
- [RAGManager](#ragmanager)
- [Configuration Classes](#configuration-classes)
- [Utility Functions](#utility-functions)
- [Exceptions](#exceptions)

## DeloNETLetta

Main orchestrator class for managing Letta agents with MetaMCP integration.

**Module**: `delonet_letta`

### Constructor

```python
DeloNETLetta(
    letta_config: Optional[LettaConfig] = None,
    metamcp_config: Optional[MetaMCPConfig] = None,
    rag_config: Optional[RAGConfig] = None
)
```

Initialize the DeloNET Letta orchestrator.

**Parameters:**
- `letta_config` (Optional[LettaConfig]): Letta configuration. If None, loads from environment.
- `metamcp_config` (Optional[MetaMCPConfig]): MetaMCP configuration. If None, loads from environment.
- `rag_config` (Optional[RAGConfig]): RAG configuration. If None, loads from environment.

**Attributes:**
- `client` (Letta): Letta client instance
- `mcp` (MCPManager): MCP manager instance
- `agents` (AgentManager): Agent manager instance
- `rag` (RAGManager): RAG manager instance
- `letta_config` (LettaConfig): Letta configuration
- `metamcp_config` (MetaMCPConfig): MetaMCP configuration
- `rag_config` (RAGConfig): RAG configuration

**Example:**
```python
from delonet_letta import DeloNETLetta

# Use environment variables
orchestrator = DeloNETLetta()

# Custom configuration
from delonet_letta import LettaConfig

config = LettaConfig(base_url="http://localhost:8283/v1")
orchestrator = DeloNETLetta(letta_config=config)
```

### setup_agent()

```python
setup_agent(
    agent_name: str,
    system_prompt: Optional[str] = None,
    enable_rag: bool = False,
    sync_rag_folder: bool = False,
    tool_filter: Optional[callable] = None,
    **agent_kwargs
) -> dict
```

Complete setup for a Letta agent with MetaMCP integration.

**Parameters:**
- `agent_name` (str): Name of the agent (unique identifier)
- `system_prompt` (Optional[str]): System prompt defining agent behavior
- `enable_rag` (bool): Whether to create and attach a RAG folder. Default: False
- `sync_rag_folder` (bool): Whether to sync local folder to RAG. Default: False
- `tool_filter` (Optional[callable]): Function to filter tools. Takes tool object, returns bool
- `**agent_kwargs`: Additional agent configuration (llm_model, embedding_model, etc.)

**Returns:**
Dictionary with the following keys:
- `agent_name` (str): Name of the agent
- `agent_id` (str): Letta agent ID
- `mcp_server` (str): Name of registered MCP server
- `tools_registered` (list[str]): Successfully registered tool names
- `tools_failed` (list[str]): Failed tool names
- `rag_folder` (Optional[str]): RAG folder name if enabled
- `rag_sync_stats` (Optional[dict]): Sync statistics if synced
  - `successful` (int): Number of files uploaded
  - `failed` (int): Number of failed uploads

**Raises:**
- `MCPServerError`: If MCP server registration fails
- `ToolRegistrationError`: If critical tool registration fails
- `AgentError`: If agent creation fails

**Example:**
```python
# Basic setup
results = orchestrator.setup_agent(
    agent_name="my-agent",
    system_prompt="You are a helpful assistant."
)

# With RAG enabled
results = orchestrator.setup_agent(
    agent_name="code-agent",
    system_prompt="You are a code assistant.",
    enable_rag=True,
    sync_rag_folder=True
)

# With tool filtering
def filesystem_only(tool):
    return tool.name.startswith('filesystem_')

results = orchestrator.setup_agent(
    agent_name="file-agent",
    tool_filter=filesystem_only
)

print(f"Agent ID: {results['agent_id']}")
print(f"Tools: {len(results['tools_registered'])}")
```

---

## MCPManager

Manages MCP server and tool registration for Letta agents.

**Module**: `delonet_letta.mcp_manager`

### Constructor

```python
MCPManager(
    client: Letta,
    config: MetaMCPConfig
)
```

Initialize the MCP manager.

**Parameters:**
- `client` (Letta): Letta client instance
- `config` (MetaMCPConfig): MetaMCP configuration

**Note:** Typically instantiated by DeloNETLetta, not directly.

### register_mcp_server()

```python
register_mcp_server(
    agent_name: str,
    force_recreate: bool = False
) -> str
```

Register the MetaMCP hub endpoint as an MCP server in Letta.

**Parameters:**
- `agent_name` (str): Name of the agent (determines endpoint URL)
- `force_recreate` (bool): If True, delete and recreate if server exists. Default: False

**Returns:**
- `str`: The server name that was registered

**Raises:**
- `MCPServerError`: If registration fails

**Retry Behavior:**
- Maximum attempts: 3
- Initial delay: 1.0 seconds
- Backoff multiplier: 2.0

**Example:**
```python
server_name = orchestrator.mcp.register_mcp_server(
    agent_name="devops-agent"
)
# Returns: "metamcp_devops-agent_proxy"
```

### list_mcp_tools()

```python
list_mcp_tools(
    server_name: str
) -> list
```

List all tools available from an MCP server.

**Parameters:**
- `server_name` (str): Name of the MCP server

**Returns:**
- `list`: List of tool objects with `.name` attribute

**Raises:**
- `MCPServerError`: If listing fails

**Example:**
```python
server_name = orchestrator.metamcp_config.get_server_name("my-agent")
tools = orchestrator.mcp.list_mcp_tools(server_name)

for tool in tools:
    print(f"Tool: {tool.name}")
```

### register_mcp_tools()

```python
register_mcp_tools(
    server_name: str,
    tool_filter: Optional[callable] = None,
    skip_existing: bool = True
) -> tuple[list[str], list[str]]
```

Register all tools from an MCP server with Letta.

**Parameters:**
- `server_name` (str): Name of the MCP server
- `tool_filter` (Optional[callable]): Function that takes a tool object and returns bool. Only tools returning True are registered
- `skip_existing` (bool): If True, skip tools that already exist. Default: True

**Returns:**
- `tuple[list[str], list[str]]`: (successfully_registered_tools, failed_tools)

**Example:**
```python
# Register all tools
registered, failed = orchestrator.mcp.register_mcp_tools(
    server_name="metamcp_agent_proxy"
)

# Register with filter
def read_only(tool):
    return 'read' in tool.name.lower()

registered, failed = orchestrator.mcp.register_mcp_tools(
    server_name="metamcp_agent_proxy",
    tool_filter=read_only
)

print(f"Registered: {len(registered)}, Failed: {len(failed)}")
```

### setup_agent_mcp_tools()

```python
setup_agent_mcp_tools(
    agent_name: str,
    force_recreate_server: bool = False,
    tool_filter: Optional[callable] = None
) -> tuple[str, list[str], list[str]]
```

Complete MCP setup for an agent: register server and all tools.

**Parameters:**
- `agent_name` (str): Name of the agent
- `force_recreate_server` (bool): Whether to recreate the MCP server. Default: False
- `tool_filter` (Optional[callable]): Optional filter function for tools

**Returns:**
- `tuple[str, list[str], list[str]]`: (server_name, registered_tools, failed_tools)

**Example:**
```python
server, registered, failed = orchestrator.mcp.setup_agent_mcp_tools(
    agent_name="my-agent"
)
```

---

## AgentManager

Manages Letta agent lifecycle operations.

**Module**: `delonet_letta.agent_manager`

### Constructor

```python
AgentManager(
    client: Letta,
    config: LettaConfig
)
```

Initialize the agent manager.

**Parameters:**
- `client` (Letta): Letta client instance
- `config` (LettaConfig): Letta configuration

**Note:** Typically instantiated by DeloNETLetta, not directly.

### get_or_create_agent()

```python
get_or_create_agent(
    agent_name: str,
    system_prompt: Optional[str] = None,
    tool_names: Optional[list[str]] = None,
    folder_name: Optional[str] = None,
    **kwargs
) -> str
```

Get existing agent by name or create a new one.

**Parameters:**
- `agent_name` (str): Name of the agent
- `system_prompt` (Optional[str]): System prompt for the agent
- `tool_names` (Optional[list[str]]): List of tool names to attach
- `folder_name` (Optional[str]): RAG folder to attach
- `**kwargs`: Additional agent configuration
  - `llm_model` (str): LLM model override
  - `embedding_model` (str): Embedding model override

**Returns:**
- `str`: Agent ID

**Raises:**
- `AgentError`: If agent operations fail

**Idempotency:**
This method is idempotent. If an agent with the same name exists, it returns the existing agent's ID.

**Example:**
```python
agent_id = orchestrator.agents.get_or_create_agent(
    agent_name="code-reviewer",
    system_prompt="You review code for quality.",
    tool_names=["filesystem_read", "git_status"],
    folder_name="codebase_rag",
    llm_model="openai/gpt-4-turbo"
)
```

### attach_folder_to_agent()

```python
attach_folder_to_agent(
    agent_id: str,
    folder_name: str
) -> None
```

Attach a RAG folder to an agent.

**Parameters:**
- `agent_id` (str): Agent ID
- `folder_name` (str): Name of the folder to attach

**Raises:**
- `AgentError`: If attachment fails or folder not found

**Example:**
```python
orchestrator.agents.attach_folder_to_agent(
    agent_id="agent-123",
    folder_name="documentation_rag"
)
```

### update_agent_tools()

```python
update_agent_tools(
    agent_id: str,
    tool_names: list[str]
) -> None
```

Update the tools available to an agent.

**Parameters:**
- `agent_id` (str): Agent ID
- `tool_names` (list[str]): List of tool names to attach

**Raises:**
- `AgentError`: If update fails

**Example:**
```python
orchestrator.agents.update_agent_tools(
    agent_id="agent-123",
    tool_names=["filesystem_read", "filesystem_write", "git_commit"]
)
```

---

## RAGManager

Manages RAG folder synchronization for semantic search.

**Module**: `delonet_letta.rag_manager`

### Constructor

```python
RAGManager(
    client: Letta,
    config: RAGConfig
)
```

Initialize the RAG manager.

**Parameters:**
- `client` (Letta): Letta client instance
- `config` (RAGConfig): RAG configuration

**Note:** Typically instantiated by DeloNETLetta, not directly.

### get_or_create_folder()

```python
get_or_create_folder(
    folder_name: Optional[str] = None
) -> str
```

Get existing folder or create a new one.

**Parameters:**
- `folder_name` (Optional[str]): Name of the folder. If None, uses config default

**Returns:**
- `str`: Folder ID

**Idempotency:**
This method is idempotent. If a folder with the same name exists, it returns the existing folder's ID.

**Example:**
```python
folder_id = orchestrator.rag.get_or_create_folder("my_rag_folder")
```

### should_include_file()

```python
should_include_file(
    file_path: Path
) -> bool
```

Check if a file should be included based on patterns.

**Parameters:**
- `file_path` (Path): Path to the file

**Returns:**
- `bool`: True if file should be included

**Logic:**
1. Check exclude patterns first - if matched, return False
2. If no include patterns specified, return True
3. Check include patterns - if matched, return True
4. Otherwise return False

**Example:**
```python
from pathlib import Path

file_path = Path("/path/to/file.py")
if orchestrator.rag.should_include_file(file_path):
    print("File will be synced")
```

### sync_folder()

```python
sync_folder(
    local_folder: Optional[Path] = None,
    folder_name: Optional[str] = None,
    progress_callback: Optional[callable] = None
) -> tuple[int, int]
```

Sync a local folder to Letta RAG storage.

**Parameters:**
- `local_folder` (Optional[Path]): Local folder to sync. If None, uses config default
- `folder_name` (Optional[str]): Letta folder name. If None, uses config default
- `progress_callback` (Optional[callable]): Callback function with signature:
  ```python
  def callback(current: int, total: int, file_path: Path) -> None:
      pass
  ```

**Returns:**
- `tuple[int, int]`: (successful_uploads, failed_uploads)

**Raises:**
- `ValueError`: If no local folder specified or folder doesn't exist

**Example:**
```python
from pathlib import Path

# Simple sync
successful, failed = orchestrator.rag.sync_folder(
    local_folder=Path("/path/to/codebase"),
    folder_name="codebase_rag"
)
print(f"Synced {successful} files, {failed} failed")

# With progress callback
def show_progress(current, total, file_path):
    print(f"[{current}/{total}] Uploading {file_path.name}")

successful, failed = orchestrator.rag.sync_folder(
    local_folder=Path("/path/to/codebase"),
    folder_name="codebase_rag",
    progress_callback=show_progress
)
```

---

## Configuration Classes

### LettaConfig

Configuration for Letta client connection.

**Module**: `delonet_letta.config`

```python
@dataclass
class LettaConfig:
    base_url: str = "http://localhost:8283/v1"
    token: Optional[str] = None
    project: Optional[str] = None
    llm_model: str = "openai/gpt-4"
    embedding_model: str = "openai/text-embedding-3-small"
```

**Attributes:**
- `base_url` (str): Letta API endpoint. Default from `LETTA_BASE_URL` env var
- `token` (Optional[str]): Authentication token. Default from `LETTA_TOKEN` env var. Required for Letta Cloud
- `project` (Optional[str]): Project name. Default from `LETTA_PROJECT` env var. Required for Letta Cloud
- `llm_model` (str): Default LLM model. Default from `LETTA_LLM_MODEL` env var
- `embedding_model` (str): Default embedding model. Default from `LETTA_EMBEDDING_MODEL` env var

**Properties:**
- `is_cloud` (bool): Returns True if using Letta Cloud

**Validation:**
- Automatically detects Letta Cloud (URL contains "letta.com" or "api.letta")
- Requires `token` and `project` for Letta Cloud deployments

**Example:**
```python
from delonet_letta import LettaConfig

# Self-hosted
config = LettaConfig(
    base_url="http://localhost:8283/v1"
)

# Letta Cloud
config = LettaConfig(
    base_url="https://api.letta.com",
    token="your-token",
    project="your-project"
)

print(f"Is Cloud: {config.is_cloud}")
```

### MetaMCPConfig

Configuration for MetaMCP hub integration.

**Module**: `delonet_letta.config`

```python
@dataclass
class MetaMCPConfig:
    hub_base_url: str = "https://mcp.delo.sh/metamcp"
    bearer_token: Optional[str] = None
```

**Attributes:**
- `hub_base_url` (str): MetaMCP hub base URL. Default from `METAMCP_HUB_URL` env var
- `bearer_token` (Optional[str]): Bearer token for authentication. Default from `METAMCP_BEARER_TOKEN` env var

**Methods:**

#### get_endpoint()

```python
get_endpoint(agent_name: str) -> str
```

Generate the MetaMCP endpoint URL for a specific agent.

**Parameters:**
- `agent_name` (str): Name of the agent

**Returns:**
- `str`: Full endpoint URL

**Example:**
```python
config = MetaMCPConfig()
url = config.get_endpoint("devops-agent")
# Returns: "https://mcp.delo.sh/metamcp/devops-agent/mcp"
```

#### get_server_name()

```python
get_server_name(agent_name: str) -> str
```

Generate a consistent MCP server name for Letta registration.

**Parameters:**
- `agent_name` (str): Name of the agent

**Returns:**
- `str`: Server name

**Example:**
```python
config = MetaMCPConfig()
name = config.get_server_name("devops-agent")
# Returns: "metamcp_devops-agent_proxy"
```

### RAGConfig

Configuration for RAG folder synchronization.

**Module**: `delonet_letta.config`

```python
@dataclass
class RAGConfig:
    local_folder: Optional[Path] = None
    folder_name: str = "default_rag"
    duplicate_handling: str = "replace"
    include_patterns: list[str] = field(default_factory=lambda: [
        "**/*.py", "**/*.md", "**/*.txt", "**/*.json"
    ])
    exclude_patterns: list[str] = field(default_factory=lambda: [
        "**/__pycache__/**", "**/.git/**", "**/node_modules/**",
        "**/.venv/**", "**/venv/**", "**/*.pyc"
    ])
```

**Attributes:**
- `local_folder` (Optional[Path]): Local folder to sync. Default from `RAG_LOCAL_FOLDER` env var
- `folder_name` (str): Letta folder name. Default from `RAG_FOLDER_NAME` env var or "default_rag"
- `duplicate_handling` (str): How to handle duplicates. Options: "replace", "skip". Default: "replace"
- `include_patterns` (list[str]): Glob patterns for files to include
- `exclude_patterns` (list[str]): Glob patterns for files to exclude

**Example:**
```python
from delonet_letta import RAGConfig
from pathlib import Path

config = RAGConfig(
    local_folder=Path("/path/to/codebase"),
    folder_name="my_rag",
    include_patterns=["**/*.py", "**/*.md"],
    exclude_patterns=["**/test_*.py", "**/.git/**"]
)
```

### load_config()

```python
load_config() -> tuple[LettaConfig, MetaMCPConfig, RAGConfig]
```

Load all configuration from environment variables.

**Returns:**
- `tuple[LettaConfig, MetaMCPConfig, RAGConfig]`: All configuration objects

**Side Effects:**
- Attempts to load `.env` file if `python-dotenv` is available

**Example:**
```python
from delonet_letta.config import load_config

letta_config, metamcp_config, rag_config = load_config()
```

---

## Utility Functions

### handle_already_exists()

```python
handle_already_exists(error_message: str) -> bool
```

Check if an error is due to a resource already existing.

**Module**: `delonet_letta.utils`

**Parameters:**
- `error_message` (str): The error message to check

**Returns:**
- `bool`: True if the error indicates resource already exists

**Patterns Matched:**
- "already exists"
- "already registered"
- "duplicate"
- "conflict"

**Example:**
```python
from delonet_letta.utils import handle_already_exists

try:
    # Some operation
    pass
except Exception as e:
    if handle_already_exists(str(e)):
        print("Resource already exists, continuing...")
    else:
        raise
```

### retry_on_failure()

```python
retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
)
```

Decorator to retry a function on failure with exponential backoff.

**Module**: `delonet_letta.utils`

**Parameters:**
- `max_attempts` (int): Maximum number of retry attempts. Default: 3
- `delay` (float): Initial delay between retries in seconds. Default: 1.0
- `backoff` (float): Backoff multiplier for subsequent retries. Default: 2.0
- `exceptions` (tuple): Tuple of exceptions to catch and retry. Default: (Exception,)

**Example:**
```python
from delonet_letta.utils import retry_on_failure

@retry_on_failure(max_attempts=5, delay=2.0)
def flaky_operation():
    # This will retry up to 5 times with delays: 2s, 4s, 8s, 16s
    result = call_external_api()
    return result
```

### safe_execute()

```python
safe_execute(
    operation: Callable[..., T],
    error_message: str,
    raise_on_error: bool = False,
    default_return: Optional[T] = None
) -> Optional[T]
```

Safely execute an operation with standardized error handling.

**Module**: `delonet_letta.utils`

**Parameters:**
- `operation` (Callable): The operation to execute
- `error_message` (str): Error message prefix to use
- `raise_on_error` (bool): Whether to re-raise exceptions. Default: False
- `default_return` (Optional[T]): Default value to return on error. Default: None

**Returns:**
- `Optional[T]`: Operation result or default_return on error

**Raises:**
- `Exception`: If `raise_on_error` is True

**Example:**
```python
from delonet_letta.utils import safe_execute

result = safe_execute(
    operation=lambda: risky_function(),
    error_message="Failed to perform risky operation",
    raise_on_error=False,
    default_return=[]
)
```

---

## Exceptions

All custom exceptions are defined in `delonet_letta.utils`.

### LettaError

Base exception for all Letta operations.

```python
class LettaError(Exception):
    """Base exception for Letta operations."""
    pass
```

### MCPServerError

Exception raised when MCP server operations fail.

```python
class MCPServerError(LettaError):
    """Exception raised when MCP server operations fail."""
    pass
```

**Raised by:**
- `MCPManager.register_mcp_server()`
- `MCPManager.list_mcp_tools()`

### ToolRegistrationError

Exception raised when tool registration fails.

```python
class ToolRegistrationError(LettaError):
    """Exception raised when tool registration fails."""
    pass
```

**Raised by:**
- `MCPManager.register_mcp_tools()`

### AgentError

Exception raised when agent operations fail.

```python
class AgentError(LettaError):
    """Exception raised when agent operations fail."""
    pass
```

**Raised by:**
- `AgentManager.get_or_create_agent()`
- `AgentManager.attach_folder_to_agent()`
- `AgentManager.update_agent_tools()`

**Example:**
```python
from delonet_letta.utils import AgentError

try:
    agent_id = orchestrator.agents.get_or_create_agent("my-agent")
except AgentError as e:
    print(f"Failed to create agent: {e}")
```

---

## Type Hints

All public APIs use type hints for better IDE support and type checking.

**Example:**
```python
from typing import Optional, Callable
from pathlib import Path

def setup_agent(
    agent_name: str,
    system_prompt: Optional[str] = None,
    tool_filter: Optional[Callable] = None
) -> dict:
    pass
```

## Version Compatibility

This API reference is for DeloNET Letta v0.1.0.

**Dependencies:**
- `letta-client >= 0.1.319`
- `python >= 3.12`

---

## Quick Reference

### Common Imports

```python
# Main classes
from delonet_letta import DeloNETLetta

# Configuration
from delonet_letta import LettaConfig, MetaMCPConfig, RAGConfig, load_config

# Managers (usually accessed via DeloNETLetta)
from delonet_letta import MCPManager, AgentManager, RAGManager

# Utilities
from delonet_letta.utils import (
    retry_on_failure,
    handle_already_exists,
    safe_execute
)

# Exceptions
from delonet_letta.utils import (
    LettaError,
    MCPServerError,
    ToolRegistrationError,
    AgentError
)
```

### Common Patterns

```python
# Initialize
orchestrator = DeloNETLetta()

# Setup agent
results = orchestrator.setup_agent("agent-name")

# Access managers
orchestrator.mcp.list_mcp_tools(server_name)
orchestrator.agents.get_or_create_agent("agent-name")
orchestrator.rag.sync_folder(folder_name="my-rag")

# Get configuration
letta_config, metamcp_config, rag_config = load_config()
```
