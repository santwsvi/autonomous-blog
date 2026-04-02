import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 px-4">
      <h2 className="text-4xl font-bold">404</h2>
      <p className="text-muted-foreground text-center max-w-md">
        Página não encontrada. O conteúdo que você procura pode ter sido
        removido ou o endereço está incorreto.
      </p>
      <Link
        href="/"
        className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
      >
        Voltar ao início
      </Link>
    </div>
  );
}
