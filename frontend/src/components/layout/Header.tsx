"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import SetLocationButton from "./SetLocationButton";


export default function Header() {
  const pathname = usePathname() || "/"

  const isActive = (path: string) => (pathname === path ? "text-foreground" : "text-muted-foreground")

  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-3">
          <span className="text-xl font-semibold">🛰️ Singularity</span>
          <span className="text-sm text-muted-foreground">track satellites</span>
        </Link>

        <nav className="flex items-center gap-4">
          <Link href="/dashboard" className={isActive("/dashboard")}>Dashboard</Link>
          <Link href="/events" className={isActive("/events")}>Events</Link>
          <Link href="/leaderboard" className={isActive("/leaderboard")}>Leaderboard</Link>
          <Link href="/profile" className={isActive("/profile")}>Profile</Link>
          <div className="ml-4">
  <SetLocationButton />
</div>

        </nav>
      </div>
    </header>
  )
}
