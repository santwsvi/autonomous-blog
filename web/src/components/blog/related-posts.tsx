"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RelatedPost {
  title: string;
  slug: string;
  excerpt: string;
  similarity: number;
}

export function RelatedPosts({ slug }: { slug: string }) {
  const [posts, setPosts] = useState<RelatedPost[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/posts/${slug}/related?limit=3`)
      .then((r) => (r.ok ? r.json() : { related: [] }))
      .then((data) => setPosts(data.related || []))
      .catch(() => {});
  }, [slug]);

  if (posts.length === 0) return null;

  return (
    <section className="mt-12 pt-8 border-t">
      <h3 className="text-lg font-semibold mb-4">Posts relacionados</h3>
      <div className="grid gap-4 sm:grid-cols-3">
        {posts.map((post) => (
          <Link
            key={post.slug}
            href={`/${post.slug}`}
            className="group rounded-lg border p-4 hover:border-foreground/20 transition-colors"
          >
            <h4 className="font-medium text-sm group-hover:text-primary transition-colors line-clamp-2 mb-2">
              {post.title}
            </h4>
            <p className="text-xs text-muted-foreground line-clamp-2">
              {post.excerpt}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
