export default function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-6 mt-10">
      <div className="max-w-7xl mx-auto text-center space-y-2">
        <p>© 2025 Singularity - Built by Harsh & Rishabh</p>
        <div className="space-x-4">
          <a href="https://github.com" target="_blank" className="hover:underline">
            GitHub
          </a>
          <a href="/about" className="hover:underline">
            About
          </a>
        </div>
      </div>
    </footer>
  );
}
