export default function AdminPage() {
  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Dashboard</h2>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border p-6">
          <p className="text-sm text-muted-foreground">Total de posts</p>
          <p className="text-3xl font-bold mt-1">—</p>
        </div>
        <div className="rounded-lg border p-6">
          <p className="text-sm text-muted-foreground">Publicados</p>
          <p className="text-3xl font-bold mt-1">—</p>
        </div>
        <div className="rounded-lg border p-6">
          <p className="text-sm text-muted-foreground">Rascunhos</p>
          <p className="text-3xl font-bold mt-1">—</p>
        </div>
      </div>
      <p className="text-sm text-muted-foreground mt-8">
        Dashboard completo será implementado na Fase 4.
      </p>
    </div>
  );
}
