# Product Requirements Document (PRD)

**Title:** TOR Monitor – Temperature-Sensitive Pharma Tracking  
**Date:** 2026-09-17  
**Owner:** TBD  
**Solution Category:** n8n Workflow + AI Agent

---

## Product Purpose & Value Proposition

**Elevator Pitch:**  
Pharmaceutical manufacturers risk product loss, regulatory penalties, and patient safety incidents when temperature-sensitive batches silently exceed their Time Out of Refrigerator (TOR) limits. This solution automates TOR tracking from fridge removal to fridge put-away, warns staff proactively, blocks non-compliant stock automatically, and maintains a complete audit trail — eliminating the manual, error-prone status quo.

**Business Need:**  
Manual TOR tracking is inefficient and unreliable. There is no automated mechanism to start a timer when a batch leaves the fridge, alert personnel before the limit is breached, or enforce stock blocking when the limit is exceeded. The result is product waste, quality deviations, regulatory risk, and patient safety exposure.

**Expected Value:**

- 80% reduction in scrapped batches due to TOR exceedance
- Proactive warning alerts at 80% of threshold — preventing violations before they occur
- 100% audit trail coverage for all TOR exposure events
- Full elimination of manual TOR logging effort

**Product Objectives (Prioritised):**

1. Automate TOR timer tracking per batch from fridge-out to fridge-in on the PSA
2. Issue role-targeted warning (80%) and breach (100%) notifications with an AI-driven expedite/hold recommendation
3. Automatically change stock status from unrestricted-use to blocked on TOR breach via SAP S/4HANA API
4. Maintain a complete, immutable regulatory audit log of all TOR exposure events
5. Deliver a production-ready solution by Q3 2025

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Scrapped batches due to TOR exceedance | — | 80% reduction | — | Warehouse & shopfloor material handling | user |
| TOR alert lead time before limit breach | Manual / none | Alert at 80% of TOR threshold | — | TOR monitoring & alerting | user |
| Audit trail coverage for TOR events | Partial / manual | 100% of batches | — | Regulatory compliance & quality management | user |
| Manual TOR tracking effort | Manual logging | Fully automated | — | Warehouse & quality operations | user |
| Go-live timeline | — | Q3 2025 | Q3 2025 | Programme delivery | user |

---

## User Profiles & Personas

### Primary Persona: Marcus — Warehouse Manager

Marcus is a 42-year-old warehouse manager at a pharmaceutical manufacturing site. He oversees incoming, outgoing, and in-process material movements across cold storage and production staging areas. He manages a team of 15 operators and is responsible for ensuring stock accuracy, GxP compliance, and timely supply to the manufacturing line. He currently relies on paper-based TOR logs and verbal handovers, which regularly result in near-misses and occasional batch scraps. He is comfortable with SAP WM but has limited experience with digital alerting tools. His success is measured by zero TOR-related batch losses and zero regulatory findings in his area.

### Secondary Persona: Priya — Shopfloor Manager

Priya is a 37-year-old shopfloor manager responsible for production schedule adherence and material availability at the point of use. She receives materials from the warehouse and must ensure that only compliant, within-TOR batches are issued to manufacturing. She is frequently unaware of how long a batch has been out of the fridge until a deviation is raised. She needs timely, actionable alerts — not data dashboards — so she can either expedite a near-breach batch to the line or quarantine it before it is used in production.

### Tertiary Persona: Kavitha — Quality Manager

Kavitha is a 45-year-old quality manager responsible for GxP compliance, deviation management, and audit readiness. She needs a complete, exportable audit trail of every TOR exposure event per batch, including timestamps, actions taken, and responsible parties, to satisfy regulatory inspectors. She is not involved in day-to-day material movements but must be notified of every TOR breach and have access to historical records for investigations.

---

## Goals and Non-Goals

### Goals (In Scope)

- Automated TOR timer per batch from warehouse fridge-out event to PSA fridge put-away confirmation
- Warning notifications at 80% of TOR threshold to warehouse manager and shopfloor manager, including an AI advisory recommendation (expedite or hold)
- Breach notifications at 100% threshold to warehouse manager, shopfloor manager, and quality manager
- Automated stock type change (unrestricted-use → blocked) in SAP S/4HANA on TOR breach
- Persistent, immutable audit log of all TOR events per batch stored in a CAP service
- TOR limit configuration table per material maintained in the CAP service
- Multi-role notification routing (email / Microsoft Teams)

### Non-Goals (Out of Scope)

