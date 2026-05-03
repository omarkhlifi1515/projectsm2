
### Quick start (development)

Install system prerequisites:

- Python 3.10+ (recommended)
- pip (package installer)

Then install dependencies:

```bash
python3 -m pip install -r backend/requirements.txt
python3 -m pip install -r frontend/requirements.txt
```

Start the backend API (port 8000):

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Start the frontend UI (port 8501):

```bash
cd frontend
BACKEND_URL="http://127.0.0.1:8000" python3 app.py
```
