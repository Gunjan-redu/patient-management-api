# Patient Management API

A REST API for managing patient records, built with FastAPI and PostgreSQL.
This is my first backend project — it started as a simple CRUD app storing
data in a JSON file, and was later migrated to a real PostgreSQL database
running in Docker.

## Stack

- **FastAPI** — routes, validation, auto-generated docs
- **PostgreSQL** (in Docker) — data storage with constraints
- **SQLAlchemy** — ORM connecting Python to the database
- **Pydantic** — request/response validation

## Features

- Full CRUD with correct HTTP semantics (201 on create, 404, 422)
- **Two-layer validation**: Pydantic checks requests at the API door
  (age 1–119, height 30–272 cm, weight 1–500 kg); database CHECK
  constraints enforce the same rules at the storage layer
- **Server-assigned IDs** — clients never send an id; PostgreSQL's
  SERIAL guarantees uniqueness
- **Separate input/output models** — `PatientCreate` (no id) for
  requests, `Patient` for responses, `UpdatePatient` (all optional)
  for partial updates via PATCH
- **Foreign-key protected appointments table** — appointments can't
  point at non-existent patients, patients with appointments can't
  be deleted
- Reproducible setup: `schema.sql` rebuilds the database,
  `requirements.txt` rebuilds the environment

## Run it locally

**Prerequisites:** Python 3.10+, Docker Desktop

1. **Start PostgreSQL in Docker:**
```
   docker run --name patient-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=patients_db -p 5432:5432 -d postgres
```

2. **Create tables and seed data** (PowerShell):
```
   Get-Content schema.sql | docker exec -i patient-db psql -U postgres -d patients_db
```

3. **Install dependencies and run:**
```
   pip install -r requirements.txt
   uvicorn main:app --reload
```

4. **Explore the API** at http://127.0.0.1:8000/docs

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/patients` | List all patients |
| POST | `/patients` | Create a patient (server assigns id) |
| GET | `/patients/{id}` | Get one patient |
| PATCH | `/patients/{id}` | Partial update (send only changed fields) |
| PUT | `/patients/{id}` | Full replacement |
| DELETE | `/patients/{id}` | Delete a patient |

## What I learned building this

- HTTP semantics: status codes as contracts, PUT vs PATCH, path vs
  query parameters
- Why databases beat files: my JSON file happily stored duplicate
  ids, age 0, and heights in three different units — PostgreSQL's
  constraints made every one of those impossible
- Docker basics: containers, port mapping, `docker exec`
- The ORM pattern: SQLAlchemy models as Python's map to existing
  tables, sessions via FastAPI's dependency injection
  (`Depends(get_db)`)