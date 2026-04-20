# Autonomous Blog

Personal technical blog with multi-agent AI-assisted content generation.

## Architecture

```
┌──────────────────┐     REST + SSE     ┌──────────────────┐
│    Next.js 16     │◄──────────────────►│     FastAPI       │
│    (Vercel)       │                    │    (Railway)      │
│                   │                    │                   │
│  Blog Feed (ISR)  │                    │  Posts CRUD       │
│  Post Page (SSG)  │                    │  Auth JWT         │
│  Admin Dashboard  │                    │  LangGraph Agent  │
│  Cmd+K Search     │                    │  SSE Streaming    │
└──────────────────┘                    └────────┬──────────┘
                                                 │
                                    ┌────────────┼────────────┐
                                    │            │            │
                               PostgreSQL    Redis      OpenAI API
                               (posts,      (cache,    (gpt-4o-mini
                                jobs)        queue)     gpt-4o)
```

### Generation Pipeline (LangGraph)

```
Researcher (gpt-4o-mini)
    → Writer (gpt-4o-mini)
    → Editor (gpt-4o) — scoring 5 dimensões
        ↑ score < 0.85? loop (max 3x)
    → SEO Optimizer (gpt-4o-mini)
    → Publisher (deterministic — sanitized MDX)
    → Saved post for draft → writer approves
```

## Stack

| Layer | Technology | Coust/month |
|--------|-----------|-----------|
| Frontend | Next.js 16 + shadcn/ui + Tailwind | $0 (Vercel Hobby) |
| Backend | FastAPI + Pydantic v2 + SQLAlchemy async | $5 (Railway Hobby) |
| IA | LangGraph 1.x + OpenAI API | ~$3 |
| Database | PostgreSQL 16 | Incl. Railway |
| Cache | Redis 7 (Upstash free) | $0 |
| **Total** | | **~$8/month** |

## Local Setup

### Pre-requirements

- Python 3.13+ and [uv](https://docs.astral.sh/uv/)
- Node.js 20+ and npm
- PostgreSQL 16
- Redis 7
- (Optional) Podman or Docker

### Backend

```bash
cd api
cp .env.example .env
# Edit .env with your own credentials (OPENAI_API_KEY, ADMIN_PASSWORD_HASH, etc)

# With Podman/Docker (PostgreSQL + Redis)
make infra

# Use local PG/Redis to adjust DATABASE_URL and REDIS_URL at .env

# Migrations
make migrate

# API run (porta 8000)
make dev
```

### Frontend

```bash
cd web
cp .env.example .env.local

# Install dependencies
npm install

# Run dev server (porta 3000)
npm run dev
```

### Generate an article

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@blog.com","password":"YOUR_PASSWORD"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Generate
curl -s -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt": "Write about X"}' | python3 -m json.tool

# Progress accomplishment (change JOB_ID)
curl -N http://localhost:8000/api/v1/generate/JOB_ID/stream \
  -H "Authorization: Bearer $TOKEN"
```

## Project Structure

```
autonomous-blog/
├── api/                        # FastAPI backend
│   ├── app/
│   │   ├── agents/             # LangGraph pipeline
│   │   │   ├── nodes/          # Researcher, Writer, Editor, SEO, Publisher
│   │   │   ├── prompts/        # Versioned prompts (.md)
│   │   │   ├── graph.py        # StateGraph definition
│   │   │   └── state.py        # AgentState (Pydantic)
│   │   ├── api/                # FastAPI routes
│   │   │   ├── auth.py         # JWT login/refresh
│   │   │   ├── v1/posts.py     # CRUD posts
│   │   │   └── v1/generate.py  # Geração + SSE streaming
│   │   ├── models/             # SQLAlchemy ORM
│   │   ├── repositories/       # Data access layer
│   │   ├── schemas/            # Pydantic request/response
│   │   ├── services/           # Business logic
│   │   └── middleware/         # CORS, security headers
│   ├── Makefile
│   └── docker-compose.dev.yml
│
├── web/                        # Next.js 16 frontend
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   ├── components/         # UI components
│   │   └── lib/api/            # API client tipado
│   └── next.config.ts          # Security headers
│
└── README.md
```

## Roadmap

- [x] **Phase 1** — Foundation (FastAPI, Next.js, Auth, CRUD, SEO)
- [x] **Phase 2** — AI Core (LangGraph, 5 agentes, quality scoring, SSE streaming)
- [x] **Phase 3** — RAG + Search (pgvector, busca semântica, Cmd+K, tags)
- [x] **Phase 4** — Observability + Admin (Sentry, structlog, metrics, dashboard funcional)
- [x] **Phase 5** — Final Polish (RSS, OG images, multi-language, seed, cleanup)

## Security

- JWT with refresh token rotation + Redis blocklist
- Security headers: HSTS, X-Frame-Options, CSP, Referrer-Policy
- Sanitized MDX: strip script/iframe/event handlers/frontmatter
- HMAC-SHA256 no webhook ISR
- Rate limiting for IP (slowapi)
- Enums PostgreSQL + Constraints check
- Secrets for each environment variable (NEVER in the code)

## Licença

Personal project. All rights reserved.
