// Mock API that returns sample ISS pass predictions for the next 7 days.
// Path: frontend/src/app/api/events/iss-passes/route.ts

import { NextResponse } from "next/server";

function samplePasses() {
  const now = Date.now();
  // create 5 sample passes spaced by a few hours
  return Array.from({ length: 5 }).map((_, i) => {
    const start = new Date(now + (i + 1) * 1000 * 60 * 60 * 4); // every ~4 hours
    const maxTime = new Date(start.getTime() + 1000 * 60 * 8); // 8 minutes later
    const end = new Date(start.getTime() + 1000 * 60 * 12); // 12 minutes later
    const elevation = Math.round(20 + Math.random() * 70); // 20..90 deg
    const azimuth = Math.round(Math.random() * 360);
    const score = Math.round((elevation / 90) * (Math.random() * 0.6 + 0.4) * 100); // 0..100-ish
    return {
      id: `pass-${i + 1}`,
      start: start.toISOString(),
      max: maxTime.toISOString(),
      end: end.toISOString(),
      maxElevationDeg: elevation,
      azimuthDeg: azimuth,
      visibilityScore: score,
      magnitude: (Math.random() * 3 + 0.5).toFixed(1), // fake brightness
    };
  });
}

export async function GET(request: Request) {
  // Optionally you can read query params lat/lng; ignore for mock
  const passes = samplePasses();
  return NextResponse.json({ passes });
}
