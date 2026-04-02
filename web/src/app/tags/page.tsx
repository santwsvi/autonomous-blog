import { getPosts } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tags",
  description: "Todas as tags do blog",
};

export const revalidate = 60;

export default async function TagsPage() {
  let tagCounts: Record<string, number> = {};

  try {
    const posts = await getPosts({ status: "published", per_page: 100 });
    for (const post of posts.items) {
      for (const tag of post.tags) {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      }
    }
  } catch {
    // API down — show empty state
  }

  const sortedTags = Object.entries(tagCounts).sort((a, b) => b[1] - a[1]);

  return (
    <div className="container mx-auto max-w-3xl px-4 md:px-8 py-8">
      <h1 className="text-3xl font-bold tracking-tight md:text-4xl mb-2">
        Tags
      </h1>
      <p className="text-muted-foreground text-lg mb-8">
        Navegue por assunto.
      </p>

      {sortedTags.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {sortedTags.map(([tag, count]) => (
            <Link key={tag} href={`/?tag=${tag}`}>
              <Badge
                variant="secondary"
                className="text-sm px-3 py-1 hover:bg-accent cursor-pointer"
              >
                {tag} ({count})
              </Badge>
            </Link>
          ))}
        </div>
      ) : (
        <p className="text-muted-foreground">Nenhuma tag encontrada.</p>
      )}
    </div>
  );
}
