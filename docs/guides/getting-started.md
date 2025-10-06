# Getting Started with Agentic Data Platform

## Overview

This guide will walk you through setting up the Agentic Data Platform in your Azure environment, from initial setup to running your first autonomous workflow. Estimated time: **30-45 minutes**.

---

## Prerequisites

### Azure Requirements
- **Azure Subscription** with the following permissions:
  - Contributor access to create resources
  - Permission to create service principals
  - Access to Azure AI Foundry (preview access if required)

### Local Development Environment
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Terraform 1.6+** or **Azure CLI 2.50+** ([Download Terraform](https://www.terraform.io/downloads))
- **Git** ([Download](https://git-scm.com/downloads))
- **Docker** (optional, for local development) ([Download](https://www.docker.com/products/docker-desktop))

### Knowledge Prerequisites
- Basic understanding of Azure services (Data Factory, Storage Accounts)
- Familiarity with Infrastructure as Code (Terraform or Bicep)
- Python programming basics

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/agentic-data-platform.git
cd agentic-data-platform

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure Azure Credentials

### Option A: Using Azure CLI (Recommended for local development)

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Verify
az account show
```

### Option B: Using Service Principal (Recommended for production)

```bash
# Create a service principal
az ad sp create-for-rbac \
  --name "agentic-data-platform-sp" \
  --role Contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID

# Output will include:
# {
#   "appId": "xxxxx",
#   "password": "xxxxx",
#   "tenant": "xxxxx"
# }

# Set environment variables
export ARM_CLIENT_ID="<appId>"
export ARM_CLIENT_SECRET="<password>"
export ARM_TENANT_ID="<tenant>"
export ARM_SUBSCRIPTION_ID="YOUR_SUBSCRIPTION_ID"
```

### Configure Environment Variables

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env with your values
nano .env
```

**.env file contents:**
```bash
# Azure Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_REGION=eastus

# AI Foundry Configuration
AI_FOUNDRY_PROJECT_NAME=agentic-data-platform
AI_FOUNDRY_RESOURCE_GROUP=rg-agentic-platform

# Environment
ENVIRONMENT=dev  # or staging, prod

# Optional: GitHub for CI/CD
GITHUB_TOKEN=your-github-token
GITHUB_REPO=your-username/agentic-data-platform
```

---

## Step 3: Deploy Core Infrastructure

You have two options for deploying infrastructure:

### Option A: Let the Infrastructure Agent Deploy (Autonomous)

This is the **recommended approach** to experience the agentic automation:

```bash
# Run the autonomous deployment script
python scripts/setup/deploy_with_agent.py \
  --environment dev \
  --region eastus \
  --approve

# The Infrastructure Agent will:
# 1. Analyze your environment
# 2. Generate Terraform configuration
# 3. Estimate costs
# 4. Deploy resources (with your approval)
# 5. Validate deployment
```

**Expected Output:**
```
🤖 Infrastructure Agent Starting...
📋 Environment: dev
📍 Region: eastus

Step 1/5: Analyzing environment requirements...
✅ Subscription validated
✅ Resource naming conventions applied

Step 2/5: Generating Terraform configuration...
✅ Created terraform/environments/dev.tfvars
✅ Created terraform/main.tf

Step 3/5: Cost estimation...
💰 Estimated monthly cost: $234
  - Azure AI Foundry: $120
  - Data Factory: $50
  - Storage Account: $24
  - Networking (VNet, Private Endpoints): $40

Step 4/5: Deploying infrastructure...
⏳ Running: terraform apply
✅ Resource Group created: rg-agentic-platform-dev
✅ AI Foundry project created
✅ Storage Account created: stadpdev001
✅ Data Factory created: adf-adp-dev-001

Step 5/5: Validation...
✅ All resources healthy
✅ Network connectivity verified

🎉 Deployment complete! (Duration: 8m 32s)

Next steps:
  1. Deploy agents: python scripts/deploy_agents.sh
  2. Run health check: python scripts/monitoring/agent_health_check.py
```

### Option B: Manual Terraform Deployment

If you prefer traditional IaC workflow:

```bash
cd infra/terraform

# Initialize Terraform
terraform init

# Create a workspace for your environment
terraform workspace new dev
terraform workspace select dev

# Review the plan
terraform plan -var-file=environments/dev.tfvars -out=tfplan

# Apply the plan
terraform apply tfplan
```

**What Gets Deployed:**
- Resource Group
- Azure AI Foundry Project (with model deployments)
- Azure Storage Account (for data lake)
- Azure Data Factory (for orchestration)
- VNet with Private Endpoints (optional, for production)
- Key Vault (for secrets)
- Log Analytics Workspace (for monitoring)

---

## Step 4: Deploy Agents to Azure AI Foundry

```bash
# Deploy all agents
python scripts/deploy_agents.sh --environment dev

# Or deploy specific agents
python scripts/deploy_agents.sh \
  --environment dev \
  --agents infrastructure,pipeline,data-quality
```

**Deployment Process:**
1. Packages agent code and dependencies
2. Creates agent definitions in Azure AI Foundry
3. Configures tools and permissions
4. Deploys to managed endpoints
5. Runs smoke tests

**Expected Output:**
```
🚀 Deploying Agents to Azure AI Foundry...

Agent 1/6: Infrastructure Agent
  ✅ Code packaged
  ✅ Agent created (ID: agent-infra-001)
  ✅ Tools configured: terraform, azure-sdk, cost-estimator
  ✅ Deployed to endpoint
  ✅ Smoke test passed

Agent 2/6: Pipeline Agent
  ✅ Code packaged
  ✅ Agent created (ID: agent-pipeline-001)
  ✅ Tools configured: adf-sdk, databricks-api
  ✅ Deployed to endpoint
  ✅ Smoke test passed

... (repeats for all 6 agents)

🎉 All agents deployed successfully!

Agent Endpoints:
  - Infrastructure: https://ai-foundry.azure.com/agents/agent-infra-001
  - Pipeline: https://ai-foundry.azure.com/agents/agent-pipeline-001
  - Data Quality: https://ai-foundry.azure.com/agents/agent-quality-001
  - ML Ops: https://ai-foundry.azure.com/agents/agent-mlops-001
  - Cost Optimizer: https://ai-foundry.azure.com/agents/agent-cost-001
  - Governance: https://ai-foundry.azure.com/agents/agent-gov-001
```

---

## Step 5: Verify Agent Health

```bash
# Run comprehensive health check
python scripts/monitoring/agent_health_check.py

# Check specific agent
python scripts/monitoring/agent_health_check.py --agent infrastructure
```

**Expected Output:**
```
🏥 Agent Health Check Report

Agent: Infrastructure Agent
  Status: ✅ Healthy
  Endpoint: https://ai-foundry.azure.com/agents/agent-infra-001
  Last Active: 2 minutes ago
  Success Rate: 100% (24/24 requests)
  Avg Response Time: 1.2s
  Tools Available: ✅ terraform, ✅ azure-sdk, ✅ cost-estimator

Agent: Pipeline Agent
  Status: ✅ Healthy
  Endpoint: https://ai-foundry.azure.com/agents/agent-pipeline-001
  Last Active: 5 minutes ago
  Success Rate: 98% (47/48 requests)
  Avg Response Time: 2.3s
  Tools Available: ✅ adf-sdk, ✅ databricks-api

... (repeats for all agents)

Overall Platform Health: ✅ Healthy
  - 6/6 agents operational
  - Average success rate: 99.2%
  - No critical alerts
```

---

## Step 6: Run Your First Autonomous Workflow

### Example 1: Create an Autonomous Data Pipeline

```bash
# Run the quickstart example
python examples/quickstart/autonomous_pipeline_creation.py \
  --source "sqlserver-prod.dbo.sales_orders" \
  --destination "datalake-bronze.sales" \
  --schedule "daily-2am"
```

**What Happens Behind the Scenes:**

1. **Supervisor Agent** receives the request and decomposes it:
   ```
   Goal: Create production-ready data pipeline
   Tasks:
     1. Provision infrastructure (Data Factory)
     2. Create pipeline definition (incremental load)
     3. Add data quality validations
     4. Deploy to production
     5. Setup monitoring
   ```

2. **Infrastructure Agent** provisions resources:
   ```bash
   # Terraform: create Data Factory and required resources
   terraform apply -auto-approve
   # Output: Data Factory 'adf-sales-pipeline-001' created
   ```

3. **Pipeline Agent** creates the pipeline:
   ```python
   # Creates ADF pipeline with:
   # - Lookup activity (get max watermark)
   # - Copy activity (incremental load)
   # - Stored procedure (update watermark)
   # - Schedule trigger (daily 2 AM)
   ```

4. **Data Quality Agent** adds validations:
   ```yaml
   # Generates validation suite:
   validations:
     - column: order_id
       type: unique
       threshold: 100%
     - column: order_date
       type: freshness
       max_age_hours: 24
     - column: total_amount
       type: range
       min: 0
       max: 1000000
   ```

5. **Deployment Agent** deploys to production:
   ```bash
   # Deploys pipeline with approval gate
   # Runs smoke test
   # Activates schedule
   ```

6. **Monitoring Agent** sets up observability:
   ```bash
   # Creates Azure Monitor alerts:
   # - Pipeline failure
   # - Data quality breach
   # - Cost anomaly
   # Creates dashboard with key metrics
   ```

**Expected Output:**
```
🤖 Autonomous Pipeline Creation

Step 1/6: Analyzing requirements...
  ✅ Source: SQL Server (sqlserver-prod.dbo.sales_orders)
  ✅ Destination: Data Lake (datalake-bronze.sales)
  ✅ Mode: Incremental (watermark on order_date)
  ✅ Schedule: Daily at 2:00 AM UTC

Step 2/6: Provisioning infrastructure...
  ⏳ Infrastructure Agent working...
  ✅ Data Factory 'adf-sales-pipeline-001' created
  ✅ Storage Account 'stadpbronze001' created
  💰 Estimated cost: $78/month

Step 3/6: Creating pipeline...
  ⏳ Pipeline Agent working...
  ✅ Pipeline 'pl-sales-incremental' created
  ✅ Watermark logic configured
  ✅ Schedule trigger created

Step 4/6: Adding data quality validations...
  ⏳ Data Quality Agent working...
  ✅ Data profiling complete
  ✅ 5 validation rules created
  ✅ Integrated with pipeline

Step 5/6: Deploying to production...
  ⏳ Deployment Agent working...
  ✅ Deployed to production
  ✅ Smoke test passed
  ✅ Schedule activated

Step 6/6: Setting up monitoring...
  ⏳ Monitoring Agent working...
  ✅ 3 alerts configured
  ✅ Dashboard created

🎉 Pipeline Created Successfully!

Summary:
  Pipeline ID: pl-sales-incremental
  Status: Active
  Next Run: Tomorrow at 2:00 AM UTC
  Estimated Monthly Cost: $78
  Data Quality Rules: 5 active
  Monitoring Dashboard: https://portal.azure.com/dashboards/...

Total Time: 8 minutes, 47 seconds
(vs. 2-3 weeks manual process)
```

### Example 2: Self-Healing Pipeline Demo

```bash
# Simulate a pipeline failure and watch it self-heal
python examples/quickstart/self_healing_demo.py
```

**Scenario**: Pipeline fails due to source schema change (new column added).

**Self-Healing Flow**:
```
1. Pipeline Failure Event
   ↓
2. Monitoring Agent detects failure
   → Triggers Incident Response Agent
   ↓
3. Incident Response Agent analyzes logs
   → Root cause: Schema mismatch (new column 'customer_segment')
   ↓
4. Schema Evolution Agent updates pipeline
   → Adds new column to mapping
   → Updates destination schema
   ↓
5. Pipeline Agent retries execution
   → Pipeline succeeds
   ↓
6. Success! No manual intervention required.
   → Notification sent to team
```

**Output:**
```
🚨 Simulating Pipeline Failure...
  ❌ Pipeline failed: Schema mismatch

🤖 Self-Healing Initiated...

Step 1: Incident Detection
  ✅ Monitoring Agent detected failure (2s after occurrence)

Step 2: Root Cause Analysis
  ⏳ Incident Response Agent analyzing...
  ✅ Root cause identified: New column 'customer_segment' in source

Step 3: Automated Fix
  ⏳ Schema Evolution Agent updating pipeline...
  ✅ Column mapping updated
  ✅ Destination schema updated

Step 4: Retry Execution
  ⏳ Pipeline Agent retrying...
  ✅ Pipeline execution successful

🎉 Self-Healing Complete!
  Total downtime: 47 seconds
  No manual intervention required
  Team notified via email
```

---

## Step 7: Explore the Dashboard

Open the monitoring dashboard to see all agent activities:

```bash
# Open dashboard in browser
python scripts/monitoring/open_dashboard.py
```

**Dashboard Features:**
- **Agent Activity Timeline**: Visual timeline of all agent actions
- **Cost Tracking**: Real-time cost by agent and resource
- **Data Quality Metrics**: Validation pass rates, anomaly detection
- **Pipeline Status**: All active pipelines and their health
- **Self-Healing Events**: Log of autonomous recovery actions

---

## Next Steps

### 1. Explore More Use Cases

```bash
# Cost optimization
python examples/cost-optimization/weekly_review.py

# ML pipeline creation
python examples/ml-ops/auto_feature_discovery.py

# Governance and compliance
python examples/governance/pii_detection.py
```

### 2. Build a Custom Agent

Follow the [Agent Development Guide](./agent-development.md) to create your own specialized agent.

### 3. Integrate with CI/CD

Set up automated deployments:
```bash
# Configure GitHub Actions
python scripts/setup/configure_cicd.py \
  --platform github \
  --repo your-username/agentic-data-platform
```

### 4. Multi-Environment Setup

Deploy to staging and production:
```bash
# Deploy to staging
python scripts/setup/deploy_with_agent.py --environment staging

# Deploy to production (with approval gates)
python scripts/setup/deploy_with_agent.py --environment prod
```

---

## Common Issues and Troubleshooting

### Issue 1: Azure AI Foundry Access Denied

**Symptom**: `Error: You don't have access to Azure AI Foundry`

**Solution**:
```bash
# Request preview access (if required)
# https://azure.microsoft.com/en-us/products/ai-foundry

# Verify your subscription has AI Foundry enabled
az provider show --namespace Microsoft.AzureAIFoundry
```

### Issue 2: Terraform State Lock

**Symptom**: `Error acquiring the state lock`

**Solution**:
```bash
# Force unlock (use with caution)
terraform force-unlock LOCK_ID

# Or delete the lock in Azure Storage
az storage blob delete \
  --account-name YOUR_STORAGE_ACCOUNT \
  --container-name tfstate \
  --name terraform.tfstate.lock
```

### Issue 3: Agent Deployment Timeout

**Symptom**: Agent deployment hangs at "Deploying to endpoint"

**Solution**:
```bash
# Check agent logs
python scripts/monitoring/agent_logs.py --agent infrastructure

# Redeploy specific agent
python scripts/deploy_agents.sh --agents infrastructure --force
```

### Issue 4: High Costs

**Symptom**: Azure bill is higher than expected

**Solution**:
```bash
# Run cost analysis
python scripts/cost/analyze_spend.py

# Let Cost Optimizer Agent find savings
python scripts/cost/optimize.py --auto-approve-nonprod
```

---

## Resource Cleanup

To delete all resources (be careful in production!):

```bash
# Delete all agents
python scripts/cleanup/delete_agents.py --environment dev

# Delete infrastructure
cd infra/terraform
terraform destroy -var-file=environments/dev.tfvars

# Or use the cleanup agent
python scripts/cleanup/autonomous_cleanup.py --environment dev --confirm
```

---

## Getting Help

- **Documentation**: [Full Docs](../README.md)
- **Examples**: [/examples](../../examples/)
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/agentic-data-platform/issues)
- **Community**: [Discord](https://discord.gg/agentic-data)
- **Commercial Support**: [Contact Sales](mailto:sales@example.com)

---

## What's Next?

You've successfully set up the Agentic Data Platform! Here are recommended next steps:

1. **[Architecture Deep Dive](../architecture/01-overview.md)**: Understand how agents work together
2. **[Build Custom Agents](./agent-development.md)**: Create specialized agents for your use cases
3. **[Multi-Agent Patterns](./multi-agent-patterns.md)**: Learn advanced orchestration patterns
4. **[Security Best Practices](./security.md)**: Harden your production deployment
5. **[Use Cases](../use-cases/)**: Explore real-world implementations

---

**Congratulations!** 🎉 You've deployed an autonomous data platform that can provision infrastructure, create pipelines, ensure data quality, and optimize costs—all with minimal human intervention.
