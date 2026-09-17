# TOR Monitor – Temperature-Sensitive Pharma Tracking

Automated Time Out of Refrigerator (TOR) monitoring, alerting, and compliance enforcement for pharmaceutical materials across manufacturing, staging, transportation, and warehouse movements.

## Business Challenge

The manufacturing and distribution of temperature-sensitive pharmaceutical products require strict compliance with Time Out of Refrigerator (TOR) limits to maintain product quality, efficacy, and regulatory compliance. Currently, tracking TOR is manual, error-prone, and inefficient. There is a real risk that ingredients, work-in-process materials, and finished goods may exceed their allowable exposure time outside controlled refrigeration environments during manufacturing, staging, transportation, or warehouse movements. Exceeding TOR means the material can no longer be used and must be scrapped. The business requires an automated solution to monitor, track, and alert personnel when materials approach or exceed their maximum allowable TOR threshold.

**TOR tracking scope:** starts when a pallet/batch/material is removed from the fridge, and stops when it is put away in the destination fridge on the Production Supply Area (PSA).

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Reduction in scrapped batches due to TOR exceedance | — | 80% reduction | — | Warehouse & shopfloor material handling | user |
| TOR alert lead time before limit breach | Manual / none | Alert at 80% of TOR threshold | — | TOR monitoring & alerting | user |
| Audit trail coverage for TOR events | Partial / manual | 100% of batches | — | Regulatory compliance & quality management | user |
| Manual TOR tracking effort | Manual logging | Fully automated (eliminate manual) | — | Warehouse & quality operations | user |
| Go-live timeline | — | Q3 2025 | Q3 2025 | Programme delivery | user |

## Key Milestones

| Milestone | Condition |
|-----------|-----------|
| TOR timer started | Batch/pallet is confirmed removed from fridge (movement event received from SAP S/4HANA EWM/WM) |
| Warning alert issued | Cumulative TOR exposure reaches 80% of the maximum allowable threshold |
| Breach alert issued | Cumulative TOR exposure reaches or exceeds 100% of the maximum allowable threshold |
| Stock status changed to blocked | Warehouse manager confirms action; stock type updated from unrestricted-use to blocked in SAP S/4HANA |
| TOR timer stopped & event logged | Batch/pallet confirmed put away in destination fridge on PSA; full audit record written |

## Business Architecture (RBA)

### End-to-End Process

Plan to Fulfill (generic) — with life sciences / pharmaceutical industry variants

### Process Hierarchy

```
Plan to Fulfill (E2E)
└── Plan to Optimize Fulfillment (generic)
    └── Monitor and optimize supply chain performance (BPS-340)
        └── Control and monitor supply chain
        └── Quality inspection and batch compliance
        └── Warehouse/inventory management and stock transfers
        └── Automated supply chain disruption alerting
```

### Summary

The TOR monitoring challenge maps to the Plan to Fulfill E2E process, specifically the supply chain monitoring sub-process (BPS-340), extended with pharmaceutical life sciences variants covering quality inspection, warehouse stock management (unrestricted-to-blocked stock transfers), and automated disruption alerting across manufacturing, staging, and warehouse movements.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Gap? | Notes / assumptions |
|------------------------|-------------------------|------------|-------------------|--------------------|------|---------------------|
| Real-time TOR timer tracking per batch/pallet from fridge removal to put-away | SAP IBP – Supply Chain Risk Management | — | — | — | Yes | SAP IBP covers supply chain risk monitoring but not granular real-time TOR timers at batch level; custom n8n workflow required |
| Warning alert at 80% TOR threshold to warehouse / shopfloor managers | SAP IBP – Supply Chain Planning Analytics | — | — | — | Yes | IBP does not provide operator-level real-time threshold alerting; n8n workflow with notification node needed |
| Breach alert at 100% TOR threshold with stock block action | — | `sap.s4:apiResource:API_MATERIAL_STOCK_SRV:v1` | — | — | Yes | No MCP server; API available for stock status read; stock block action requires S/4HANA goods movement API |
| Batch/material identification and TOR limit lookup | — | `sap.s4:apiResource:API_BATCH_SRV:v1` | — | — | Partial | Batch master record API available; TOR limit per material must be maintained as a custom batch field or separate config |
| Warehouse movement event detection (fridge out / fridge in) | — | `sap.s4:apiResource:WAREHOUSEORDER_0001:v1` | — | — | Partial | Warehouse order & task API available; movement confirmation events can be polled or triggered |
| Stock type change unrestricted → blocked on TOR breach | — | `sap.s4:apiResource:CE_WHSEPHYSICALSTOCKPRODUCTS_0001:v1` | — | — | Yes | Physical stock update API available; blocking logic must be orchestrated via workflow |
| Complete audit trail of TOR exposure events per batch | — | — | — | — | Yes | No standard SAP audit trail for TOR events; n8n workflow must log events to a persistent store or CAP service |
| Multi-role notifications (warehouse manager, shopfloor manager, quality manager) | — | — | — | — | Yes | Requires custom notification routing; n8n workflow with role-based alert routing |

