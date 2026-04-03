import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface PostContentProps {
  title: string;
  excerpt: string | null;
  contentMdx: string;
  tags: string[];
  readingTimeMinutes: number | null;
  publishedAt: string | null;
  createdAt: string;
}

function stripFrontmatter(content: string): string {
  let cleaned = content.trim();
  // Remove ```markdown ... ``` wrapper
  const wrapperMatch = cleaned.match(/^```(?:markdown|md|mdx)\s*\n([\s\S]*?)\n```\s*$/);
  if (wrapperMatch) {
    cleaned = wrapperMatch[1];
  }
  // Remove YAML frontmatter block (--- ... ---)
  cleaned = cleaned.replace(/^---[\s\S]*?---\s*/m, "");
  return cleaned.trim();
}

export function PostContent({
  title,
  excerpt,
  contentMdx,
  tags,
  readingTimeMinutes,
  publishedAt,
  createdAt,
}: PostContentProps) {
  const date = publishedAt || createdAt;
  const formattedDate = new Date(date).toLocaleDateString("pt-BR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const cleanContent = stripFrontmatter(contentMdx);

  return (
    <article className="max-w-3xl">
      <header className="mb-8">
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
          <time dateTime={date}>{formattedDate}</time>
          {readingTimeMinutes && (
            <>
              <span aria-hidden="true">&middot;</span>
              <span>{readingTimeMinutes} min de leitura</span>
            </>
          )}
        </div>

        <h1 className="text-3xl font-bold tracking-tight md:text-4xl mb-3">
          {title}
        </h1>

        {excerpt && (
          <p className="text-lg text-muted-foreground">{excerpt}</p>
        )}

        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-4">
            {tags.map((tag) => (
              <Badge key={tag} variant="secondary">
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </header>

      <Separator className="mb-8" />

      <div className="prose prose-neutral dark:prose-invert max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {cleanContent}
        </ReactMarkdown>
      </div>
    </article>
  );
}
