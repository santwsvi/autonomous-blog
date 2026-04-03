"use client";

import Giscus from "@giscus/react";
import { useTheme } from "next-themes";

export function Comments() {
  const { resolvedTheme } = useTheme();

  return (
    <section className="mt-12 pt-8 border-t">
      <Giscus
        repo="santwsvi/autonomous-blog"
        repoId=""
        category="General"
        categoryId=""
        mapping="pathname"
        strict="0"
        reactionsEnabled="1"
        emitMetadata="0"
        inputPosition="top"
        theme={resolvedTheme === "dark" ? "dark" : "light"}
        lang="pt"
      />
    </section>
  );
}
