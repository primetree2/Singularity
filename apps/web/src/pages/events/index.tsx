import { useState, useEffect } from "react";
import api from "../../services/api";
import EventCard from "../../components/EventCard";
import { Event } from "@singularity/shared";

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [type, setType] = useState("");

  const fetchEvents = async () => {
    setLoading(true);
    setError("");
    try {
      const filters: Record<string, any> = {};
      if (startDate) filters.start = startDate;
      if (endDate) filters.end = endDate;
      if (type) filters.type = type;

      const data = await api.getEvents(filters);
      setEvents(data);
    } catch {
      setError("Failed to load events");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [startDate, endDate, type]);

  const resetFilters = () => {
    setStartDate("");
    setEndDate("");
    setType("");
  };

  return (
    <div className="container mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6 text-center">All Events</h1>

      <div className="bg-white shadow p-5 rounded mb-8">
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="block mb-1 text-gray-700">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block mb-1 text-gray-700">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block mb-1 text-gray-700">Event Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">All</option>
              <option value="meteor">Meteor Shower</option>
              <option value="eclipse">Eclipse</option>
              <option value="iss">ISS Pass</option>
              <option value="conjunction">Planetary Conjunction</option>
            </select>
          </div>
        </div>

        <button
          onClick={resetFilters}
          className="mt-4 bg-gray-200 hover:bg-gray-300 px-4 py-2 rounded"
        >
          Reset Filters
        </button>
      </div>

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
