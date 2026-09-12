> InventoryIQ backend (FastAPI)

## Setup

```
py -V:3.14 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## Run

```
.venv\Scripts\uvicorn main:app --reload --port 8000
```

Health check: http://localhost:8000/health
