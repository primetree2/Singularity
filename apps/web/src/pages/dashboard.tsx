import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import useUser from "../hooks/useUser";

export default function Dashboard() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useUser();

  const [badges, setBadges] = useState<string[]>([]);
  const [visits] = useState<any[]>([]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (user) {
      const userBadges = (user as any)?.badges || [];
      setBadges(userBadges);
    }
  }, [user]);

  if (isLoading) return <p className="text-center mt-10">Loading...</p>;

  return (
    <div className="container mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">
        Welcome, {user?.email || "User"}
      </h1>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="bg-white shadow rounded p-5">
          <h2 className="text-xl font-semibold mb-2">Your Score</h2>
          <p className="text-3xl font-bold text-blue-600">
            {(user as any)?.score || 0}
          </p>
        </div>

        <div className="bg-white shadow rounded p-5">
          <h2 className="text-xl font-semibold mb-2">Badges</h2>
          <div className="flex flex-wrap gap-2">
            {badges.length > 0 ? (
              badges.map((badge, i) => (
                <span
                  key={i}
                  className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm"
                >
                  {badge}
                </span>
              ))
            ) : (
              <p className="text-gray-500">No badges yet</p>
            )}
          </div>
        </div>

        <div className="bg-white shadow rounded p-5">
          <h2 className="text-xl font-semibold mb-2">Recent Visits</h2>
          {visits.length === 0 ? (
            <p className="text-gray-500">No visits recorded yet</p>
          ) : (
            <ul className="list-disc list-inside text-gray-700">
              {visits.map((v, i) => (
                <li key={i}>{v}</li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="mt-10">
        <a
          href="/report-visit"
          className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Report Visit
        </a>
      </div>
    </div>
  );
}
