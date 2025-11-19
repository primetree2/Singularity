import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="sticky top-0 bg-white shadow z-40">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link href="/" className="text-2xl font-bold text-blue-600">
          Singularity
        </Link>
        <div className="space-x-6 hidden sm:flex">
          <Link href="/" className="text-gray-700 hover:text-blue-600">
            Home
          </Link>
          <Link href="/events" className="text-gray-700 hover:text-blue-600">
            Events
          </Link>
          <Link href="/darksites" className="text-gray-700 hover:text-blue-600">
            Dark Sites
          </Link>
          <Link href="/dashboard" className="text-gray-700 hover:text-blue-600">
            Dashboard
          </Link>
        </div>
      </div>
    </nav>
  );
}
