import { Badge } from "@singularity/shared";
import { formatDate } from "../utils/date";

type Props = {
  badges: Badge[];
};

export default function BadgeDisplay({ badges }: Props) {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {badges.map((badge) => {
        const earned = !!badge.earnedAt;

        return (
          <div
            key={badge.id}
            className={`p-5 rounded shadow bg-white flex flex-col items-start ${
              earned ? "" : "opacity-50"
            }`}
          >
            <div className="text-4xl mb-3">
              {"🏅"}
            </div>

            <h3 className="text-xl font-semibold mb-1">{badge.name}</h3>

            <p className="text-gray-600 mb-3">
              {badge.description || "No description available"}
            </p>

            <p className="text-sm text-gray-500">
              {earned
                ? `Earned: ${formatDate(badge.earnedAt as string)}`
                : "Locked"}
            </p>
          </div>
        );
      })}
    </div>
  );
}
