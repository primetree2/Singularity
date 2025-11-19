/**
 * User represents a registered user in the Singularity system.
 *
 * Example:
 * const exampleUser: User = {
 *   id: "uuid-1234",
 *   email: "harsh@example.com",
 *   displayName: "Harsh",
 *   score: 1200,
 *   createdAt: "2025-01-01T00:00:00.000Z"
 * };
 */
export interface User {
  id: string;
  email: string;
  displayName: string;
  score: number;
  createdAt: string;
}

/**
 * Event represents an astronomical event.
 *
 * Example:
 * const exampleEvent: Event = {
 *   id: "evt-1234",
 *   title: "Perseid Meteor Shower Peak",
 *   description: "Peak activity of the Perseid meteor shower.",
 *   start: "2025-08-12T20:00:00.000Z",
 *   end: "2025-08-13T04:00:00.000Z",
 *   type: "meteor_shower",
 *   location: { lat: 28.7041, lon: 77.1025, name: "New Delhi, IN" },
 *   visibilityEstimate: { score: 72.5, updatedAt: "2025-08-11T12:00:00.000Z" }
 * };
 */
export interface Event {
  id: string;
  title: string;
  description: string;
  start: string;
  end: string;
  type: string;
  location: {
    lat: number;
    lon: number;
    name: string;
  };
  visibilityEstimate: {
    score: number;
    updatedAt: string;
  };
}

/**
 * DarkSite represents a known dark-sky location.
 *
 * Example:
 * const exampleDarkSite: DarkSite = {
 *   id: "ds-001",
 *   name: "Dark Valley",
 *   location: { lat: 34.1234, lon: -118.1234 },
 *   lightPollution: 0.12,
 *   description: "Remote valley with very low light pollution.",
 *   distance: 42.7
 * };
 */
export interface DarkSite {
  id: string;
  name: string;
  location: {
    lat: number;
    lon: number;
  };
  lightPollution: number;
  description: string;
  /** optional distance in kilometers from query point */
  distance?: number;
}

/**
 * VisibilityScore is a composite score (0-100) describing how visible an event is from a location,
 * along with factor breakdowns.
 *
 * Example:
 * const exampleVisibility: VisibilityScore = {
 *   score: 78.3,
 *   updatedAt: "2025-11-01T18:00:00.000Z",
 *   factors: {
 *     cloudCover: 0.15,
 *     aqi: 42,
 *     lightPollution: 0.08,
 *     elevation: 350,
 *     moonIllumination: 0.23,
 *     horizon: 0.05
 *   }
 * };
 */
export interface VisibilityScore {
  /** 0-100 */
  score: number;
  updatedAt: string;
  factors: {
    /** 0-1 (lower is clearer) */
    cloudCover: number;
    /** AQI numeric (0-500) */
    aqi: number;
    /** 0-1 (lower is darker) */
    lightPollution: number;
    /** meters above sea level */
    elevation: number;
    /** 0-1 fraction illuminated */
    moonIllumination: number;
    /** 0-1 obstruction factor (lower is better) */
    horizon: number;
  };
}

/**
 * Badge awarded to users for achievements.
 *
 * Example:
 * const exampleBadge: Badge = {
 *   id: "badge-1",
 *   name: "First Stargaze",
 *   description: "Awarded for first verified visit to a dark site.",
 *   iconUrl: "https://example.com/badges/first-stargaze.png",
 *   earnedAt: "2025-02-10T21:00:00.000Z"
 * };
 */
export interface Badge {
  id: string;
  name: string;
  description: string;
  iconUrl: string;
  earnedAt?: string;
}

/**
 * Visit represents a user-submitted visit to an event or darksite (used for gamification).
 *
 * Example:
 * const exampleVisit: Visit = {
 *   id: "visit-123",
 *   userId: "uuid-1234",
 *   eventId: "evt-1234",
 *   darkSiteId: "ds-001",
 *   timestamp: "2025-08-12T22:15:00.000Z",
 *   photoUrl: "https://cdn.example.com/photos/visit-123.jpg",
 *   visibilityScore: 75.2,
 *   points: 50
 * };
 */
export interface Visit {
  id: string;
  userId: string;
  eventId: string;
  darkSiteId?: string;
  timestamp: string;
  photoUrl?: string;
  visibilityScore?: number;
  points: number;
}

/**
 * LeaderboardEntry represents a ranked user entry on the leaderboard.
 *
 * Example:
 * const exampleLeaderboardEntry: LeaderboardEntry = {
 *   rank: 1,
 *   user: {
 *     id: "uuid-1234",
 *     email: "harsh@example.com",
 *     displayName: "Harsh",
 *     score: 2500,
 *     createdAt: "2025-01-01T00:00:00.000Z"
 *   },
 *   score: 2500
 * };
 */
export interface LeaderboardEntry {
  rank: number;
  user: User;
  score: number;
}
