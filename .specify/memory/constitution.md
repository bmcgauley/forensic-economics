<!--
Sync Impact Report

- Version change: [UNSPECIFIED] -> 0.1.0
- Modified principles:
	- Added: "Code Modularity" (agent single-file, <=300 lines)
	- Added: "Agent Autonomy" (independent domain research)
	- Added: "Data Integrity" (traceable, verifiable calculations)
	- Added: "Minimal Dependencies" (prefer standard libraries)
	- Added: "Excel Compatibility" (legal-document-grade output)
	- Added: "Simple Architecture" (Web dashboard → agents → Excel)
- Added sections: none (principles populated into Core Principles)
- Removed sections: none
- Templates requiring updates:
	- .specify/templates/plan-template.md ✅ updated (Constitution Check filled)
	- .specify/templates/spec-template.md ✅ updated (Constitution Compliance guidance added)
	- .specify/templates/tasks-template.md ⚠ pending (verify task categories for traceability & Excel tasks)
- Follow-up TODOs:
	- TODO(RATIFICATION_DATE): original ratification date unknown — please supply
	- Verify tasks-template.md and commands/ files for agent naming and adjust if required
-->

# Forensic Economics Constitution

## Core Principles

### Code Modularity
All agent implementations MUST be self-contained in a single source file and MUST NOT exceed 300 lines of code.
- Rules:
	- Each agent is a single file representing one clearly defined responsibility.
	- No agent file may exceed 300 lines (excluding generated code or vendored libraries).
	- Cross-agent shared code SHOULD live in clearly named libraries/modules and be re-used via imports, not by expanding agent files.
- Rationale: Enforcing single-file agents with a line limit keeps review scope small, aids traceability, and reduces coupling. This rule supports auditability for legal use-cases.

### Agent Autonomy
Agents MUST be capable of independently researching and reasoning about their assigned domains without requiring synchronous orchestration.
- Rules:
	- Each agent MUST declare its domain in its header comment and list expected inputs/outputs.
	- Agents MUST include lightweight, reproducible research notes or references (source citations, data provenance) as part of their output when used for calculations.
- Rationale: Autonomy reduces brittle coordination logic, ensures each expert component can be validated independently, and provides clearer evidence trails for claims in wrongful-death calculations.

### Data Integrity
All numerical operations, assumptions, and transformations MUST be traceable and verifiable.
- Rules:
	- Every calculation MUST include an ephemeral calculation log or provenance record that lists inputs, formulas used, units, and timestamps.
	- Source data used (e.g., wage tables, mortality tables, CPI) MUST be recorded with exact version/date and an accessible reference URL or file hash.
	- Results presented to users or exported to documents MUST include an attached verification summary that maps final figures back to source inputs and intermediate steps.
- Rationale: For legal and expert testimony, calculations must be auditable. Traceability reduces dispute risk and supports cross-examination requirements.

### Minimal Dependencies
The project MUST prefer standard-library tooling and keep third-party dependencies to a minimum.
- Rules:
	- Add a dependency only when necessary and justified in a PR description (security, maintenance, and license review required).
	- Where functionality can be implemented robustly using standard libraries, external packages MUST be avoided.
- Rationale: Minimizing dependencies reduces maintenance burden, security surface, and licensing risk — important for long-lived legal artifacts.

### Excel Compatibility
All output formats intended for legal use MUST be compatible with Microsoft Excel and conform to legal document standards used in wrongful death claims.
- Rules:
	- Final exports to Excel (XLSX/CSV) MUST preserve numeric precision, formatting, and labeled metadata required in legal exhibits.
	- Export templates MUST be validated against a canonical legal template and include a verification checklist confirming match.
	- Any automated rounding or unit conversions MUST be explicit and logged in the calculation provenance.
- Rationale: Court exhibits and settlement documents commonly rely on Excel; precise, legally compatible output avoids downstream formatting disputes.

### Simple Architecture
The system architecture MUST remain deliberately simple: Web dashboard → agents → Excel output.
- Rules:
	- The canonical data flow is a single web dashboard (UI/API) that invokes independent agents and aggregates their outputs for Excel export.
	- No subsystem should be required to understand more than immediate neighbors in the pipeline; agents must accept inputs and provide outputs via simple, well-documented contracts (JSON or CSV snippets).
- Rationale: Simpler architectures are easier to validate, secure, and explain in legal contexts. This reduces integration complexity and improves testability.

## Additional Constraints

Technology and compliance constraints for this project:

- Prefer widely used, well-supported runtimes (e.g., recent Python LTS) and standard libraries for data handling and XLSX generation.
- All third-party dependencies MUST have permissive licenses compatible with legal distribution; include license stamps in the repository.

## Development Workflow

Development expectations and quality gates:

- All PRs that change calculation logic MUST include: unit tests, integration tests that run a sample calculation end-to-end, and a calculation provenance artifact for the sample.
- Every agent file MUST have a header documenting purpose, inputs, outputs, and a short provenance example.
- Code reviews MUST validate compliance with the core principles (single-file agents, traceability, minimal deps).

## Governance

Amendment and versioning policy:

- Amendment procedure: Any proposed amendment MUST be submitted as a PR modifying this file and include:
	1. A clear description of the change and rationale.
	2. Classification of the version bump (MAJOR/MINOR/PATCH) with justification.
	3. A migration or compliance plan if the amendment changes contracts or outputs.
- Approval: Amendments require approval from at least two maintainers or one domain expert plus one maintainer. Major governance changes require a documented stakeholder review.
- Versioning policy:
	- MAJOR: Backwards-incompatible governance or principle removals/redefinitions.
	- MINOR: Addition of new principles or material expansions of guidance.
	- PATCH: Clarifications, typo fixes, or non-semantic refinements.
- Compliance review expectations:
	- Every release that modifies calculation code MUST include a compliance checklist referencing these principles and sample verification artifacts.

**Version**: 0.1.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2025-10-29
