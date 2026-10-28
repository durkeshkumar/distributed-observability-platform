# Distributed Observability & Root-Cause Analysis Platform

A full-stack observability platform designed to collect and inspect telemetry data, monitor application behavior, surface alerts, and help investigate potential root causes across distributed services.

> **Project status:** The backend and frontend Docker images have been built. Full container startup and end-to-end connectivity still need to be verified.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Environment Configuration](#environment-configuration)
- [Run with Docker Compose](#run-with-docker-compose)
- [Service URLs](#service-urls)
- [Database](#database)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [Future Enhancements](#future-enhancements)

## Overview

Modern distributed applications generate telemetry across multiple services. Investigating incidents can be difficult when events, metrics, traces, and alerts are spread across different components.

This project brings telemetry ingestion and operational visibility into one application. Its backend provides API services for ingesting and managing observability data, while the frontend presents the information through a web interface.

## Key Features

- **Telemetry ingestion:** Backend services for receiving telemetry data.
- **Metrics, logs, and traces:** Database tables are present for metric records, log records, and trace spans.
- **Alert management:** Persistent storage for alerts.
- **Ingestion tracking:** Records ingestion events and ingestion attempts.
- **Service map and investigation UI:** Frontend includes a service-map page intended to help inspect service relationships.
- **Workspace settings:** Stores workspace-level configuration.
- **REST API:** FastAPI-based backend.
- **Web interface:** React, TypeScript, and Vite frontend.
- **Containerized deployment:** Dockerfiles are available for backend and frontend; Docker Compose configuration is provided.

> The exact feature behavior depends on the implementation in the current source code. Features not yet validated end-to-end should be considered under development.

## Technology Stack

| Component | Technology |
|---|---|
| Backend API | Python, FastAPI, Uvicorn |
| Frontend | React, TypeScript, Vite |
| UI components | Material UI |
| Database | MySQL |
| Message broker | RabbitMQ |
| Containerization | Docker, Docker Compose |
| Frontend web server | Nginx |

## Architecture

```text
Browser
   |
   | http://localhost:5177
   v
Frontend container (Nginx serving the built React app)
   |
   | API requests to http://localhost:8001
   v
Backend container (FastAPI / Uvicorn)
   |                         |
   |                         |
   v                         v
Windows MySQL             Existing RabbitMQ
localhost:3306            localhost:5672
(accessed from Docker     (accessed from Docker
 through host.docker.internal) through host.docker.internal)
```

The existing Windows MySQL server and existing RabbitMQ container are intended to be reused rather than starting duplicate database or broker containers.

## Repository Structure

The main paths relevant to running the application are:

```text
distributed-observability-platform/
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env                 # Local configuration; do not commit secrets
│   ├── requirements.txt
│   └── services/
│       └── telemetry_ingestion/
│           └── app/
│               └── main.py
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json
│   ├── package-lock.json
│   └── src/
├── compose.yaml
└── README.md
```

Additional source files and directories may exist in the repository.

## Prerequisites

For local development:

- Python 3.12
- Node.js 22 or a compatible supported version
- npm
- MySQL server with the project database and migrations configured
- RabbitMQ with the application credentials and permissions configured

For containerized execution:

- Docker Desktop
- Docker Compose v2

## Local Development Setup

### 1. Configure the backend

Open a terminal in the repository root and move to the backend directory:

```bash
cd backend
```

Create or activate your Python virtual environment, then install the dependencies:

```bash
python -m venv venv
```

On Windows Git Bash:

```bash
source venv/Scripts/activate
```

On Windows Command Prompt:

```bat
venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Make sure `backend/.env` exists and contains the required local database and RabbitMQ configuration. See [Environment Configuration](#environment-configuration).

Start the API from the repository root so the Python package import path resolves as expected:

```bash
cd ..
cd backend
uvicorn services.telemetry_ingestion.app.main:app --host 0.0.0.0 --port 8001
```

If the application package cannot be imported from that working directory, run the command from the directory that contains the top-level `services` package and adjust the import path only if the repository layout requires it.

### 2. Configure the frontend

Open a separate terminal:

```bash
cd frontend
npm ci
npm run dev
```

Vite prints the local frontend URL in the terminal. The Docker-served frontend is configured to use port `5177`; the local Vite development server may use a different port.

For a production build:

```bash
npm run build
```

## Environment Configuration

The backend reads its local configuration from `backend/.env`. Configure values appropriate for your environment. Do not put real passwords, access tokens, or other secrets in this README.

Example variable names:

```dotenv
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=observability_ingestion

RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=observability
```

Add any other variables required by the application's settings. **Do not replace your actual `.env` with this abbreviated example**: it illustrates the variable names only and may not include every required setting.

When the backend runs inside Docker Desktop on Windows and connects to services published on the Windows host, the Compose configuration uses `host.docker.internal` for the MySQL and RabbitMQ hosts. When running the backend directly on Windows, `localhost` is normally appropriate.

## Run with Docker Compose

The repository includes Dockerfiles for both services and a `compose.yaml` file.

From the repository root:

```bash
docker compose config
```

If the configuration validates, build the images:

```bash
docker compose build
```

Start the services:

```bash
docker compose up -d
```

Check the container state:

```bash
docker compose ps
docker ps -a
```

View logs:

```bash
docker compose logs --tail=100 backend
docker compose logs --tail=100 frontend
```

Stop the application services:

```bash
docker compose down
```

The intended host ports are:

- Frontend: `5177`
- Backend API: `8001`

The Compose setup is intended to reuse the existing `observability-rabbitmq` container and the Windows-hosted MySQL server. The container startup and service connectivity have **not yet been confirmed**, so validate these steps in your environment before relying on the deployment.

## Service URLs

When the corresponding services are running:

| Service | URL |
|---|---|
| Frontend | http://localhost:5177 |
| Backend API | http://localhost:8001 |
| FastAPI Swagger UI | http://localhost:8001/docs |
| FastAPI ReDoc | http://localhost:8001/redoc |
| RabbitMQ Management UI | http://localhost:15672 |

The RabbitMQ management URL requires the configured RabbitMQ credentials. Do not publish credentials in project documentation.

## Database

The application is configured to use the MySQL database `observability_ingestion`.

Tables identified in the existing database include:

- `alembic_version`
- `alerts`
- `ingestion_attempts`
- `ingestion_events`
- `log_records`
- `metric_records`
- `trace_spans`
- `workspace_settings`

Use the project's existing migration process when changing the schema. Back up important data before running migrations or making destructive database changes.

## Troubleshooting

### Docker Compose reports a bridge network alias error

If you see an error similar to:

```text
invalid config for network bridge:
network-scoped aliases are only supported for user-defined networks
```


```

## Security Notes

- Keep `backend/.env` out of version control.
- Never commit database passwords, RabbitMQ passwords, tokens, or production secrets.
- Use strong, unique credentials and rotate any credentials that have been exposed.
- Restrict access to database and RabbitMQ management ports as appropriate for your environment.
- Before publishing the repository, inspect the staged files and Git history for secrets.

## Future Enhancements

Potential next steps, depending on project requirements:

- Add end-to-end health checks for the API, database, and message broker.
- Add integration tests for telemetry ingestion and alert workflows.
- Document concrete API endpoints and request/response examples from the implemented routes.
- Add structured logs, metrics, and distributed tracing for the platform itself.
- Add deployment-specific configuration and CI checks.
- Validate container startup and service connectivity before declaring the deployment ready.
