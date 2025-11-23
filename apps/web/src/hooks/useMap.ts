import { useState } from "react";

type Marker = {
  id: string;
  lat: number;
  lon: number;
  label?: string;
};

export default function useMap() {
  const [center, setCenter] = useState<[number, number]>([0, 0]);
  const [zoom, setZoom] = useState<number>(10);
  const [markers, setMarkers] = useState<Marker[]>([]);

  const addMarker = (marker: Marker) => {
    setMarkers((prev) => [...prev, marker]);
  };

  const clearMarkers = () => {
    setMarkers([]);
  };

  return {
    center,
    zoom,
    markers,
    setCenter,
    setZoom,
    setMarkers,
    addMarker,
    clearMarkers
  };
}
