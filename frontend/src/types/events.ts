// frontend/src/types/events.ts
export type SatellitePass = {
  id: string;
  start: string; // ISO datetime
  max: string; // ISO datetime
  end: string; // ISO datetime
  maxElevationDeg: number;
  azimuthDeg: number;
  visibilityScore: number; // 0-100
  magnitude?: string; // brightness (mock)
};

export type PassesResponse = {
  passes: SatellitePass[];
};
