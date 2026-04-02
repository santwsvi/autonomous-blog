import Link from "next/link";
import { ThemeToggle } from "./theme-toggle";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-14 items-center justify-between px-4 md:px-8">
        <Link href="/" className="flex items-center gap-2 font-bold text-lg">
          <span className="hidden sm:inline">Victor Gabriel</span>
          <span className="sm:hidden">VG</span>
        </Link>

        <nav className="flex items-center gap-6">
          <Link
            href="/"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Blog
          </Link>
          <Link
            href="/tags"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors hidden sm:block"
          >
            Tags
          </Link>
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}
