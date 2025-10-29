# Constitution Compliance Guidance

This document contains guidance for spec authors to document how a feature satisfies project constitution gates.

Minimum items to include in a spec when the constitution applies:

- Agent Modularity: List each agent (name and single-file path) and an estimated line count (<=300).
- Agent Autonomy: For each agent, state the domain it covers and required external data sources.
- Data Integrity: List source datasets, provenance capture approach, and storage/visibility of calculation logs.
- Minimal Dependencies: Declare third-party dependencies and justify why they are necessary.
- Excel Compatibility: Define target workbook structure (sheets and key labels) and the approach to validate against any legal template.
- Simple Architecture: Provide a concise data-flow mapping (Web dashboard → agents → aggregator → Excel generator).

Attach an example provenance output for a sample calculation in the implementation plan.
