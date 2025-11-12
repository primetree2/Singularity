export default function Footer() {
  return (
    <footer className="border-t border-border bg-card/50 text-center py-4 text-sm text-muted-foreground">
      © {new Date().getFullYear()} Singularity — Satellite Visibility Tracker
    </footer>
  )
}
