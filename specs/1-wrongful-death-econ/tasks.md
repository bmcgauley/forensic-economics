# Tasks: Wrongful Death Economic Loss Calculator

**Input**: Design documents from `specs/1-wrongful-death-econ/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup (Project initialization)

- [ ] T001 Create project structure per implementation plan: create `src/`, `src/agents/`, `src/models/`, `src/api/`, `src/jobs/`, `src/utils/`, `src/xlsx/`, `static/`, `tests/`, `licenses/`, `docs/` (path: repository root)
- [ ] T002 Initialize Python virtual environment and `requirements.txt` (path: repository root) — include `flask`, `openpyxl`, `requests`, `pytest`
- [ ] T003 Add `.gitignore` and `README.md` with project overview (paths: `.gitignore`, `README.md`)
- [ ] T004 Create minimal Flask app scaffold `src/api/app.py` implementing app factory and basic routing
- [ ] T005 Add single-page dashboard scaffold `static/index.html`, `static/css/styles.css`, `static/js/app.js`

## Phase 2: Foundational (Blocking prerequisites)

- [ ] T006 Create agent stubs directory and placeholder files: `src/agents/__init__.py`, `src/agents/life_expectancy_agent.py`, `src/agents/worklife_expectancy_agent.py`, `src/agents/wage_growth_agent.py`, `src/agents/discount_rate_agent.py`, `src/agents/present_value_agent.py` (each must implement `run(input_json: dict) -> dict` contract)
- [ ] T007 Implement aggregator stub `src/aggregator.py` that accepts AgentResult objects and produces `FinalWorkbook` JSON
- [ ] T008 Implement XLSX generator stub `src/xlsx/xlsx_generator.py` that consumes `FinalWorkbook` and writes an XLSX to a temp path using `openpyxl`
- [ ] T009 Add temporary storage utility `src/utils/temp_storage.py` for job temp directories and cleanup policy
- [ ] T010 Implement HTTP API wrappers `src/utils/external_apis.py` with timeouts and retries for BLS/SSA/Fed calls
- [ ] T011 Implement provenance helper `src/utils/provenance.py` to normalize provenance_log entries and serialize to JSON
- [ ] T012 Add `licenses/` folder and include license text files for `openpyxl` and `requests` (paths: `licenses/openpyxl_LICENSE.txt`, `licenses/requests_LICENSE.txt`)
- [ ] T013 Configure testing harness: `pytest.ini`, `tests/__init__.py`, and CI-friendly test layout

## Phase 3: User Story 1 - Quick Intake & Export (Priority: P1) 🎯 MVP

**Goal**: Allow an analyst to submit an intake and receive a verified XLSX workbook including summary and year-by-year calculations.

**Independent Test**: Submit `specs/1-wrongful-death-econ/samples/sample_intake.json` to `POST /api/generate` and assert a downloadable XLSX with Summary, Detailed Years, Data Sources, and Methodology sheets exists.

### Implementation Tasks (US1)

- [ ] T014 [US1] Create Intake model `src/models/intake.py` with validation rules per `data-model.md`
- [ ] T015 [US1] Implement POST endpoint `src/api/generate.py` that accepts Intake JSON and returns `{ job_id, status_url }`
- [ ] T016 [US1] Implement in-memory job manager `src/jobs/manager.py` to queue jobs, track status, and manage temp job folders
- [ ] T017 [P] [US1] Implement `src/agents/life_expectancy_agent.py` (single-file, <=300 lines) — produce `expected_remaining_years_by_age` and provenance_log
- [ ] T018 [P] [US1] Implement `src/agents/worklife_expectancy_agent.py` (single-file, <=300 lines) — produce `worklife_years` and provenance_log
- [ ] T019 [P] [US1] Implement `src/agents/wage_growth_agent.py` (single-file, <=300 lines) — produce `growth_rate_series` and provenance_log
- [ ] T020 [P] [US1] Implement `src/agents/discount_rate_agent.py` (single-file, <=300 lines) — produce `recommended_discount_curve` and provenance_log
- [ ] T021 [P] [US1] Implement `src/agents/present_value_agent.py` (single-file, <=300 lines) — compute `yearly_cashflows` and `pv_table` and provide provenance_log
- [ ] T022 [US1] Implement `src/aggregator.py` to assemble AgentResults into `FinalWorkbook` JSON (path: `src/aggregator.py`)
- [ ] T023 [US1] Implement `src/xlsx/xlsx_generator.py` to generate the XLSX workbook and include validation against the canonical template (path: `src/xlsx/xlsx_generator.py`)
- [ ] T024 [US1] Add integration test `tests/integration/test_generate_xlsx.py` that runs through `POST /api/generate` → status → download and validates workbook sheets and key labels
- [ ] T025 [US1] Add sample input file `specs/1-wrongful-death-econ/samples/sample_intake.json` for integration tests

## Phase 4: User Story 2 - Source-verified Calculations (Priority: P2)

**Goal**: Provide reviewers with a provenance sheet and data sources that map inputs and formulas to outputs for legal verification.

**Independent Test**: Open generated workbook and ensure `Data Sources` and `Provenance` worksheets contain URL/version/license entries mapping to values in Summary.

- [ ] T026 [US2] Implement standardized `provenance_log` capture across agents in `src/utils/provenance.py` and refactor agents to use it
- [ ] T027 [US2] Populate `Data Sources` worksheet from `FinalWorkbook.data_sources` inside `src/xlsx/xlsx_generator.py`
- [ ] T028 [US2] Create reviewer checklist and sample verified workbook `docs/examples/verified_sample_workbook.xlsx` and `docs/reviewer_checklist.md`
- [ ] T029 [US2] Add integration test `tests/integration/test_provenance_sheet.py` verifying provenance entries map to final totals

## Phase 5: User Story 3 - Parameter Overrides & Re-run (Priority: P3)

**Goal**: Allow users to override parameters (e.g., discount rate) and re-run calculations to produce versioned workbooks for sensitivity analysis.

**Independent Test**: Change discount rate via API or UI, re-run job, and assert new workbook is produced with updated `version_metadata` and provenance containing prior version reference.

- [ ] T030 [US3] Implement parameter override endpoint `src/api/override.py` or extend `POST /api/generate` to accept overrides and reference previous jobs
- [ ] T031 [US3] Implement workbook versioning metadata in `src/jobs/manager.py` and in `FinalWorkbook.version_metadata`
- [ ] T032 [US3] Add frontend override UI `static/js/overrides.js` and UI controls in `static/index.html`
- [ ] T033 [US3] Add integration test `tests/integration/test_override_scenario.py` that runs an initial job, then an override job, and validates versioning and provenance

## Phase N: Polish & Cross-Cutting Concerns

- [ ] T034 Configure formatting and linting: add `pyproject.toml` or `setup.cfg` with Black and Flake8 settings (path: repository root)
- [ ] T035 Add dependency license & security review task: include `licenses/` entries and `docs/dependency_justification.md`
- [ ] T036 Add CI workflow `/.github/workflows/ci.yml` to run tests and style checks
- [ ] T037 Write developer docs `docs/developer.md` and update `specs/1-wrongful-death-econ/quickstart.md` with any changes
- [ ] T038 Run constitution compliance audit: verify each agent file is single-file and <=300 lines and that provenance is produced (task owner: reviewer) — report path: `specs/1-wrongful-death-econ/constituion-audit.md`

## Dependencies & Execution Order

- Foundational Phase (T006..T013) MUST complete before User Story implementation (T014..T025)
- User Story 1 (US1) tasks are core MVP; US2 and US3 depend on US1 but can be developed in parallel after foundational tasks

## Parallel Opportunities

- Agent implementation tasks T017..T021 are parallelizable (different files, no internal dependencies) — mark as [P].
- License and docs tasks (T012, T035, T037) are parallelizable.

## Summary

- Total task count: 38
- Task count per user story:
  - US1: 12 tasks (T014..T025)
  - US2: 4 tasks (T026..T029)
  - US3: 4 tasks (T030..T033)
  - Setup/Foundational/Polish: 18 tasks (T001..T013, T034..T038)
- Parallel opportunities: Agent implementations (T017..T021) and several infra/docs tasks
- Suggested MVP scope: User Story 1 only (T014..T025) after Foundational tasks T006..T013

## Files created by this task generator
- `specs/1-wrongful-death-econ/tasks.md` (this file)


*All tasks follow the required checklist format and include explicit file paths where appropriate.*
