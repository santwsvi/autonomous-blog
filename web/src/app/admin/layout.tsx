"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/admin", label: "Overview" },
  { href: "/admin/posts", label: "Posts" },
  { href: "/admin/generate", label: "Gerar" },
  { href: "/admin/analytics", label: "Analytics" },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="container mx-auto px-4 md:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Admin</h1>
        <Link
          href="/"
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          Ver blog
        </Link>
      </div>

      <nav className="flex gap-1 mb-8 border-b">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`px-4 py-2 text-sm border-b-2 -mb-px transition-colors ${
              pathname === item.href
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      {children}
    </div>
  );
}
