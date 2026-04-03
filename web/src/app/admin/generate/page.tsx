"use client";

import { useState, useEffect, useRef } from "react";
import { useAdminAuth } from "@/hooks/use-admin-auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminGeneratePage() {
  const { token, isReady, fetchWithAuth } = useAdminAuth();
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState<string[]>([]);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  const progressRef = useRef<HTMLDivElement>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    progressRef.current?.scrollTo(0, progressRef.current.scrollHeight);
  }, [progress]);

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const handleGenerate = async () => {
    if (!token || !prompt.trim()) return;
    setGenerating(true);
    setProgress([]);
    setResult(null);
    setError("");

    try {
      const res = await fetchWithAuth(`${API_URL}/api/v1/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        setError(res.status === 401 ? "Sessão expirada. Faça login novamente." : "Falha ao iniciar geração.");
        setGenerating(false);
        return;
      }

      const { job_id } = await res.json();
      setProgress((p) => [...p, "Geração iniciada..."]);

      pollRef.current = setInterval(async () => {
        try {
          const statusRes = await fetch(`${API_URL}/api/v1/generate/${job_id}`);
          if (!statusRes.ok) return;
          const data = await statusRes.json();

          if (data.status === "completed") {
            if (pollRef.current) clearInterval(pollRef.current);
            pollRef.current = null;
            setResult(data);
            setProgress((p) => [...p, "Artigo gerado com sucesso!"]);
            setGenerating(false);
          } else if (data.status === "failed") {
            if (pollRef.current) clearInterval(pollRef.current);
            pollRef.current = null;
            setError(data.error_message || "Geração falhou.");
            setGenerating(false);
          } else if (data.status === "running") {
            setProgress((p) => {
              const last = p[p.length - 1];
              if (last !== "Processando...") return [...p, "Processando..."];
              return p;
            });
          }
        } catch {
          // Polling error — continue
        }
      }, 5000);
    } catch {
      setError("Erro de conexão.");
      setGenerating(false);
    }
  };

  if (!isReady) return null;
  if (!token) return <p className="text-muted-foreground">Faça login na aba Overview primeiro.</p>;

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Gerar Artigo com IA</h2>

      <div className="max-w-2xl space-y-4">
        <div>
          <label className="text-sm font-medium mb-1 block">Sobre o que escrever?</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ex: Escreva sobre como implementar autenticação JWT segura em FastAPI..."
            rows={4}
            className="w-full rounded-md border px-3 py-2 text-sm bg-background resize-none"
            disabled={generating}
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating || !prompt.trim()}
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {generating ? "Gerando..." : "Gerar Artigo"}
        </button>

        {progress.length > 0 && (
          <div ref={progressRef} className="rounded-md border p-4 max-h-48 overflow-y-auto bg-muted/30">
            {progress.map((msg, i) => (
              <p key={i} className="text-sm text-muted-foreground">{msg}</p>
            ))}
          </div>
        )}

        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {result && (
          <div className="rounded-md border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-900/20">
            <p className="text-sm font-medium text-green-700 dark:text-green-300">Artigo gerado!</p>
            <p className="text-sm text-green-600 dark:text-green-400 mt-1">
              Score: {(result.quality_scores as Record<string, number>)?.overall?.toFixed(2) || "—"} |
              Iterações: {String(result.iterations)} |
              Duração: {String(result.duration_seconds)}s
            </p>
            <a href="/admin/posts" className="text-sm text-green-600 underline mt-2 inline-block dark:text-green-400">
              Ver nos posts
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
