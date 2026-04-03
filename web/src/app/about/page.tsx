import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About",
  description: "Sobre Victor Gabriel — engenheiro de software, arquiteto e entusiasta de IA.",
};

export default function AboutPage() {
  return (
    <article className="container mx-auto max-w-3xl px-4 md:px-8 py-8">
      <div className="flex flex-col sm:flex-row gap-8 items-start mb-12">
        <div className="shrink-0">
          <div className="w-32 h-32 rounded-full bg-muted flex items-center justify-center text-4xl font-bold text-muted-foreground">
            VG
          </div>
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight md:text-4xl mb-2">
            Victor Gabriel
          </h1>
          <p className="text-lg text-muted-foreground mb-4">
            Engenheiro de Software &middot; Arquiteto &middot; Segurança
          </p>
          <div className="flex gap-3">
            <SocialLink href="https://github.com/santwsvi" label="GitHub">
              <GithubIcon />
            </SocialLink>
            <SocialLink href="https://linkedin.com/in/" label="LinkedIn">
              <LinkedinIcon />
            </SocialLink>
          </div>
        </div>
      </div>

      <div className="prose prose-neutral dark:prose-invert max-w-none">
        <p>
          Engenheiro de software com foco em arquitetura de sistemas, segurança e
          inteligência artificial aplicada. Trabalho com tecnologia há anos e escrevo
          sobre o que aprendo no caminho.
        </p>

        <h2>Sobre este blog</h2>
        <p>
          Este blog é um experimento em geração de conteúdo assistida por IA. Os artigos
          são produzidos por um pipeline de 5 agentes de IA (Researcher, Writer, Editor,
          SEO Optimizer e Publisher) orquestrados por LangGraph, com revisão e aprovação
          humana antes da publicação.
        </p>
        <p>
          A stack por trás: Next.js 16, FastAPI, PostgreSQL com pgvector pra busca
          semântica, e OpenAI API como LLM provider. O código é open source.
        </p>

        <h2>Stack técnica</h2>
        <ul>
          <li><strong>Frontend</strong>: Next.js 16, shadcn/ui, Tailwind CSS</li>
          <li><strong>Backend</strong>: FastAPI, SQLAlchemy, Pydantic v2</li>
          <li><strong>IA</strong>: LangGraph, OpenAI API (gpt-4o-mini + gpt-4o)</li>
          <li><strong>Database</strong>: PostgreSQL + pgvector</li>
          <li><strong>Cache</strong>: Redis</li>
        </ul>

        <h2>Contato</h2>
        <p>
          A melhor forma de entrar em contato é pelo{" "}
          <a href="https://github.com/santwsvi" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>.
        </p>
      </div>
    </article>
  );
}

function SocialLink({ href, label, children }: { href: string; label: string; children: React.ReactNode }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" aria-label={label}
      className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors">
      {children}
    </a>
  );
}

function GithubIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
    </svg>
  );
}

function LinkedinIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
    </svg>
  );
}
