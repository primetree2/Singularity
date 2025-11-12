// frontend/src/components/events/PassesList.tsx
"use client";

import React from "react";
import { useState } from "react"; 
import { useFetchPasses } from "@/hooks/useFetchPasses";
import Card from "@/components/ui/card";
import { format } from "date-fns";
import NotificationToggle from "@/components/ui/NotificationToggle";
import AddToCalendarButton from "@/components/ui/AddToCalendarButton";
import ReportSightingForm from "@/components/events/ReportSightingForm"
import LoadingSkeleton from "@/components/ui/LoadingSkeleton"

export default function PassesList({ lat, lng }: { lat?: number; lng?: number }) {
    const [openReport, setOpenReport] = useState<string | null>(null);

  const { data, loading, error } = useFetchPasses(lat, lng);

  if (loading) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="p-4 border rounded-lg">
          <LoadingSkeleton lines={5} />
        </div>
      ))}
    </div>
  )
}

  if (error) {
    return <div className="text-destructive">Error: {error}</div>;
  }
  if (!data || data.length === 0) {
    return <div className="text-muted-foreground">No passes available.</div>;
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {data.map((p) => {
        const start = new Date(p.start);
        const max = new Date(p.max);
        const end = new Date(p.end);
        return (
          <Card key={p.id} className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-sm text-muted-foreground">Pass start</div>
                <div className="font-semibold">{format(start, "PPpp")}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  Max at {format(max, "pp")} • End {format(end, "pp")}
                </div>
              </div>

              <div className="text-right">
                <div className="text-sm text-muted-foreground">Elevation</div>
                <div className="text-xl font-bold">{p.maxElevationDeg}°</div>
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between gap-4">
              <div className="text-sm">
                <div className="text-muted-foreground">Direction</div>
                <div className="font-medium">{p.azimuthDeg}°</div>
              </div>

              <div className="text-sm">
                <div className="text-muted-foreground">Visibility</div>
                <div className="font-medium">{p.visibilityScore}/100</div>
              </div>

              <div className="text-sm">
                <div className="text-muted-foreground">Mag.</div>
                <div className="font-medium">{p.magnitude ?? "—"}</div>
              </div>
            </div>

            <div className="mt-3 flex flex-col gap-2">
  <div className="flex items-center gap-2">
    <NotificationToggle />
    <AddToCalendarButton
      title={`ISS Pass ${format(start, "PPpp")}`}
      start={p.start}
      end={p.end}
    />
    <button
      onClick={() => setOpenReport(p.id)}
      className="text-xs px-3 py-1 rounded-md border border-border"
    >
      🛰️ Report Sighting
    </button>
  </div>

  {openReport === p.id && (
    <ReportSightingForm eventId={p.id} onClose={() => setOpenReport(null)} />
  )}
</div>


          </Card>
        );
      })}
    </div>
  );
}
