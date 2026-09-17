# Specification: tor-monitoring-workflow

> **Guidelines**: Read [guidelines-n8n-workflow.md](../guidelines-n8n-workflow.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` for full business context
- [ ] Set up solution structure using the `setup-solution` skill — create asset `tor-monitoring-workflow` of type `n8n-workflow`

## API Integration Setup

> No MCP servers exist for these APIs. Workflow will call SAP S/4HANA APIs via HTTP Request nodes using placeholder URLs.

- [ ] Generate MCP translation files from all 4 downloaded API specs using the `mcp-translation-file` skill:
  - `specification/tor-monitoring-workflow/api-specs/API_BATCH_SRV.edmx` → ORD ID: `sap.s4:apiResource:API_BATCH_SRV:v1`
  - `specification/tor-monitoring-workflow/api-specs/WAREHOUSEORDER_0001.edmx` → ORD ID: `sap.s4:apiResource:WAREHOUSEORDER_0001:v1`
  - `specification/tor-monitoring-workflow/api-specs/API_MATERIAL_STOCK_SRV.edmx` → ORD ID: `sap.s4:apiResource:API_MATERIAL_STOCK_SRV:v1`
  - `specification/tor-monitoring-workflow/api-specs/CE_WHSEPHYSICALSTOCKPRODUCTS_0001.edmx` → ORD ID: `sap.s4:apiResource:CE_WHSEPHYSICALSTOCKPRODUCTS_0001:v1`

## REQ-01: Automated TOR Timer Start on Fridge Removal

- [ ] Create a scheduled trigger node (polling interval ≤ 5 minutes) to poll SAP S/4HANA for confirmed warehouse task movements
- [ ] Add an HTTP Request node to query `WAREHOUSEORDER_0001` WarehouseTask entity, filtering by `WarehouseTaskStatus = "C"` (confirmed) and source storage bin matching fridge location
- [ ] Add a Filter node to isolate fridge-out tasks not yet registered in the CAP TOR audit log
- [ ] Add an HTTP Request node to look up the TOR limit for the batch's material from the CAP service `TORConfig` entity
- [ ] Add an HTTP Request node to create a new TOR timer record in the CAP service `TOREvents` entity with fields: `batchId`, `materialId`, `fridgeOutTimestamp`, `torLimitMinutes`, `status: "ACTIVE"`
- [ ] Add a structured log node: `M1.achieved: TOR timer started for batch {batchId}, material {materialId}, fridge-out at {timestamp}, TOR limit {torLimitMinutes} min`
- [ ] Add an error branch: if timer creation fails, log `M1.missed: fridge-out event received for batch {batchId} but TOR timer could not be started — {reason}`

## REQ-05: TOR Limit Configuration Lookup

- [ ] Add a sub-flow for TOR config read: HTTP GET to CAP service `TORConfig` filtered by `materialId`
- [ ] Add a fallback node: if no TOR limit found for material, skip TOR tracking and log a warning
- [ ] Validate that TOR limit value is > 0 before proceeding

## REQ-02: Warning Alert at 80% TOR Threshold with AI Recommendation

- [ ] Add a threshold evaluation node: compute `elapsedMinutes = now - fridgeOutTimestamp` for each ACTIVE TOR timer
- [ ] Add a Switch node: route to warning branch if `elapsedMinutes >= torLimitMinutes * 0.8` AND warning not yet sent
- [ ] Add an HTTP Request node to call the TOR Warning Advisory AI Agent: `POST https://tor-advisory-agent.company.com/invoke` with payload `{ batchId, materialId, elapsedMinutes, torLimitMinutes, remainingMinutes }`
- [ ] Add a timeout node: if agent response exceeds 30 seconds, proceed without recommendation and log the failure
- [ ] Add a notification node (email / Teams) to send warning alert to Warehouse Manager and Shopfloor Manager only — include: batch ID, material description, elapsed time, remaining time, AI recommendation (or "Unavailable" if agent timed out)
- [ ] Update TOR timer record in CAP service: set `warningAlertSentAt = now`, `aiRecommendation = <response>`
- [ ] Add structured log: `M2.achieved: warning alert issued for batch {batchId}, elapsed {elapsedMinutes} min of {torLimitMinutes} min, AI recommendation: {recommendation}`
- [ ] Add error branch: `M2.missed: 80% threshold reached for batch {batchId} but warning alert could not be sent — {reason}`

## REQ-03: Breach Alert and Automatic Stock Block at 100% TOR

- [ ] Add a Switch node: route to breach branch if `elapsedMinutes >= torLimitMinutes` AND breach not yet processed
- [ ] Add an HTTP Request node to look up the physical stock record in `CE_WHSEPHYSICALSTOCKPRODUCTS_0001` for the batch
- [ ] Add an HTTP Request node to call `ChangeStockType` action on `WarehousePhysicalStockProducts` entity, setting `EWMStockType` to blocked stock value
- [ ] Add a notification node (email / Teams) to send breach alert to ALL three roles: Warehouse Manager, Shopfloor Manager, Quality Manager — include: batch ID, material, elapsed time, breach confirmation, stock block status, link to audit record
- [ ] Update TOR timer record in CAP service: set `breachAlertSentAt = now`, `stockBlockedAt = now`, `status: "BREACHED"`
- [ ] Add structured log: `M3.achieved: TOR breach confirmed for batch {batchId}, stock blocked in S/4HANA, breach notifications sent to all roles`
- [ ] Add error branch (stock block fails): `M3.missed: TOR breach detected for batch {batchId} but stock block action failed — {reason}; manual intervention required` + send high-priority alert to Warehouse Manager and Quality Manager

## REQ-04: TOR Timer Stop and Audit Log on Fridge Put-Away

- [ ] Add polling logic to detect confirmed warehouse tasks with destination bin matching fridge location on PSA
- [ ] Add Filter node to match put-away tasks to active TOR timer records by batch ID
- [ ] Add computation node: `totalExposureMinutes = fridgeInTimestamp - fridgeOutTimestamp`
- [ ] Add HTTP Request node to update TOR timer record in CAP service: set `fridgeInTimestamp`, `totalExposureMinutes`, `status: "COMPLETED"`, write complete audit record
- [ ] Add structured log: `M4.achieved: TOR timer stopped for batch {batchId}, total exposure {totalMinutes} min, full audit record written`
- [ ] Add error branch: `M4.missed: put-away event received for batch {batchId} but audit record could not be written — {reason}`

## REQ-06: Multi-Role Notification Routing

- [ ] Implement role-based routing: define configuration variables for each role's email / Teams webhook
  - `WAREHOUSE_MANAGER_CHANNEL` — receives warning (80%) and breach (100%) alerts
  - `SHOPFLOOR_MANAGER_CHANNEL` — receives warning (80%) and breach (100%) alerts
  - `QUALITY_MANAGER_CHANNEL` — receives breach (100%) alerts only
- [ ] Warning notification payload must include: batch ID, material description, elapsed TOR time, remaining time, AI recommendation, link to audit record
- [ ] Breach notification payload must include: batch ID, material description, elapsed TOR time, breach confirmation, stock block status, link to audit record

## Workflow Finalisation

- [ ] Combine all branches into a single unified TOR monitoring workflow JSON file: `assets/n8n/workflows/tor-monitoring-workflow.n8n.json`
- [ ] Ensure `connections` reference nodes by `name`, not `id`
- [ ] Set placeholder URLs:
  - SAP S/4HANA: `https://your-s4hana.company.com/sap/opu/odata/...`
  - CAP service: `https://your-cap-service.company.com/...`
  - AI Agent: `https://tor-advisory-agent.company.com/invoke`
- [ ] Do NOT include `credentials` blocks in any node
- [ ] Validate workflow JSON is well-formed
- [ ] Run `n8n-mcp__validate-n8n-workflow` to confirm workflow passes validation before finalising