- Real-time IoT temperature sensor integration (TOR tracking is time-based, not sensor-based)
- UI dashboard for batch monitoring (role-targeted notifications replace a monitoring screen in this phase)
- TOR tracking for finished goods in outbound logistics
- Changes to SAP S/4HANA master data configuration or batch classification setup (assumed pre-existing)
- Integration with laboratory information management systems (LIMS)

---

## Requirements

### Must-Have Requirements

**REQ-01: Automated TOR Timer Start on Fridge Removal**

- **Problem to Solve**: There is no automated mechanism to detect when a batch leaves the fridge and start tracking its time outside refrigeration.
- **User Story**: As a warehouse manager, I need the TOR timer to start automatically when my team confirms removal of a batch from the fridge, so that I do not have to rely on manual logging.
- **Acceptance Criteria**:
  - Given a warehouse movement order is confirmed in SAP S/4HANA (fridge-out transfer), when the event is received by the workflow, then a TOR timer is started for that batch with a timestamp recorded in the audit log.
- **Maps to Objective**: 1
- **Priority Rank**: 1

---

**REQ-02: Warning Alert at 80% TOR Threshold with AI Recommendation**

- **Problem to Solve**: Staff have no advance warning before a TOR limit is breached, leaving no time to act preventively.
- **User Story**: As a shopfloor manager, I need to receive a warning notification when a batch reaches 80% of its TOR limit, including a recommendation on whether to expedite it to the production line or hold it, so that I can prevent waste and production disruption.
- **Acceptance Criteria**:
  - Given a batch TOR timer is active, when the elapsed time reaches 80% of the configured TOR limit for that material, then a warning notification is sent to the warehouse manager and shopfloor manager including the batch ID, remaining time, and an AI-generated expedite/hold recommendation.
- **Maps to Objective**: 2
- **Priority Rank**: 2

---

**REQ-03: Breach Alert and Automatic Stock Block at 100% TOR**

- **Problem to Solve**: When a TOR limit is exceeded, there is no automated mechanism to prevent the batch from being used in manufacturing.
- **User Story**: As a warehouse manager, I need the system to automatically change the stock status of a breached batch to blocked and notify all relevant managers, so that non-compliant materials cannot be used in production.
- **Acceptance Criteria**:
  - Given a batch TOR timer is active, when elapsed time reaches or exceeds 100% of the TOR limit, then a breach notification is sent to all three roles (warehouse manager, shopfloor manager, quality manager), and the stock type is changed from unrestricted-use to blocked in SAP S/4HANA via API call.
- **Maps to Objective**: 2, 3
- **Priority Rank**: 3

---

**REQ-04: TOR Timer Stop and Audit Log on Fridge Put-Away**

- **Problem to Solve**: The TOR exposure window must be closed and formally recorded when the batch reaches its destination fridge on the PSA.
- **User Story**: As a quality manager, I need the system to stop the TOR timer and write a complete audit record when the batch is confirmed put away in the destination fridge on the PSA, so that I have a full, accurate record of each batch's exposure for regulatory inspections.
- **Acceptance Criteria**:
  - Given a batch TOR timer is active, when a put-away confirmation event is received from SAP S/4HANA for the destination fridge location on the PSA, then the timer is stopped and a full audit record (fridge-out timestamp, warning event if any, breach event if any, fridge-in timestamp, total exposure time, action taken) is written to the CAP audit log.
- **Maps to Objective**: 1, 4
- **Priority Rank**: 4

---

**REQ-05: TOR Limit Configuration per Material**

- **Problem to Solve**: No standard SAP field exists for TOR limit per material; the system needs a reliable source of truth for this value.
- **User Story**: As a quality manager, I need to maintain the maximum allowable TOR time per material in a central configuration table, so that the monitoring workflow uses the correct threshold for every batch.
- **Acceptance Criteria**:
  - Given a material number exists in the system, when a quality manager accesses the TOR configuration table, then they can create, read, update, and view the maximum TOR minutes for that material. The workflow must read this table before evaluating thresholds.
- **Maps to Objective**: 1
- **Priority Rank**: 5

---

**REQ-06: Multi-Role Notification Routing**

- **Problem to Solve**: Different roles require different notifications at different threshold points; a single broadcast is insufficient and creates noise.
- **User Story**: As a warehouse manager, shopfloor manager, or quality manager, I need to receive only the notifications relevant to my role, so that I can act quickly without being overwhelmed by irrelevant alerts.
- **Acceptance Criteria**:
  - Warning alerts (80%) are routed to warehouse manager and shopfloor manager only. Breach alerts (100%) are routed to warehouse manager, shopfloor manager, and quality manager. Notifications include batch ID, material description, elapsed TOR time, remaining time (if any), recommended action, and a link to the audit record.
