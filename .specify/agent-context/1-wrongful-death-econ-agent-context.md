# Agent Context: 1-wrongful-death-econ

**Purpose**: Describe agent responsibilities, input/output contracts, constraints and single-file requirement for developers and AI agent orchestration scripts.

## Agent contract

Each agent MUST be a single Python file named `{agent_name}.py` and implement a `run(input_json: dict) -> dict` function that returns:

- outputs: dict (domain-specific computed values)
- provenance_log: list of {step, description, formula, source_url, source_date, value}

Header requirements (top of file):
- Brief description (1-2 lines)
- Inputs expected (fields and units)
- Outputs produced (fields and units)
- Estimated max lines: integer (target <=300)

## Agents (roles)

- life_expectancy_agent.py
  - Domain: life expectancy tables (SSA/national life tables)
  - Primary outputs: expected_remaining_years_by_age, table_reference
  - Estimated lines: 150

- worklife_expectancy_agent.py
  - Domain: worklife horizon (occupation, retirement age)
  - Primary outputs: worklife_years, retirement_assumptions
  - Estimated lines: 180

- wage_growth_agent.py
  - Domain: wage projection (BLS occupation series or jurisdiction median)
  - Primary outputs: growth_rate_series, assumptions
  - Estimated lines: 200

- discount_rate_agent.py
  - Domain: discount rate suggestion (government yields, legal guidance)
  - Primary outputs: recommended_discount_curve, chosen_rate
  - Estimated lines: 120

- present_value_agent.py
  - Domain: assemble cashflows and compute present values
  - Primary outputs: yearly_cashflows, pv_table
  - Estimated lines: 220

- aggregator.py
  - Domain: collect agent outputs into FinalWorkbook data structure
  - Primary outputs: FinalWorkbook JSON for XLSX generator
  - Estimated lines: 140

- xlsx_generator.py
  - Domain: produce XLSX (openpyxl) from FinalWorkbook structure
  - Primary outputs: generated XLSX path and a validation result
  - Estimated lines: 260

## Constraints & Notes

- Each agent MUST embed small examples of provenance entries in comments.
- No agent will access the filesystem beyond reading small cached reference tables; all agent outputs are returned to the orchestrator.
- Agents must avoid long blocking network calls; use timeouts and retries.


*End of agent context*