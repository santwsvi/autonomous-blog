import { getPosts } from "@/lib/api";

export async function GET() {
  const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

  let items = "";
  try {
    const posts = await getPosts({ status: "published", per_page: 50 });
    items = posts.items
      .map(
        (post) => `
    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${SITE_URL}/${post.slug}</link>
      <guid isPermaLink="true">${SITE_URL}/${post.slug}</guid>
      <description><![CDATA[${post.excerpt || ""}]]></description>
      <pubDate>${new Date(post.published_at || post.created_at).toUTCString()}</pubDate>
      ${post.tags.map((t) => `<category>${t}</category>`).join("\n      ")}
    </item>`
      )
      .join("\n");
  } catch {
    // API down — return empty feed
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Victor Gabriel — Blog</title>
    <link>${SITE_URL}</link>
    <description>Blog pessoal sobre engenharia de software, arquitetura, segurança e tecnologia.</description>
    <language>pt-BR</language>
    <atom:link href="${SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
    ${items}
  </channel>
</rss>`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "s-maxage=3600, stale-while-revalidate",
    },
  });
}
