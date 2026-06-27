# Frontend

React + TypeScript frontend for AI Bidding Multi-Agent Platform.

## Run

```bash
cd frontend
npm install
npm run dev
```

Default URL:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/api` to:

```text
http://127.0.0.1:8000
```

The frontend also supports direct FastAPI configuration:

```bash
copy .env.example .env
```

Default value:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

All frontend API modules call FastAPI through `src/api/client.ts`.

## Login API

The login page calls:

```text
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

## Connected FastAPI Endpoints

```text
GET    /health
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/me
GET    /api/v1/dashboard/summary
GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/enterprises
POST   /api/v1/projects/enterprises
GET    /api/v1/projects/{project_id}/files
POST   /api/v1/projects/{project_id}/files
POST   /api/v1/projects/{project_id}/analysis/start
GET    /api/v1/analysis-tasks/{analysis_id}
GET    /api/v1/projects/{project_id}/reports/latest
GET    /api/v1/reports/{analysis_id}
```
