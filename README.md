# IncidentSense

Agentic production incident investigator that turns error logs and stack traces into ranked root-cause hypotheses and remediation reports.

## Local setup

### Server

```powershell
cd server
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Set `ANTHROPIC_API_KEY` in `server/.env` before running Claude-backed investigations. The health endpoint is available at `http://127.0.0.1:8000/api/health`.

### Client

```powershell
cd client
npm install
npm run dev
```

Open `http://localhost:5173`. Set `VITE_API_URL=http://127.0.0.1:8000` in `client/.env.local` if you do not want to use the frontend's default API URL.

## Server environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | None | API key for Claude Sonnet 4.6 accessed through the Anthropic Python SDK. |
| `ALLOWED_ORIGIN` | Yes | `http://localhost:5173` | Full URL of the deployed frontend; controls backend CORS. |
| `CHROMA_PERSIST_PATH` | No | `./chroma_db` | Directory where ChromaDB persists local vector data. |
| `SQLITE_DB_PATH` | No | `./incidentsense.db` | SQLite database file path. |
| `GITHUB_TOKEN` | No | None | Optional PyGithub authentication token; unavailable private repositories remain out of scope. |

## Client environment variable

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `VITE_API_URL` | Yes | `http://localhost:8000` | Full URL of the Railway backend used for API and SSE requests. |

## Live demo

[Live demo - URL placeholder](https://example.com)
