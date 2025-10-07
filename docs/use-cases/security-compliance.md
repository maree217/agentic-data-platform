# Security & Compliance Automation

## Overview

Autonomous agents for continuous security scanning, vulnerability detection, and compliance management.

## Key Capabilities

- Vulnerability scanning (CVE detection)
- Secret detection in code repositories
- Policy compliance (PCI-DSS, HIPAA, SOC2)
- Auto-remediation of security issues
- Compliance report generation

## Example

```
🛡️ Security Score: 85/100
🔴 Critical Issues: 2
🟡 High Issues: 5

Auto-fixed:
✅ NSG rule (SSH from 0.0.0.0/0) → restricted to VPN
✅ Storage account (public access) → private endpoint
✅ Service principal (Owner role) → Contributor

Requires approval:
👤 Rotate storage keys (impacts 3 apps)
```

## Implementation

See [Framework Comparison](../guides/framework-comparison.md) for details.

## Next Steps

- [Disaster Recovery](./disaster-recovery.md)
- [Getting Started](../guides/getting-started.md)
