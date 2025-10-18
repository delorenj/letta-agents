#!/usr/bin/env python3
"""
Advanced Setup Example for DeloNET Letta

This example demonstrates advanced agent setup features including:
1. Custom configuration
2. RAG folder integration
3. Tool filtering
4. Progress tracking
5. Multiple agent patterns

Prerequisites:
- Letta instance running (self-hosted or cloud)
- MetaMCP Hub accessible
- Local folder for RAG synchronization (optional)

Usage:
    python advanced_setup.py
"""

from pathlib import Path
from delonet_letta import (
    DeloNETLetta,
    LettaConfig,
    MetaMCPConfig,
    RAGConfig
)


def print_section(title: str):
    """Print a formatted section header."""
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)
    print()


def example_1_custom_configuration():
    """Example 1: Using custom configuration instead of environment variables."""

    print_section("Example 1: Custom Configuration")

    # Define custom configuration
    letta_config = LettaConfig(
        base_url="http://localhost:8283/v1",
        llm_model="openai/gpt-4-turbo",
        embedding_model="openai/text-embedding-3-small"
    )

    metamcp_config = MetaMCPConfig(
        hub_base_url="https://mcp.delo.sh/metamcp",
        bearer_token=None  # Optional authentication
    )

    rag_config = RAGConfig(
        folder_name="custom_rag",
        include_patterns=["**/*.py", "**/*.md", "**/*.yaml"],
        exclude_patterns=["**/test_*.py", "**/.git/**"]
    )

    # Initialize with custom config
    orchestrator = DeloNETLetta(
        letta_config=letta_config,
        metamcp_config=metamcp_config,
        rag_config=rag_config
    )

    print("✅ Custom configuration loaded successfully")
    print(f"   LLM Model: {letta_config.llm_model}")
    print(f"   Embedding Model: {letta_config.embedding_model}")
    print(f"   MetaMCP Hub: {metamcp_config.hub_base_url}")

    return orchestrator


def example_2_tool_filtering(orchestrator: DeloNETLetta):
    """Example 2: Setup agent with tool filtering."""

    print_section("Example 2: Tool Filtering")

    print("Setting up a read-only agent with filtered tools...")
    print()

    # Define a tool filter for read-only operations
    def read_only_tools(tool):
        """Only allow read-only tools."""
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)

        # List of allowed read-only tool prefixes
        allowed_prefixes = [
            'filesystem_read',
            'filesystem_list',
            'git_status',
            'git_log',
            'git_diff',
            'kubernetes_get',
            'kubernetes_describe'
        ]

        return any(tool_name.startswith(prefix) for prefix in allowed_prefixes)

    # Setup agent with tool filter
    results = orchestrator.setup_agent(
        agent_name="readonly-analyst",
        system_prompt="""You are a read-only code analyst.

Your capabilities:
- Read and analyze files
- Review git history and status
- Examine Kubernetes resources

You CANNOT:
- Modify files
- Commit changes
- Deploy or modify Kubernetes resources

Always provide insights and recommendations, but never make changes.""",
        tool_filter=read_only_tools,
        enable_rag=False
    )

    print("✅ Read-only agent created successfully")
    print(f"   Agent ID: {results['agent_id']}")
    print(f"   Filtered tools: {len(results['tools_registered'])} registered")
    print()

    # Display registered tools
    if results['tools_registered']:
        print("Allowed Tools:")
        for tool_name in results['tools_registered'][:15]:
            print(f"  ✓ {tool_name}")

        if len(results['tools_registered']) > 15:
            print(f"  ... and {len(results['tools_registered']) - 15} more")

    return results


def example_3_rag_integration(orchestrator: DeloNETLetta):
    """Example 3: Setup agent with RAG integration."""

    print_section("Example 3: RAG Integration")

    # Check if local folder is configured
    if not orchestrator.rag_config.local_folder:
        print("⚠️  No local folder configured for RAG sync")
        print("   Set RAG_LOCAL_FOLDER environment variable to enable sync")
        print()
        print("Creating agent with RAG folder (no sync)...")

        results = orchestrator.setup_agent(
            agent_name="code-searcher",
            system_prompt="""You are a code search expert.

Use the semantic_search_files tool to find relevant code across the codebase.
When you find relevant files, use MCP tools to read their full content.""",
            enable_rag=True,
            sync_rag_folder=False  # No local folder to sync
        )

    else:
        print(f"Syncing local folder: {orchestrator.rag_config.local_folder}")
        print()

        # Define progress callback
        def show_progress(current: int, total: int, file_path: Path):
            """Display upload progress."""
            percentage = (current / total) * 100
            print(f"[{current}/{total}] ({percentage:.1f}%) {file_path.name}")

        print("Setting up agent with RAG sync...")
        results = orchestrator.setup_agent(
            agent_name="code-searcher",
            system_prompt="""You are a code search expert.

Use the semantic_search_files tool to find relevant code across the codebase.
When you find relevant files, use MCP tools to read their full content.""",
            enable_rag=True,
            sync_rag_folder=True
        )

    print()
    print("✅ RAG-enabled agent created successfully")
    print(f"   Agent ID: {results['agent_id']}")
    print(f"   RAG Folder: {results['rag_folder']}")

    if results.get('rag_sync_stats'):
        stats = results['rag_sync_stats']
        print(f"   Files synced: {stats['successful']}")
        print(f"   Failed: {stats['failed']}")

    return results


