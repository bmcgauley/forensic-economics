# Forensic Economics - MVP Quickstart Guide

This guide will help you get the Wrongful Death Economic Loss Calculator MVP up and running.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Installation

### 1. Clone or download the repository

```bash
cd forensic-economics
```

### 2. Create a virtual environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Start the development server

**Option 1: Using the run script**
```bash
python run.py
```

**Option 2: Using the Flask app directly**
```bash
python -m src.api.app
```

The server will start on `http://localhost:5000`

### Access the dashboard

Open your web browser and navigate to:
```
http://localhost:5000
```

## Using the Application

### 1. Fill out the intake form

The dashboard presents a form with the following sections:

- **Victim Information**: Age, sex, occupation, education
- **Financial Information**: Salary, location, dependents
- **Additional Benefits**: Retirement contributions, health benefits (optional)

### 2. Generate a report

1. Fill in all required fields (marked with *)
2. Click "Generate Report"
3. The system will queue your job and start processing

### 3. Monitor progress

The status panel will show:
- Job queued
- Running calculations (with progress updates)
- Report generated successfully

### 4. Download the report

When complete, a download link will appear. Click it to download the Excel workbook.

## Report Structure

The generated Excel workbook contains four worksheets:

1. **Summary**: High-level victim info and economic calculations
   - Victim demographics
   - Life and worklife expectancy
   - Total future earnings and present value

2. **Yearly Detail**: Year-by-year breakdown
   - Age for each year
   - Base wage and total compensation
   - Discount rates and present values

3. **Data Sources**: Provenance tracking
   - All data sources used
   - URLs and dates
   - Agent usage information

4. **Methodology**: Calculation methodology
   - Detailed explanation of approach
   - Formulas and assumptions
   - Timestamp and version information

## Testing

### Run all tests

```bash
pytest
```

### Run specific test categories

**Unit tests only:**
```bash
pytest tests/unit/ -v
```

**Integration tests only:**
```bash
pytest tests/integration/ -v
```

### Run with coverage

```bash
pytest --cov=src tests/
```

## API Endpoints

### POST /api/generate

Generate a new report.

**Request body:**
```json
{
  "victim_age": 35,
  "victim_sex": "M",
  "occupation": "Software Engineer",
  "education": "bachelors",
  "salary": 85000.00,
  "salary_type": "current",
  "location": "US",
  "dependents": 2,
  "benefits": {
    "retirement_contribution": 5000.00,
    "health_benefits": 8000.00
  }
}
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status_url": "/api/status/uuid-here",
  "message": "Report generation started"
}
```

### GET /api/status/{job_id}

Get job status.

**Response (in progress):**
```json
{
  "job_id": "uuid-here",
  "status": "running",
  "message": "Running calculations..."
}
```

**Response (completed):**
```json
{
  "job_id": "uuid-here",
  "status": "completed",
  "message": "Report generated successfully",
  "download_url": "/api/download/uuid-here",
  "filename": "wrongful_death_report_uuid.xlsx"
}
```

### GET /api/download/{job_id}

Download the generated report (XLSX file).

## Sample Data

A sample intake file is provided at:
```
specs/1-wrongful-death-econ/samples/sample_intake.json
```

You can use this as a reference for the expected data format.

## Troubleshooting

### Port already in use

If port 5000 is already in use, set a different port:

```bash
export PORT=8000  # macOS/Linux
set PORT=8000     # Windows
python run.py
```

### Import errors

Make sure you've activated the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Dependencies not installed

Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

## Configuration

### Environment Variables

- `PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: True)
- `SECRET_KEY`: Flask secret key (set in production)

## Next Steps

- Review the generated reports
- Customize agent calculations for your jurisdiction
- Add integration with actual BLS/SSA/Fed data sources
- Deploy to a production server

## Support

For issues or questions:
- Review the [README.md](../README.md)
- Check the [specification docs](../specs/1-wrongful-death-econ/)
- Open an issue in the repository

## License

See the [licenses/](../licenses/) directory for dependency license information.
