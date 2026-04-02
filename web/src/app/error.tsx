"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Global error:", error);
  }, [error]);

  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 px-4">
      <h2 className="text-2xl font-bold">Algo deu errado</h2>
      <p className="text-muted-foreground text-center max-w-md">
        Ocorreu um erro inesperado. Tente recarregar a página.
      </p>
      <button
        onClick={reset}
        className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
      >
        Tentar novamente
      </button>
    </div>
  );
}
