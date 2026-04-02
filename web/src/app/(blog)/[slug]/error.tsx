"use client";

import Link from "next/link";

export default function PostError({ reset }: { reset: () => void }) {
  return (
    <div className="container mx-auto max-w-3xl px-4 md:px-8 py-8">
      <div className="flex flex-col items-center justify-center gap-4 min-h-[40vh]">
        <h2 className="text-2xl font-bold">Erro ao carregar o post</h2>
        <p className="text-muted-foreground text-center">
          Ocorreu um problema ao carregar este conteúdo.
        </p>
        <div className="flex gap-3">
          <button
            onClick={reset}
            className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
          >
            Tentar novamente
          </button>
          <Link
            href="/"
            className="rounded-md border px-4 py-2 text-sm hover:bg-accent"
          >
            Voltar ao blog
          </Link>
        </div>
      </div>
    </div>
  );
}
