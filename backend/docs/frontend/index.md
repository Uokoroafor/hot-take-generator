# Frontend Overview

The React/Vite frontend (inside `frontend/`) communicates with the backend via the `/api` routes defined in FastAPI. While this documentation site focuses on the Python backend, here are the essentials for working with the UI:

- **Stack**: React 19 + TypeScript + Vite + Vitest. Styling is handled via modern CSS with gradients/animations.
- **Environment**: Configure `frontend/.env` (and `.env.example`) with `VITE_API_BASE_URL` to point to your running backend (default `http://localhost:8000`).
- **Development**: `npm install` then `npm run dev` to start the Vite dev server on port 5173.
- **Testing**: Run `npm run test` to execute the Vitest suite, which is configured with `frontend/src/test/setup.ts`.
- **Docker**: The root `docker-compose.yml` contains a `frontend` service wired to the backend container for both dev and prod overrides.

For deeper information, see the root `README.md` and inline comments within the frontend repository.
