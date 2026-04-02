# Security Policy

## Reporting

Se encontrar uma vulnerabilidade, **não abra issue pública**.
Entre em contato diretamente pelo email no perfil do GitHub.

## Práticas implementadas

- JWT com expiração curta (15min access) + refresh token rotation
- Bcrypt para hashing de senhas
- HMAC-SHA256 para webhook signatures
- Security headers (HSTS, X-Frame-Options, CSP, X-Content-Type-Options)
- Rate limiting por IP
- MDX sanitizado (allowlist approach)
- PostgreSQL ENUMs + CHECK constraints
- Secrets exclusivamente via variáveis de ambiente
- Nenhum secret commitado no repositório

## Ambiente de desenvolvimento

- `LLM_SSL_VERIFY=false` existe para ambientes com proxy corporativo (Zscaler)
- **Nunca** usar `LLM_SSL_VERIFY=false` em produção
- `DEBUG=true` habilita Swagger UI — desabilitar em produção
