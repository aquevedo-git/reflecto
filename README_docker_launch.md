## 🚀 Local Development with Docker Compose

Reflecto provides a one-command local development environment using Docker Compose.

### Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/) installed

### Quick Start

1. **Clone the repository** (if you haven't already):

   ```sh
   git clone https://github.com/your-org/reflecto.git
   cd reflecto
   ```

2. **Build and launch the full stack:**

   ```sh
   docker-compose up --build
   ```

   - The backend (FastAPI) will be available at [http://localhost:8000](http://localhost:8000)
   - The frontend (static site) will be available at [http://localhost:8080](http://localhost:8080)

3. **Hot Reloading:**
   - Backend code changes will auto-reload (via Uvicorn `--reload`).
   - For frontend changes, restart the frontend container if needed.

4. **Stopping the stack:**

   ```sh
   docker-compose down
   ```

### Notes

- The frontend is served via a static server and proxies `/api` requests to the backend.
- For production, adjust Dockerfiles and Compose as needed for security and performance.

---

For troubleshooting, see the [docs/](docs/) directory or open an issue.
