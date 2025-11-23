import { useState, useEffect } from "react";
import api from "../../services/api";
import { DarkSite } from "@singularity/shared";

export default function DarkSitesPage() {
  const [sites, setSites] = useState<DarkSite[]>([]);
  const [loading, setLoading] = useState(true);
  const [locError, setLocError] = useState("");
  const [fetchError, setFetchError] = useState("");

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        try {
          const data = await api.getDarkSites(lat, lon);
          setSites(data);
        } catch {
          setFetchError("Failed to load dark sites");
        } finally {
          setLoading(false);
        }
      },
      () => {
        setLocError("Location permission denied");
        setLoading(false);
      }
    );
  }, []);

  if (loading) return <p className="text-center mt-10">Getting location...</p>;
  if (locError) return <p className="text-center text-red-500 mt-10">{locError}</p>;
  if (fetchError) return <p className="text-center text-red-500 mt-10">{fetchError}</p>;

  return (
    <div className="container mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6 text-center">Nearest Dark Sites</h1>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {sites.map((site) => (
          <div
            key={site.id}
            className="shadow p-5 rounded bg-white hover:shadow-lg transition"
          >
            <h2 className="text-xl font-semibold mb-2">{site.name}</h2>

            {site.description && (
              <p className="text-gray-600 mb-2">{site.description}</p>
            )}

            {typeof site.lightPollution === "number" && (
              <p className="text-sm text-gray-500 mb-2">
                Light Pollution Level: {site.lightPollution}
              </p>
            )}

            {typeof site.distance === "number" && (
              <p className="text-sm text-gray-500 mb-2">
                Distance: {site.distance.toFixed(2)} km
              </p>
            )}

            <a
              href="#"
              className="inline-block mt-3 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              View on Map
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
