# Specification: tor-advisory-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` for full business context
- [ ] Bootstrap agent code in `assets/tor-advisory-agent/` using instructions from the `sap-agent-bootstrap` section (invoke from inside `assets/tor-advisory-agent/`, use copy commands — do NOT create files manually)
- [ ] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

- [ ] Create runtime skill `assets/tor-advisory-agent/app/skills/tor-expedite-hold-advisor/SKILL.md` with:
  - Frontmatter: `name: tor-expedite-hold-advisor`, `description: Evaluates near-breach batches and recommends expedite or hold`
  - Body: Step-by-step decision logic:
    1. If remaining TOR time > 30 minutes AND production line has demand for this material: recommend EXPEDITE with urgency level
    2. If remaining TOR time < 15 minutes AND batch quantity exceeds immediate line demand: recommend HOLD and flag for quality review
    3. If batch is already breached (remaining <= 0): recommend SCRAP and notify quality manager
    4. Otherwise: recommend EXPEDITE with standard priority
  - Include pharmaceutical handling compliance note (GxP requirement)

---

## Project-Specific Tasks

### Agent Identity & System Prompt

- [ ] Configure agent identity in `app/agent.py`:
  - Name: `TOR Warning Advisory Agent`
  - Description: `Provides expedite or hold recommendations for near-breach temperature-sensitive pharmaceutical batches`
  - System prompt must include:
    - Role: pharmaceutical supply chain advisor for TOR compliance
    - Available tools: `get_batch_info` (via MCP), `get_material_stock` (via MCP), `load` (runtime skill loader)
    - Decision criteria: remaining TOR time, batch quantity, production schedule context, GxP compliance
    - Guardrails: NEVER recommend use of a batch that has already exceeded TOR; always include remaining time in recommendation; always cite the TOR limit used

### MCP Tool Integration

- [ ] API discovery results are in `specification/tor-advisory-agent/api-specs/` — invoke `mcp-translation-file` skill to generate MCP assets for:
  - `API_BATCH_SRV.edmx` → ORD ID: `sap.s4:apiResource:API_BATCH_SRV:v1` (batch identification and material lookup)
  - `API_MATERIAL_STOCK_SRV.edmx` → ORD ID: `sap.s4:apiResource:API_MATERIAL_STOCK_SRV:v1` (stock status read)
- [ ] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module
- [ ] Add MCP server dependencies to `asset.yaml` under `requires` — one entry per generated MCP server ORD ID
- [ ] Agent must use MCP tools for ALL SAP data lookups — NEVER use direct HTTP clients

### Agent Input / Output Contract

- [ ] Agent accepts a structured JSON payload from the n8n workflow:
  ```json
  {
    "batchId": "string",
    "materialId": "string",
    "elapsedMinutes": "number",
    "torLimitMinutes": "number",
    "remainingMinutes": "number"
  }
  ```
- [ ] Agent returns a natural language recommendation including:
  - Decision: EXPEDITE / HOLD / SCRAP
  - Urgency level: HIGH / MEDIUM / LOW
  - Reasoning: brief explanation (1–2 sentences)
  - Remaining TOR time used in decision
  - Compliance note: GxP / GDP handling requirement reference

### Fail-Safe Behaviour

- [ ] If MCP tool call fails to retrieve batch info, proceed with available data and note in recommendation: "Batch data unavailable — recommendation based on TOR time only"
- [ ] Agent must respond within 30 seconds; if LLM call times out, return: `{ "decision": "EXPEDITE", "urgency": "HIGH", "reasoning": "Advisory timeout — defaulting to expedite. Manual verification required." }`
- [ ] NEVER recommend EXPEDITE for a batch with `remainingMinutes <= 0`

---

## Business Instrumentation

- [ ] Implement structured logging for each milestone:
  - `[M2.achieved]: TOR advisory recommendation generated for batch {batchId} — decision: {decision}, urgency: {urgency}`
  - `[M2.missed]: TOR advisory agent failed to generate recommendation for batch {batchId} — {reason}`
- [ ] Add OpenTelemetry span for each advisory request with attributes: `batch_id`, `material_id`, `elapsed_minutes`, `tor_limit_minutes`, `decision`
- [ ] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## API Specs for MCP Translation

- [ ] Copy API specs from the workflow asset (they are shared):
  - `specification/tor-advisory-agent/api-specs/API_BATCH_SRV.edmx`
  - `specification/tor-advisory-agent/api-specs/API_MATERIAL_STOCK_SRV.edmx`
- [ ] After `mcp-translation-file` generates the MCP assets, generate `mcp-mock.json` using the `mcp-mock-config` skill

---

## Testing

- [ ] `conftest.py` only sets `IBD_TESTING=true`
- [ ] Write unit tests in `assets/tor-advisory-agent/tests/`:
  - `test_expedite_recommendation.py` — batch with 25% TOR remaining → EXPEDITE
  - `test_hold_recommendation.py` — batch with 5% TOR remaining and high quantity → HOLD
  - `test_scrap_recommendation.py` — batch with 0% remaining (already breached) → SCRAP
  - `test_mcp_tool_failure.py` — MCP batch lookup fails → recommendation still returned with caveat
  - `test_timeout_fallback.py` — LLM timeout → default EXPEDITE response returned
- [ ] Write one integration test: end-to-end agent flow with mocked MCP tools and mocked LLM, verify correct recommendation returned for a 80%-threshold batch
- [ ] Run `pytest` from `assets/tor-advisory-agent/` — if coverage < 70%, add tests
- [ ] Verify `assets/tor-advisory-agent/app/agent.py` has exactly 9 decorated functions — run `grep -c "^@agent_model\|^@agent_config\|^@prompt_section" assets/tor-advisory-agent/app/agent.py` and confirm it returns 9
- [ ] Run `pytest` again to generate final `test_report.json`
- [ ] Verify `test_report.json` exists in `assets/tor-advisory-agent/`
