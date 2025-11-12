"use client"

import * as React from "react"
import { cn } from "@/lib/utils/utils"
import { X } from "lucide-react"

export type ToastProps = {
  id?: string
  title?: string
  description?: string
  variant?: "default" | "success" | "error" | "info"
  onClose?: () => void
}

const variantClass = {
  default: "bg-card text-foreground",
  success: "bg-green-600 text-white",
  error: "bg-red-600 text-white",
  info: "bg-blue-600 text-white",
} as const

export function Toast({ title, description, variant = "default", onClose }: ToastProps) {
  return (
    <div
      role="status"
      className={cn(
        "flex w-full max-w-md items-start gap-3 rounded-md p-3 shadow-lg",
        variantClass[variant]
      )}
    >
      <div className="flex-1">
        {title && <div className="text-sm font-semibold">{title}</div>}
        {description && <div className="mt-1 text-sm opacity-90">{description}</div>}
      </div>
      <button onClick={onClose} aria-label="close" className="rounded-md p-1 hover:opacity-80">
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}

export default Toast
