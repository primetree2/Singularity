"use client"

import * as React from "react"
import { cn } from "@/lib/utils/utils"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  help?: string
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, label, help, ...props }, ref) => {
  return (
    <div className={cn("flex flex-col gap-1", className)}>
      {label && <label className="text-sm font-medium text-foreground">{label}</label>}
      <input
        ref={ref}
        {...props}
        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      />
      {help && <p className="text-xs text-muted-foreground">{help}</p>}
    </div>
  )
})
Input.displayName = "Input"
export default Input
