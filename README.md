# pHera FastAPI BFF

FastAPI-based **Backend-for-Frontend (BFF) microservice** used in the pHera architecture.

This service acts as a dedicated integration layer between the application backend and the AI / RAG processing services.

The microservice is designed to be reusable across multiple pHera projects, including:

- Project 1 (Beta)
- Project 2 (MVP)
- future pHera products

Keeping the AI integration logic in a separate service allows the platform to scale and evolve without coupling AI logic to the main backend.

---

# Architecture

High-level architecture:

Frontend  
↓  
Node Backend / API Layer  
↓  
FastAPI BFF Service  
↓  
RAG / AI Backend  

The FastAPI service acts as a gateway to the AI backend and handles:

- request forwarding
- authentication validation
- API key management
- user context forwarding

---

# Current Scope

The service currently provides the following endpoints:

## Always available

- `GET /health` — health check endpoint
- `POST /api/analyze` — forwards analysis requests to the RAG backend

## MVP-only routes

- `POST /auth/dev-token` — local development JWT generator
- `GET /api/me` — returns authenticated user information
- `POST /scans` — creates a scan history item
- `GET /history` — retrieves scan history
- `GET /trends` — provides basic trend statistics

---

# BFF Request Flow

## Beta mode

`Frontend / Node Backend → FastAPI BFF → RAG beta backend`

Behavior:

- no persistence
- no user-specific storage
- no auth headers sent to RAG
- request body forwarded directly

## MVP mode

`Frontend / Node Backend → FastAPI BFF → RAG backend`

Behavior:

- validates JWT on the BFF side
- sends `X-API-Key` header to the RAG service
- sends `X-User-Id` when an authenticated user exists
- persistence routes are enabled

The same codebase supports both modes through configuration.

---

# Environment Configuration

Configuration values are defined in the `.env` file.

Important environment variables:

- `DATABASE_URL`
- `ZITADEL_ISSUER`
- `ZITADEL_AUDIENCE`
- `DEV_JWT_SECRET`
- `CORS_ORIGINS`
- `DEPLOYMENT_MODE`
- `RAG_BASE_URL`
- `RAG_API_KEY`

`DEPLOYMENT_MODE` controls the runtime behavior:

- `beta` → proxy-only mode
- `mvp` → authenticated + persistence-enabled mode

---

# Local Development

Run the service locally using Docker:

```bash
docker compose up --build
```

After startup the service will be available at:

`http://localhost:8000`

Swagger API documentation:

`http://localhost:8000/docs`

---

# Example Analyze Request

Example payload sent to `/api/analyze`:

```json
{
  "ph_value": 4.5,
  "age": 30,
  "diagnoses": [],
  "symptoms": {
    "vulva_vagina": ["itching"]
  }
}
```

The request will be forwarded to the configured RAG backend.

---

# Repository Purpose

This repository contains the FastAPI AI integration microservice used within the pHera platform architecture.

The service is intentionally separated from the main backend so that it can be reused across multiple projects.

Benefits of this approach:

- reusable AI service layer
- independent deployment
- easier scaling
- flexible architecture evolution

---

# Status

Current stage: MVP / Beta-ready development.

Planned improvements:

- improved request validation
- logging and monitoring
- rate limiting
- improved authentication flow
- production deployment configuration
