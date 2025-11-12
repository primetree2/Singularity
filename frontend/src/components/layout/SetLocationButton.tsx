// frontend/src/components/layout/SetLocationButton.tsx
"use client";

import { useGeolocation } from "@/hooks/useGeolocation";
import { Button } from "@/components/ui/button";

export default function SetLocationButton() {
  const { location, loading, error, requestLocation, clearLocation } = useGeolocation();

  return (
    <div className="flex items-center gap-2">
      <Button
        size="sm"
        onClick={() => {
          if (location) clearLocation();
          else requestLocation();
        }}
        disabled={loading}
        className="border"
      >
        {loading ? "Locating..." : location ? "Clear Location" : "Set Location"}
      </Button>

      {location && (
        <span className="text-xs text-muted-foreground">
          {location.lat.toFixed(2)}, {location.lng.toFixed(2)}
        </span>
      )}

      {error && <span className="text-xs text-destructive">{error}</span>}
    </div>
  );
}