### Key Findings

- No MCP servers exist for any of the identified SAP S/4HANA APIs (batch, warehouse stock, warehouse order); direct API calls via n8n HTTP nodes or an AI agent with MCP-translated tools will be required.
- SAP IBP covers supply chain risk and planning analytics at a strategic level but does not address real-time, batch-level TOR countdown and threshold alerting — a custom solution is required.
- The core orchestration (TOR timer, threshold evaluation, alert routing, stock blocking) is a well-defined deterministic workflow — ideal for **n8n Workflow**.
- An **AI Agent** adds value for one open-ended reasoning step: dynamically assessing whether a near-breach batch should be expedited to the line or held, based on production schedule context and remaining TOR time.
- Five SAP S/4HANA OData APIs are available to integrate with: Material Stock, Batch Master Record, Warehouse Order & Task, Warehouse Physical Stock, and Warehouse Available Stock.
- TOR limit per material/batch will need to be maintained as a configuration table (custom CAP service or batch classification value), as no standard SAP field exists for this.

## Recommendations

### Automated TOR Monitoring, Alerting & Compliance Enforcement

#### Executive Summary

n8n workflow for deterministic TOR tracking + AI agent for expedite/hold advisory reasoning.

#### Recommended Solution

A two-component solution built on SAP BTP:

1. **n8n Workflow** — the core TOR engine:
   - Triggered by warehouse movement events from SAP S/4HANA (fridge-out confirmed).
   - Starts a TOR countdown timer per batch/pallet using the configured TOR limit for that material.
   - Evaluates elapsed TOR time on a scheduled polling basis.
   - Issues warning notifications (at 80% threshold) to warehouse and shopfloor managers via email/Teams.
   - Issues breach notifications (at 100% threshold) and automatically initiates a stock type change from unrestricted-use to blocked stock in SAP S/4HANA via API.
   - Stops the timer and logs a complete audit event when put-away in the destination fridge is confirmed.
   - Routes notifications to the correct roles: warehouse manager, shopfloor manager, quality manager.

2. **AI Agent** — advisory reasoning sub-step (invoked from the n8n workflow at warning stage):
   - Assesses whether a near-breach batch should be expedited to the production line or held, based on remaining TOR time, production schedule, and batch quantity.
   - Returns a natural language recommendation to the shopfloor manager as part of the warning alert.

Supporting components:
- **CAP Service** — maintains the TOR limit configuration table (material → max TOR minutes) and serves as the persistent audit log store for all TOR exposure events.
- **SAP S/4HANA APIs** — Batch Master Record, Warehouse Order & Task, Material Stock, and Physical Stock APIs provide movement event data and enable the stock blocking action.

#### Problem Statement

Manual TOR tracking is inefficient and error-prone, creating risk of undetected exceedances, product waste, regulatory non-compliance, and patient safety issues. An automated solution is needed that tracks TOR from the moment a batch leaves the fridge, warns staff proactively, enforces stock blocking at breach, and maintains a complete regulatory audit trail — all without manual intervention.

#### Affected User Roles

- **Warehouse Manager** — receives breach alerts, confirms stock block action, monitors all active TOR timers.
- **Shopfloor Manager** — receives warning and breach alerts, acts on expedite/hold recommendations, prevents use of non-compliant materials in manufacturing.
- **Quality Manager** — reviews audit trail for regulatory compliance, receives breach notifications for quality investigation initiation.

#### Important Factors

##### Real-time Timer Accuracy
TOR tracking requires sub-minute accuracy for timers. The n8n workflow scheduler must be configured with an appropriately short polling interval (e.g. every 1–5 minutes) to ensure warning and breach notifications fire promptly.

##### TOR Limit Configuration
No standard SAP field exists for TOR limit per material. A configuration table (maintained in the CAP service or as a batch classification value in SAP) must be established and kept up to date by the quality team before go-live.

##### Stock Blocking API Authorization
The automated stock type change (unrestricted → blocked) via API requires appropriate SAP S/4HANA authorisation. This must be provisioned for the integration user in the SAP system before deployment.

##### Regulatory Audit Trail
The complete TOR event log (fridge-out timestamp, warning event, breach event if any, fridge-in timestamp, action taken, responsible user) must be retained for the regulatory-required period. The CAP service audit log must be designed to be immutable and exportable for GxP compliance purposes.

#### Potential Risks

##### Integration Dependency on SAP S/4HANA Movement Events
The TOR timer relies on receiving timely warehouse movement confirmations from SAP S/4HANA. If movements are confirmed late or out of sequence, TOR tracking accuracy will be affected. A reconciliation / catch-up mechanism should be designed.

##### Scope of Materials Covered
Not all materials in the warehouse may be temperature-sensitive. The solution must reliably distinguish TOR-applicable batches from non-applicable ones to avoid false alerts. Material-level TOR configuration must be comprehensive at go-live.

#### Recommended Solution Category

n8n Workflow, AI Agent

#### Intent Fit

88%