- **Maps to Objective**: 2
- **Priority Rank**: 6

---

## Solution Architecture

**Architecture Overview:**  
A two-component solution on SAP BTP: an n8n workflow as the core TOR engine and an AI agent for advisory reasoning at the warning stage, backed by a CAP service for configuration and audit persistence, integrating with SAP S/4HANA via OData APIs.

**Key Components:**

- **n8n Workflow (TOR Engine)**: orchestrates the full TOR lifecycle — timer start, threshold evaluation, notification dispatch, stock blocking, timer stop, and audit logging
- **AI Agent (Expedite/Hold Advisor)**: invoked at the 80% warning stage; reasons over remaining TOR time, batch quantity, and production schedule context to produce a natural language recommendation
- **CAP Service**: maintains the TOR limit configuration table and serves as the immutable audit log store for all TOR exposure events
- **SAP S/4HANA**: source of warehouse movement events and target for stock status change actions

**Integration Points:**

- SAP S/4HANA Batch Master Record API (`API_BATCH_SRV:v1`) — batch identification and material lookup
- SAP S/4HANA Warehouse Order & Task API (`WAREHOUSEORDER_0001:v1`) — fridge-out and fridge-in movement event detection
- SAP S/4HANA Material Stock API (`API_MATERIAL_STOCK_SRV:v1`) — stock status read
- SAP S/4HANA Physical Stock API (`CE_WHSEPHYSICALSTOCKPRODUCTS_0001:v1`) — stock type change (unrestricted → blocked)
- Notification channel (email / Microsoft Teams) — role-targeted alert delivery

### Agent Extensibility & Instrumentation

**Agent Extensibility:**  
The AI agent is designed with extension points to allow additional advisory reasoning capabilities in future phases, such as: cross-batch priority ranking when multiple near-breach batches compete for line access, integration with production scheduling systems for richer context, and escalation logic for repeated TOR violations.

**Business Step Instrumentation:**  
All business steps must emit structured log statements following the pattern `[MILESTONE_ID].[achieved|missed]: [description]` to enable observability and debugging in production.

### Automation & Agent Behaviour

**Automation Level:** Hybrid (rule-based workflow + autonomous AI advisory)

**Actions performed without human approval:**

- Start TOR timer on fridge-out movement confirmation
- Evaluate elapsed TOR time against configured thresholds on each polling cycle
- Send warning and breach notifications to the appropriate roles
- Change stock type from unrestricted-use to blocked in SAP S/4HANA on breach
- Stop timer and write audit record on fridge-in confirmation

**Actions requiring human review or approval:**

- Physical transfer of batch to scrap bin (warehouse manager manual action, triggered by breach notification)
- Override of an AI expedite/hold recommendation (shopfloor manager decision)

**Model / engine:** SAP Generative AI Hub (GPT-4o or equivalent) for the AI advisory agent; n8n rule-based scheduler for the workflow engine

**Knowledge & data sources accessed:**

- TOR configuration table (CAP service): TOR limit per material
- SAP S/4HANA warehouse movement events: batch/pallet location state
- SAP S/4HANA batch master: material description and classification
- Production schedule context (future phase): line demand and batch priority

**Tools or connectors invoked:**

- `TOR-monitor` workflow (via `tor-warning-advisory` MCP tool): invoked by the AI agent at the 80% warning stage to provide the expedite/hold recommendation back to the n8n workflow
- SAP S/4HANA Physical Stock API: write action to block stock (high-risk — requires authorised integration user)
- Notification connector (email / Teams): send role-targeted alerts (write — no rollback)

**Guardrails & fail-safes:**

- The stock blocking action is only triggered after the TOR limit is confirmed breached; no speculative blocking occurs
- If the SAP S/4HANA stock blocking API call fails, a high-priority manual intervention alert is sent to the warehouse manager and quality manager immediately
- If the AI agent fails to return a recommendation within the timeout window, the warning notification is sent without a recommendation and the failure is logged
- The TOR timer polling interval must be ≤5 minutes to ensure threshold evaluations are timely

### Configuration & Data

**Configuration Scope:**  
TOR limit per material must be configured in the CAP service before go-live. The SAP S/4HANA integration user must be provisioned with authorisation for the Physical Stock API write operation.

**Master Data:**

- TOR limit configuration table: material number → maximum TOR minutes; owned by the Quality team
- Material-to-role mapping: which materials are TOR-applicable; owned by the Quality team

---

## Milestones

### M1: TOR Timer Started

