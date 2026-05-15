# FraudDetector

FastAPI service for evaluating financial transactions against configurable fraud rules.

## Features

- JWT bearer authentication with role claims loaded from the database
- Rule-based transaction checks such as balance, value, duplicate detection, and transaction limits
- Single-transaction processing and background batch processing
- SQLAlchemy models and repositories for users, roles, currencies, customers, and transactions

## Requirements

- Python 3.11 or later
- Dependencies listed in `requirements.txt`

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

From the `src` directory, create the database schema and seed reference data:

```bash
cd src
python seed.py
```

By default, `configuration.py` uses a local SQLite database at `fraud.db` and a one-hour transaction lookback window.

## Run

Start the API from the `src` directory:

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## Authentication

Log in at `POST /auth/login` with JSON credentials. The response includes a bearer token with `sub` and `roles` claims.

Use the token on protected routes:

```http
Authorization: Bearer <access_token>
```

Seeded users are defined in `seed.py`.

## API routes

- `GET /` — health check, requires authentication
- `POST /auth/login` — obtain a JWT
- `POST /process/transaction` — process one transaction
- `POST /process/process_all` — start background batch processing

Interactive API docs are available at `/docs` while the server is running.

## Project layout

- `src/main.py` — FastAPI application entry point
- `src/models/` — SQLAlchemy models
- `src/repositories/` — database access layer
- `src/rules/` — fraud rule implementations
- `src/services/` — transaction processing
- `src/routers/` — HTTP routes
- `src/seed.py` — initial data loader
