# DeloNET Letta Architecture

This document describes the architecture, design decisions, and implementation patterns of the DeloNET Letta AgentForge.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Design Decisions](#design-decisions)
- [Integration Patterns](#integration-patterns)

## Overview

DeloNET Letta implements a hybrid architecture that separates concerns between **discovery** (RAG) and **interaction** (MCP). This separation prevents the common anti-pattern of treating a RAG index as a bidirectional filesystem.

### Core Principles

1. **Separation of Concerns**: RAG for semantic search, MCP for file operations
2. **Single Source of Truth**: MCP tools operate on actual files, not RAG copies
3. **Centralized Tool Management**: MetaMCP Hub aggregates multiple MCP servers
4. **Configuration-Driven**: Environment variables and dataclasses for all configuration
5. **Graceful Error Handling**: Retry logic and clear error messages

## System Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│                         User Application                          │
│                                                                   │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            │ import DeloNETLetta
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│                        DeloNETLetta                               │
│                    (Main Orchestrator)                            │
│                                                                   │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐      │
│  │  LettaConfig    │  │ MetaMCPConfig│  │   RAGConfig    │      │
│  └─────────────────┘  └──────────────┘  └────────────────┘      │
│                                                                   │
└──┬────────────────────────┬────────────────────────┬─────────────┘
   │                        │                        │
   │ Uses                   │ Uses                   │ Uses
   ▼                        ▼                        ▼
┌──────────────┐     ┌──────────────┐       ┌──────────────┐
│              │     │              │       │              │
│  MCPManager  │     │ AgentManager │       │  RAGManager  │
│              │     │              │       │              │
└──────┬───────┘     └──────┬───────┘       └──────┬───────┘
       │                    │                      │
       │                    │                      │
       ▼                    ▼                      ▼
┌──────────────────────────────────────────────────────────┐
│                                                          │
│                   Letta Client SDK                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
       │                    │                      │
       │                    │                      │
       ▼                    ▼                      ▼
┌──────────────┐     ┌──────────────┐       ┌──────────────┐
│              │     │              │       │              │
│  MCP Tools   │     │    Agents    │       │   Folders    │
│              │     │              │       │              │
└──────┬───────┘     └──────────────┘       └──────────────┘
       │
       │ HTTP Request
       ▼
┌──────────────────────────────────────────────────────────┐
│                                                          │
│                   MetaMCP Hub                            │
│              https://mcp.delo.sh/metamcp                 │
│                                                          │
│  Routes to agent-specific endpoints:                    │
│  /metamcp/{agent_name}/mcp                              │
│                                                          │
└──────────────────────────────────────────────────────────┘
       │
       │ Proxies to appropriate MCP server
       ▼
┌──────────────────────────────────────────────────────────┐
│                                                          │
│              Underlying MCP Servers                      │
│                                                          │
│  ┌────────────┐  ┌─────────┐  ┌──────────────┐         │
│  │ filesystem │  │   git   │  │  kubernetes  │  ...    │
│  └────────────┘  └─────────┘  └──────────────┘         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Component Details

### DeloNETLetta (Orchestrator)

**Location**: `/home/delorenj/code/agents/letta/src/delonet_letta/__init__.py`

The main orchestrator class that ties all components together.

**Responsibilities:**
- Initialize and configure all managers
- Coordinate agent setup workflow
- Provide high-level API for common operations
- Manage Letta client lifecycle

**Key Methods:**
- `__init__()`: Initialize orchestrator with configuration
- `setup_agent()`: Complete agent setup with MCP and RAG

**Dependencies:**
- `letta_client.Letta`: Official Letta SDK
- `MCPManager`: MCP server and tool registration
- `AgentManager`: Agent lifecycle management
- `RAGManager`: RAG folder synchronization

### MCPManager

**Location**: `/home/delorenj/code/agents/letta/src/delonet_letta/mcp_manager.py`

Manages all MCP-related operations including server registration and tool management.

**Responsibilities:**
- Register MetaMCP Hub endpoints as MCP servers in Letta
- List available tools from MCP servers
- Register individual tools with Letta
- Handle tool filtering based on custom criteria
- Retry failed operations with exponential backoff

**Key Methods:**
- `register_mcp_server()`: Register MetaMCP endpoint
- `list_mcp_tools()`: Get available tools from server
- `register_mcp_tools()`: Register tools with optional filtering
- `setup_agent_mcp_tools()`: Complete MCP setup for an agent

**Connection Type:**
The MCP servers are registered as `STREAMABLE_HTTP` type, which is appropriate for production HTTP-based MCP endpoints.

### AgentManager

**Location**: `/home/delorenj/code/agents/letta/src/delonet_letta/agent_manager.py`

Manages Letta agent creation, configuration, and lifecycle.

**Responsibilities:**
- Create new agents or retrieve existing ones
- Configure agent system prompts and models
- Attach tools to agents
- Attach RAG folders to agents for semantic search
- Update agent configuration

**Key Methods:**
- `get_or_create_agent()`: Idempotent agent creation
- `attach_folder_to_agent()`: Attach RAG folder
- `update_agent_tools()`: Update agent's available tools

**Agent Configuration:**
Agents are configured with:
- Name (unique identifier)
- System prompt (defines agent behavior)
- LLM model (e.g., `openai/gpt-4`)
- Embedding model (for RAG)
- Tools (list of available tool names)
- Folders (attached RAG folders)

### RAGManager

**Location**: `/home/delorenj/code/agents/letta/src/delonet_letta/rag_manager.py`

Manages RAG folder creation and file synchronization.

**Responsibilities:**
- Create and manage Letta folders
- Sync local filesystem to RAG storage
- Filter files based on include/exclude patterns
- Handle duplicate file policies
- Track upload progress

**Key Methods:**
- `get_or_create_folder()`: Idempotent folder creation
- `should_include_file()`: Apply include/exclude patterns
- `sync_folder()`: Sync local directory to Letta

**File Filtering:**
Default patterns:
- **Include**: `**/*.py`, `**/*.md`, `**/*.txt`, `**/*.json`
- **Exclude**: `**/__pycache__/**`, `**/.git/**`, `**/node_modules/**`, `**/.venv/**`

### Configuration System

**Location**: `/home/delorenj/code/agents/letta/src/delonet_letta/config.py`

Provides dataclass-based configuration management.

#### LettaConfig

Manages Letta client connection settings:

```python
@dataclass
class LettaConfig:
    base_url: str              # Letta API endpoint
    token: Optional[str]       # Auth token (Cloud only)
    project: Optional[str]     # Project name (Cloud only)
    llm_model: str            # Default LLM model
    embedding_model: str      # Default embedding model
```

**Validation:**
- Automatically detects Letta Cloud vs self-hosted
- Requires `token` and `project` for Cloud deployments
- Provides sensible defaults for all fields

#### MetaMCPConfig

Manages MetaMCP Hub integration:

```python
@dataclass
class MetaMCPConfig:
    hub_base_url: str              # MetaMCP hub URL
    bearer_token: Optional[str]    # Optional auth token
```

**Helper Methods:**
- `get_endpoint(agent_name)`: Returns agent-specific endpoint URL
- `get_server_name(agent_name)`: Returns consistent server name

**Endpoint Pattern:**
- Format: `{hub_base_url}/{agent_name}/mcp`
- Example: `https://mcp.delo.sh/metamcp/devops-agent/mcp`

#### RAGConfig

Manages RAG folder synchronization:

```python
@dataclass
class RAGConfig:
    local_folder: Optional[Path]     # Local directory to sync
    folder_name: str                 # Letta folder name
    duplicate_handling: str          # "replace" or "skip"
    include_patterns: list[str]      # Glob patterns to include
    exclude_patterns: list[str]      # Glob patterns to exclude
```

### Utility Functions

**Location**: `/home/delorenj/code/agents/letta/src/delonet_letta/utils.py`

Provides error handling and retry logic.

#### Error Hierarchy

```python
LettaError (base)
├── MCPServerError
├── ToolRegistrationError
└── AgentError
```

#### Retry Decorator

```python
@retry_on_failure(
    max_attempts=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(Exception,)
)
def operation():
    # Will retry up to 3 times with exponential backoff
    pass
```

**Retry Pattern:**
- Attempt 1: Immediate
- Attempt 2: Wait 1.0s
- Attempt 3: Wait 2.0s
- Failure: Raise exception

#### Error Detection

```python
handle_already_exists(error_message: str) -> bool
```

Detects if an error is due to a resource already existing, allowing for idempotent operations.

## Data Flow

### Agent Setup Flow

```
┌─────────────────────┐
│ User calls          │
│ setup_agent()       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ 1. MCP Setup                                │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ MCPManager.setup_agent_mcp_tools()   │  │
│  │                                      │  │
│  │  a. Register MCP server              │  │
│  │     - Generate endpoint URL          │  │
│  │     - Create STREAMABLE_HTTP server  │  │
│  │                                      │  │
│  │  b. List available tools             │  │
│  │     - Query MetaMCP hub              │  │
│  │                                      │  │
│  │  c. Register tools                   │  │
│  │     - Apply filters if provided      │  │
│  │     - Register each tool with Letta  │  │
│  └──────────────────────────────────────┘  │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ 2. RAG Setup (if enabled)                   │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ RAGManager.get_or_create_folder()    │  │
│  │  - Create folder in Letta            │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ RAGManager.sync_folder() (optional)  │  │
│  │  - Scan local directory              │  │
│  │  - Filter files by patterns          │  │
│  │  - Upload to Letta folder            │  │
│  └──────────────────────────────────────┘  │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ 3. Agent Creation                           │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ AgentManager.get_or_create_agent()   │  │
│  │                                      │  │
│  │  a. Check for existing agent         │  │
│  │  b. Create new agent if needed       │  │
│  │     - Set system prompt              │  │
│  │     - Configure models               │  │
│  │     - Attach tools                   │  │
│  │  c. Attach RAG folder                │  │
│  └──────────────────────────────────────┘  │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────┐
│ Return results      │
│ - agent_id          │
│ - mcp_server        │
│ - tools_registered  │
│ - rag_folder        │
└─────────────────────┘
```

### Tool Invocation Flow

When an agent uses an MCP tool at runtime:

```
┌─────────────────────┐
│ Agent decides to    │
│ use a tool          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ Letta Core                                  │
│ - Validates tool availability               │
│ - Prepares tool parameters                  │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ MCP Server (Registered)                     │
│ - Server: metamcp_{agent_name}_proxy        │
│ - Type: STREAMABLE_HTTP                     │
│ - URL: https://mcp.delo.sh/metamcp/...      │
└──────────────┬──────────────────────────────┘
               │
               │ HTTP POST with tool request
               ▼
┌─────────────────────────────────────────────┐
│ MetaMCP Hub                                 │
│ - Receives request at /metamcp/.../mcp      │
│ - Routes to appropriate underlying server   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ Underlying MCP Server                       │
│ (e.g., filesystem, git, kubernetes)         │
│ - Executes actual operation                 │
│ - Returns result                            │
└──────────────┬──────────────────────────────┘
               │
               │ Response flows back
               ▼
┌─────────────────────┐
│ Agent receives      │
│ tool result         │
└─────────────────────┘
```

### RAG Search Flow

When an agent performs semantic search:

```
┌─────────────────────┐
│ Agent uses          │
│ semantic_search     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ Letta Core                                  │
│ - Receives search query                     │
│ - Generates query embedding                 │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ Letta Folder (RAG Storage)                  │
│ - Vector similarity search                  │
│ - Retrieves relevant chunks                 │
│ - Returns matched content                   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────┐
│ Agent receives      │
│ relevant snippets   │
└─────────────────────┘
```

**Important**: The agent receives *snippets* from RAG, not file paths. To act on files, the agent must then use MCP tools.

## Design Decisions

### 1. Hybrid RAG + MCP Architecture

**Decision**: Use RAG for discovery, MCP for interaction.

**Rationale:**
- Letta Folders are a one-way RAG pipeline, not a filesystem
- RAG excels at semantic search: "find authentication code"
- MCP provides direct, real-time file operations
- Prevents data drift between RAG index and actual files
- Follows official Letta best practices

**Alternative Considered:**
Using RAG alone with hypothetical `edit_file` tools was rejected because:
- Creates synchronization complexity
- Requires manual download/upload workflow
- Introduces state management issues
- Not the intended use case for RAG

### 2. MetaMCP Hub Pattern

**Decision**: Use a centralized hub to aggregate MCP servers.

**Rationale:**
- Single endpoint per agent simplifies configuration
- Hub handles server selection and routing
- Easier to add/remove capabilities without reconfiguring agents
- Reduces Letta configuration complexity
- Follows microservices proxy pattern

**Alternative Considered:**
Directly registering multiple MCP servers per agent was rejected because:
- Increases configuration complexity
- Harder to maintain consistent tool sets
- More error-prone with many servers
- Doesn't scale well

### 3. Idempotent Operations

**Decision**: All setup operations are idempotent.

**Rationale:**
- Safe to re-run setup scripts
- Handles partial failures gracefully
- "Already exists" is not an error condition
- Simplifies automation and CI/CD

**Implementation:**
- `get_or_create_agent()` checks existence before creating
- `register_mcp_server()` handles "already exists" errors
- `register_mcp_tools()` skips existing tools by default

### 4. Configuration via Environment Variables

**Decision**: Use environment variables with dataclass defaults.

**Rationale:**
- 12-factor app methodology
- Easy to configure in different environments
- No secrets in code
- Clear configuration schema via dataclasses
- Type safety with Python type hints

**Precedence:**
1. Explicit parameters to constructors
2. Environment variables
3. Dataclass defaults

### 5. Separation of Managers

**Decision**: Split concerns into three managers (MCP, Agent, RAG).

**Rationale:**
- Single Responsibility Principle
- Each manager has clear domain boundaries
- Easier to test in isolation
- Simpler to understand and maintain
- Allows for independent enhancement

**Boundaries:**
- **MCPManager**: Everything MCP-related (servers, tools)
- **AgentManager**: Agent lifecycle only
- **RAGManager**: RAG folder operations only
- **DeloNETLetta**: Orchestration and coordination

### 6. STREAMABLE_HTTP Connection Type

**Decision**: Use `STREAMABLE_HTTP` for MCP servers.

**Rationale:**
- Appropriate for HTTP-based MCP endpoints
- Supports production deployments
- Works with MetaMCP Hub's HTTP interface
- More robust than stdio for remote servers

**Alternative Considered:**
`stdio` was rejected because:
- Requires local process execution
- Not suitable for remote hubs
- Harder to deploy and scale

## Integration Patterns

### Pattern 1: Basic Agent Setup

Simplest possible setup:

```python
from delonet_letta import DeloNETLetta

orchestrator = DeloNETLetta()
results = orchestrator.setup_agent(
    agent_name="basic-agent",
    system_prompt="You are a helpful assistant."
)
```

**When to use:**
- Quick prototypes
- Simple use cases
- Default configuration is sufficient

### Pattern 2: RAG-Enabled Agent

Agent with semantic search capabilities:

```python
from delonet_letta import DeloNETLetta, RAGConfig
from pathlib import Path

rag_config = RAGConfig(
    local_folder=Path("/path/to/codebase"),
    include_patterns=["**/*.py", "**/*.md"]
)

orchestrator = DeloNETLetta(rag_config=rag_config)
results = orchestrator.setup_agent(
    agent_name="search-agent",
    enable_rag=True,
    sync_rag_folder=True
)
```

**When to use:**
- Code analysis agents
- Documentation assistants
- Large codebases requiring discovery

### Pattern 3: Tool-Filtered Agent

Agent with selective tool access:

```python
from delonet_letta import DeloNETLetta

def safe_tools_only(tool):
    """Only allow read-only operations."""
    tool_name = tool.name if hasattr(tool, 'name') else str(tool)
    safe_prefixes = ['filesystem_read', 'git_status', 'git_log']
    return any(tool_name.startswith(prefix) for prefix in safe_prefixes)

orchestrator = DeloNETLetta()
results = orchestrator.setup_agent(
    agent_name="readonly-agent",
    tool_filter=safe_tools_only
)
```

**When to use:**
- Security-sensitive environments
- Limited permission agents
- Testing and development

### Pattern 4: Multi-Environment Setup

Different configurations per environment:

```python
import os
from delonet_letta import DeloNETLetta, LettaConfig

# Development
if os.getenv("ENV") == "development":
    letta_config = LettaConfig(
        base_url="http://localhost:8283/v1"
    )
# Production
else:
    letta_config = LettaConfig(
        base_url="https://api.letta.com",
        token=os.getenv("LETTA_PROD_TOKEN"),
        project=os.getenv("LETTA_PROD_PROJECT")
    )

orchestrator = DeloNETLetta(letta_config=letta_config)
```

**When to use:**
- Multi-environment deployments
- Different Letta instances (dev/staging/prod)
- Environment-specific configuration

### Pattern 5: Incremental RAG Sync

Periodic RAG updates:

```python
from delonet_letta import DeloNETLetta
from pathlib import Path
import schedule

orchestrator = DeloNETLetta()

def sync_codebase():
    successful, failed = orchestrator.rag.sync_folder(
        local_folder=Path("/path/to/codebase"),
        folder_name="codebase_rag"
    )
    print(f"Synced: {successful} files")

# Sync every hour
schedule.every(1).hours.do(sync_codebase)
```

**When to use:**
- Keeping RAG index current
- Monitoring changing codebases
- Scheduled maintenance tasks

## Performance Considerations

### MCP Server Registration

- **Cost**: One-time per agent setup
- **Retry**: Up to 3 attempts with exponential backoff
- **Caching**: Server registrations persist in Letta

### Tool Registration

- **Cost**: Linear with number of tools
- **Optimization**: Use `tool_filter` to reduce tool count
- **Idempotency**: Existing tools are skipped

### RAG Synchronization

- **Cost**: Linear with number of files
- **Optimization**: Use include/exclude patterns aggressively
- **File Size**: Large files may take longer to process
- **Chunking**: Letta handles chunking automatically

**Recommendations:**
- Sync only necessary files
- Use specific include patterns
- Exclude build artifacts and dependencies
- Consider incremental syncs for large codebases

## Security Considerations

### MCP Tool Access

MCP tools provide direct filesystem access. Consider:

1. **Tool Filtering**: Restrict tools to minimum required set
2. **Read-Only Agents**: Use tool filters to allow only read operations
3. **Path Restrictions**: MCP servers should enforce path restrictions
4. **Authentication**: Use bearer tokens for MetaMCP Hub access

### RAG Data Exposure

RAG folders contain file content. Consider:

1. **Sensitive Files**: Exclude via patterns (e.g., `**/.env`, `**/secrets/**`)
2. **Access Control**: Folder attachments determine agent access
3. **Data Retention**: RAG data persists until explicitly deleted

### Configuration Security

1. **Token Storage**: Never commit tokens to version control
2. **Environment Variables**: Use `.env` files (gitignored)
3. **Secret Management**: Consider using secret managers in production

## Troubleshooting Architecture Issues

### MCP Connection Failures

**Symptom**: Tools fail to register or invoke

**Diagnosis:**
1. Verify MetaMCP Hub is accessible
2. Check network connectivity
3. Validate bearer token if required
4. Confirm MCP server type is `STREAMABLE_HTTP`

### RAG Sync Problems

**Symptom**: Files not appearing in RAG

**Diagnosis:**
1. Check include/exclude patterns
2. Verify local folder exists and is readable
3. Confirm file extensions match patterns
4. Check Letta logs for upload errors

### Agent Tool Mismatch

**Symptom**: Agent reports tools not available

**Diagnosis:**
1. List tools: `client.tools.list_mcp_tools_by_server()`
2. Check agent configuration: `client.agents.get(agent_id)`
3. Verify tools were registered successfully
4. Check for tool name mismatches

## Future Enhancements

Potential areas for expansion:

1. **Tool Discovery**: Automatic detection of new tools in hub
2. **RAG Incremental Sync**: Only upload changed files
3. **Multi-Agent Coordination**: Shared tools and folders
4. **Monitoring**: Metrics and observability hooks
5. **Caching**: Cache tool lists and folder contents
6. **Batch Operations**: Bulk agent creation and management

## References

- [Letta Documentation](https://docs.letta.com)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MetaMCP Hub Documentation](https://mcp.delo.sh/docs)
- [12-Factor App Methodology](https://12factor.net/)
