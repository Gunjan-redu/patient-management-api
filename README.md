# Patient Management API

A REST API for managing patient records, built with FastAPI and PostgreSQL.
This is my first backend project — it started as a simple CRUD app storing
data in a JSON file, and was later migrated to a real PostgreSQL database
running in Docker, then secured with JWT authentication.

## Stack

- **FastAPI** — routes, validation, auto-generated docs
- **PostgreSQL** (in Docker) — data storage with constraints
- **SQLAlchemy** — ORM connecting Python to the database
- **Alembic** — database migrations
- **Pydantic** — request/response validation
- **bcrypt** — password hashing
- **python-jose** — JWT creation and verification

## Features

- Full CRUD with correct HTTP semantics (201 on create, 401, 404, 409, 422)
- **JWT authentication** protecting all patient and appointment endpoints;
  passwords stored as bcrypt hashes, never in plain text
- **Two-layer validation**: Pydantic checks requests at the API door
  (age 1–119, height 30–272 cm, weight 1–500 kg); database CHECK
  constraints enforce the same rules at the storage layer
- **Server-assigned IDs** — clients never send an id; PostgreSQL's
  SERIAL guarantees uniqueness
- **Separate input/output models** — `PatientCreate` (no id) for
  requests, `Patient` for responses, `UpdatePatient` (all optional)
  for partial updates via PATCH
- **Foreign-key protected appointments table** — appointments can't
  point at non-existent patients; deleting a patient with appointments
  returns 409 instead of orphaning data
- Config via environment variables (`.env`), schema changes managed
  with Alembic migrations
- Reproducible setup: `schema.sql`, `requirements.txt`, `.env.example`

## Authentication

All patient and appointment endpoints require a JWT bearer token.
Only `/`, `/register`, and `/login` are public.

**Flow:**

1. Register: `POST /register` with `{"username": "...", "password": "..."}`
2. Login: `POST /login` (OAuth2 form fields: `username`, `password`) —
   returns `{"access_token": "...", "token_type": "bearer"}`
3. Authenticated requests: send the header
   `Authorization: Bearer <access_token>`
4. Tokens expire after 30 minutes — log in again for a fresh one.

**In the interactive docs (`/docs`):** click **Authorize**, enter your
username and password, and Swagger attaches the token to every
request automatically.

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

3. **Configure environment:** copy `.env.example` to `.env` and fill in
   your database URL and a SECRET_KEY
   (generate one: `python -c "import secrets; print(secrets.token_hex(32))"`)

4. **Install dependencies and run:**

```
pip install -r requirements.txt
uvicorn main:app --reload
```

5. **Open** http://127.0.0.1:8000/docs — register a user, click
   **Authorize**, and explore the endpoints.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Welcome message |
| POST | `/register` | — | Create a user account |
| POST | `/login` | — | Get a JWT access token |
| GET | `/patients` | 🔒 | List patients (filter: `?city=`, `?min_age=`, sort: `?sort_by=`) |
| POST | `/patients` | 🔒 | Create a patient (server assigns id) |
| GET | `/patients/{id}` | 🔒 | Get one patient |
| PATCH | `/patients/{id}` | 🔒 | Partial update |
| PUT | `/patients/{id}` | 🔒 | Full replacement |
| DELETE | `/patients/{id}` | 🔒 | Delete (409 if appointments exist) |
| POST | `/patients/{id}/appointments` | 🔒 | Book an appointment |
| GET | `/patients/{id}/appointments` | 🔒 | List a patient's appointments |

## What I learned building this

- HTTP semantics: status codes as contracts, PUT vs PATCH, path vs
  query parameters
- Why databases beat files: my JSON file happily stored duplicate
  ids, age 0, and heights in three different units — PostgreSQL's
  constraints made every one of those impossible
- Docker basics: containers, port mapping, `docker exec`
- The ORM pattern: SQLAlchemy models as Python's map to existing
  tables, sessions via FastAPI's dependency injection (`Depends`)
- Migrations with Alembic — including catching real schema drift
  between my models and the live database
- Authentication: bcrypt hashing (one-way), JWTs (signed, expiring,
  readable-but-unforgeable), and why login errors never reveal
  whether the username or the password was wrong