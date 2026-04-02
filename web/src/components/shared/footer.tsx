export function Footer() {
  return (
    <footer className="border-t py-8 mt-16">
      <div className="container mx-auto flex flex-col items-center gap-2 px-4 md:px-8 text-sm text-muted-foreground">
        <p>
          Feito com Next.js, FastAPI e IA multiagente.
        </p>
        <p>&copy; {new Date().getFullYear()} Victor Gabriel. Todos os direitos reservados.</p>
      </div>
    </footer>
  );
}
