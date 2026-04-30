## ENISO Assistant (Frontend + Backend)

This project contains:

- **`backend/`**: FastAPI service (auth, chat, admin console APIs, document upload + retrieval)
- **`frontend/`**: Flask app serving the web UI (chat + admin console)

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

Open:

- Chat UI: `http://127.0.0.1:8501/`
- Admin console: `http://127.0.0.1:8501/admin`

### Admin setup

- The **first registered user** becomes **admin** automatically.
- The admin can configure the LLM gateway from the UI:
  - Admin Console → **Settings** → **LLM Gateway**
  - This stores the configuration in the backend database (`backend/eniso_assistant.db`)

### Environment variables

Backend:

- **`JWT_SECRET`**: JWT signing secret (set in production)
- **`LLM_BASE_URL`**: fallback base URL if not configured in admin settings
- **`LLM_MODEL`**: fallback model if not configured in admin settings
- **`LLM_API_KEY`**: fallback API key if not configured in admin settings

Frontend:

- **`BACKEND_URL`**: API base URL injected into the UI templates

