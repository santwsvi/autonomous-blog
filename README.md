# Autonomous Blog

Blog pessoal técnico com geração de conteúdo assistida por IA multiagente.

## Arquitetura

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

### Pipeline de Geração (LangGraph)

```
Researcher (gpt-4o-mini)
    → Writer (gpt-4o-mini)
    → Editor (gpt-4o) — scoring 5 dimensões
        ↑ score < 0.85? loop (max 3x)
    → SEO Optimizer (gpt-4o-mini)
    → Publisher (determinístico — sanitiza MDX)
    → Post salvo como draft → autor aprova
```

## Stack

| Camada | Tecnologia | Custo/mês |
|--------|-----------|-----------|
| Frontend | Next.js 16 + shadcn/ui + Tailwind | $0 (Vercel Hobby) |
| Backend | FastAPI + Pydantic v2 + SQLAlchemy async | $5 (Railway Hobby) |
| IA | LangGraph 1.x + OpenAI API | ~$3 |
| Database | PostgreSQL 16 | Incl. Railway |
| Cache | Redis 7 (Upstash free) | $0 |
| **Total** | | **~$8/mês** |

## Setup Local

### Pré-requisitos

- Python 3.13+ e [uv](https://docs.astral.sh/uv/)
- Node.js 20+ e npm
- PostgreSQL 16
- Redis 7
- (Opcional) Podman ou Docker

### Backend

```bash
cd api
cp .env.example .env
# Editar .env com suas credenciais (OPENAI_API_KEY, ADMIN_PASSWORD_HASH, etc)

# Com Podman/Docker (PostgreSQL + Redis)
make infra

# Ou usar PG/Redis locais e ajustar DATABASE_URL e REDIS_URL no .env

# Migrations
make migrate

# Rodar API (porta 8000)
make dev
```

### Frontend

```bash
cd web
cp .env.example .env.local

# Instalar dependências
npm install

# Rodar dev server (porta 3000)
npm run dev
```

### Gerar um artigo

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@blog.com","password":"SUA_SENHA"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Disparar geração
curl -s -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt": "Escreva sobre X"}' | python3 -m json.tool

# Acompanhar progresso (substituir JOB_ID)
curl -N http://localhost:8000/api/v1/generate/JOB_ID/stream \
  -H "Authorization: Bearer $TOKEN"
```

## Estrutura do Projeto

```
autonomous-blog/
├── api/                        # FastAPI backend
│   ├── app/
│   │   ├── agents/             # LangGraph pipeline
│   │   │   ├── nodes/          # Researcher, Writer, Editor, SEO, Publisher
│   │   │   ├── prompts/        # Prompts versionados (.md)
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

- [x] **Fase 1** — Fundação (FastAPI, Next.js, Auth, CRUD, SEO, Deploy config)
- [x] **Fase 2** — IA Core (LangGraph, 5 agentes, quality scoring, SSE streaming)
- [ ] **Fase 3** — RAG + Search (embeddings, busca semântica, Cmd+K)
- [ ] **Fase 4** — Observability (Prometheus, LangSmith, Sentry, OAuth2)
- [ ] **Fase 5** — Features Avançadas (geração agendada, multi-idioma, RSS, OG images)

## Segurança

- JWT com refresh token rotation + Redis blocklist
- Security headers: HSTS, X-Frame-Options, CSP, Referrer-Policy
- MDX sanitizado: strip script/iframe/event handlers/frontmatter
- HMAC-SHA256 no webhook ISR
- Rate limiting por IP (slowapi)
- Enums PostgreSQL + CHECK constraints
- Secrets em variáveis de ambiente (nunca no código)

## Licença

Projeto pessoal. Todos os direitos reservados.
