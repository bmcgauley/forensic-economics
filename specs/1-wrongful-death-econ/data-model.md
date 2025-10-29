# Data Model: Wrongful Death Economic Loss Calculator

**Feature**: specs/1-wrongful-death-econ/spec.md
**Date**: 2025-10-29

## Entities

### Intake
Represents the user-supplied victim data collected from the web dashboard.

- id: string (UUID)
- victim_age: integer
- victim_sex: string (M/F/Other)
- occupation: string (SOC code or textual)
- salary: number (annual, in local currency)
- salary_type: enum (current, median_jurisdiction)
- location: string (jurisdiction code)
- education: string (highest level)
- dependents: integer
- benefits: object (employer benefits, retirement contributions)
- metadata: object (submission timestamp, user id, UI notes)

### AgentResult
Output from each agent; used by aggregator.

- agent_name: string
- inputs_used: object (snapshotted inputs and any config)
- outputs: object (domain-specific outputs, numbers, tables)
- provenance_log: array of {step, description, formula, source_url, source_date, value}

### FinalWorkbook
Structure used by XLSX generator.

- summary: object (top-level totals, present values)
- yearly: array of {year, pre-tax-amount, post-tax-amount (if applicable), notes}
- data_sources: array of {name, url, version, license}
- methodology_notes: string
- version_metadata: {created_at, generator_version, spec_ref, input_id}

## Validation Rules

- Intake.victim_age MUST be 0 <= age <= 120
- salary MUST be >= 0
- dependents MUST be >=0
- occupation SHOULD map to standardized codes (SOC/NOC) when available (fallback: free text)

## State Transitions

- intake -> job queued -> agents run in parallel -> aggregator collects AgentResults -> workbook_generated -> transient storage -> download -> cleanup


*End of data-model.md*