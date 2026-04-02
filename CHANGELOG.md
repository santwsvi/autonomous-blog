# Changelog

Todas as mudanças notáveis do projeto serão documentadas aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [0.2.0] — Em desenvolvimento

### Fase 3 — RAG + Search
- (em breve)

## [0.1.0] — 2026-04-02

### Fase 1 — Fundação
#### Adicionado
- **Backend (FastAPI)**: config, structlog, health check, global exception handler
- **Auth JWT**: login, refresh com rotation, Redis blocklist, middleware
- **Security**: CORS allowlist, rate limiting (slowapi), headers (HSTS, X-Frame, CSP, Referrer-Policy)
- **Database**: PostgreSQL com ENUMs (`post_status`, `job_status`), CHECK constraints, Alembic migrations (raw SQL)
- **Posts API**: CRUD completo com repository layer, Pydantic schemas, paginação, filtros
- **Webhook ISR**: HMAC-SHA256 com `timingSafeEqual`
- **Frontend (Next.js 16)**: App Router, shadcn/ui, dark/light mode, Geist fonts
- **Blog**: feed com PostCard (ISR 60s), post page com ReactMarkdown + remark-gfm
- **SEO**: sitemap dinâmico, robots.txt, metadata Open Graph, `generateStaticParams`
- **Error boundaries**: global, por route, por post individual
- **Admin**: layout com navegação (shell para fases futuras)
- **Infra**: Makefile, docker-compose (PG + Redis), `.env.example`

### Fase 2 — IA Core
#### Adicionado
- **LangGraph StateGraph**: 5 nós (Researcher → Writer → Editor → SEO Optimizer → Publisher)
- **Self-reflection loop**: Editor com scoring de 5 dimensões, threshold 0.85, max 3 iterações
- **LLM service**: wrapper sobre OpenAI SDK com usage tracking
- **Publisher**: sanitização MDX (strip script, iframe, event handlers, frontmatter, markdown wrapper)
- **SSE streaming**: progresso de geração em tempo real por job
- **Prompt versioning**: SHA-256 hash salvo em `generation_jobs.prompt_versions`
- **Generation service**: orquestração do pipeline + persistência no banco

#### Corrigido (review pós-implementação)
- Pipeline rodava 2x (astream + ainvoke) — corrigido para acumular estado do astream
- `_merge_usage` duplicada em 4 nodes — extraída para `agents/utils.py`
- `prompt_versions` calculadas mas nunca salvas — propagadas e persistidas
- `AgentState` rejeitava campos extras do LangGraph — adicionado `extra="ignore"`
- SSL verify atrelado a `DEBUG` — separado em `LLM_SSL_VERIFY`
- Import inline no `auth.py` — movido para topo do módulo
- SEO Optimizer recebia 500 chars — aumentado para 1500
- `rehype-raw` instalado mas não usado — removido
- Slug collision na geração — `_ensure_unique_slug` com suffix incremental

