import Link from "next/link";
import { Event } from "@singularity/shared";
import VisibilityScoreBadge from "./VisibilityScoreBadge";

type Props = {
  event: Event;
  score?: number;
};

export default function EventCard({ event, score }: Props) {
  const desc =
    event.description && event.description.length > 100
      ? event.description.slice(0, 100) + "..."
      : event.description;

  const date = event.start ? new Date(event.start).toLocaleDateString() : "";

  return (
    <div className="shadow rounded-lg p-5 hover:shadow-lg transition bg-white">
      <h3 className="text-xl font-semibold mb-2">{event.title}</h3>
      <p className="text-gray-600 mb-3">{desc}</p>
      <p className="text-sm text-gray-500 mb-2">{date}</p>

      {event.location && (
       <p className="text-sm text-gray-500 mb-3">{event.location.name}</p>

      )}

      {typeof score === "number" && (
        <div className="mb-3">
          <VisibilityScoreBadge score={score} />
        </div>
      )}

      <Link
        href={`/events/${event.id}`}
        className="inline-block mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        View Details
      </Link>
    </div>
  );
}
