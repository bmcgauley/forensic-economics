# Implementation Plan: Wrongful Death Economic Loss Calculator

**Branch**: `1-wrongful-death-econ` | **Date**: 2025-10-29 | **Spec**: specs/1-wrongful-death-econ/spec.md

## Summary

Deliver a minimal, auditable wrongful-death economic-loss calculator with a single-page web dashboard that captures intake data, triggers a set of independent Python agents (single-file, <=300 lines each) that research and compute domain-specific components, aggregates results, and produces a legally-compatible Excel workbook (XLSX) containing summary, year-by-year calculations, data sources, and methodology notes.

## Technical Context

**Language/Version**: Python 3.10+ (LTS recommended)
**Backend**: Flask (lightweight web server)
**Agents**: Python classes, each agent implemented in a single file (<=300 lines)
**Primary Dependencies**: openpyxl (XLSX generation), requests (HTTP to external data sources)
**Storage**: In-memory JSON object per request (stateless server) and temporary file storage for generated workbooks
**Testing**: pytest for unit tests; sample calculation integration tests
**Target Platform**: Linux or Windows server (small scale)
**Performance Goals**: Single intake end-to-end generation within 120 seconds in 90% of trials
**Constraints**:
- Agents must be single-file and include header documentation (purpose, inputs, outputs, sample provenance)
- Minimal external dependencies; each third-party package must be justified with license and maintenance notes
- Excel output must conform to canonical legal workbook template (to be provided)

## Constitution Check

This plan must satisfy the Forensic Economics constitution gates. Evaluation below documents compliance or required justification.

- Agent Modularity: Planned agents and estimated line counts (target <=300 lines each):
  - `life_expectancy_agent.py` — 150 lines (fetch SSA / national life tables, compute expectancy by age/sex)
  - `worklife_expectancy_agent.py` — 180 lines (derive worklife horizon by occupation, retirement norms)
  - `wage_growth_agent.py` — 200 lines (project wage growth using BLS series or occupation-specific growth)
  - `discount_rate_agent.py` — 120 lines (suggest discount rates from Treasury yield curves and legal guidance)
  - `present_value_agent.py` — 220 lines (assemble cashflow, discount and compute PV table)
  - `aggregator.py` — 140 lines (collect AgentResult objects, assemble final data structure)
  - `xlsx_generator.py` — 260 lines (consume final data structure and produce canonical XLSX via openpyxl)

  All agent files will be single-file Python modules; line counts are estimates and will be validated during Phase 1 design.

- Agent Autonomy: Each agent will accept a defined JSON input and return {outputs, provenance_log}. Agents will run in parallel and MUST include research notes and source citations in their provenance output.

- Data Integrity: The plan requires provenance logs for every calculation (inputs, formulas, source URLs, timestamps, data versions). Provenance will be attached to the XLSX as a Data Sources worksheet and a machine-readable JSON provenance file saved alongside the workbook.

- Minimal Dependencies: openpyxl and requests are third-party. Justification:
  - `openpyxl` is the most widely-used, well-maintained library for writing XLSX with formatting and preserved numeric precision. Implementing XLSX directly via stdlib is impractical for legal-grade formatting.
  - `requests` simplifies robust HTTP interactions (timeouts, retries) vs. urllib; it reduces code complexity and subtle bugs.
  Mitigation: Lock dependency versions, include license text in repo, and perform security review before inclusion.

- Excel Compatibility: The `xlsx_generator.py` will accept a canonical template and include a validation routine that compares generated workbook labels, formats, and cell precisions against the template; mismatches will fail a validation step and require manual approval.

- Simple Architecture: The planned flow is: Web dashboard (index.html) → Flask API (/api/generate) → Agent Orchestrator (parallel invocation of single-file agents) → Aggregator → XLSX generator → return workbook.

## Phase 0: Outline & Research

Purpose: Resolve open technical questions and create `research.md` with decisions.

### Open questions (Phase 0 research tasks)

- Q0.1: API endpoints and rate limits for SSA, BLS, Federal Reserve — authentication or API keys required?
- Q0.2: Canonical legal Excel template(s) and jurisdictional differences (we need example templates from legal team)
- Q0.3: Acceptable rounding and numeric precision standards for exhibits
- Q0.4: Hosting considerations for ephemeral workbook storage and download (temp file lifecycle, cleanup)
- Q0.5: License review for `openpyxl` and `requests` (compatibility with legal distribution)

### Phase 0 tasks (research agent-like tasks)

- R001: Research SSA/BLS/Fed API usage, endpoints, authentication, sample payloads
- R002: Collect canonical legal Excel templates and document label/format requirements
- R003: Define numeric precision and rounding rules for legal exhibits
- R004: Document temporary file lifecycle pattern and secure download approach (signed URLs or direct transfer)
- R005: License and security review for openpyxl and requests

Deliverable: `research.md` (see generated file)

## Phase 1: Design & Contracts

Prerequisite: research.md complete

1. Generate `data-model.md` (entities, validation rules). See generated file in this spec directory.
2. Create API contract(s): minimal REST endpoints for intake and status/download:
   - POST /api/generate → accepts Intake JSON; returns {job_id, status_url}
   - GET /api/status/{job_id} → returns status and, when complete, download URL
   - GET /api/download/{job_id} → returns the XLSX file (or redirects to temp storage)
   Contracts will be output to `contracts/openapi.yaml`.
3. Agent context update: create `.specify/agent-context/1-wrongful-death-econ-agent-context.md` describing agent prompts, data schema, and constraints (single-file, <=300 lines).

## Phase 2: Planning (Phase 2 scope)

- Break down implementation tasks into T1..Tx in `tasks.md` (not generated here) for code writing, tests, and validation.
- Include constitution compliance checklist references in tasks (verify single-file limits, provenance outputs, dependency sign-off).

## Artifacts generated by this plan

- specs/1-wrongful-death-econ/plan.md (this file)
- specs/1-wrongful-death-econ/research.md
- specs/1-wrongful-death-econ/data-model.md
- specs/1-wrongful-death-econ/contracts/openapi.yaml
- specs/1-wrongful-death-econ/quickstart.md
- .specify/agent-context/1-wrongful-death-econ-agent-context.md

## Risks & Mitigations

- External API rate limits or downtime: add retries/backoff and cache commonly used reference tables locally with version stamps.
- Dependency license concerns: freeze versions and include license files; if incompatible, swap to alternative libraries or CSV-based exports.
- Excel template mismatches: include validation step; require manual approval for mismatches before delivering final workbook to claim files.

## Next steps

1. Phase 0 research: complete `research.md` tasks (R001-R005).
2. Phase 1 design: produce `data-model.md`, `contracts/openapi.yaml`, and `quickstart.md`.
3. Create agent stubs and unit tests that validate single-file constraint and provenance output.


---

*Plan authored automatically from spec. Ensure the legal team provides canonical Excel templates and jurisdictional rules before Phase 1.*
