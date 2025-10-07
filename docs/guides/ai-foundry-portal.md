# AI Foundry Portal Setup Guide

## Overview

Quick start guide for building agentic DataOps using AI Foundry Portal (Prompt Flow).

**Best for**: Rapid prototyping, POCs, teams without Python expertise.

---

## Prerequisites

- Azure subscription
- AI Foundry project created
- Azure CLI installed

---

## Quick Start

### 1. Create AI Foundry Project

```bash
# Via Azure Portal
# Navigate to portal.azure.com → AI Foundry → Create Project
```

### 2. Import Prompt Flow Template

```bash
# Import workspace provisioning flow
az ml flow create --file flows/workspace-provisioning.yaml \
  --name workspace-provisioning \
  --resource-group rg-data-platform

# Deploy as endpoint
az ml online-endpoint create \
  --name workspace-api \
  --deployment workspace-provisioning
```

### 3. Test the Flow

```bash
curl -X POST https://workspace-api.azureml.net/invoke \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"user_request": "Create Spark workspace"}'
```

---

## Next Steps

- [Framework Comparison](./framework-comparison.md)
- [AI Foundry SDK Setup](./ai-foundry-sdk.md)
- [Architecture Overview](../architecture/01-overview.md)
