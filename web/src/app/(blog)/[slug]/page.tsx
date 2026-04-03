import { notFound } from "next/navigation";
import { getPostBySlug, getPosts } from "@/lib/api";
import { PostContent } from "@/components/blog/post-content";
import type { Metadata } from "next";

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;

  try {
    const post = await getPostBySlug(slug);
    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
    return {
      title: post.title,
      description: post.excerpt || undefined,
      openGraph: {
        title: post.title,
        description: post.excerpt || undefined,
        type: "article",
        publishedTime: post.published_at || post.created_at,
        tags: post.tags,
        images: [`${siteUrl}/og/${slug}`],
      },
      twitter: {
        card: "summary_large_image",
        title: post.title,
        description: post.excerpt || undefined,
        images: [`${siteUrl}/og/${slug}`],
      },
    };
  } catch {
    return { title: "Post não encontrado" };
  }
}

export async function generateStaticParams() {
  try {
    const posts = await getPosts({ status: "published", per_page: 100 });
    return posts.items.map((post) => ({ slug: post.slug }));
  } catch {
    return [];
  }
}

export const revalidate = 60;

export default async function PostPage({ params }: Props) {
  const { slug } = await params;

  let post;
  try {
    post = await getPostBySlug(slug);
  } catch {
    notFound();
  }

  if (post.status !== "published") {
    notFound();
  }

  return (
    <PostContent
      title={post.title}
      excerpt={post.excerpt}
      contentMdx={post.content_mdx}
      tags={post.tags}
      readingTimeMinutes={post.reading_time_minutes}
      publishedAt={post.published_at}
      createdAt={post.created_at}
    />
  );
}