- **Description**: The TOR countdown for a batch begins.
- **Achieved when**: A fridge-out warehouse movement confirmation event is received from SAP S/4HANA and the timer record is created in the CAP audit log.
- **Log on achievement**: `M1.achieved: TOR timer started for batch {batchId}, material {materialId}, fridge-out at {timestamp}, TOR limit {torLimitMinutes} min`
- **Log on miss**: `M1.missed: fridge-out event received for batch {batchId} but TOR timer could not be started — {reason}`

### M2: Warning Alert Issued

- **Description**: The 80% TOR threshold has been reached and stakeholders are notified.
- **Achieved when**: Elapsed TOR time reaches 80% of the configured limit and warning notifications are dispatched to the warehouse manager and shopfloor manager.
- **Log on achievement**: `M2.achieved: warning alert issued for batch {batchId}, elapsed {elapsedMinutes} min of {torLimitMinutes} min, AI recommendation: {recommendation}`
- **Log on miss**: `M2.missed: 80% threshold reached for batch {batchId} but warning alert could not be sent — {reason}`

### M3: Breach Alert Issued and Stock Blocked

- **Description**: The TOR limit has been reached or exceeded; stock is blocked and all roles are notified.
- **Achieved when**: Elapsed TOR time reaches or exceeds 100% of the configured limit, breach notifications are dispatched to all three roles, and the SAP S/4HANA stock type change API call succeeds.
- **Log on achievement**: `M3.achieved: TOR breach confirmed for batch {batchId}, stock blocked in S/4HANA, breach notifications sent to all roles`
- **Log on miss**: `M3.missed: TOR breach detected for batch {batchId} but stock block action failed — {reason}; manual intervention required`

### M4: TOR Timer Stopped and Audit Record Written

- **Description**: The batch has been put away in the destination fridge on the PSA; the TOR exposure window is closed.
- **Achieved when**: A fridge-in put-away confirmation event is received from SAP S/4HANA for the PSA destination and the complete audit record is written to the CAP service.
- **Log on achievement**: `M4.achieved: TOR timer stopped for batch {batchId}, total exposure {totalMinutes} min, full audit record written`
- **Log on miss**: `M4.missed: put-away event received for batch {batchId} but audit record could not be written — {reason}`

---

## Risks, Assumptions, and Dependencies

### Risks

- **Late movement confirmations in SAP S/4HANA**: If fridge-out or fridge-in movements are confirmed late, TOR timers will be inaccurate. A catch-up / reconciliation mechanism should be designed for phase 2.
- **Incomplete TOR configuration at go-live**: If not all temperature-sensitive materials have a TOR limit configured before go-live, the workflow cannot track those batches. A pre-go-live data completeness check is required.
- **API authorisation provisioning**: The stock blocking API write requires a specifically authorised SAP integration user. Delays in SAP Basis provisioning could block go-live.

### Assumptions

- SAP S/4HANA warehouse movement confirmations are performed by operators in near-real time (within the polling interval).
- The integration user for the SAP S/4HANA Physical Stock API will be provisioned by the SAP Basis team prior to UAT.
- Notification channel (email or Microsoft Teams) is available and configured in the BTP subaccount.
- The scope of TOR-applicable materials is defined and owned by the Quality team before go-live.

### Dependencies

- SAP S/4HANA OData APIs (Batch, Warehouse Order, Material Stock, Physical Stock) — available and accessible from BTP
- SAP Generative AI Hub access for the AI advisory agent
- Quality team availability to populate the TOR configuration table before go-live
- SAP Basis team for integration user provisioning

---

## Governance, Risk & Compliance

**Data Handling:**

- All TOR event records in the CAP audit log are immutable once written; no delete or update operations are permitted post-creation.
- The audit log must be retained for the regulatory-required period (minimum per applicable GxP / GDP guidelines; to be confirmed with Quality).
- No PII is stored in TOR event records; batch IDs, material numbers, timestamps, and SAP user IDs only.

**Compliance Frameworks:**

- GxP / GDP pharmaceutical handling requirements (regulatory audit trail mandate)
- 21 CFR Part 11 or EU Annex 11 (electronic records and audit trail) — as applicable to the site

**Approval Flows:**

- Stock blocking action is system-automated on breach confirmation; warehouse manager receives notification and is responsible for physical scrap bin transfer.
- Quality manager must acknowledge all breach events in the audit log within the site-defined investigation SLA.

---

## Schedule & Timeline Context

**Target Timeline:** Q3 2025

**Business Drivers:**

- Product waste and regulatory risk are ongoing; each TOR exceedance incident carries financial and compliance cost.
- Forthcoming regulatory inspection requires demonstrable automated audit trail capability.

**Key Milestones:** See the Milestones section above.
