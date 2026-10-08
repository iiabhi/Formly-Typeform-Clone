"use client";

import { useQuery } from "@tanstack/react-query";
import { getHealth } from "@/lib/api/health";

export function HealthStatus() {
  const { data, isPending, isError } = useQuery({ queryKey: ["health"], queryFn: getHealth });

  if (isPending) return <p className="text-neutral-500">Checking API…</p>;
  if (isError) return <p className="text-red-600">API unreachable</p>;
  return (
    <p className="text-neutral-700">
      API status: <span className="font-semibold text-green-700">{data.status}</span>
    </p>
  );
}
