# Backend

FastAPI backend for AI Bidding Multi-Agent Platform.

## Run Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Health

```text
GET http://127.0.0.1:8000/health
```

## API Docs

```text
http://127.0.0.1:8000/docs
```

## Main API Prefix

```text
/api/v1
```

## Environment

```text
DATABASE_URL=sqlite:///./database/app.db
SECRET_KEY=change-me
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
```
