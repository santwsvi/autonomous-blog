"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Metrics {
  posts: { total: number; by_status: Record<string, number> };
  generations: {
    total: number;
    completed: number;
    failed: number;
    avg_duration_seconds: number | null;
    avg_quality_score: number | null;
  };
  llm: { total_cost_usd: number };
  embeddings: { total_chunks: number };
  recent_generations: Array<{
    id: string;
    prompt: string;
    status: string;
    quality_score: number | null;
    duration_seconds: number | null;
    post_title: string | null;
    post_slug: string | null;
    created_at: string | null;
  }>;
}

export default function AdminPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState("");
  const [token, setToken] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setToken(localStorage.getItem("admin_token"));
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    if (!token) {
      setError("Faça login primeiro.");
      return;
    }
    fetch(`${API_URL}/api/v1/metrics`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => (r.ok ? r.json() : Promise.reject("Unauthorized")))
      .then(setMetrics)
      .catch(() => setError("Erro ao carregar métricas. Verifique o login."));
  }, [token, mounted]);

  if (!mounted) return null;

  if (error) {
    return (
      <div>
        <p className="text-muted-foreground">{error}</p>
        <LoginForm onSuccess={() => window.location.reload()} />
      </div>
    );
  }

  if (!metrics) {
    return <p className="text-muted-foreground">Carregando...</p>;
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Dashboard</h2>

      <div className="grid gap-4 md:grid-cols-4 mb-8">
        <StatCard label="Posts" value={metrics.posts.total} />
        <StatCard
          label="Publicados"
          value={metrics.posts.by_status?.published || 0}
        />
        <StatCard
          label="Gerações"
          value={`${metrics.generations.completed}/${metrics.generations.total}`}
        />
        <StatCard
          label="Custo LLM"
          value={`$${metrics.llm.total_cost_usd.toFixed(3)}`}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-3 mb-8">
        <StatCard
          label="Score médio"
          value={
            metrics.generations.avg_quality_score
              ? metrics.generations.avg_quality_score.toFixed(2)
              : "—"
          }
        />
        <StatCard
          label="Tempo médio"
          value={
            metrics.generations.avg_duration_seconds
              ? `${metrics.generations.avg_duration_seconds.toFixed(0)}s`
              : "—"
          }
        />
        <StatCard label="Embeddings" value={metrics.embeddings.total_chunks} />
      </div>

      <h3 className="text-lg font-semibold mb-3">Gerações recentes</h3>
      {metrics.recent_generations.length > 0 ? (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left p-3 font-medium">Prompt</th>
                <th className="text-left p-3 font-medium">Status</th>
                <th className="text-left p-3 font-medium">Score</th>
                <th className="text-left p-3 font-medium">Duração</th>
              </tr>
            </thead>
            <tbody>
              {metrics.recent_generations.map((g) => (
                <tr key={g.id} className="border-t">
                  <td className="p-3 max-w-xs truncate">{g.prompt}</td>
                  <td className="p-3">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                        g.status === "completed"
                          ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                          : g.status === "failed"
                            ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                            : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
                      }`}
                    >
                      {g.status}
                    </span>
                  </td>
                  <td className="p-3">
                    {g.quality_score ? g.quality_score.toFixed(2) : "—"}
                  </td>
                  <td className="p-3">
                    {g.duration_seconds ? `${g.duration_seconds}s` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-muted-foreground">Nenhuma geração registrada.</p>
      )}
    </div>
  );
}

function StatCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-lg border p-6">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
  );
}

function LoginForm({ onSuccess }: { onSuccess: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("admin_token", data.access_token);
        onSuccess();
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-4 max-w-sm space-y-3">
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full rounded-md border px-3 py-2 text-sm bg-background"
      />
      <input
        type="password"
        placeholder="Senha"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full rounded-md border px-3 py-2 text-sm bg-background"
      />
      <button
        type="submit"
        disabled={loading}
        className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
      >
        {loading ? "Entrando..." : "Entrar"}
      </button>
    </form>
  );
}
