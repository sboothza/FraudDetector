# FraudDetector

FastAPI service for evaluating financial transactions against configurable fraud rules.5000

## Features

- JWT bearer authentication with role claims loaded from the database
- Rule-based transaction checks such as balance, value, duplicate detection, and transaction limits
- Single-transaction processing and background batch processing
- SQLAlchemy models and repositories for users, roles, currencies, customers, and transactions

## Requirements

- Python 3.11 or later
- Dependencies listed in `requirements.txt`
- [Docker](https://www.docker.com/) and Docker Compose (recommended for running the full stack)

## Docker Compose

From the project root, copy the environment template and start all services:

```bash
cp .env.example .env
docker compose up --build -d
```

This starts:


| Service             | Role                                                          |
| ------------------- | ------------------------------------------------------------- |
| `**db**`            | PostgreSQL database                                           |
| `**api**`           | FastAPI application                                           |
| `**elasticsearch**` | Log storage and search                                        |
| `**logstash**`      | Ships application log files into Elasticsearch                |
| `**kibana**`        | Log search and dashboards                                     |
| `**kibana-setup**`  | One-shot job: data view, logs dashboard, default landing page |


On first start, the API waits for Postgres, then runs `seed.py` only if the database has no tables yet.


| Service       | URL                                                      |
| ------------- | -------------------------------------------------------- |
| API           | [http://localhost:5000/docs](http://localhost:5000/docs) |
| Postgres      | `localhost:5432`                                         |
| Elasticsearch | [http://localhost:9200](http://localhost:9200)           |
| Kibana        | [http://localhost:5601](http://localhost:5601)           |


Postgres credentials (Compose defaults): user `fraud`, password `fraud`, database `fraud`.

### Viewing logs in Kibana

1. Open [http://localhost:5601](http://localhost:5601) — the **Fraud Detector Logs** dashboard is the default page
2. Adjust the time range (top-right) if needed; default is **Last 24 hours**
3. Generate API traffic (`curl http://localhost:5000/`) to see new log lines

If the dashboard is empty, confirm Logstash is running and indices exist:

```bash
docker compose logs logstash
curl "http://localhost:9200/_cat/indices/fraud-detector-*?v"
```

Stop the stack:

```bash
docker compose down
```

Remove volumes (database, logs, Elasticsearch data):

```bash
docker compose down -v
```

Data persists in volumes `fraud-db-data`, `fraud-logs`, `es-data`, and `logstash-data`.

### Compose environment overrides

The `api` service loads variables from `.env` via `env_file`, then applies Compose-specific overrides:


| Variable       | Value in Compose                                 | Notes                                                  |
| -------------- | ------------------------------------------------ | ------------------------------------------------------ |
| `DATABASE_URL` | `postgresql+psycopg://fraud:fraud@db:5432/fraud` | Hostname `db` is the Postgres service name             |
| `LOG_FILE`     | `/app/logs/fraud-detector.log`                   | Written to the shared `fraud-logs` volume for Logstash |


All other variables come from your `.env` file unchanged.

## Configuration

Configuration is read from **environment variables**. For local development, copy the template and edit as needed:

```bash
cp .env.example .env
```

The application loads `.env` from the project root on startup (`src/configuration.py` uses `python-dotenv`). Do not commit `.env` — it is listed in `.gitignore`. Use `.env.example` as the reference for all supported variables.

### Database


| Variable            | Required | Default                                                 | Description                                                                          |
| ------------------- | -------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `DATABASE_URL`      | No       | `postgresql+psycopg://fraud:fraud@localhost:5432/fraud` | SQLAlchemy connection string. Use `postgresql+psycopg://` with the `psycopg` driver. |
| `CONNECTION_STRING` | No       | —                                                       | Legacy alias for `DATABASE_URL` if `DATABASE_URL` is unset                           |


**Local development** (API on host, Postgres via Compose): use `localhost` as the host:

```env
DATABASE_URL=postgresql+psycopg://fraud:fraud@localhost:5432/fraud
```

**Inside Docker Compose**: the `api` service overrides this to use hostname `db` (see table above).

### Authentication (JWT)


| Variable                          | Required | Default                             | Description                                                              |
| --------------------------------- | -------- | ----------------------------------- | ------------------------------------------------------------------------ |
| `JWT_SECRET_KEY`                  | No       | `dev-only-change-before-production` | Secret used to sign access tokens. **Set a strong value in production.** |
| `JWT_ALGORITHM`                   | No       | `HS256`                             | JWT signing algorithm                                                    |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No       | `60`                                | Access token lifetime in minutes                                         |


### Fraud processing


| Variable      | Required | Default | Description                                              |
| ------------- | -------- | ------- | -------------------------------------------------------- |
| `TIME_WINDOW` | No       | `1h`    | Lookback window for fraud rules (e.g. `30m`, `1h`, `2d`) |
| `BATCH_COUNT` | No       | `100`   | Maximum transactions processed per batch run             |


### Logging


| Variable           | Required | Default                   | Description                                                      |
| ------------------ | -------- | ------------------------- | ---------------------------------------------------------------- |
| `LOG_LEVEL`        | No       | `INFO`                    | Root log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)             |
| `LOG_FILE`         | No       | `logs/fraud-detector.log` | Log file path; relative paths are resolved from the project root |
| `LOG_MAX_BYTES`    | No       | `10485760` (10 MB)        | Size per file before rotation                                    |
| `LOG_BACKUP_COUNT` | No       | `5`                       | Number of rotated backup files to retain                         |


Logs are written to **stdout** and to `LOG_FILE`. In Compose, Logstash reads the file from the shared volume and indexes it into Elasticsearch for Kibana.

## Setup

For local development without running the API in Docker:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Start Postgres (if not already running via Compose):

```bash
docker compose up -d db
```

Create the schema and seed reference data from the `src` directory:

```bash
cd src
python seed.py
```

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

- `GET /` — health check
- `POST /auth/login` — obtain a JWT
- `GET /customers/{customer_id}/transactions` — list a customer's transactions (authenticated)
- `POST /process/transaction` — process one transaction
- `POST /process/process_all` — start background batch processing

Interactive API docs are available at `/docs` while the server is running.

## Project layout

- `src/main.py` — FastAPI application entry point
- `src/configuration.py` — environment variable loading
- `src/models/` — SQLAlchemy models
- `src/repositories/` — database access layer
- `src/rules/` — fraud rule implementations
- `src/services/` — transaction processing
- `src/routers/` — HTTP routes
- `src/seed.py` — initial data loader
- `docker-compose.yml` — full stack (API, Postgres, ELK)
- `logstash/pipeline/` — Logstash pipeline configuration
- `scripts/setup-kibana.sh` — Kibana data view and dashboard setup

