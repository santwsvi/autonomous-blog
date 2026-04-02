const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  token?: string;
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, headers: customHeaders, ...rest } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((customHeaders as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    headers,
    ...rest,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// --- Types ---

export interface PostListItem {
  id: string;
  title: string;
  slug: string;
  excerpt: string | null;
  status: string;
  tags: string[];
  category: string | null;
  reading_time_minutes: number | null;
  language: string;
  featured: boolean;
  published_at: string | null;
  created_at: string;
}

export interface PostListPaginated {
  items: PostListItem[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface Post extends PostListItem {
  content_mdx: string;
  quality_score: number | null;
  seo_meta: Record<string, string> | null;
  word_count: number | null;
  updated_at: string;
}

// --- Public endpoints ---

export async function getPosts(params?: {
  page?: number;
  per_page?: number;
  status?: string;
  tag?: string;
}): Promise<PostListPaginated> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.per_page) searchParams.set("per_page", String(params.per_page));
  if (params?.status) searchParams.set("status", params.status);
  if (params?.tag) searchParams.set("tag", params.tag);

  const query = searchParams.toString();
  return apiFetch(`/api/v1/posts${query ? `?${query}` : ""}`);
}

export async function getPostBySlug(slug: string): Promise<Post> {
  return apiFetch(`/api/v1/posts/${slug}`);
}

// --- Authenticated endpoints ---

export async function createPost(
  data: Record<string, unknown>,
  token: string
): Promise<Post> {
  return apiFetch("/api/v1/posts", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export async function updatePost(
  postId: string,
  data: Record<string, unknown>,
  token: string
): Promise<Post> {
  return apiFetch(`/api/v1/posts/${postId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
    token,
  });
}

export async function deletePost(
  postId: string,
  token: string
): Promise<void> {
  return apiFetch(`/api/v1/posts/${postId}`, {
    method: "DELETE",
    token,
  });
}

// --- Auth ---

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export async function login(
  email: string,
  password: string
): Promise<TokenResponse> {
  return apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function refreshToken(
  refresh_token: string
): Promise<TokenResponse> {
  return apiFetch("/api/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token }),
  });
}
