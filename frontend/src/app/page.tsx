"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import Card from "@/components/ui/card"

export default function HomePage() {
  const router = useRouter()

  return (
    <section className="flex flex-col items-center justify-center text-center gap-10 py-20">
      <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
        Track the <span className="text-primary">ISS</span> and Starlink from Your Sky
      </h1>

      <p className="max-w-2xl text-muted-foreground text-lg">
        Singularity helps you discover when satellites like the International Space Station or Starlink
        will be visible from your location — all in one intuitive dashboard.
      </p>

      <div className="flex gap-4 mt-4">
        <Button size="lg" onClick={() => router.push("/dashboard")}>
          View Dashboard
        </Button>
        <Button size="lg" variant="outline" onClick={() => router.push("/events")}>
          Explore Events
        </Button>
      </div>

      <div className="grid gap-6 mt-16 md:grid-cols-3">
        <Card>
          <h2 className="font-semibold text-lg mb-2">🌍 Real-Time Visibility</h2>
          <p className="text-sm text-muted-foreground">
            Get accurate ISS and satellite pass predictions based on your location and sky conditions.
          </p>
        </Card>

        <Card>
          <h2 className="font-semibold text-lg mb-2">📍 Dark Site Finder</h2>
          <p className="text-sm text-muted-foreground">
            Find the nearest dark-sky locations to enjoy the best possible view with minimal light pollution.
          </p>
        </Card>

        <Card>
          <h2 className="font-semibold text-lg mb-2">🏆 Leaderboard & Rewards</h2>
          <p className="text-sm text-muted-foreground">
            Report sightings, earn points, and climb the leaderboard as you watch the night sky.
          </p>
        </Card>
      </div>
    </section>
  )
}
