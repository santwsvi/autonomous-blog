import { getPosts } from "@/lib/api";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Arquivo",
  description: "Todos os posts do blog organizados por data.",
};

export const revalidate = 60;

export default async function ArchivePage() {
  let grouped: Record<string, Array<{ title: string; slug: string; date: string }>> = {};

  try {
    const posts = await getPosts({ status: "published", per_page: 200 });

    for (const post of posts.items) {
      const date = new Date(post.published_at || post.created_at);
      const key = `${date.getFullYear()} - ${date.toLocaleString("pt-BR", { month: "long" })}`;
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push({
        title: post.title,
        slug: post.slug,
        date: date.toLocaleDateString("pt-BR", { day: "numeric", month: "short", year: "numeric" }),
      });
    }
  } catch {
    // API down
  }

  const months = Object.entries(grouped);

  return (
    <div className="container mx-auto max-w-3xl px-4 md:px-8 py-8">
      <h1 className="text-3xl font-bold tracking-tight md:text-4xl mb-2">Arquivo</h1>
      <p className="text-muted-foreground text-lg mb-8">Todos os posts por data.</p>

      {months.length > 0 ? (
        <div className="space-y-8">
          {months.map(([month, posts]) => (
            <section key={month}>
              <h2 className="text-lg font-semibold mb-3 text-muted-foreground">{month}</h2>
              <ul className="space-y-2">
                {posts.map((post) => (
                  <li key={post.slug} className="flex items-baseline gap-3">
                    <span className="text-xs text-muted-foreground shrink-0 w-20">{post.date}</span>
                    <Link href={`/${post.slug}`} className="text-sm hover:text-primary transition-colors">
                      {post.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      ) : (
        <p className="text-muted-foreground">Nenhum post encontrado.</p>
      )}
    </div>
  );
}