def example_4_specialized_agents(orchestrator: DeloNETLetta):
    """Example 4: Create multiple specialized agents."""

    print_section("Example 4: Specialized Agents")

    agents = []

    # Agent 1: DevOps Engineer
    print("1. Creating DevOps Engineer agent...")

    def devops_tools(tool):
        """Tools relevant for DevOps."""
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        return any(prefix in tool_name for prefix in [
            'git_', 'kubernetes_', 'docker_', 'terraform_'
        ])

    devops_result = orchestrator.setup_agent(
        agent_name="devops-engineer",
        system_prompt="""You are an expert DevOps engineer.

Your responsibilities:
- Manage Kubernetes clusters
- Handle git repositories
- Deploy applications
- Monitor infrastructure

Use git and kubernetes tools to help users with infrastructure tasks.""",
        tool_filter=devops_tools,
        enable_rag=False
    )

    agents.append(("DevOps Engineer", devops_result))
    print(f"   ✅ Created with {len(devops_result['tools_registered'])} tools")

    # Agent 2: Code Reviewer
    print()
    print("2. Creating Code Reviewer agent...")

    def code_review_tools(tool):
        """Tools for code review."""
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        # Read-only filesystem + git tools
        return tool_name.startswith('filesystem_read') or tool_name.startswith('git_')

    review_result = orchestrator.setup_agent(
        agent_name="code-reviewer",
        system_prompt="""You are a senior code reviewer.

Your responsibilities:
- Review code for best practices
- Identify potential bugs and security issues
- Suggest improvements
- Check git history for context

Use filesystem and git tools to review code thoroughly.""",
        tool_filter=code_review_tools,
        enable_rag=True,  # Enable RAG for code search
        sync_rag_folder=False
    )

    agents.append(("Code Reviewer", review_result))
    print(f"   ✅ Created with {len(review_result['tools_registered'])} tools + RAG")

    # Agent 3: Documentation Writer
    print()
    print("3. Creating Documentation Writer agent...")

    def docs_tools(tool):
        """Tools for documentation."""
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        # Filesystem tools for reading and writing docs
        return 'filesystem_' in tool_name

    docs_result = orchestrator.setup_agent(
        agent_name="docs-writer",
        system_prompt="""You are a technical documentation writer.

Your responsibilities:
- Write clear, comprehensive documentation
- Update existing docs based on code changes
- Create examples and tutorials

Use filesystem tools to read code and write documentation.""",
        tool_filter=docs_tools,
        enable_rag=True,
        sync_rag_folder=False
    )

    agents.append(("Documentation Writer", docs_result))
    print(f"   ✅ Created with {len(docs_result['tools_registered'])} tools + RAG")

    # Summary
    print()
    print("=" * 70)
    print("Summary of Specialized Agents")
    print("=" * 70)
    for name, result in agents:
        print(f"\n{name}:")
        print(f"  Agent ID: {result['agent_id']}")
        print(f"  Tools: {len(result['tools_registered'])}")
        print(f"  RAG: {'✓' if result['rag_folder'] else '✗'}")

    return agents


def example_5_manual_rag_operations(orchestrator: DeloNETLetta):
    """Example 5: Manual RAG folder operations."""

    print_section("Example 5: Manual RAG Operations")

    # Create a RAG folder
    print("Creating a custom RAG folder...")
    folder_id = orchestrator.rag.get_or_create_folder("documentation_rag")
    print(f"✅ Folder created/retrieved: {folder_id}")

    # Check if we can sync
    if orchestrator.rag_config.local_folder:
        print()
        print(f"Syncing from: {orchestrator.rag_config.local_folder}")

        # Custom RAG config for docs only
        custom_rag_config = RAGConfig(
            local_folder=orchestrator.rag_config.local_folder,
            folder_name="documentation_rag",
            include_patterns=["**/*.md", "**/*.rst", "**/*.txt"],
            exclude_patterns=["**/node_modules/**", "**/.git/**"]
        )

        # Create a new RAG manager with custom config
        from delonet_letta import RAGManager
        rag_manager = RAGManager(orchestrator.client, custom_rag_config)

        successful, failed = rag_manager.sync_folder()

        print()
        print(f"✅ Sync complete: {successful} files uploaded, {failed} failed")
    else:
        print()
        print("⚠️  No local folder configured for sync demonstration")

    return folder_id


def main():
    """Run all advanced examples."""

    print("=" * 70)
    print(" DeloNET Letta - Advanced Setup Examples")
    print("=" * 70)
    print()
    print("This script demonstrates advanced features of DeloNET Letta:")
    print("  1. Custom configuration")
    print("  2. Tool filtering")
    print("  3. RAG integration")
    print("  4. Specialized agents")
    print("  5. Manual RAG operations")
    print()

    try:
        # Example 1: Custom configuration
        orchestrator = example_1_custom_configuration()

        # Example 2: Tool filtering
        example_2_tool_filtering(orchestrator)

        # Example 3: RAG integration
        example_3_rag_integration(orchestrator)

        # Example 4: Specialized agents
        example_4_specialized_agents(orchestrator)

        # Example 5: Manual RAG operations
        example_5_manual_rag_operations(orchestrator)

        # Final summary
        print_section("Completion")
        print("✅ All examples completed successfully!")
        print()
        print("Next steps:")
        print("  - Interact with your agents via the Letta API")
        print("  - Review the API documentation for more options")
        print("  - Check the architecture docs for design patterns")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Examples cancelled by user.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error during examples: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check your Letta instance is running")
        print("  2. Verify MetaMCP Hub is accessible")
        print("  3. Review environment variables or configuration")
        print("  4. Check the logs for detailed error messages")
        print()
        raise


if __name__ == "__main__":
    main()
