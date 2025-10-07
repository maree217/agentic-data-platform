# AI Foundry SDK Setup Guide

## Overview

Production-ready agentic DataOps using Azure AI Foundry SDK (Python).

**Best for**: Enterprise Azure deployments, need governance and managed identity.

---

## Prerequisites

- Python 3.11+
- Azure subscription with AI Foundry
- Azure CLI

---

## Installation

```bash
# Install dependencies
pip install azure-ai-projects azure-identity python-dotenv

# Configure credentials
cp .env.example .env
# Edit .env with your Azure AI Foundry details
```

---

## Quick Start

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Initialize client
client = AIProjectClient(
    credential=DefaultAzureCredential(),
    subscription_id="...",
    resource_group_name="rg-ai-foundry",
    project_name="data-platform-automation"
)

# Create agent
agent = client.agents.create_agent(
    model="gpt-4o",
    name="workspace-provisioner",
    instructions="You provision data workspaces",
    tools=[...]
)

# Create thread and run
thread = client.agents.create_thread()
client.agents.create_message(thread_id=thread.id, content="Create workspace")
run = client.agents.create_run(thread_id=thread.id, agent_id=agent.id)
```

---

## Next Steps

- [Framework Comparison](./framework-comparison.md)
- [Agent Development Guide](./agent-development.md)
- [Multi-Agent Patterns](./multi-agent-patterns.md)
