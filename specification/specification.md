# Specification

> **Guidelines**: Read [guidelines.md](./guidelines.md) before executing ANY tasks below.

Check off items as completed.

## Solution Setup

- [x] Create asset directories: `mkdir -p assets/tor-monitoring-workflow/ assets/tor-advisory-agent/`
- [x] Invoke `setup-solution` skill to create `solution.yaml` and `asset.yaml` files for every asset:
  - `tor-monitoring-workflow` — type: `n8n-workflow`
  - `tor-advisory-agent` — type: `agent`
- [x] Validate all `asset.yaml` and `solution.yaml` files exist and are well-formed

## Asset Implementation

- [x] Execute `specification/tor-monitoring-workflow/specification.md` (all items)
- [x] Execute `specification/tor-advisory-agent/specification.md` (all items)
- [x] Cross-implementation compatibility check:
  - ✅ n8n workflow calls agent via `CUSTOM.sapAgent` node using ORD ID `customer.build:agent:tor-monitor-1fdde.tor-advisory-agent:v1`
  - ✅ JSON payload sent from n8n includes `batchId`, `materialId`, `elapsedMinutes`, `torLimitMinutes`, `remainingMinutes` (all in the `input` string expression)
  - ✅ Both assets reference same CAP service placeholder `https://your-cap-service.company.com`
  - ✅ Warning notifications route to Warehouse Manager + Shopfloor Manager only; breach notifications route to all three roles
  - ✅ Agent uses `customer.build:agent:` ORD ID format in n8n `agents` / `agentName` parameters
