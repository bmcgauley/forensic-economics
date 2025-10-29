# Phase 0 Research: Wrongful Death Economic Loss Calculator

**Feature**: specs/1-wrongful-death-econ/spec.md
**Date**: 2025-10-29

## R001: SSA/BLS/Federal Reserve APIs

Decision: Use public BLS and Federal Reserve APIs and SSA published life tables. Implement small HTTP wrappers with defined timeouts and retries. If API keys are required (BLS offers keys for higher quotas), allow optional API key config in environment variables.

Rationale: These public sources are authoritative for wage and life-expectancy data. Wrappers centralize request behavior and error handling.

Alternatives considered:
- Scraping HTML pages (fragile) — rejected.
- Purchasing commercial data feeds (costly, complicated licensing) — deferred.

## R002: Canonical Excel templates

Decision: Require legal team to provide at least one canonical Excel template. In absence, use an internal canonical template matching common exhibit conventions (Summary, Detailed years, Data Sources, Methodology) and validate structure with a checklist.

Rationale: Legal templates vary; having at least one canonical template enables automated validation.

Alternatives:
- Auto-generate free-form Excel (risky for court exhibits).

## R003: Numeric precision & rounding

Decision: Store intermediate calculations at full double precision (IEEE 754), but display and export with configurable rounding (default: 2 decimal places for currency). All rounding steps MUST be logged in provenance and the final workbook must indicate rounding rules.

Rationale: Preserving internal precision avoids cumulative rounding errors; legal exhibits require explicit rounding rules.

## R004: Temporary file lifecycle

Decision: Generate XLSX on disk in a temporary directory (per-request subfolder named by job_id), expose a secure download endpoint that streams the file, and schedule background cleanup of temp folders older than 24 hours by a periodic job.

Rationale: Simplicity and stateless request handling; avoids long-term storage of sensitive data.

## R005: Dependency license/security review

Decision: `openpyxl` (MIT-compatible) and `requests` (Apache 2.0) will be used. Add a `licenses/` folder with copies of dependency licenses and add a dependency justification entry to PRs that add or change versions.

Rationale: Both libraries are widely used and maintained; including license documents satisfies traceability requirements.

## Research outcomes

All Phase 0 unknowns have been resolved with reasonable defaults. Items requiring legal-team input:
- Provide canonical Excel template(s) for target jurisdictions.
- Confirm acceptable rounding policy if jurisdictionally constrained.


*End of research.md*