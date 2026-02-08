#!/bin/sh

set -e

# Cross-platform echo
cecho() {
  printf "\033[1;32m%s\033[0m\n" "$1"
}

# Validate Docker
if ! command -v docker >/dev/null 2>&1; then
  cecho "[ERROR] Docker is not installed. Please install Docker and try again."
  exit 1
fi

# Validate .env
if [ ! -f .env ]; then
  cecho "[ERROR] .env file not found in project root. Please create it before starting."
  exit 1
fi

case "$1" in
  start|dev)
    cecho "Launching Reflecto dev environment..."
    docker compose -f docker-compose.dev.yml up --build -d
    cecho "Backend: http://localhost:8000"
    cecho "Frontend: http://localhost:8080"
    cecho "View logs: make logs or ./run_reflecto.sh logs"
    ;;
  stop)
    cecho "Stopping Reflecto containers..."
    docker compose -f docker-compose.dev.yml down
    ;;
  rebuild)
    cecho "Rebuilding Reflecto containers..."
    docker compose -f docker-compose.dev.yml build --no-cache
    ;;
  logs)
    cecho "Showing Reflecto logs..."
    docker compose -f docker-compose.dev.yml logs -f
    ;;
  cleanup)
    cecho "Cleaning up Docker resources..."
    docker compose -f docker-compose.dev.yml down --remove-orphans
    docker system prune -f
    ;;
  *)
    cecho "Usage: ./run_reflecto.sh [start|stop|rebuild|logs|cleanup]"
    exit 1
    ;;
esac
