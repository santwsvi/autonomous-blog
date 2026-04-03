import { ImageResponse } from "@vercel/og";
import { getPostBySlug } from "@/lib/api";

export const runtime = "edge";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;

  let title = "Victor Gabriel — Blog";
  let excerpt = "Engenharia de software, arquitetura, segurança e tecnologia.";

  try {
    const post = await getPostBySlug(slug);
    title = post.title;
    excerpt = post.excerpt || excerpt;
  } catch {
    // Use defaults
  }

  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "60px 80px",
          backgroundColor: "#0a0a0a",
          color: "#fafafa",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            fontSize: 18,
            color: "#a1a1aa",
            marginBottom: 16,
          }}
        >
          Victor Gabriel — Blog
        </div>
        <div
          style={{
            fontSize: 48,
            fontWeight: 700,
            lineHeight: 1.2,
            marginBottom: 24,
            maxWidth: 900,
          }}
        >
          {title}
        </div>
        <div
          style={{
            fontSize: 22,
            color: "#a1a1aa",
            lineHeight: 1.5,
            maxWidth: 800,
          }}
        >
          {excerpt.slice(0, 150)}
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    }
  );
}
