import { DarkSite } from "@singularity/shared";

type Props = {
  darkSites: DarkSite[];
};

export default function DarkSiteList({ darkSites }: Props) {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {darkSites.map((site) => {
        const desc =
          site.description && site.description.length > 100
            ? site.description.slice(0, 100) + "..."
            : site.description;

        const pollution = site.lightPollution || 0;
        const distance = site.distance ? site.distance.toFixed(2) : null;

        return (
          <div
            key={site.id}
            className="bg-white shadow rounded p-5 hover:shadow-lg transition"
          >
            <h2 className="text-xl font-semibold mb-2">{site.name}</h2>

            {desc && <p className="text-gray-600 mb-3">{desc}</p>}

            {distance && (
              <p className="text-sm text-gray-500 mb-2">Distance: {distance} km</p>
            )}

            <div className="mb-3">
              <p className="text-sm text-gray-500">Light Pollution</p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${Math.min(pollution, 100)}%` }}
                />
              </div>
            </div>

            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Get Directions
            </button>
          </div>
        );
      })}
    </div>
  );
}
