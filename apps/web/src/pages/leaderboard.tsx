import { useState, useEffect } from "react";
import api from "../services/api";
import { LeaderboardEntry } from "@singularity/shared";
import useUser from "../hooks/useUser";

export default function Leaderboard() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { user } = useUser();

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const data = await api.getLeaderboard();
        setEntries(data.slice(0, 100));
      } catch {
        setError("Failed to load leaderboard");
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  if (loading) return <p className="text-center mt-10">Loading leaderboard...</p>;
  if (error) return <p className="text-center text-red-500 mt-10">{error}</p>;

  return (
    <div className="container mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6 text-center">Leaderboard</h1>

      <div className="overflow-x-auto rounded shadow bg-white">
        <table className="min-w-full text-left text-gray-700">
          <thead className="bg-gray-100">
            <tr>
              <th className="py-3 px-4">Rank</th>
              <th className="py-3 px-4">User</th>
              <th className="py-3 px-4">Score</th>
            </tr>
          </thead>

          <tbody>
            {entries.map((entry, index) => {
              const userObj = entry.user || {};
              const isCurrentUser = user && userObj.id === user.id;

              return (
                <tr
                  key={userObj.id || index}
                  className={`border-t ${isCurrentUser ? "bg-blue-100" : ""}`}
                >
                  <td className="py-2 px-4">{index + 1}</td>

                  {/* USER EMAIL (since .name does not exist) */}
                  <td className="py-2 px-4">
                    {userObj.email || "Unknown User"}
                  </td>

                  <td className="py-2 px-4">{entry.score}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
