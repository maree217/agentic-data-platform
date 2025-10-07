# Framework Comparison: AI Foundry vs. Direct SDKs

## Overview

This guide compares three approaches for building agentic DataOps automation:

1. **Azure AI Foundry** (Portal + Prompt Flow)
2. **Azure AI Foundry SDK** (Python with Agent Service)
3. **Direct AI SDKs** (Anthropic, OpenAI, etc.)

Plus comparisons with: **Semantic Kernel**, **AutoGen**, and **LangGraph**.

---

## Azure AI Foundry Agent Service Deep Dive

### What IS the Agent Service?

The **Agent Service** is Azure AI Foundry's managed runtime for deploying **stateful, multi-turn AI agents**. Think of it as "Agents-as-a-Service."

**Architecture**:

```
┌─────────────────────────────────────────────────────────┐
│  Agent Service Components                               │
│                                                         │
│  ┌─────────────┐    ┌──────────────┐   ┌────────────┐ │
│  │   Agent     │───▶│   Thread     │──▶│  Message   │ │
│  │ (stateless) │    │ (stateful)   │   │  History   │ │
│  └─────────────┘    └──────────────┘   └────────────┘ │
│         │                                              │
│         ▼                                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Built-in Tools                                  │ │
│  │  • Code Interpreter (Python sandbox)            │ │
│  │  • File Search (vector search)                  │ │
│  │  • Custom Functions (Azure SDK, APIs)           │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Agent-to-Agent (A2A) Protocol                   │ │
│  │  • Inter-agent communication                     │ │
│  │  • Shared context                                │ │
│  │  • Handoffs                                       │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Key Concepts

**Agent**: Stateless definition (model, instructions, tools)
- Like a function definition
- Reusable across multiple conversations

**Thread**: Stateful conversation
- Persists messages across requests
- Managed by Azure (no database needed)

**Run**: Execution of agent on a thread
- Agent processes thread messages
- Calls tools automatically
- Returns when complete or needs input

---

## Detailed Comparison Matrix

| Feature | AI Foundry Portal | AI Foundry SDK | Anthropic SDK | Semantic Kernel | AutoGen | LangGraph |
|---------|-------------------|----------------|---------------|-----------------|---------|-----------|
| **Provider** | Microsoft (Azure) | Microsoft (Azure) | Anthropic | Microsoft (OSS) | Microsoft Research | LangChain |
| **Hosting** | Fully managed | Fully managed | Self-hosted | Self-hosted | Self-hosted | Self-hosted |
| **State Management** | ⚙️ HTTP-based | ✅ Built-in (threads) | ❌ Manual | ❌ Manual | ⚙️ Conversation history | ✅ Built-in (checkpoints) |
| **Multi-Agent** | ⚙️ Via Prompt Flow | ✅ A2A protocol | ✅ Custom | ⚙️ Via plugins | ✅ Native (group chat) | ✅ Native (graph) |
| **Tool Calling** | ⚙️ HTTP wrappers | ✅ Automatic | ✅ Manual | ✅ Plugins | ✅ Function calling | ✅ Tool nodes |
| **Language Support** | YAML/Python | Python, .NET, REST | Python, TypeScript | .NET, Python, Java | Python only | Python only |
| **Orchestration Model** | Visual workflows | Thread-based | Custom | Planner + Kernel | Conversational | Graph (DAG) |
| **Governance** | ✅ Built-in | ✅ Built-in | ❌ DIY | ❌ DIY | ❌ DIY | ❌ DIY |
| **Cost Model** | Azure consumption | Azure consumption | Direct API pricing | Free (OSS) + LLM | Free (OSS) + LLM | Free (OSS) + LLM |
| **Learning Curve** | ✅ Low | ⚙️ Medium | 🔺 High | ⚙️ Medium | 🔺 High | 🔺 High |
| **Best For** | Rapid prototyping | Enterprise Azure | Multi-cloud, cost | Cross-platform apps | Research, experiments | Complex workflows |

---

## Approach 1: AI Foundry Portal (Prompt Flow)

### What You Get

**Out-of-Box**:
- Visual workflow designer
- Built-in evaluations and monitoring
- Pre-built templates (RAG, Code, Multi-agent)
- HTTP-based orchestration

**What You DON'T Get**:
- ❌ Pre-built industry agents
- ❌ Direct code execution (need wrapper APIs)
- ❌ Complex conditional logic

### Example: Self-Service Provisioning

```yaml
# Prompt Flow: workspace-provisioning.yaml
name: Data Workspace Provisioning
description: Self-service workspace creation

inputs:
  user_request:
    type: string
  requester_email:
    type: string

