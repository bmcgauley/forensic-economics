# Feature Specification: Wrongful Death Economic Loss Calculator

**Feature Branch**: `1-wrongful-death-econ`
**Created**: 2025-10-29
**Status**: Draft
**Input**: User description: "Build a wrongful death economic loss calculator with AI agents:\n\n**Intake Form**: Web dashboard captures victim data (age, occupation, salary, location, education, dependents)\n\n**Agent System**: Separate agents research and calculate:\n- Life expectancy data\n- Worklife expectancy \n- Wage growth projections\n- Discount rates\n- Present value calculations\n\n**Output**: Generate formal Excel workbook with:\n- Summary worksheet\n- Detailed calculations by year\n- Supporting data sources\n- Methodology notes\n\n**Flow**: User submits form → agents execute parallel research → compile results → generate downloadable Excel file"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quick Intake & Export (Priority: P1)
A claims analyst uses the web dashboard to enter victim data and requests an expert-calculated economic-loss workbook.

**Why this priority**: Core value — produces the legally usable output (Excel) required by downstream stakeholders.

**Independent Test**: Submit a sample intake; system returns a downloadable XLSX with a summary and detailed yearly calculations and provenance sheet.

**Acceptance Scenarios**:
1. **Given** an intake form with valid fields, **When** the analyst submits, **Then** the system queues/starts agents and returns a ready-to-download Excel file within acceptable time (see Success Criteria).
2. **Given** missing non-critical fields (e.g., education), **When** submitted, **Then** the system uses documented assumptions and includes them in methodology notes.

---

### User Story 2 - Source-verified Calculations (Priority: P2)
A domain expert reviews the generated workbook to verify data sources and calculation provenance.

**Why this priority**: Legal admissibility depends on traceable sourcing and reproducible calculations.

**Independent Test**: Reviewer opens workbook; verifies a provenance worksheet listing inputs, data source versions/URLs, formulas, and per-year intermediate values.

**Acceptance Scenarios**:
1. **Given** a generated workbook, **When** a reviewer inspects the provenance sheet, **Then** all input data sources and formulas are present and map to final totals.

---

### User Story 3 - Parameter Overrides & Re-run (Priority: P3)
A user adjusts a key assumption (e.g., discount rate) and re-runs calculations to produce a variant report.

**Why this priority**: Allows sensitivity analysis and supports settlement negotiation scenarios.

**Independent Test**: User modifies the discount rate via UI or config, re-runs, and receives an updated workbook where the only changes are the recalculated values and an updated provenance entry.

**Acceptance Scenarios**:
1. **Given** an existing intake, **When** the discount rate is changed and re-run, **Then** the output workbook includes prior-version metadata and updated per-year calculations.

---

### Edge Cases

- Missing or partial wage history: system uses jurisdictional median wages with provenance note.
- Very young or very old ages outside common tables: system uses extrapolation rules and documents assumptions.
- Jurisdiction-specific legal caps or multipliers: system flags jurisdiction and requires manual confirmation if detected.
- Extremely large/deep dependence chains: system caps projection horizon (documented) and notes approximation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The web dashboard MUST capture victim data fields: age, occupation, salary (current/median), location (jurisdiction), education, number of dependents, and optional employer benefits.
- **FR-002**: The system MUST invoke independent agents to research and produce: life expectancy, worklife expectancy, wage growth projections, discount rate recommendations, and present-value tables.
- **FR-003**: The system MUST produce a downloadable Excel workbook (XLSX) with: a Summary worksheet, a Detailed Year-by-Year worksheet, a Data Sources worksheet, and a Methodology & Assumptions worksheet.
- **FR-004**: Every calculation MUST include provenance metadata that maps inputs to outputs, including source URLs, version/date, formula descriptions, units, and timestamps.
- **FR-005**: The workbook MUST preserve numeric precision and include explicit rounding rules; any rounding or unit conversions MUST be logged in the provenance.
- **FR-006**: The system MUST support a parameter override flow (e.g., discount rate, wage growth scenarios) and produce versioned workbooks.
- **FR-007**: All third-party data or algorithms used MUST be recorded with an explicit license and citation entry in the Data Sources worksheet.

### Non-Functional Requirements

- **NFR-001**: The initial end-to-end generation for a single intake MUST complete within 120 seconds for typical data and normal network access to sources.
- **NFR-002**: All agent modules MUST be single-file implementations not exceeding 300 lines, and must include header documentation (purpose, inputs, outputs).
- **NFR-003**: The system MUST minimize third-party dependencies; any added dependency requires justification and license check.
- **NFR-004**: The Excel output format MUST be validated against a canonical legal template; mismatches MUST be flagged.

## Key Entities *(include if feature involves data)*

- **Intake**: {victim_age, occupation, salary, location, education, dependents, benefits}
- **AgentResult**: {agent_name, inputs_used, outputs, provenance_log}
- **Workbook**: {summary_sheet, detailed_years, data_sources, methodology_notes, version_metadata}

## Success Criteria *(mandatory)*

- **SC-001**: Analysts can produce a complete, verified XLSX workbook from a single intake in under 120 seconds in 90% of trials (measured on test infra).
- **SC-002**: 100% of generated workbooks include a provenance worksheet mapping every final numeric total to one or more documented sources.
- **SC-003**: Reviewers can validate the workbook against the canonical legal template with zero critical mismatches (format, labels, precision).
- **SC-004**: Parameter override flows produce versioned workbooks where differences are confined to recalculated numbers and updated provenance entries.

## Assumptions

- Jurisdiction-specific legal rules (e.g., caps, multipliers) will be provided or flagged for manual review; default behavior is to use national-standard inputs and flag jurisdictional overrides.
- Discount rates will be suggested by an agent that references public finance sources (e.g., government yield curves) and legal-admissibility guidance; final selection is user-overridable.
- Wage growth projection agent will prefer government/industry wage series when available; if unavailable, it will use conservative default growth assumptions documented in the methodology.

## Data & Sources

- Agents MUST record exact data source identifiers (URL or file hash) and the date/version used.
- Canonical sources expected: life tables (national actuarial tables), labor statistics (median wages by occupation), CPI/Inflation, official government yield curves.

## Implementation Notes (for planning only)

- The canonical flow is: Web dashboard receives intake → triggers agent orchestration (agents run in parallel) → aggregator collects AgentResult objects → generator composes XLSX workbook with provenanced worksheets.
- Agents must expose simple JSON contracts: {inputs} → {outputs, provenance_log}.

## Open Questions (if any)

- None marked; reasonable defaults used for jurisdiction/data source selection and discount rate sourcing. If you want stricter jurisdictional rules, specify the jurisdictions and legal templates to enforce.

## Success: Spec ready for planning

This spec is ready to be used by `/speckit.plan` for implementation planning and task breakdown.
