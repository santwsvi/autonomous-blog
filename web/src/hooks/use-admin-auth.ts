"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface UseAdminAuth {
  token: string | null;
  isReady: boolean;
  logout: () => void;
  fetchWithAuth: (url: string, options?: RequestInit) => Promise<Response>;
}

export function useAdminAuth(): UseAdminAuth {
  const [token, setToken] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setToken(localStorage.getItem("admin_token"));
    setIsReady(true);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("admin_token");
    setToken(null);
    router.push("/admin");
  }, [router]);

  const fetchWithAuth = useCallback(
    async (url: string, options: RequestInit = {}): Promise<Response> => {
      const headers = new Headers(options.headers);
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      const res = await fetch(url, { ...options, headers });
      if (res.status === 401) {
        localStorage.removeItem("admin_token");
        setToken(null);
      }
      return res;
    },
    [token]
  );

  return { token, isReady, logout, fetchWithAuth };
}
