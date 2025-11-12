// frontend/src/app/profile/page.tsx
"use client";

import { useGeolocation } from "@/hooks/useGeolocation";
import Card from "@/components/ui/card";

export default function ProfilePage() {
  const { location, loading, error, requestLocation, clearLocation } = useGeolocation();

  return (
    <div className="max-w-xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Profile</h1>
      <p className="text-sm text-muted-foreground">
        Manage your account and saved location here.
      </p>

      <Card className="p-4 space-y-3">
        <h2 className="font-semibold text-lg">Your Location</h2>
        {location ? (
          <div>
            <p className="text-sm">
              <span className="font-medium">Latitude:</span> {location.lat.toFixed(4)}
            </p>
            <p className="text-sm">
              <span className="font-medium">Longitude:</span> {location.lng.toFixed(4)}
            </p>
            <button
              onClick={clearLocation}
              className="mt-3 px-3 py-1 text-sm rounded-md border border-border"
            >
              Clear Location
            </button>
          </div>
        ) : (
          <button
            onClick={requestLocation}
            disabled={loading}
            className="px-3 py-1 text-sm rounded-md border border-border"
          >
            {loading ? "Locating..." : "Set Current Location"}
          </button>
        )}

        {error && <p className="text-destructive text-sm mt-2">{error}</p>}
      </Card>
    </div>
  );
}
