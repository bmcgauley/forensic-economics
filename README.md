# Forensic Economics - Wrongful Death Economic Loss Calculator

A minimal, auditable wrongful-death economic-loss calculator with a web dashboard that captures intake data, triggers independent Python agents to compute domain-specific components, aggregates results, and produces a legally-compatible Excel workbook.

## Features

- **Single-page web dashboard** for data intake
- **Independent Python agents** for specialized calculations:
  - Life expectancy analysis
  - Worklife expectancy estimation
  - Wage growth projections
  - Discount rate recommendations
  - Present value calculations
- **Excel workbook generation** with:
  - Summary calculations
  - Year-by-year breakdown
  - Data sources and provenance
  - Methodology documentation

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd forensic-economics
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Flask server:
```bash
python src/api/app.py
```

2. Open your browser to `http://localhost:5000`

3. Enter victim information and generate a report

## Project Structure

```
forensic-economics/
├── src/
│   ├── agents/          # Independent calculation agents
│   ├── models/          # Data models and validation
│   ├── api/             # Flask API endpoints
│   ├── jobs/            # Job management
│   ├── utils/           # Utilities (provenance, external APIs, storage)
│   └── xlsx/            # Excel workbook generation
├── static/              # Web dashboard (HTML, CSS, JS)
├── tests/               # Unit and integration tests
├── licenses/            # Third-party dependency licenses
├── docs/                # Documentation
└── specs/               # Project specifications

```

## Architecture

The system follows a modular agent-based architecture:

1. **Web Dashboard** → captures intake data
2. **Flask API** → receives requests and manages jobs
3. **Agent Orchestrator** → runs agents in parallel
4. **Agents** → perform specialized calculations with provenance tracking
5. **Aggregator** → combines agent results
6. **XLSX Generator** → produces the final workbook

Each agent is self-contained (single file, ≤300 lines) and includes:
- Clear inputs and outputs
- Provenance logging (data sources, formulas, timestamps)
- Error handling and validation

## Testing

Run tests with pytest:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src tests/
```

## Constitution Compliance

This project adheres to the Forensic Economics constitution:
- **Agent Modularity**: Each agent is a single file (≤300 lines)
- **Agent Autonomy**: Agents accept JSON input and return structured outputs with provenance
- **Data Integrity**: All calculations include provenance logs
- **Minimal Dependencies**: Only essential third-party packages with license documentation
- **Excel Compatibility**: Generated workbooks conform to legal templates

## License

See individual dependency licenses in the [licenses/](licenses/) directory.

## Contributing

See [docs/developer.md](docs/developer.md) for development guidelines.

## Documentation

- [Implementation Plan](specs/1-wrongful-death-econ/plan.md)
- [Technical Specification](specs/1-wrongful-death-econ/spec.md)
- [Data Model](specs/1-wrongful-death-econ/data-model.md)
- [Quick Start Guide](specs/1-wrongful-death-econ/quickstart.md)
