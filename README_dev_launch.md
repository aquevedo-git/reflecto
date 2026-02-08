# Reflecto Developer Launch

## Quick Start

To launch the full Reflecto stack for development:

```
make dev
```

or

```
./run_reflecto.sh start
```

## Available Commands

- `make dev` / `./run_reflecto.sh start` — Start dev environment
- `make stop` / `./run_reflecto.sh stop` — Stop containers
- `make rebuild` / `./run_reflecto.sh rebuild` — Rebuild containers
- `make logs` / `./run_reflecto.sh logs` — Show logs
- `make cleanup` / `./run_reflecto.sh cleanup` — Remove containers and prune Docker

## Requirements

- Docker installed
- .env file in project root

## Service URLs

- Backend: http://localhost:8000
- Frontend: http://localhost:8080

## Troubleshooting

- If Docker is not installed, install it from [docker.com](https://www.docker.com/).
- If .env is missing, copy `.env.example` or create your own.

## Clean Architecture

This launch process keeps backend and frontend containers cleanly separated.
