// frontend/src/hooks/useFetchPasses.ts
"use client";

import { useEffect, useState } from "react";
import type { PassesResponse, SatellitePass } from "@/types/events";

export function useFetchPasses(lat?: number, lng?: number) {
  const [data, setData] = useState<SatellitePass[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function fetchPasses() {
      setLoading(true);
      setError(null);
      try {
        const q = new URLSearchParams();
        if (lat !== undefined) q.set("lat", String(lat));
        if (lng !== undefined) q.set("lng", String(lng));
        const res = await fetch(`/api/events/iss-passes?${q.toString()}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as PassesResponse;
        if (!mounted) return;
        setData(json.passes || []);
      } catch (err: any) {
        if (!mounted) return;
        setError(err?.message || "Failed to fetch");
      } finally {
        if (mounted) setLoading(false);
      }
    }

    fetchPasses();
    return () => {
      mounted = false;
    };
  }, [lat, lng]);

  return { data, loading, error };
}