nodes:
  # Parse requirements
  - name: parse_requirements
    type: llm
    model: gpt-4o
    prompt: |
      Parse this infrastructure request into JSON:
      Request: {{ user_request }}

      Extract: workload_type, data_volume_tb, budget_monthly, etc.

  # Validate policies
  - name: validate_policies
    type: llm
    model: gpt-4o
    prompt: |
      Validate against policies:
      Request: {{ parse_requirements.output }}
      Policies: max budget $15K/month, GPU requires approval

  # Generate Terraform (via HTTP call to wrapper)
  - name: generate_terraform
    type: http
    url: https://your-api.com/terraform/generate
    method: POST
    body:
      requirements: "{{ parse_requirements.output }}"

  # Send approval request
  - name: send_approval
    type: http
    url: https://api.teams.microsoft.com/webhooks/...
    method: POST

outputs:
  workspace_details:
    type: string
    value: "{{ generate_terraform.response }}"
```

### Pros & Cons

**Pros**:
- ✅ Non-engineers can build workflows
- ✅ Visual debugging (see each step)
- ✅ Built-in versioning
- ✅ Easy handoff to ops teams

**Cons**:
- ❌ Cannot execute Terraform directly (needs wrapper)
- ❌ Complex logic is awkward
- ❌ Limited error handling

### When to Use

Use AI Foundry Portal when:
- Non-technical team iterating quickly
- Simple workflows (RAG, Q&A)
- Don't need complex conditional logic
- Want built-in evaluations

---

## Approach 2: AI Foundry SDK (Agent Service)

### Key Advantages

1. **Stateful Threads** - No manual state management
2. **Automatic Tool Execution** - Agent Service handles routing
3. **A2A Protocol** - Easy multi-agent coordination
4. **Azure-Native** - Managed identity, VNet, governance

### Example: Self-Service Provisioning

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

class WorkspaceProvisioningAgent:
    def __init__(self):
        self.client = AIProjectClient(
            credential=DefaultAzureCredential(),
            subscription_id="...",
            resource_group_name="rg-ai-foundry",
            project_name="data-platform-automation"
        )

        # Create agent with tools
        self.agent = self.client.agents.create_agent(
            model="gpt-4o",
            name="workspace-provisioner",
            instructions="You provision data workspaces from natural language",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "generate_terraform",
                        "description": "Generate Terraform for Azure infrastructure",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "workload_type": {"type": "string"},
                                "data_volume_tb": {"type": "number"},
                                "gpu_needed": {"type": "boolean"}
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "apply_terraform",
                        "description": "Execute Terraform to provision",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "terraform_code": {"type": "string"}
                            }
                        }
                    }
                }
            ]
        )

    def provision_workspace(self, user_request: str):
        # Create thread (stateful conversation)
        thread = self.client.agents.create_thread()

        # Send user request
        self.client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=user_request
        )

        # Run agent
        run = self.client.agents.create_run(
            thread_id=thread.id,
            agent_id=self.agent.id
        )

        # Handle tool calls automatically
        while run.status in ["queued", "in_progress", "requires_action"]:
            if run.status == "requires_action":
                tool_outputs = []

                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    if tool_call.function.name == "generate_terraform":
                        output = self._generate_terraform(
                            json.loads(tool_call.function.arguments)
                        )
                    elif tool_call.function.name == "apply_terraform":
                        output = self._apply_terraform(
                            json.loads(tool_call.function.arguments)
                        )

                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(output)
                    })

                # Submit tool outputs
                run = self.client.agents.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            time.sleep(1)
            run = self.client.agents.get_run(thread_id=thread.id, run_id=run.id)

        # Get final response
        messages = self.client.agents.list_messages(thread_id=thread.id)
        return messages.data[0].content[0].text.value
```

### Benefits Over Portal

**Code Reduction**: 60% less code vs. manual orchestration

**Example**:
- Without Agent Service: 90 lines (manual state, tool routing, error handling)
- With Agent Service: 35 lines (automatic state, tool routing, retries)

### When to Use

Use AI Foundry SDK when:
- Azure is primary cloud
- Need enterprise governance
- Want managed service
- Multi-turn workflows
- A2A multi-agent coordination
- Team lacks ML engineering depth

---

## Approach 3: Direct AI SDKs (Anthropic)

### Key Advantages

1. **Platform Independence** - Multi-cloud, on-prem
2. **Cost Optimization** - No Azure markup
3. **Maximum Flexibility** - Build exactly what you need
4. **Latest Features** - Access immediately

### Example: Self-Service Provisioning

