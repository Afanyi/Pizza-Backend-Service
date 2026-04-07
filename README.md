# 1337 Pizza Backend Service

Backend service for the 1337 Pizza delivery platform. The application exposes a versioned REST API built with FastAPI and stores its data in PostgreSQL via SQLAlchemy and Alembic migrations.

## Overview

The service currently provides API endpoints for:

- users
- orders
- beverages
- pizza types
- doughs
- toppings
- sauces

The API is mounted under `/v1`, and interactive documentation is available through FastAPI's Swagger UI.

## Tech Stack

- Python 3.10
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Poetry
- Pytest
- Tavern
- Docker

## Repository Structure

```text
.
├── app/                    Application source code
├── doc/                    Project documentation
├── infra/                  Docker and deployment artifacts
├── tests/                  Unit, integration, and service tests
├── docker-compose.yml      Local development services
├── pyproject.toml          Python dependencies and tool configuration
└── alembic.ini             Database migration configuration
```

## Prerequisites

- Python 3.10
- Poetry 1.8.5 or compatible
- Docker
- Docker Compose v2
- PostgreSQL 15 if you run the app without Docker

## Environment Variables

The application reads its database configuration from the following variables:

- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_USERNAME`
- `DATABASE_PASSWORD`
- `DATABASE_NAME`

The default Docker Compose setup uses:

```env
DATABASE_HOST=db-dev
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=mysecretpassword
DATABASE_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=postgres
```

## Getting Started

### Option 1: Recommended local setup

The repository ships with documentation for running the project through PyCharm with a Docker Compose interpreter:

- [Local development setup](doc/local_dev_setup/README.md)

This is the most complete setup path documented in the repository.

### Option 2: Run from the command line

1. Install dependencies:

```bash
poetry install
```

2. Make sure PostgreSQL is running and the required database environment variables are set.

3. Apply database migrations:

```bash
PYTHONPATH=. poetry run alembic upgrade head
```

4. Start the API:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5. Open the API documentation:

```text
http://localhost:8000/docs
```

## Database Migrations

Apply the latest schema changes:

```bash
PYTHONPATH=. poetry run alembic upgrade head
```

Create a new migration after changing the SQLAlchemy models:

```bash
PYTHONPATH=. poetry run alembic revision --autogenerate -m "my_new_feature"
```

Migration files are stored in `app/database/migrations/versions/`.

## Testing

Run linting:

```bash
poetry run flakeheaven lint app/ tests/
```

Run unit tests:

```bash
PYTHONPATH=. poetry run pytest -x tests/unit/
```

Run integration tests:

```bash
PYTHONPATH=. poetry run pytest -x tests/integration/
```

Run service tests:

```bash
export API_SERVER=localhost
export API_PORT=8000
PYTHONPATH=. poetry run pytest -x tests/service/
```

Service tests expect the API to be running and reachable through `API_SERVER` and `API_PORT`.

## API Notes

- Base path: `/v1`
- Swagger UI: `/docs`
- ReDoc: `/redoc`

Current route groups are defined in [app/api/v1/router.py](app/api/v1/router.py).

## Additional Documentation

- [Documentation index](doc/README.md)
- [Local development setup](doc/local_dev_setup/README.md)
- [Testing](doc/testing/README.md)
- [Tooling](doc/tooling/README.md)
- [CI/CD strategy](doc/cicd_strategy/README.md)
- [Coding conventions](doc/coding_conventions/README.md)
- [Versioning and commit messages](doc/versioning_commit_messages/README.md)
