import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import useUser from "../../hooks/useUser";
import api from "../../services/api";
import { Event, DarkSite, Badge } from "@singularity/shared";

export default function ReportVisit() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useUser();

  const [events, setEvents] = useState<Event[]>([]);
  const [darkSites, setDarkSites] = useState<DarkSite[]>([]);
  const [selectedEvent, setSelectedEvent] = useState("");
  const [selectedDarkSite, setSelectedDarkSite] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [location, setLocation] =
    useState<{ lat: number; lon: number } | null>(null);
  const [loading, setLoading] = useState(false);
  const [successBadges, setSuccessBadges] = useState<Badge[]>([]);
  const [error, setError] = useState("");

  /* ------------------------------------------
     AUTH PROTECTION
  ------------------------------------------- */
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isLoading, isAuthenticated, router]);

  /* ------------------------------------------
     FETCH EVENTS
  ------------------------------------------- */
  useEffect(() => {
    api.getEvents().then(setEvents).catch(() => setEvents([]));
  }, []);

  /* ------------------------------------------
     GET USER LOCATION + DARK SITES
  ------------------------------------------- */
  useEffect(() => {
    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        const lat = coords.latitude;
        const lon = coords.longitude;

        setLocation({ lat, lon });

        api.getDarkSites(lat, lon).then(setDarkSites).catch(() => setDarkSites([]));
      },
      () => setLocation(null)
    );
  }, []);

  /* ------------------------------------------
     SUBMIT VISIT REPORT
  ------------------------------------------- */
  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (!selectedEvent) {
      setError("Please select an event.");
      setLoading(false);
      return;
    }

    try {
      const authToken = localStorage.getItem("token") || "";
      const photoUrl = photo ? "https://example.com/photo.jpg" : undefined;

      const payload = {
        eventId: selectedEvent,
        darkSiteId: selectedDarkSite || undefined,
        lat: location?.lat || 0,
        lon: location?.lon || 0,
        photoUrl
      };

      await api.reportVisit(payload, authToken);

      /* Fetch updated badges */
      if (user) {
        const badges = await api.getUserBadges(user.id);
        setSuccessBadges(badges);
      }

      setTimeout(() => {
        router.push("/dashboard");
      }, 1500);
    } catch (err) {
      setError("Failed to submit visit.");
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="container mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Report Your Visit</h1>

      <form
        onSubmit={handleSubmit}
        className="bg-white shadow rounded p-6 space-y-6"
      >
        {error && <p className="text-red-500">{error}</p>}

        {/* EVENT SELECT */}
        <div>
          <label className="block mb-2 font-medium">Event</label>
          <select
            value={selectedEvent}
            onChange={(e) => setSelectedEvent(e.target.value)}
            className="w-full border px-3 py-2 rounded"
            required
          >
            <option value="">Select an event...</option>
            {events.map((ev) => (
              <option key={ev.id} value={ev.id}>
                {ev.title}
              </option>
            ))}
          </select>
        </div>

        {/* DARK SITE SELECT */}
        <div>
          <label className="block mb-2 font-medium">Dark Site (Optional)</label>
          <select
            value={selectedDarkSite}
            onChange={(e) => setSelectedDarkSite(e.target.value)}
            className="w-full border px-3 py-2 rounded"
          >
            <option value="">None</option>
            {darkSites.map((ds) => (
              <option key={ds.id} value={ds.id}>
                {ds.name}
                {ds.distance ? ` (${ds.distance.toFixed(1)} km)` : ""}
              </option>
            ))}
          </select>
        </div>

        {/* PHOTO UPLOAD */}
        <div>
          <label className="block mb-2 font-medium">Upload Photo</label>
          <input
            type="file"
            onChange={(e) => setPhoto(e.target.files?.[0] || null)}
            className="w-full border px-3 py-2 rounded"
          />
        </div>

        {/* LOCATION */}
        <div>
          <label className="block mb-2 font-medium">Your Location</label>
          {location ? (
            <p>
              Lat: {location.lat.toFixed(4)}, Lon: {location.lon.toFixed(4)}
            </p>
          ) : (
            <p className="text-sm text-gray-500">Location unavailable</p>
          )}
        </div>

        {/* SUBMIT */}
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? "Submitting..." : "Submit Visit"}
        </button>

        {/* SUCCESS BADGES */}
        {successBadges.length > 0 && (
          <div className="mt-4 p-4 bg-green-100 border rounded">
            <p className="font-semibold mb-2">You earned new badges!</p>
            <ul className="list-disc list-inside">
              {successBadges.map((b) => (
                <li key={b.id}>{b.name}</li>
              ))}
            </ul>
          </div>
        )}
      </form>
    </div>
  );
}
