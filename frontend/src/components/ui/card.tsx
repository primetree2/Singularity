import * as React from "react"
import { cn } from "@/lib/utils/utils"

export const Card = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  return <div className={cn("rounded-lg border border-border bg-card p-4 shadow-sm", className)}>{children}</div>
}
export default Card
