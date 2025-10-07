# Self-Service Data Workspace Provisioning

## Overview

Enable data teams to provision complete data workspaces in minutes using natural language requests.

**Problem**: Infrastructure provisioning takes weeks, requires multiple teams, and involves manual handoffs.

**Solution**: Autonomous agents parse requirements, generate IaC, validate policies, and provision infrastructure automatically.

---

## User Journey

### Step 1: Natural Language Request

```
User: "I need a Spark environment for our ML team to process 5TB of
customer data daily. Budget: $8K/month. Need GPU support for model training."
```

### Step 2: Agent Processing

```python
from agents.infrastructure import WorkspaceProvisioningAgent

agent = WorkspaceProvisioningAgent(approach="ai-foundry-sdk")

result = agent.provision_workspace(
    user_request="Spark environment, 5TB daily, GPU support, $8K/month",
    requester="ml-lead@company.com"
)
```

### Step 3: Automated Execution

**Timeline**:
- `[00:00]` Parse requirements → Extract: Spark, 5TB, GPU, budget
- `[00:30]` Validate policies → Check budget limits, approvals
- `[02:00]` Generate Terraform → AKS + GPU nodes + ADLS Gen2
- `[03:00]` Cost estimate → $7,800/month (within budget ✅)
- `[04:00]` Request approval → Send to manager
- `[05:00]` Approval received → Auto-approve (within policy)
- `[06:00]` Provision infrastructure → Terraform apply
- `[12:00]` **Complete** → Workspace ready

**Result**: Infrastructure provisioned in **12 minutes** (vs. 2-4 weeks manual)

---

## Implementation: Three Approaches

### Approach 1: AI Foundry Portal (Prompt Flow)

**File**: `flows/workspace-provisioning.yaml`

```yaml
name: Workspace Provisioning
nodes:
  - name: parse_requirements
    type: llm
    model: gpt-4o
    prompt: "Parse infrastructure request: {{ user_request }}"

  - name: generate_terraform
    type: http
    url: https://terraform-api.company.com/generate

  - name: apply_infrastructure
    type: http
    url: https://terraform-api.company.com/apply
```

**Pros**:
- ✅ Visual workflow designer
- ✅ Non-engineers can modify

**Cons**:
- ❌ Requires wrapper APIs (cannot execute Terraform directly)

---

### Approach 2: AI Foundry SDK (Recommended)

**File**: `agents/infrastructure/workspace_agent.py`

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import json

class WorkspaceProvisioningAgent:
    def __init__(self):
        self.client = AIProjectClient(
            credential=DefaultAzureCredential(),
            subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
            resource_group_name="rg-ai-foundry",
            project_name="data-platform-automation"
        )

        self.agent = self.client.agents.create_agent(
            model="gpt-4o",
            name="workspace-provisioner",
            instructions="""You provision data workspaces from natural language.

            Your workflow:
            1. Parse user requirements (workload type, size, budget)
            2. Validate against organizational policies
            3. Generate Terraform code
            4. Estimate costs
            5. Request approval if needed
            6. Provision infrastructure
            7. Generate onboarding guide

            Always prioritize security, cost optimization, and compliance.""",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "parse_requirements",
                        "description": "Parse natural language into structured requirements",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_request": {"type": "string"}
                            }
                        }
                    }
                },
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
                                "gpu_needed": {"type": "boolean"},
                                "budget_monthly": {"type": "number"}
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "apply_terraform",
                        "description": "Execute Terraform to provision infrastructure",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "terraform_code": {"type": "string"},
                                "workspace_name": {"type": "string"}
                            }
                        }
                    }
                }
            ]
        )

    def provision_workspace(self, user_request: str, requester: str) -> dict:
        # Create stateful thread
        thread = self.client.agents.create_thread()

        # Send request
        self.client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=f"User: {requester}\nRequest: {user_request}"
        )

        # Run agent (handles tool calls automatically)
        run = self.client.agents.create_run(
            thread_id=thread.id,
            agent_id=self.agent.id
        )

        # Wait for completion with tool execution
        while run.status in ["queued", "in_progress", "requires_action"]:
            if run.status == "requires_action":
                tool_outputs = self._execute_tools(run.required_action.submit_tool_outputs.tool_calls)

                run = self.client.agents.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            time.sleep(1)
            run = self.client.agents.get_run(thread_id=thread.id, run_id=run.id)

        # Get result
        messages = self.client.agents.list_messages(thread_id=thread.id)
        return {
            "status": "success",
            "result": messages.data[0].content[0].text.value
        }
