import { useEffect, useRef } from "react";
import "leaflet/dist/leaflet.css";

type MarkerPoint = {
  id: string;
  lat: number;
  lon: number;
  label?: string;
};

type Props = {
  markers: MarkerPoint[];
  center: { lat: number; lon: number };
  zoom?: number;
};

export default function Map({ markers, center, zoom = 10 }: Props) {
  const mapRef = useRef<any>(null);

  useEffect(() => {
    const loadMap = async () => {
      const L = await import("leaflet");

      if (mapRef.current) return;

      mapRef.current = L.map("map").setView([center.lat, center.lon], zoom);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors"
      }).addTo(mapRef.current);

      markers.forEach((m) => {
        L.marker([m.lat, m.lon])
          .addTo(mapRef.current)
          .bindPopup(m.label || "Location");
      });
    };

    loadMap();
  }, [center, markers, zoom]);

  return <div id="map" style={{ height: "400px", width: "100%" }} />;
}
