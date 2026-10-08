import { HealthStatus } from "@/components/HealthStatus";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-3">
      <h1 className="text-4xl font-semibold text-neutral-900">Formly</h1>
      <HealthStatus />
    </main>
  );
}
