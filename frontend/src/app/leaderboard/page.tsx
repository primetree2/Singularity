import Card from "@/components/ui/card"
import type { UserScore } from "@/types/leaderboard"

const mockLeaderboard: UserScore[] = [
 { id: "1", name: "Aarav", points: 220, streak: 5, badge: "🌟 Explorer" },
 { id: "2", name: "Isha", points: 190, streak: 4, badge: "🚀 Observer" },
 { id: "3", name: "Rohan", points: 150, streak: 3, badge: "🛰️ Tracker" },
 { id: "4", name: "Tara", points: 120, streak: 2, badge: "✨ Stargazer" },
]

export default function LeaderboardPage() {
 return (
  <div className="max-w-3xl mx-auto p-6 space-y-6">
    <h1 className="text-2xl font-semibold">Leaderboard</h1>
    <p className="text-sm text-muted-foreground">
      Top users based on reported sightings and photo uploads.
    </p>

    <div className="space-y-2">
      {mockLeaderboard.map((u, i) => (
        <Card key={u.id} className="flex items-center justify-between p-3">
          <div className="flex items-center gap-3">
            <span className="font-bold w-6 text-right">{i + 1}.</span>
            <span className="font-medium">{u.name}</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">{u.badge}</span>
            <span className="text-sm font-semibold">{u.points} pts</span>
            <span className="text-xs text-muted-foreground">{u.streak}-day streak</span>
          </div>
        </Card>
      ))}
    </div>
  </div>
 )
}
