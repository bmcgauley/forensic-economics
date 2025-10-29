# Quickstart: Wrongful Death Economic Loss Calculator (Developer)

This quickstart shows how to run the minimal server locally for development.

Prerequisites

- Python 3.10+
- pip

Install dependencies (recommended in a virtual environment):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install --upgrade pip; pip install flask openpyxl requests pytest
```

Run server (development):

```powershell
$env:FLASK_APP='app.py'; $env:FLASK_ENV='development'; python -m flask run --host=127.0.0.1 --port=5000
```

Open `index.html` in the browser (served or opened file://). Submit an intake and follow the job status and download endpoints.

Notes

- The server is stateless and stores temporary XLSX files in a temp directory per job.
- For production, run behind a WSGI server (gunicorn or similar) and secure the download endpoints.
- Provide API keys as environment variables for BLS or other sources if needed.
