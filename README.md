
# SkinIntel

## Local frontend development

Run `npm i` to install dependencies.

Run `npm run dev` to start the Vite app.

## Dockerized setup

This repository includes complete Docker support for frontend and backend.

### Services

- `frontend` (Vite build served by Nginx) on `http://localhost:5173`
- `backend` (Flask via Gunicorn) on `http://localhost:5000`

### Run with Docker Compose

1. Optional: copy `.env.example` to `.env` and customize values.
2. Build and start all services:

If your machine supports Docker Compose plugin:

docker compose up --build

If your machine uses standalone Docker Compose:

docker-compose up --build

### Useful checks

- Backend health check: `http://localhost:5000/health`

### Stop services

Plugin variant:

docker compose down

Standalone variant:

docker-compose down
  