```python
import anthropic
import subprocess

class AnthropicWorkspaceAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def provision_workspace(self, user_request: str) -> dict:
        # Parse requirements
        requirements = self._parse_requirements(user_request)

        # Validate policies
        validation = self._validate_policies(requirements)
        if not validation["approved"]:
            return {"status": "rejected", "reason": validation["violations"]}

        # Generate infrastructure
        infrastructure = self._generate_infrastructure(requirements)

        # Apply infrastructure
        result = self._apply_infrastructure(infrastructure)

        return result

    def _parse_requirements(self, request: str) -> dict:
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": f"Parse this request into JSON: {request}"
            }]
        )

        return json.loads(response.content[0].text)

    def _generate_infrastructure(self, requirements: dict) -> dict:
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": f"""Generate production-ready Terraform:
                Requirements: {json.dumps(requirements, indent=2)}

                Include: VNet, AKS, Storage, Security, Monitoring"""
            }]
        )

        return self._parse_terraform_files(response.content[0].text)

    def _apply_infrastructure(self, infrastructure: dict) -> dict:
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Write Terraform files
            for filename, content in infrastructure['terraform'].items():
                with open(f"{tmpdir}/{filename}", 'w') as f:
                    f.write(content)

            # Execute Terraform
            subprocess.run(["terraform", "init"], cwd=tmpdir, check=True)
            subprocess.run(["terraform", "apply", "-auto-approve"], cwd=tmpdir, check=True)

            # Get outputs
            result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )

            return json.loads(result.stdout)
```

### Benefits Over AI Foundry

**Cost**: ~40% cheaper (no Azure AI Foundry fees)
**Flexibility**: Can execute Terraform directly (no wrapper needed)
**Multi-Cloud**: Works on AWS, GCP, on-prem

### When to Use

Use Anthropic SDK when:
- Multi-cloud strategy
- Cost optimization critical
- Maximum flexibility needed
- Latest Claude features required
- Strong ML/platform engineering team
- Vendor lock-in is concern

---

## Hybrid Approach (Recommended)

### Best of Both Worlds

```python
class HybridDataPlatformAgent:
    """
    User-facing: AI Foundry SDK (governed, audited)
    Background automation: Anthropic SDK (cost-effective)
    """

    def __init__(self):
        # AI Foundry for user-facing workflows
        self.agent_service = AIProjectClient(...)

        # Anthropic for background automation
        self.automation = anthropic.Anthropic()

    def user_request(self, request: str):
        """User-facing: Use Agent Service (stateful, audited)"""
        agent = self.agent_service.agents.create_agent(...)
        thread = self.agent_service.agents.create_thread()
        # Governance, audit trail, managed identity

    def background_optimization(self):
        """Background: Use Anthropic (cost-effective)"""
        # Daily cost analysis, security scans
        result = self.automation.messages.create(...)
```

### Why Hybrid?

- **Governance where needed**: User-facing workflows use AI Foundry
- **Cost optimization**: Background tasks use Anthropic
- **Best of both**: Azure integration + flexibility

---

## Comparison with Other Frameworks

### Semantic Kernel

**Philosophy**: Cross-platform, plugin-based

**When to Use**:
- Need .NET/Java in addition to Python
- Want plugin ecosystem
- No vendor lock-in
- Prefer OSS

**Trade-off**: No built-in state management (you build it)

---

### AutoGen

**Philosophy**: Multi-agent conversational framework

**When to Use**:
- Research/experimentation
- Complex problem-solving (agents debate)
- Code review, architecture debates

**Trade-off**: Can be chatty (high token costs), non-deterministic

---

### LangGraph

**Philosophy**: Agent workflows as graphs (DAGs)

**When to Use**:
- Complex branching logic
- Human-in-the-loop at specific points
- Need to pause/resume execution

**Trade-off**: More verbose, steeper learning curve

---

## Decision Tree

```
Start: What's your primary goal?
│
├─ Rapid prototyping (POC in days)?
│  └─ Use: AI Foundry Portal
│
├─ Enterprise Azure deployment?
│  └─ Use: AI Foundry SDK
│
├─ Multi-cloud / cost optimization?
│  └─ Use: Anthropic SDK (or hybrid)
│
├─ Cross-platform (.NET/Java)?
│  └─ Use: Semantic Kernel
│
├─ Research / complex multi-agent?
│  └─ Use: AutoGen
│
└─ Complex branching workflows?
   └─ Use: LangGraph
```

---

## Summary Recommendations

### For DataOps Automation

**Scenario 1: Azure-first enterprise**
→ **AI Foundry SDK** (governance, managed identity)

**Scenario 2: Multi-cloud startup**
→ **Anthropic SDK** (cost, flexibility)

**Scenario 3: Hybrid approach**
→ **AI Foundry SDK for user-facing + Anthropic for background**

**Scenario 4: Cross-platform product**
→ **Semantic Kernel** (works everywhere)

**Scenario 5: Research project**
→ **AutoGen** (exploration, experimentation)

---

## Next Steps

- [AI Foundry Portal Setup Guide](./ai-foundry-portal.md)
- [AI Foundry SDK Setup Guide](./ai-foundry-sdk.md)
- [Direct SDK Setup Guide](./direct-sdk.md)
- [Hybrid Approach Implementation](./hybrid-approach.md)
