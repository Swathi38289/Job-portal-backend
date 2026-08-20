# Django Jobs Backend

This is the backend for the Jobs application. Built with **Django** and **Django REST Framework**, it supports candidate data submission and resume uploads.

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

### Sample request

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

## Design tradeoffs

- **TF-IDF is the default:** It is fast, deterministic, and works offline after installation. It is less effective when a resume and job description use different wording for the same idea.
- **Semantic matching is opt-in:** `use_semantic=true` enables `all-MiniLM-L6-v2`. The model is loaded lazily and cached, but the first request downloads model files and uses more memory.
- **Known-skill extraction is deliberately bounded:** The extractor uses a maintainable alias dictionary rather than an opaque model, which makes scoring explainable but means uncommon skills must be added to the dictionary.
- **No database model for screening results yet:** Results are returned immediately and are not persisted, keeping the first API version simple while sacrificing history and auditability.

## Testing

Run the full test suite with:

```bash
python manage.py test
```

The tests cover PDF and DOCX parsing, job-description parsing, skill extraction, similarity scoring, ranking, validation, and the screening API.

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
python manage.py makemigrations
python manage.py migrate
```

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
