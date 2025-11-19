import { useState, useEffect } from "react";
import api from "../services/api";
import EventCard from "../components/EventCard";
import { Event } from "@singularity/shared";

export default function Home() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const data = await api.getEvents();
        setEvents(data);
      } catch {
        setError("Failed to load events");
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  return (
    <div className="container mx-auto px-4 py-10">
      <section className="text-center mb-10">
        <h1 className="text-4xl font-bold mb-3">Discover Cosmic Events</h1>
        <p className="text-gray-600 max-w-xl mx-auto">
          Stay updated with upcoming astronomical events, dark sites, and visibility insights.
        </p>
      </section>

      {loading && <p className="text-center text-gray-600">Loading events...</p>}
      {error && <p className="text-center text-red-500">{error}</p>}

      {!loading && !error && (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {events.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>
      )}
    </div>
  );
}
