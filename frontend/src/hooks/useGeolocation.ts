// frontend/src/hooks/useGeolocation.ts
"use client";

import { useState, useEffect } from "react";

export type GeoLocation = {
  lat: number;
  lng: number;
};

export function useGeolocation() {
  const [location, setLocation] = useState<GeoLocation | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("userLocation");
    if (saved) {
      setLocation(JSON.parse(saved));
    }
  }, []);

  async function requestLocation() {
    setLoading(true);
    setError(null);
    try {
      if (!navigator.geolocation) {
        throw new Error("Geolocation not supported by this browser");
      }
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const { latitude, longitude } = pos.coords;
          const newLoc = { lat: latitude, lng: longitude };
          setLocation(newLoc);
          localStorage.setItem("userLocation", JSON.stringify(newLoc));
          setLoading(false);
        },
        (err) => {
          setError(err.message);
          setLoading(false);
        }
      );
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  }

  function clearLocation() {
    localStorage.removeItem("userLocation");
    setLocation(null);
  }

  return { location, loading, error, requestLocation, clearLocation };
}
