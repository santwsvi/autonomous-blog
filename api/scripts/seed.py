"""Seed script — populates the database with initial data."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings  # noqa: E402
from app.db.session import async_session  # noqa: E402
from app.models.post import Post, PostStatus  # noqa: E402


SEED_POST = {
    "title": "Bem-vindo ao Blog Autônomo",
    "slug": "bem-vindo",
    "excerpt": "O primeiro post do blog — gerado e mantido com ajuda de IA multiagente.",
    "content_mdx": """# Bem-vindo ao Blog Autônomo

Este blog é um experimento em geração de conteúdo assistida por IA.

## Como funciona

O conteúdo é gerado por um pipeline de 5 agentes de IA que trabalham em sequência:

1. **Researcher** — pesquisa contexto sobre o tema
2. **Writer** — redige o rascunho do artigo
3. **Editor** — revisa, pontua e pede correções se necessário
4. **SEO Optimizer** — gera metadata otimizada
5. **Publisher** — sanitiza e formata o conteúdo final

O autor humano mantém controle editorial — todo post gerado é revisado antes de ser publicado.

## Stack

- **Frontend**: Next.js 16 + shadcn/ui
- **Backend**: FastAPI + PostgreSQL
- **IA**: LangGraph + OpenAI API
- **Busca**: pgvector (busca semântica)

Boa leitura!
""",
    "tags": ["blog", "ia", "boas-vindas"],
    "category": "geral",
    "language": "pt-BR",
    "featured": True,
}


async def seed():
    async with async_session() as db:
        from sqlalchemy import select

        # Check if seed post already exists
        result = await db.execute(select(Post).where(Post.slug == SEED_POST["slug"]))
        if result.scalar_one_or_none():
            print(f"Seed post '{SEED_POST['slug']}' already exists, skipping.")
            return

        post = Post(
            title=SEED_POST["title"],
            slug=SEED_POST["slug"],
            excerpt=SEED_POST["excerpt"],
            content_mdx=SEED_POST["content_mdx"],
            tags=SEED_POST["tags"],
            category=SEED_POST["category"],
            language=SEED_POST["language"],
            featured=SEED_POST["featured"],
            status=PostStatus.PUBLISHED,
            word_count=len(SEED_POST["content_mdx"].split()),
            reading_time_minutes=1,
        )
        db.add(post)
        await db.commit()
        print(f"Seed post '{SEED_POST['title']}' created and published.")


if __name__ == "__main__":
    asyncio.run(seed())
