# Direct AI SDK Setup Guide

## Overview

Platform-agnostic agentic DataOps using Anthropic or OpenAI SDKs directly.

**Best for**: Multi-cloud, on-prem, cost optimization priority.

---

## Installation

```bash
# Anthropic SDK
pip install anthropic python-dotenv

# Or OpenAI SDK  
pip install openai python-dotenv

# Configure API keys
cp .env.example .env
# Add ANTHROPIC_API_KEY or OPENAI_API_KEY
```

---

## Quick Start (Anthropic)

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    messages=[{
        "role": "user",
        "content": "Generate Terraform for AKS cluster"
    }]
)

print(response.content[0].text)
```

---

## Next Steps

- [Framework Comparison](./framework-comparison.md)
- [Hybrid Approach](./hybrid-approach.md)
