import { useRouter } from "next/router";
import { useState, useEffect } from "react";
import api from "../../services/api";
import { Event } from "@singularity/shared";
import Link from "next/link";

export default function EventDetail() {
  const router = useRouter();
  const { id } = router.query;

  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;

    const fetchEvent = async () => {
      try {
        const data = await api.getEventById(id as string);
        setEvent(data);
      } catch {
        setError("Failed to load event details");
      } finally {
        setLoading(false);
      }
    };

    fetchEvent();
  }, [id]);

  if (loading) return <p className="text-center mt-10">Loading event...</p>;
  if (error) return <p className="text-center text-red-500 mt-10">{error}</p>;
  if (!event) return <p className="text-center mt-10">Event not found</p>;

  const hasLocation = event.location && event.location.lat && event.location.lon;

  return (
    <div className="container mx-auto px-4 py-10">
      <h1 className="text-4xl font-bold mb-4">{event.title}</h1>

      <p className="text-gray-700 mb-4">{event.description}</p>

      <div className="space-y-2 mb-6">
        <p className="text-sm text-gray-600">
          Start: {event.start ? new Date(event.start).toLocaleString() : "N/A"}
        </p>
        <p className="text-sm text-gray-600">
          End: {event.end ? new Date(event.end).toLocaleString() : "N/A"}
        </p>

        {hasLocation && (
          <p className="text-sm text-gray-600">
            Location: {event.location.name}
          </p>
        )}
      </div>

      {hasLocation && (
        <div className="mb-6">
          <div className="w-full h-64 bg-gray-200 rounded flex items-center justify-center">
            <span className="text-gray-600">Map Placeholder</span>
          </div>

          <Link
            href={`/darksites?lat=${event.location.lat}&lon=${event.location.lon}`}
            className="inline-block mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Find Nearest Dark Site
          </Link>
        </div>
      )}
    </div>
  );
}
