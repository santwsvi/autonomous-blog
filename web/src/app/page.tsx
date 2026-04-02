import { getPosts } from "@/lib/api";
import { PostCard } from "@/components/blog/post-card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

export const revalidate = 60;

interface Props {
  searchParams: Promise<{ tag?: string }>;
}

export default async function BlogHome({ searchParams }: Props) {
  const { tag } = await searchParams;
  let posts;
  let error = false;

  try {
    posts = await getPosts({ status: "published", per_page: 20, tag: tag });
  } catch {
    error = true;
  }

  return (
    <div className="container mx-auto max-w-3xl px-4 md:px-8 py-8">
      <section className="mb-12">
        <h1 className="text-3xl font-bold tracking-tight md:text-4xl mb-2">
          Blog
        </h1>
        <p className="text-muted-foreground text-lg">
          Engenharia de software, arquitetura, segurança e o que mais aparecer.
        </p>
      </section>

      {tag && (
        <div className="flex items-center gap-2 mb-6">
          <span className="text-sm text-muted-foreground">Filtrando por:</span>
          <Badge variant="secondary">{tag}</Badge>
          <Link
            href="/"
            className="text-sm text-muted-foreground hover:text-foreground underline"
          >
            Limpar filtro
          </Link>
        </div>
      )}

      {error ? (
        <p className="text-muted-foreground">
          Não foi possível carregar os posts. Tente novamente mais tarde.
        </p>
      ) : posts && posts.items.length > 0 ? (
        <div className="flex flex-col gap-4">
          {posts.items.map((post) => (
            <PostCard
              key={post.id}
              slug={post.slug}
              title={post.title}
              excerpt={post.excerpt}
              tags={post.tags}
              category={post.category}
              readingTimeMinutes={post.reading_time_minutes}
              publishedAt={post.published_at}
              createdAt={post.created_at}
            />
          ))}
        </div>
      ) : (
        <p className="text-muted-foreground">
          {tag
            ? `Nenhum post encontrado com a tag "${tag}".`
            : "Nenhum post publicado ainda. Em breve!"}
        </p>
      )}
    </div>
  );
}