```

**Pros**:
- ✅ Stateful threads (conversation preserved)
- ✅ Automatic tool execution
- ✅ Azure-native (managed identity)

---

### Approach 3: Direct Anthropic SDK

**File**: `agents/infrastructure/anthropic_workspace_agent.py`

```python
import anthropic
import subprocess
import json

class AnthropicWorkspaceAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def provision_workspace(self, user_request: str) -> dict:
        # Step 1: Parse requirements
        requirements = self._parse_requirements(user_request)

        # Step 2: Validate policies
        validation = self._validate_policies(requirements)
        if not validation["approved"]:
            return {"status": "rejected", "reason": validation["violations"]}

        # Step 3: Generate Terraform
        infrastructure = self._generate_terraform(requirements)

        # Step 4: Apply infrastructure
        result = self._apply_terraform(infrastructure)

        return result

    def _parse_requirements(self, request: str) -> dict:
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": f"""Parse this infrastructure request into JSON:

{request}

Output JSON with: workload_type, data_volume_tb, gpu_needed, budget_monthly, etc."""
            }]
        )

        return json.loads(response.content[0].text)

    def _generate_terraform(self, requirements: dict) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": f"""Generate production-ready Terraform for:

{json.dumps(requirements, indent=2)}

Include:
- AKS cluster (with GPU node pool if needed)
- ADLS Gen2 storage
- VNet with proper segmentation
- Key Vault
- Managed identities
- Monitoring (Azure Monitor)

Output valid Terraform HCL."""
            }]
        )

        return response.content[0].text
```

**Pros**:
- ✅ Platform-agnostic (multi-cloud, on-prem)
- ✅ Lower cost (no Azure AI Foundry fees)
- ✅ Direct Terraform execution

---

## Policy Validation

Agents automatically validate requests against organizational policies:

```python
policies = {
    "max_budget_per_team": 15000,
    "gpu_requires_vp_approval": True,
    "data_over_1tb_requires_security_review": True,
    "allowed_regions": ["eastus", "westus2"],
    "encryption_required": True
}
```

**Enforcement**:
- ❌ Reject if violates hard limits
- ⏸️ Pause for approval if requires review
- ✅ Auto-approve if within policy

---

## Cost Estimation

Before provisioning, agents estimate monthly costs:

```
Estimated Monthly Cost: $7,800

Breakdown:
  • AKS (6 nodes, Standard_NC6s_v3): $6,200
  • ADLS Gen2 (5TB storage): $800
  • Networking (VNet, Private Endpoints): $400
  • Monitoring (Log Analytics): $300
  • Other (Key Vault, etc.): $100

Optimization suggestions:
  ✓ Use spot instances for dev (save $1,200/month)
  ✓ Reserved capacity (save $800/month with 1-year commit)
```

---

## Onboarding Guide Generation

After provisioning, agent generates user guide:

```markdown
# Your Workspace is Ready! 🎉

## Quick Start

1. **Connect to AKS cluster:**
   ```bash
   az aks get-credentials --resource-group rg-ml-workspace \
     --name aks-ml-workspace
   ```

2. **Submit a Spark job:**
   ```bash
   kubectl apply -f spark-job.yaml
   ```

3. **Access data lake:**
   ```python
   storage_account = "adlsmlworkspace"
   container = "data-bronze"
   ```

## Monitoring
- Dashboard: https://portal.azure.com/...
- Logs: https://logs.azure.com/...

## Support
- Slack: #ml-workspace-support
- Email: platform-team@company.com
```

---

## Metrics

### Time Savings
- **Traditional**: 2-4 weeks (manual coordination)
- **With Agents**: 10-15 minutes (automated)
- **Improvement**: 95% faster

### Cost Savings
- Automated cost optimization (spot instances, reserved capacity)
- Policy enforcement prevents overprovisioning
- Typical savings: 20-30% vs. manual provisioning

### Quality Improvements
- Consistent infrastructure (no manual errors)
- Security best practices (encryption, networking)
- Compliance checks (automated)

---

## Next Steps

- [Monitoring & Observability](./monitoring-observability.md)
- [Cost Optimization](./cost-optimization.md)
- [Framework Comparison](../guides/framework-comparison.md)
