# AI Resume Screening Agent

An executable Django REST API that extracts text from resumes, identifies relevant skills, scores candidates against a job description, and returns a ranked shortlist. The repository also retains the original candidate-submission API.

## Submission overview

- **Selected agent:** AI Resume Screening Agent.
- **Public repository:** https://github.com/Swathi38289/Job-portal-backend
- **Credentials:** No API keys or external service credentials are required.
- **Scope:** Upload resumes and a job description, extract text and skills, score matches, and return a ranked result in one API response.
- **Agent-specific deliverables:** PDF/DOCX parsing, job-description parsing, skill extraction, TF-IDF scoring, optional semantic scoring, candidate ranking, REST API, automated tests, and a reproducible demo script.

---

## Features

- REST API endpoint to create candidates with:
  - Name, Address, Skills, GitHub link, Age, Email, Phone number
  - College Name and Passing Year
  - Resume upload (PDF/DOC/DOCX)
- Validation for email, numeric fields, and resume file type/size
- Admin dashboard for managing candidates
- Export candidate list to Excel/CSV
- CORS enabled for frontend integration
- Whitenoise for static file serving
- Docker-ready
- SQLite database (default Django DB)

---

## Resume screening API

The screening endpoint accepts one job description and one or more PDF or DOCX resumes. It extracts text, identifies known skills, calculates a match score, and returns candidates ordered from highest to lowest score.

## Browser interface

The project includes a simple browser interface for the screening agent. Start Django and open:

```text
http://127.0.0.1:8000/
```

In the interface:

1. Paste the job description.
2. Choose one or more PDF or DOCX resumes.
3. Optionally enable semantic matching.
4. Select **Screen resumes**.

The page sends the files to the screening API and displays each candidate's rank, filename, score, and match bar. No frontend build step is required.

### Endpoint

```text
POST http://127.0.0.1:8000/api/screen/
```

Use multipart form data with these fields:

| Field                  | Required                       | Description                                          |
| ---------------------- | ------------------------------ | ---------------------------------------------------- |
| `job_description`      | Yes, unless a file is supplied | Plain-text job description                           |
| `job_description_file` | Yes, unless text is supplied   | PDF, DOCX, or TXT job description                    |
| `resumes`              | Yes                            | One or more PDF or DOCX files                        |
| `use_semantic`         | No                             | Set to `true` to use sentence-transformer embeddings |

### Sample request with real files

The following request assumes you provide your own files at the shown paths. For a guaranteed no-file demo, use `python demo_agent.py` below.

```bash
curl -X POST http://127.0.0.1:8000/api/screen/ \
  -F "job_description=Python Django backend developer with REST API experience" \
  -F "resumes=@./samples/jane-doe.pdf" \
  -F "resumes=@./samples/alex-smith.docx" \
  -F "use_semantic=true"
```

### Sample response

```json
{
  "results": [
    { "rank": 1, "filename": "jane-doe.pdf", "score": 84.38 },
    { "rank": 2, "filename": "alex-smith.docx", "score": 61.27 }
  ]
}
```

Scores are percentages from 0 to 100. Missing job descriptions or resumes return HTTP 400 with a `detail` message. Unsupported file formats also return HTTP 400.

### One-command demo

After installing dependencies, run this from the repository root. No server, API key, or sample file is required:

```bash
python demo_agent.py
```

The script creates a sample PDF resume in memory, sends it through the same screening API view, and prints output similar to:

```text
HTTP 200
{
  "results": [
    {
      "rank": 1,
      "filename": "sample-jane-doe.pdf",
      "score": 74.78
    }
  ]
}
```

To run the semantic model path instead, use `python demo_agent.py --semantic`. The first semantic run downloads `all-MiniLM-L6-v2` and caches it locally.

### Processing flow

```text
Upload job description and resumes
  -> parse PDF/DOCX/TXT content
  -> extract known skills
  -> calculate text and skill scores
  -> rank candidates
  -> return JSON results
```

## Design tradeoffs

- **TF-IDF is the default:** It is fast, deterministic, and works offline after installation. It is less effective when a resume and job description use different wording for the same idea.
- **Semantic matching is opt-in:** `use_semantic=true` enables `all-MiniLM-L6-v2`. The model is loaded lazily and cached, but the first request downloads model files and uses more memory.
- **Known-skill extraction is deliberately bounded:** The extractor uses a maintainable alias dictionary rather than an opaque model, which makes scoring explainable but means uncommon skills must be added to the dictionary.
- **No database model for screening results yet:** Results are returned immediately and are not persisted, keeping the first API version simple while sacrificing history and auditability.
- **Synchronous processing:** The first version processes uploads in the request, which keeps the demo easy to run but is not ideal for large batches or production-scale workloads.

## Limitations and next steps

- Scanned/image-only PDFs need OCR, which is not included yet.
- The known-skill dictionary should be expanded or made configurable for new domains.
- Screening results could be persisted with timestamps and reviewer feedback.
- Large uploads should move to a background task queue with file-size and timeout controls.

## Testing

The project uses Django's built-in `unittest` test runner. Tests are stored in
`jobs/test_jobs.py` and `screening/test_screening.py`.

Always run the tests with the same Python environment where `requirements.txt`
was installed. Running `python manage.py test` with a different system Python
can fail during test discovery with `ModuleNotFoundError: No module named
'fitz'`, before any test case runs.

From the repository root on Windows, use the workspace environment shown below
if it exists:

```powershell
..\venv\Scripts\python.exe manage.py test
```

For a fresh clone using a local virtual environment, use:

```powershell
venv\Scripts\python.exe manage.py test
```

### Run all tests

```bash
python manage.py test
```

Expected output:

```text
Ran 24 tests
OK
```

### Run a specific test group

```bash
python manage.py test jobs
python manage.py test screening
python manage.py test screening.tests.ScreeningAPITests
```

The focused screening command should report `Ran 21 tests` and finish with
`OK` when the dependencies are installed in the selected environment.

The tests cover:

- Candidate creation, validation, and resume file restrictions.
- PDF and DOCX resume parsing.
- Plain-text, PDF, DOCX, and TXT job-description parsing.
- Known-skill and custom-keyword extraction.
- TF-IDF similarity, semantic similarity, and score validation.
- Candidate ranking and tie handling.
- Screening API success and validation responses.
- Forwarding of the `use_semantic=true` option.

### Live API smoke test

Start the server first:

```bash
python manage.py runserver
```

Then upload a real resume from another terminal:

```bash
curl -X POST http://127.0.0.1:8000/api/screen/ \
  -F "job_description=Python Django REST API developer" \
  -F "resumes=@./samples/resume.pdf" \
  -F "use_semantic=false"
```

The response should be HTTP 200 with a `results` array containing `rank`, `filename`, and `score` fields.

On Windows systems where numerical libraries report an OpenBLAS memory allocation error, limit their thread count before starting Django:

```powershell
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
python manage.py runserver 127.0.0.1:8000
```

---

## Prerequisites

- Python 3.12+
- Git
- Docker (optional)

---

## Quick Start (Local Development)

### 1. Clone the repository

```bash
git clone https://github.com/Swathi38289/Job-portal-backend.git
cd Job-portal-backend
```

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

```bash
python manage.py migrate
```

The admin account is optional. Create one only if you need the admin panel:

```bash
python manage.py createsuperuser
```

## Start the development server

```bash
python manage.py runserver
```

## Your backend is now running at:

```bash
http://127.0.0.1:8000/
```

## Admin panel: http://127.0.0.1:8000/admin/

## API endpoint: http://127.0.0.1:8000/api/candidates/
