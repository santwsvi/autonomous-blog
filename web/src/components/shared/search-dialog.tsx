"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
} from "@/components/ui/command";

interface SearchResult {
  title: string;
  slug: string;
  excerpt: string;
  similarity: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function SearchDialog() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  // Cmd+K to open
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((o) => !o);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  // Debounced search
  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await fetch(
          `${API_URL}/api/v1/search?q=${encodeURIComponent(query)}&limit=8`
        );
        if (res.ok) {
          const data = await res.json();
          setResults(data.results);
        }
      } catch {
        // Search failed silently
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = useCallback(
    (slug: string) => {
      setOpen(false);
      setQuery("");
      router.push(`/${slug}`);
    },
    [router]
  );

  return (
    <CommandDialog open={open} onOpenChange={setOpen} title="Buscar" description="Busca semântica nos posts do blog">
      <CommandInput
        placeholder="Buscar posts..."
        value={query}
        onValueChange={setQuery}
      />
      <CommandList>
        {loading && (
          <div className="py-6 text-center text-sm text-muted-foreground">
            Buscando...
          </div>
        )}
        {!loading && query.length >= 2 && results.length === 0 && (
          <CommandEmpty>Nenhum resultado encontrado.</CommandEmpty>
        )}
        {results.length > 0 && (
          <CommandGroup heading="Posts">
            {results.map((r) => (
              <CommandItem
                key={r.slug}
                value={r.slug}
                onSelect={() => handleSelect(r.slug)}
              >
                <div className="flex flex-col gap-0.5">
                  <span className="font-medium">{r.title}</span>
                  <span className="text-xs text-muted-foreground line-clamp-1">
                    {r.excerpt}
                  </span>
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        )}
      </CommandList>
    </CommandDialog>
  );
}
