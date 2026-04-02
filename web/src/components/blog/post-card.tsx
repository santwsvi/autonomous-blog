import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";

interface PostCardProps {
  slug: string;
  title: string;
  excerpt: string | null;
  tags: string[];
  category: string | null;
  readingTimeMinutes: number | null;
  publishedAt: string | null;
  createdAt: string;
}

export function PostCard({
  slug,
  title,
  excerpt,
  tags,
  readingTimeMinutes,
  publishedAt,
  createdAt,
}: PostCardProps) {
  const date = publishedAt || createdAt;
  const formattedDate = new Date(date).toLocaleDateString("pt-BR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <Link href={`/${slug}`} className="group">
      <Card className="transition-colors hover:border-foreground/20">
        <CardHeader>
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
            <time dateTime={date}>{formattedDate}</time>
            {readingTimeMinutes && (
              <>
                <span aria-hidden="true">&middot;</span>
                <span>{readingTimeMinutes} min de leitura</span>
              </>
            )}
          </div>
          <CardTitle className="group-hover:text-primary transition-colors">
            {title}
          </CardTitle>
          {excerpt && <CardDescription>{excerpt}</CardDescription>}
        </CardHeader>
        {tags.length > 0 && (
          <CardContent>
            <div className="flex flex-wrap gap-1">
              {tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          </CardContent>
        )}
      </Card>
    </Link>
  );
}
