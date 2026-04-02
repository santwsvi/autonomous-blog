# Contributing

## Branch Strategy

**Trunk-based development** — `main` é o trunk, sempre deployável.

```
main ← feat/xxx (curta duração, merge fast-forward)
     ← fix/xxx
     ← chore/xxx
```

## Commits

**Conventional Commits** em português (exceto o prefixo):

```
feat(api): adicionar endpoint de busca semântica
fix(web): corrigir rendering de code blocks no dark mode
refactor(api): extrair lógica de slug para util
chore: atualizar dependências
docs: adicionar diagrama de sequência da geração
test(api): adicionar testes do editor parser
```

### Escopos válidos

- `api` — backend FastAPI
- `web` — frontend Next.js
- `agents` — pipeline LangGraph
- (sem escopo) — mudanças transversais

## Tags e Releases

Versionamento semântico: `vX.Y.Z`

- **Major** (X): breaking changes na API ou arquitetura
- **Minor** (Y): nova fase ou feature significativa
- **Patch** (Z): fixes e melhorias incrementais

```bash
git tag -a v0.1.0 -m "Fase 1 + 2: fundação + IA core"
git push origin v0.1.0
```

## Código

- **Backend**: `ruff check` + `ruff format` (config em `api/ruff.toml`)
- **Frontend**: `eslint` + `prettier` (via eslint-config-next)
- Rodar antes de commitar: `cd api && make lint` e `cd web && npm run lint`
