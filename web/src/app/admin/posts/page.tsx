"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Post {
  id: string;
  title: string;
  slug: string;
  status: string;
  tags: string[];
  created_at: string;
}

export default function AdminPostsPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setToken(localStorage.getItem("admin_token"));
    setMounted(true);
  }, []);

  const fetchPosts = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/posts?per_page=50`);
      if (res.ok) {
        const data = await res.json();
        setPosts(data.items);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mounted) fetchPosts();
  }, [mounted]);

  const updateStatus = async (postId: string, status: string) => {
    if (!token) return;
    await fetch(`${API_URL}/api/v1/posts/${postId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ status }),
    });
    fetchPosts();
  };

  const deletePost = async (postId: string) => {
    if (!token || !confirm("Tem certeza que deseja deletar este post?")) return;
    await fetch(`${API_URL}/api/v1/posts/${postId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    fetchPosts();
  };

  if (!mounted) return null;

  if (!token) {
    return (
      <p className="text-muted-foreground">
        Faça login na aba Overview primeiro.
      </p>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Gerenciar Posts</h2>

      {loading ? (
        <p className="text-muted-foreground">Carregando...</p>
      ) : posts.length === 0 ? (
        <p className="text-muted-foreground">Nenhum post encontrado.</p>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left p-3 font-medium">Título</th>
                <th className="text-left p-3 font-medium">Status</th>
                <th className="text-left p-3 font-medium">Tags</th>
                <th className="text-left p-3 font-medium">Ações</th>
              </tr>
            </thead>
            <tbody>
              {posts.map((post) => (
                <tr key={post.id} className="border-t">
                  <td className="p-3 font-medium max-w-xs truncate">
                    {post.title}
                  </td>
                  <td className="p-3">
                    <Badge
                      variant={
                        post.status === "published" ? "default" : "secondary"
                      }
                    >
                      {post.status}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <div className="flex gap-1 flex-wrap">
                      {post.tags.slice(0, 3).map((t) => (
                        <Badge key={t} variant="outline" className="text-xs">
                          {t}
                        </Badge>
                      ))}
                    </div>
                  </td>
                  <td className="p-3">
                    <div className="flex gap-2">
                      {post.status === "draft" ? (
                        <button
                          onClick={() => updateStatus(post.id, "published")}
                          className="text-xs text-green-600 hover:underline dark:text-green-400"
                        >
                          Publicar
                        </button>
                      ) : (
                        <button
                          onClick={() => updateStatus(post.id, "draft")}
                          className="text-xs text-yellow-600 hover:underline dark:text-yellow-400"
                        >
                          Despublicar
                        </button>
                      )}
                      <button
                        onClick={() => deletePost(post.id)}
                        className="text-xs text-red-600 hover:underline dark:text-red-400"
                      >
                        Deletar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
