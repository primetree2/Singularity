import type { Metadata } from "next"
import "@/styles/globals.css"
import Header from "@/components/layout/Header"
import Footer from "@/components/layout/Footer"
import ToastProvider from "@/components/ui/toast-provider"

export const metadata: Metadata = {
  title: "Singularity – Satellite Visibility Tracker",
  description: "Check when you can see the ISS or Starlink from your location.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ToastProvider />
        <Header />
        <main className="min-h-screen bg-background px-4 py-6 sm:px-6 lg:px-8">
          {children}
        </main>
        <Footer />
        {children}
      </body>
    </html>
  )
}
