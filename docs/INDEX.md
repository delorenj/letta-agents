# Documentation Index

Welcome to the DeloNET Letta documentation! This index helps you find the information you need.

## Quick Links

- **[Main README](../README.md)** - Start here for project overview and quick start
- **[API Reference](API.md)** - Complete API documentation
- **[Architecture Guide](ARCHITECTURE.md)** - Deep dive into design and architecture
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project

## Documentation Structure

### Getting Started

**New to DeloNET Letta?** Start with these resources:

1. **[README.md](../README.md)** - Project overview, installation, and quick start
   - What is DeloNET Letta?
   - Key features
   - Installation instructions
   - Quick start guide
   - Basic usage examples

2. **[Basic Setup Example](../examples/basic_setup.py)** - Simple, runnable example
   - Minimal configuration
   - Creating your first agent
   - Understanding the results

### Understanding the System

**Want to understand how it works?** Read these:

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architecture
   - System overview with diagrams
   - Component descriptions
   - Data flow diagrams
   - Design decisions and rationale
   - Integration patterns
   - Performance considerations

2. **[TASK.md](../TASK.md)** - Original architecture discussion
   - Background on RAG vs MCP
   - Why the hybrid approach?
   - MetaMCP Hub pattern

### Using the API

**Ready to build?** Reference these:

1. **[API.md](API.md)** - Complete API reference
   - DeloNETLetta class
   - MCPManager class
   - AgentManager class
   - RAGManager class
   - Configuration classes
   - Utility functions
   - Exception types

2. **[Advanced Setup Example](../examples/advanced_setup.py)** - Advanced patterns
   - Custom configuration
   - Tool filtering
   - RAG integration
   - Multiple specialized agents

### Contributing

**Want to contribute?** Check out:

1. **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
   - Development setup
   - Code style
   - Testing requirements
   - Pull request process

## Documentation by Topic

### Configuration

- [Configuration Guide](../README.md#configuration-guide) - Environment variables and config classes
- [LettaConfig API](API.md#lettaconfig) - Letta connection configuration
- [MetaMCPConfig API](API.md#metamcpconfig) - MetaMCP Hub configuration
- [RAGConfig API](API.md#ragconfig) - RAG folder configuration
- [.env.example](../.env.example) - Example environment file

### MCP Integration

- [MCP Architecture](ARCHITECTURE.md#mcpmanager) - How MCP integration works
- [MCPManager API](API.md#mcpmanager) - MCP server and tool management
- [MetaMCP Hub Pattern](ARCHITECTURE.md#2-metamcp-hub-pattern) - Why use a hub?
- [Tool Filtering Example](../examples/advanced_setup.py) - Selective tool access

### RAG Integration

- [RAG Architecture](ARCHITECTURE.md#ragmanager) - How RAG works
- [RAGManager API](API.md#ragmanager) - RAG folder management
- [Hybrid Architecture](../README.md#understanding-the-hybrid-architecture) - RAG + MCP explained
- [RAG Integration Example](../examples/advanced_setup.py) - Using RAG with agents

### Agent Management

- [Agent Setup](../README.md#quick-start) - Creating and configuring agents
- [AgentManager API](API.md#agentmanager) - Agent lifecycle operations
- [Agent Patterns](ARCHITECTURE.md#integration-patterns) - Common usage patterns
- [Specialized Agents Example](../examples/advanced_setup.py) - Multiple agent types

### Error Handling

- [Error Handling](ARCHITECTURE.md#utility-functions) - Retry and error patterns
- [Exception Types](API.md#exceptions) - Custom exceptions
- [Troubleshooting](../README.md#troubleshooting) - Common issues and solutions

## Examples by Use Case

### Basic Use Cases

- **[Simple Agent Setup](../examples/basic_setup.py)** - Get started quickly
- **[Custom Configuration](../examples/advanced_setup.py#example_1_custom_configuration)** - Configure without env vars

### Security Use Cases

- **[Read-Only Agent](../examples/advanced_setup.py#example_2_tool_filtering)** - Restrict to read operations
- **[Tool Filtering](ARCHITECTURE.md#pattern-3-tool-filtered-agent)** - Custom tool selection

### Advanced Use Cases

- **[RAG-Enabled Agent](../examples/advanced_setup.py#example_3_rag_integration)** - Semantic search
- **[Multiple Specialized Agents](../examples/advanced_setup.py#example_4_specialized_agents)** - Agent team
- **[Manual RAG Operations](../examples/advanced_setup.py#example_5_manual_rag_operations)** - Direct RAG control

### Production Use Cases

- **[Multi-Environment Setup](ARCHITECTURE.md#pattern-4-multi-environment-setup)** - Dev/staging/prod
- **[Incremental RAG Sync](ARCHITECTURE.md#pattern-5-incremental-rag-sync)** - Periodic updates

## Architecture Diagrams

All diagrams are in [ARCHITECTURE.md](ARCHITECTURE.md):

- [System Architecture](ARCHITECTURE.md#system-architecture) - Overall system design
- [Agent Setup Flow](ARCHITECTURE.md#agent-setup-flow) - Agent creation process
- [Tool Invocation Flow](ARCHITECTURE.md#tool-invocation-flow) - MCP tool execution
- [RAG Search Flow](ARCHITECTURE.md#rag-search-flow) - Semantic search process

## API Quick Reference

### Main Classes

```python
from delonet_letta import (
    DeloNETLetta,      # Main orchestrator
    MCPManager,        # MCP management
    AgentManager,      # Agent lifecycle
    RAGManager,        # RAG operations
)
```

### Configuration

```python
from delonet_letta import (
    LettaConfig,       # Letta connection
    MetaMCPConfig,     # MetaMCP Hub
    RAGConfig,         # RAG folders
    load_config,       # Load from env
)
```

### Utilities

```python
from delonet_letta.utils import (
    retry_on_failure,      # Retry decorator
    handle_already_exists, # Error detection
    safe_execute,          # Safe operation wrapper
)
```

### Exceptions

```python
from delonet_letta.utils import (
    LettaError,            # Base exception
    MCPServerError,        # MCP failures
    ToolRegistrationError, # Tool failures
    AgentError,            # Agent failures
)
```

## Version Information

This documentation is for DeloNET Letta v0.1.0.

**Dependencies:**
- Python >= 3.12
- letta-client >= 0.1.319

## Getting Help

- **Issues**: Report bugs or request features on GitHub
- **Discussions**: Ask questions or share ideas
- **Examples**: Check the [examples/](../examples/) directory

## Contributing to Documentation

Documentation improvements are always welcome! See the [Contributing Guide](../CONTRIBUTING.md#documentation) for details.

When updating documentation:
1. Keep it clear and concise
2. Include code examples
3. Update this index if adding new docs
4. Test all code examples

## Documentation Standards

Our documentation follows these principles:

- **Accessibility**: Easy to find and navigate
- **Completeness**: Cover all features and use cases
- **Clarity**: Clear explanations with examples
- **Currency**: Keep up-to-date with code changes
- **Consistency**: Uniform style and formatting

## External Resources

- [Letta Documentation](https://docs.letta.com)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MetaMCP Hub](https://mcp.delo.sh/docs)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

**Last Updated**: 2025-10-08

**Next**: Start with the [README](../README.md) or dive into the [Architecture Guide](ARCHITECTURE.md)
