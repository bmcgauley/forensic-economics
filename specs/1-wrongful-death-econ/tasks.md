# Tasks: Wrongful Death Economic Loss Calculator

**Input**: Design documents from `specs/1-wrongful-death-econ/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

---

# 📊 PROJECT STATUS

## Current State: MVP Complete, Assignment Compliance In Progress

| Metric | Status |
|--------|--------|
| **Total Tasks** | 107 |
| **Completed** | ✅ 35 tasks (32.7%) |
| **Remaining** | ⏳ 72 tasks (67.3%) |
| **Critical Path** | ⚠️ 21 tasks (P0 + P1) |
| **MVP Status** | ✅ **WORKING** (Phases 1-4 complete) |
| **Assignment Compliance** | ⚠️ **IN PROGRESS** (Phase 5 complete, 72 tasks remain) |

## What's Working (MVP - Phases 1-4) ✅

- ✅ Dashboard form with assignment-compliant fields (Phase 4 complete)
- ✅ Date pickers, JSON upload, California counties, SOC codes
- ✅ REST API (generate, status, download endpoints)
- ✅ 5 core agents (life, worklife, wage, discount, present value)
- ✅ Excel generation (4 worksheets)
- ✅ Job management with async processing
- ✅ Basic provenance tracking
- ✅ 13 passing tests

## What's Missing (Assignment Compliance) ❌

### P0 BLOCKING (8 tasks - MUST DO)
- ✅ Dashboard fields don't match assignment (Phase 4 - COMPLETE)
- ✅ Skoog Tables not included (Phase 5 - COMPLETE)
- ✅ CDC Life Tables not included (Phase 5 - COMPLETE)
- ❌ Federal Reserve H.15 live API (Phase 6)
- ❌ CA Labor Market Info live API (Phase 6)
- ❌ Federal Reserve Rate Agent (Phase 7)
- ❌ Skoog Table Agent (Phase 7)

### P1 HIGH (13 tasks - STRONGLY RECOMMENDED)
- ❌ Supervisor Agent orchestration (Phase 8)
- ❌ Real-time progress dashboard (Phase 9)
- ❌ Excel output format verification (Phase 10)

## 🚀 Next Steps

**START HERE:** Phase 6 - Live API Integrations (T049..T052)

1. ✅ Update form fields to match assignment exactly (Phase 4 complete)
2. ✅ Add Skoog Tables and CDC Life Tables data (Phase 5 complete)
3. Implement live API clients (Federal Reserve H.15, CA Labor Market)
4. Create supporting agents
5. Build supervisor agent
6. Add real-time progress UI
7. Verify Excel output format

---

# ⚠️ ASSIGNMENT COMPLIANCE GAP ANALYSIS

## Critical Gaps Identified (Must Fix Before Submission)

### 1. Dashboard Fields Do NOT Match Assignment Requirements

**Current Dashboard Issues:**
- ❌ Missing: Full Name * (required field)
- ❌ Missing: Date of Birth * (only has "Age")
- ❌ Missing: Date of Death (required field)
- ❌ Missing: Present Date * (required field)
- ❌ Missing: California County * (has generic "Jurisdiction" instead)
- ❌ Missing: Employment Status * (required dropdown)
- ❌ Missing: JSON file upload option ("Or Load Existing Data")
- ❌ Extra fields not in assignment: Salary Type, Dependents, Retirement/Health Benefits

**Required Fields Per Assignment:**
1. Full Name * (text input)
2. Date of Birth * (date picker - mm/dd/yyyy)
3. Date of Death (date picker - mm/dd/yyyy)
4. Present Date * (date picker - default: 10/20/2025)
5. Annual Salary * (number, no $ sign or comma)
6. Occupation * (dropdown - "Select occupation from SOC")
7. Gender * (dropdown - "Select gender")
8. California County * (dropdown - "Select CA county")
9. Employment Status * (dropdown - "Select employment status")
10. Level of Schooling * (dropdown - "Select level of schooling")
11. JSON Upload Zone (drag & drop or click to browse)

### 2. Data Sources NOT Implemented Per Assignment

**LEFT SIDE - Static Data Files (MUST be included in project):**
- ✅ **Skoog Tables** - "Markov Model of Labor Force Activity 2012-17" by Skoog, Ciecka, and Krueger, Journal of Forensic Economics 28(1-2), 2019, pp. 15-108
  - Status: ✅ **COMPLETE** - Added to project
  - Location: `data/skoog_tables/skoog_2019_markov_model.json`
  - Used by: WorklifeExpectancyAgent
  - Includes: Worklife expectancy by age, gender, and education level

- ✅ **CDC Life Tables** - National Vital Statistics Reports, U.S. Life Tables, https://www.cdc.gov
  - Status: ✅ **COMPLETE** - Added to project
  - Location: `data/life_tables/cdc_us_life_tables_2023.json`
  - Used by: LifeExpectancyAgent
  - Includes: Life expectancy by age and gender

**RIGHT SIDE - Live API Fetches (MUST fetch in real-time):**
- ❌ **Federal Reserve H.15 Selected Interest Rates** - 1-Year Treasury Constant Maturity Rate
  - URL: https://www.federalreserve.gov/releases/h15/current/
  - Status: Returns hardcoded 3.5%
  - Code location: `src/utils/external_apis.py` FedClient.get_treasury_rates()
  - Used by: DiscountRateAgent

- ❌ **California Labor Market Info** - Salary change per occupation in CA
  - URL: https://labormarketinfo.edd.ca.gov/
  - Status: NOT IMPLEMENTED AT ALL
  - Code location: Need to add CALaborMarketClient to `src/utils/external_apis.py`
  - Used by: WageGrowthAgent

### 3. Real-Time Progress Dashboard NOT Implemented

**Assignment requires live dashboard showing:**
- Session ID
- Person name (e.g., "Robert Johnson")
- Status progress (e.g., "8/8 agents")
- Current step (e.g., "Analysis completed successfully")
- Agent Flow table with columns:
  - Agent name
  - Status (COMPLETED/IN_PROGRESS/PENDING)
  - Message (what agent is doing)
  - Output (detailed result)
- Real-time updates every 3 seconds
- Generated Files section
- Errors & Issues section

**Current Status Panel:**
- ✓ Has basic status polling
- ❌ Does NOT show individual agent progress
- ❌ Does NOT show real-time agent messages/outputs
- ❌ Does NOT update every 3 seconds with detailed info

### 4. Supporting Agents Missing

**Per assignment requirements, need these additional agents:**

- ❌ **Federal Reserve Rate Agent** (Supporting Function)
  - Role: Provides current treasury/discount rates to DiscountFactorAgent
  - Function: Fetches real-time federal interest rates for time value calculations
  - Impact: Ensures discount factors reflect current economic conditions
  - File: `src/agents/fed_rate_agent.py`

- ❌ **Skoog Table Agent** (Supporting Function)
  - Role: Provides actuarial worklife data to WorklifeRemainingYearsAgent
  - Function: Supplies statistical worklife expectancy tables by age/gender
  - Impact: Enables accurate remaining work years calculations
  - File: `src/agents/skoog_table_agent.py`

- ❌ **Supervisor Agent** (Coordination & Integration)
  - Role: Orchestrates all 9 agents and generates final Excel/Word reports
  - Function: Coordinates agent execution, extracts results, integrates data
  - Impact: Ensures proper data flow between agents and creates final deliverables
  - File: `src/agents/supervisor_agent.py`

- ❌ **Comprehensive Excel Generator** (Coordination & Integration)
  - Role: Takes agent results and populates Excel worksheets
  - Function: Formats data, creates worksheets, applies styling, generates final Excel file
  - Impact: Transforms agent calculations into professional presentation format
  - File: `src/xlsx/comprehensive_generator.py`

### 5. Excel Output Format May Not Match Template

**Required Excel Structure (per assignment slide):**
- Top section with:
  - Base Value: $86,894.89
  - Discount rate: 4.25%
  - Annual growth rate: 2.34%
- Item label: "Earnings Loss (More Conservative)"
- Cumulative Present Value: $1,700,727
- Present Value Date breakdown:
  - Month → Jan
  - Day → 10
  - Year → 2025
- Table with columns:
  - Age | Start Date | Year Number | Portion of Year | Full Year Value | Actual Value | Cumulative Value | Discount Factor | Present Value | Cumulative Present Value
- Rows from age 40.0 to 63.5 with highlighted starting age

## Quick Start Guide for Assignment Compliance

**Status**:
- ✅ **MVP + DASHBOARD + STATIC DATA COMPLETE** (35/107 tasks done - Phases 1-5)
- ⏳ **72 tasks remaining** for assignment compliance
- ⚠️ **21 critical tasks** (P0 + P1) must be done before submission

**To start working on assignment compliance:**

1. Read the gap analysis above carefully
2. **BEGIN HERE** → Phase 6 (Live API Integrations) - Tasks T049..T052
3. Follow the recommended execution order in the Summary section
4. All P0 (BLOCKING) tasks MUST be completed before submission - 8 tasks
5. P1 (HIGH) tasks are strongly recommended for full compliance - 13 tasks

**Key Files to Update:**
- ✅ `static/index.html` - Dashboard form fields (Phase 4 complete)
- ✅ `src/models/intake.py` - Input validation (Phase 4 complete)
- ✅ `data/skoog_tables/` - Skoog worklife tables (Phase 5 complete)
- ✅ `data/life_tables/` - CDC life expectancy tables (Phase 5 complete)
- ✅ `src/utils/data_loader.py` - Data loading utility (Phase 5 complete)
- ❌ `src/utils/external_apis.py` - Live API clients
- ❌ `src/agents/fed_rate_agent.py` - NEW supporting agent
- ❌ `src/agents/skoog_table_agent.py` - NEW supporting agent
- ❌ `src/agents/supervisor_agent.py` - NEW coordination agent

**What Works Now:**
- ✓ Assignment-compliant dashboard form with all required fields
- ✓ Date pickers, JSON upload, California counties, SOC occupation codes
- ✓ 5 core agents (life expectancy, worklife, wage, discount, present value)
- ✓ Excel generation (4 sheets)
- ✓ Job management and status polling
- ✓ Basic provenance tracking
- ✓ Skoog Tables data (worklife expectancy by age, gender, education)
- ✓ CDC Life Tables data (life expectancy by age and gender)
- ✓ Data loading utility with caching and validation

**What's Missing (Per Assignment):**
- ✅ Dashboard fields don't match (Phase 4 complete)
- ✅ Static data files (Skoog, CDC) not included (Phase 5 complete)
- ❌ Live APIs (Fed H.15, CA Labor Market) not implemented
- ❌ Supporting agents (Fed Rate, Skoog Table) don't exist
- ❌ Supervisor agent doesn't exist
- ❌ Real-time progress dashboard not implemented
- ❌ Excel format may not match template exactly

---

## Phase 1: Setup (Project initialization) ✅ COMPLETE

- [x] T001 Create project structure per implementation plan: create `src/`, `src/agents/`, `src/models/`, `src/api/`, `src/jobs/`, `src/utils/`, `src/xlsx/`, `static/`, `tests/`, `licenses/`, `docs/` (path: repository root) ✅
- [x] T002 Initialize Python virtual environment and `requirements.txt` (path: repository root) — include `flask`, `openpyxl`, `requests`, `pytest` ✅
- [x] T003 Add `.gitignore` and `README.md` with project overview (paths: `.gitignore`, `README.md`) ✅
- [x] T004 Create minimal Flask app scaffold `src/api/app.py` implementing app factory and basic routing ✅
- [x] T005 Add single-page dashboard scaffold `static/index.html`, `static/css/styles.css`, `static/js/app.js` ✅

## Phase 2: Foundational (Blocking prerequisites) ✅ COMPLETE

- [x] T006 Create agent stubs directory and placeholder files: `src/agents/__init__.py`, `src/agents/life_expectancy_agent.py`, `src/agents/worklife_expectancy_agent.py`, `src/agents/wage_growth_agent.py`, `src/agents/discount_rate_agent.py`, `src/agents/present_value_agent.py` (each must implement `run(input_json: dict) -> dict` contract) ✅
- [x] T007 Implement aggregator stub `src/aggregator.py` that accepts AgentResult objects and produces `FinalWorkbook` JSON ✅
- [x] T008 Implement XLSX generator stub `src/xlsx/xlsx_generator.py` that consumes `FinalWorkbook` and writes an XLSX to a temp path using `openpyxl` ✅
- [x] T009 Add temporary storage utility `src/utils/temp_storage.py` for job temp directories and cleanup policy ✅
- [x] T010 Implement HTTP API wrappers `src/utils/external_apis.py` with timeouts and retries for BLS/SSA/Fed calls ✅
- [x] T011 Implement provenance helper `src/utils/provenance.py` to normalize provenance_log entries and serialize to JSON ✅
- [x] T012 Add `licenses/` folder and include license text files for `openpyxl` and `requests` (paths: `licenses/openpyxl_LICENSE.txt`, `licenses/requests_LICENSE.txt`) ✅ (also includes flask_LICENSE.txt)
- [x] T013 Configure testing harness: `pytest.ini`, `tests/__init__.py`, and CI-friendly test layout ✅

## Phase 3: User Story 1 - Quick Intake & Export (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Allow an analyst to submit an intake and receive a verified XLSX workbook including summary and year-by-year calculations.

**Independent Test**: Submit `specs/1-wrongful-death-econ/samples/sample_intake.json` to `POST /api/generate` and assert a downloadable XLSX with Summary, Detailed Years, Data Sources, and Methodology sheets exists.

### Implementation Tasks (US1) ✅ ALL COMPLETE

- [x] T014 [US1] Create Intake model `src/models/intake.py` with validation rules per `data-model.md` ✅
- [x] T015 [US1] Implement POST endpoint `src/api/generate.py` that accepts Intake JSON and returns `{ job_id, status_url }` ✅
- [x] T016 [US1] Implement in-memory job manager `src/jobs/manager.py` to queue jobs, track status, and manage temp job folders ✅
- [x] T017 [P] [US1] Implement `src/agents/life_expectancy_agent.py` (single-file, <=300 lines) — produce `expected_remaining_years_by_age` and provenance_log ✅ (106 lines)
- [x] T018 [P] [US1] Implement `src/agents/worklife_expectancy_agent.py` (single-file, <=300 lines) — produce `worklife_years` and provenance_log ✅ (117 lines)
- [x] T019 [P] [US1] Implement `src/agents/wage_growth_agent.py` (single-file, <=300 lines) — produce `growth_rate_series` and provenance_log ✅ (121 lines)
- [x] T020 [P] [US1] Implement `src/agents/discount_rate_agent.py` (single-file, <=300 lines) — produce `recommended_discount_curve` and provenance_log ✅ (98 lines)
- [x] T021 [P] [US1] Implement `src/agents/present_value_agent.py` (single-file, <=300 lines) — compute `yearly_cashflows` and `pv_table` and provide provenance_log ✅ (144 lines)
- [x] T022 [US1] Implement `src/aggregator.py` to assemble AgentResults into `FinalWorkbook` JSON (path: `src/aggregator.py`) ✅
- [x] T023 [US1] Implement `src/xlsx/xlsx_generator.py` to generate the XLSX workbook and include validation against the canonical template (path: `src/xlsx/xlsx_generator.py`) ✅
- [x] T024 [US1] Add integration test `tests/integration/test_generate_xlsx.py` that runs through `POST /api/generate` → status → download and validates workbook sheets and key labels ✅
- [x] T025 [US1] Add sample input file `specs/1-wrongful-death-econ/samples/sample_intake.json` for integration tests ✅

## Phase 4: Assignment Compliance - Dashboard Fixes (Priority: P0 - BLOCKING)

**Goal**: Update dashboard and intake model to match exact assignment requirements.

**Critical**: This phase MUST be completed before submission. Dashboard fields do not match assignment.

### Dashboard Field Updates (T039-T044)

- [x] T039 [P0] Update `static/index.html` dashboard form to match assignment requirements:
  - Remove: victim_age (replace with date_of_birth)
  - Remove: salary_type, dependents, retirement_contribution, health_benefits
  - Add: full_name (text input, required)
  - Add: date_of_birth (date picker, mm/dd/yyyy, required)
  - Add: date_of_death (date picker, mm/dd/yyyy)
  - Add: present_date (date picker, default: 10/20/2025, required)
  - Update: victim_sex → gender (dropdown: Male/Female/Other)
  - Update: location → california_county (dropdown with all 58 CA counties)
  - Add: employment_status (dropdown: Employed Full-Time/Part-Time/Self-Employed/Unemployed/Retired)
  - Update: occupation (dropdown with SOC codes)
  - Keep: salary, education (as level_of_schooling)
  - Add: JSON file upload zone with drag-and-drop

- [x] T040 [P0] Update `src/models/intake.py` validation to match new field requirements:
  - Add full_name validation (non-empty string)
  - Add date_of_birth validation (valid date, must be in past)
  - Add date_of_death validation (optional, if present must be after DOB)
  - Add present_date validation (defaults to today)
  - Add california_county validation (must be one of 58 CA counties)
  - Add employment_status validation
  - Remove: salary_type, dependents, benefits fields
  - Update: Calculate age from date_of_birth and present_date

- [x] T041 [P0] Add California counties data file `data/california_counties.json` with all 58 county names

- [x] T042 [P0] Add SOC occupation codes data file `data/soc_occupations.json` with standard occupation codes and titles

- [x] T043 [P0] Update `static/js/app.js` to handle:
  - Date picker interactions for DOB, DOD, Present Date
  - JSON file upload (drag-and-drop and file browse)
  - Pre-populate form from uploaded JSON
  - Calculate age from dates automatically

- [x] T044 [P0] Update `static/css/styles.css` to match assignment UI styling (green header, clean form layout)

## Phase 5: Assignment Compliance - Static Data Sources (Priority: P0 - BLOCKING) ✅ COMPLETE

**Goal**: Add required static data files (Skoog Tables, CDC Life Tables) to project.

**Critical**: These data sources MUST be included per assignment
requirements (left side of sources slide).
Reference:
==================================================================
(for life expectancy) National Vital Statistics Reports, U.S. Life Tables, U.S. Dept of Health and Human Services, https://www.cdc.gov

(for work-life expectancy) the Markov Model of Labor Force Activity 2012-17: Extended, tables of Central Tendency, Shape, Percentile Points, and Bootstrap Standard Errors by Gary R. Skoog, James E. Ciecka, and Kurt V. Krueger, Journal of Forensic Economics 28(1-2), 2019, pp. 15-108
==================================================================

### Static Data Files (T045-T048) ✅ ALL COMPLETE

- [x] T045 [P0] Download/obtain Skoog Tables data from "Markov Model of Labor Force Activity 2012-17" (Journal of Forensic Economics 28(1-2), 2019):
  - Create `data/skoog_tables/` directory ✅
  - Add worklife expectancy tables by age, gender, education ✅
  - Format as JSON or CSV for easy parsing ✅
  - Include metadata: source citation, publication year, table version ✅
  - Path: `data/skoog_tables/skoog_2019_markov_model.json` ✅

- [x] T046 [P0] Download/obtain CDC Life Tables from National Vital Statistics Reports:
  - Create `data/life_tables/` directory ✅
  - Add U.S. Life Tables (latest available, recommend 2021-2023) ✅
  - Include tables by age and gender ✅
  - Format as JSON or CSV ✅
  - Include metadata: source URL, table year, publication date ✅
  - Path: `data/life_tables/cdc_us_life_tables_2023.json` ✅

- [x] T047 [P0] Create data loading utility `src/utils/data_loader.py`:
  - Function: load_skoog_tables() → returns parsed Skoog data ✅
  - Function: load_life_tables() → returns parsed CDC life table data ✅
  - Include caching to avoid repeated file I/O ✅
  - Add validation to ensure data files exist and are valid ✅

- [x] T048 [P0] Add data source documentation `data/README.md`:
  - Document each data file with full citation ✅
  - Include download URLs and retrieval dates ✅
  - Note any preprocessing or formatting applied ✅
  - Include license information for each source ✅

## Phase 6: Assignment Compliance - Live API Integrations (Priority: P0 - BLOCKING)

**Goal**: Implement real-time data fetching from Federal Reserve H.15 and California Labor Market Info.

**Critical**: Assignment explicitly requires LIVE fetching of these sources (right side of sources slide).

### Live API Clients (T049-T052)

- [ ] T049 [P0] Implement Federal Reserve H.15 live data fetching in `src/utils/external_apis.py`:
  - Update FedClient.get_treasury_rates() to fetch real data
  - Source: https://www.federalreserve.gov/releases/h15/current/
  - Target: 1-Year Treasury Constant Maturity Rate (daily updates)
  - Parse H.15 data release page or use Fed FRED API
  - Return: current 1-year Treasury rate as decimal (e.g., 0.0425 for 4.25%)
  - Include error handling with fallback to recent cached rate
  - Add provenance: retrieval timestamp, source URL, data vintage

- [ ] T050 [P0] Add California Labor Market Info client to `src/utils/external_apis.py`:
  - Create CALaborMarketClient class extending ExternalAPIClient
  - Source: https://labormarketinfo.edd.ca.gov/
  - Function: get_wage_growth_by_occupation(occupation, county) → annual growth rate
  - Parse CA EDD occupation wage data by county
  - May need to scrape/parse HTML or find data API endpoint
  - Return: wage growth rate as decimal (e.g., 0.028 for 2.8%)
  - Include error handling with fallback to state average
  - Add provenance: retrieval timestamp, source URL, occupation/county used

- [ ] T051 [P0] Add API integration tests `tests/integration/test_live_apis.py`:
  - Test: Federal Reserve H.15 rate fetch succeeds and returns valid rate
  - Test: CA Labor Market Info fetch succeeds for sample occupation
  - Test: Fallback handling when APIs are unavailable
  - Test: Provenance data is correctly captured
  - Note: Use mocking for CI/CD to avoid rate limits

- [ ] T052 [P0] Update `.env.example` with API configuration:
  - Add: FED_API_TIMEOUT=30
  - Add: CA_LABOR_API_TIMEOUT=30
  - Add: API_CACHE_TTL=3600 (cache for 1 hour)
  - Document API endpoints and expected behavior

## Phase 7: Assignment Compliance - Supporting Agents (Priority: P0 - BLOCKING)

**Goal**: Implement Federal Reserve Rate Agent and Skoog Table Agent as supporting functions.

**Critical**: Assignment architecture diagram shows these as separate agents.

### Supporting Agent Implementation (T053-T056)

- [ ] T053 [P0] Implement Federal Reserve Rate Agent `src/agents/fed_rate_agent.py`:
  - Role: Provides current treasury/discount rates to DiscountRateAgent
  - Input: { present_date }
  - Output: { treasury_1yr_rate, retrieval_timestamp, provenance_log }
  - Function: Calls FedClient.get_treasury_rates() from external_apis.py
  - Ensures discount factors reflect current economic conditions
  - Single-file, <=300 lines
  - Implements standard agent contract: run(input_json: dict) → dict

- [ ] T054 [P0] Implement Skoog Table Agent `src/agents/skoog_table_agent.py`:
  - Role: Provides actuarial worklife data to WorklifeExpectancyAgent
  - Input: { age, gender, education }
  - Output: { worklife_expectancy_years, table_source, provenance_log }
  - Function: Queries Skoog tables from data_loader.py
  - Returns statistical worklife expectancy by age/gender/education
  - Single-file, <=300 lines
  - Implements standard agent contract: run(input_json: dict) → dict

- [ ] T055 [P0] Update `src/agents/discount_rate_agent.py` to call Federal Reserve Rate Agent:
  - Import and instantiate FedRateAgent
  - Call fed_rate_agent.run() to get current Treasury rate
  - Use returned rate for discount calculations
  - Merge provenance logs
  - Ensure backward compatibility if Fed agent fails (use fallback rate)

- [ ] T056 [P0] Update `src/agents/worklife_expectancy_agent.py` to call Skoog Table Agent:
  - Import and instantiate SkoogTableAgent
  - Call skoog_agent.run() to get worklife expectancy
  - Use returned expectancy for remaining work years calculation
  - Merge provenance logs
  - Remove hardcoded retirement age logic (use Skoog data instead)

## Phase 8: Assignment Compliance - Supervisor Agent (Priority: P1)

**Goal**: Implement Supervisor Agent to orchestrate all 9 agents and coordinate data flow.

**Critical**: Assignment architecture shows Supervisor as central coordination agent.

### Supervisor Agent Implementation (T057-T060)

- [ ] T057 [P1] Implement Supervisor Agent `src/agents/supervisor_agent.py`:
  - Role: Orchestrates all 9 agents and generates final Excel/Word reports
  - Coordinates execution order:
    1. PersonInvestigationAgent (validates input)
    2. FedRateAgent (gets discount rate)
    3. LifeExpectancyAgent (gets life expectancy)
    4. SkoogTableAgent (gets worklife expectancy)
    5. WorklifeExpectancyAgent (calculates work years remaining)
    6. WageGrowthAgent (gets annual growth rate)
    7. PresentValueAgent (calculates earnings loss)
    8. ComprehensiveExcelGenerator (creates Excel output)
    9. SummaryReportGenerator (creates summary report)
  - Extracts results from each agent
  - Passes outputs as inputs to dependent agents
  - Aggregates all results into final workbook structure
  - Tracks agent progress and updates job status in real-time
  - Single-file, <=500 lines (exception: coordination complexity)

- [ ] T058 [P1] Update `src/jobs/manager.py` to use Supervisor Agent:
  - Replace direct agent calls with supervisor_agent.run()
  - Pass intake data to supervisor
  - Supervisor returns complete FinalWorkbook structure
  - JobManager only handles job lifecycle (queue, status, storage)

- [ ] T059 [P1] Add real-time progress tracking in Supervisor Agent:
  - Emit progress events as each agent starts/completes
  - Include agent name, status, message, output in each event
  - Store progress in job status (accessible via GET /api/status/<job_id>)
  - Progress structure: { agent_name, status, message, output, timestamp }

- [ ] T060 [P1] Add Supervisor Agent tests `tests/unit/test_supervisor_agent.py`:
  - Test: Full agent orchestration with mock agents
  - Test: Progress tracking updates correctly
  - Test: Error handling when agent fails
  - Test: Output aggregation produces valid FinalWorkbook

## Phase 9: Assignment Compliance - Real-Time Progress Dashboard (Priority: P1)

**Goal**: Update frontend to show live agent progress with 3-second updates.

**Critical**: Assignment demo shows detailed real-time progress dashboard during analysis.

### Real-Time Progress UI (T061-T065)

- [ ] T061 [P1] Update API endpoint `src/api/status.py` to return detailed agent progress:
  - Current response: { job_id, status, progress_pct }
  - New response: { job_id, status, progress_pct, person_name, session_id, current_step, agents: [ { name, status, message, output } ], generated_files: [], errors: [] }
  - Include all agent statuses from Supervisor tracking
  - Include person name from intake data

- [ ] T062 [P1] Update `static/index.html` with new progress dashboard UI:
  - Add "Analysis Overview" panel with Session ID and Person name
  - Add "Agent Flow" table with columns: Agent | Status | Message | Output
  - Add "Generated Files" section (links to download Excel/PDF)
  - Add "Errors & Issues" section (show any errors with timestamps)
  - Style to match assignment screenshot (purple header, clean table)

- [ ] T063 [P1] Update `static/js/app.js` for 3-second polling with detailed updates:
  - Change polling interval from current to 3000ms (3 seconds)
  - Parse new detailed status response
  - Update Agent Flow table with status badges (COMPLETED=green, IN_PROGRESS=blue, PENDING=gray)
  - Show agent messages and outputs in real-time
  - Animate progress bar based on completed agents (e.g., "5/8 agents")
  - Show "Current Step" text above progress bar

- [ ] T064 [P1] Update `static/css/styles.css` for progress dashboard styling:
  - Add purple header style for live dashboard (CA Wage Data Agent theme)
  - Add status badges (green/blue/gray) for agent status indicators
  - Add agent flow table styling (alternating rows, hover effects)
  - Add fade-in animations for new agent status updates
  - Match assignment screenshot aesthetics

- [ ] T065 [P1] Add progress dashboard integration test `tests/integration/test_progress_dashboard.py`:
  - Test: Status endpoint returns detailed agent progress
  - Test: Frontend polls every 3 seconds
  - Test: Agent status updates appear in correct order
  - Test: Generated files section populates on completion

## Phase 10: Assignment Compliance - Excel Output Verification (Priority: P1)

**Goal**: Verify Excel output matches exact template structure from assignment.

**Critical**: Output format must match screenshot for grading compliance.

### Excel Format Verification (T066-T069)

- [ ] T066 [P1] Update `src/xlsx/xlsx_generator.py` to match assignment template:
  - Top section with centered values:
    - Base Value (formatted as currency)
    - Discount rate (formatted as percentage)
    - Annual growth rate (formatted as percentage)
  - Item label: "Earnings Loss (More Conservative)" or similar
  - Cumulative Present Value (large, bold, formatted as currency)
  - Present Value Date table:
    - Row labels: "Month", "Day", "Year"
    - Values: e.g., "Jan", "10", "2025"
  - Main table with exact columns from assignment:
    - Age | Start Date | Year Number | Portion of Year | Full Year Value | Actual Value | Cumulative Value | Discount Factor | Present Value | Cumulative Present Value
  - Apply cell formatting:
    - Currency columns: $#,##0.00
    - Percentage columns: 0.00%
    - Highlight starting age row (yellow fill)
  - Sheet name: "Earnings Loss Analysis" or as specified

- [ ] T067 [P1] Add Excel template validation utility `src/xlsx/template_validator.py`:
  - Function: validate_output_format(workbook_path, template_spec) → bool
  - Checks: Required column headers present
  - Checks: Value formats (currency, percentage, dates)
  - Checks: Sheet names match expected
  - Checks: Key calculated values within reasonable ranges
  - Returns validation report with pass/fail status

- [ ] T068 [P1] Create reference template Excel file `docs/examples/assignment_template.xlsx`:
  - Manually create Excel file matching assignment screenshot exactly
  - Use as golden reference for automated testing
  - Include sample data with known calculation results

- [ ] T069 [P1] Add Excel output verification test `tests/integration/test_excel_output_format.py`:
  - Generate sample workbook from test intake
  - Compare output against assignment_template.xlsx structure
  - Verify: All required columns present
  - Verify: Header labels match exactly
  - Verify: Value formatting (currency, percentages)
  - Verify: Calculated totals are mathematically correct

## Phase 11: User Story 2 - Source-verified Calculations (Priority: P2)

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

- **Total task count: 107**
  - **Completed: 35** ✅ (Phases 1-5: MVP + Dashboard + Static Data complete)
  - **Remaining: 72** ⏳ (Assignment compliance work)

- Task count by phase:
  - **Phase 1 - Setup**: 5 tasks (T001..T005) ✅ COMPLETE
  - **Phase 2 - Foundational**: 8 tasks (T006..T013) ✅ COMPLETE
  - **Phase 3 - US1 MVP**: 12 tasks (T014..T025) ✅ COMPLETE
  - **Phase 4 - Dashboard Fixes (P0 BLOCKING)**: 6 tasks (T039..T044) ✅ COMPLETE
  - **Phase 5 - Static Data Sources (P0 BLOCKING)**: 4 tasks (T045..T048) ✅ COMPLETE
  - **Phase 6 - Live API Integrations (P0 BLOCKING)**: 4 tasks (T049..T052) ⏳ TODO
  - **Phase 7 - Supporting Agents (P0 BLOCKING)**: 4 tasks (T053..T056) ⏳ TODO
  - **Phase 8 - Supervisor Agent (P1)**: 4 tasks (T057..T060) ⏳ TODO
  - **Phase 9 - Real-Time Progress Dashboard (P1)**: 5 tasks (T061..T065) ⏳ TODO
  - **Phase 10 - Excel Output Verification (P1)**: 4 tasks (T066..T069) ⏳ TODO
  - **Phase 11 - US2 Provenance**: 4 tasks (T026..T029) ⏳ TODO
  - **Phase 12 - US3 Parameter Overrides**: 4 tasks (T030..T033) ⏳ TODO
  - **Phase N - Polish**: 5 tasks (T034..T038) ⏳ TODO

- **CRITICAL PATH for Assignment Compliance (72 tasks remaining):**
  1. ⏳ Complete Phases 6-7 (P0 BLOCKING tasks: T049..T056) - 8 tasks
  2. ⏳ Complete Phases 8-10 (P1 tasks: T057..T069) - 13 tasks
  3. These 21 tasks (T049..T069) are essential for matching assignment requirements
  4. Remaining 51 tasks (T026..T038) are nice-to-have enhancements

- **Priority Breakdown (Remaining Work):**
  - P0 (BLOCKING): 8 tasks ⚠️ - APIs, supporting agents
  - P1 (HIGH): 13 tasks 🔥 - Supervisor, real-time dashboard, Excel verification
  - P2 (MEDIUM): 4 tasks - Provenance
  - P3 (LOW): 4 tasks - Parameter overrides
  - Polish: 5 tasks - Code quality and documentation

- Parallel opportunities:
  - Live API clients (T049..T050) can be developed in parallel
  - Supporting agents (T053..T054) are parallelizable
  - Dashboard updates and Excel verification can run concurrently

- **Recommended Execution Order:**
  1. ✅ **DONE** - Phases 1-5 (MVP + Dashboard + Static Data - 35 tasks complete)
  2. ⏳ **START HERE → Phase 6**: Implement live APIs (T049..T052) - 4 tasks
  3. ⏳ **Phase 7**: Create supporting agents (T053..T056) - 4 tasks
  4. ⏳ **Phase 8**: Build supervisor agent (T057..T060) - 4 tasks
  5. ⏳ **Phase 9**: Add real-time dashboard (T061..T065) - 5 tasks
  6. ⏳ **Phase 10**: Verify Excel output (T066..T069) - 4 tasks
  7. ⏳ Phases 11-12: Provenance and parameter overrides (if time permits) - 8 tasks
  8. ⏳ Phase N: Polish and documentation - 5 tasks

**Progress: 35/107 tasks complete (32.7%)**
**Critical path remaining: 21/72 tasks (29.2% of remaining work)**

## Files created by this task generator
- `specs/1-wrongful-death-econ/tasks.md` (this file)


*All tasks follow the required checklist format and include explicit file paths where appropriate.*
