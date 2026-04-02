import { getPosts } from "@/lib/api";
import type { MetadataRoute } from "next";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const entries: MetadataRoute.Sitemap = [
    {
      url: SITE_URL,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
  ];

  try {
    const posts = await getPosts({ status: "published", per_page: 100 });
    for (const post of posts.items) {
      entries.push({
        url: `${SITE_URL}/${post.slug}`,
        lastModified: new Date(post.published_at || post.created_at),
        changeFrequency: "weekly",
        priority: 0.8,
      });
    }
  } catch {
    // If API is down, return at least the homepage
  }

  return entries;
}
