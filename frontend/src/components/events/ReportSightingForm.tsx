"use client"
import { toast } from "sonner"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

type ReportSightingFormProps = {
  eventId: string
  onClose: () => void
}

export default function ReportSightingForm({ eventId, onClose }: ReportSightingFormProps) {
  const [sawIt, setSawIt] = useState<"yes" | "no" | null>(null)
  const [photo, setPhoto] = useState<File | null>(null)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
    toast.success(
  `Report submitted for ${eventId}`,
  {
    description: sawIt === "yes"
      ? "You earned 10 points!"
      : "No points this time.",
  }
)
onClose()

  }

  if (submitted) return null

  return (
    <form onSubmit={handleSubmit} className="space-y-3 p-4 border rounded-lg bg-card">
      <h3 className="font-semibold">Report Sighting</h3>

      <div className="flex gap-3">
        <Button
          type="button"
          variant={sawIt === "yes" ? "default" : "outline"}
          onClick={() => setSawIt("yes")}
          size="sm"
        >
          👀 Saw It
        </Button>
        <Button
          type="button"
          variant={sawIt === "no" ? "default" : "outline"}
          onClick={() => setSawIt("no")}
          size="sm"
        >
          ❌ Did Not
        </Button>
      </div>

      <div>
        <Input type="file" accept="image/*" onChange={(e) => setPhoto(e.target.files?.[0] || null)} />
        <p className="text-xs text-muted-foreground mt-1">Optional photo (earns extra points)</p>
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="outline" type="button" onClick={onClose} size="sm">
          Cancel
        </Button>
        <Button type="submit" size="sm" disabled={!sawIt}>
          Submit
        </Button>
      </div>
    </form>
  )
}
