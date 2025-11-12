import Card from "@/components/ui/card"

export default function EventsPage() {
  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <h1 className="text-2xl font-semibold">Events</h1>

      <p className="text-sm text-muted-foreground">
        A catalog of upcoming satellite events (ISS passes, Starlink trains, bright satellites, meteor showers).
      </p>

      <div className="grid gap-6 md:grid-cols-3 mt-6">
        <Card>
          <h3 className="font-semibold">ISS Pass</h3>
          <p className="mt-2 text-sm text-muted-foreground">Sample event card. Replace with real event data.</p>
        </Card>

        <Card>
          <h3 className="font-semibold">Starlink Train</h3>
          <p className="mt-2 text-sm text-muted-foreground">Sample event card. Replace with real event data.</p>
        </Card>

        <Card>
          <h3 className="font-semibold">Meteor Shower</h3>
          <p className="mt-2 text-sm text-muted-foreground">Sample event card. Replace with real event data.</p>
        </Card>
      </div>
    </div>
  )
}
