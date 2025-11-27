import axios, { AxiosHeaders } from "axios";
import {
  Event,
  DarkSite,
  LeaderboardEntry,
  Badge,
  AuthResponse,
  Visit
} from "@singularity/shared";

const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000"
});

/* ---------------------------------------------
   AUTH TOKEN INTERCEPTOR
---------------------------------------------- */
axiosInstance.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");

    if (token) {
      if (!config.headers) config.headers = new AxiosHeaders();
      (config.headers as AxiosHeaders).set("Authorization", `Bearer ${token}`);
    }
  }
  return config;
});

/* ---------------------------------------------
   REQUEST WRAPPER
---------------------------------------------- */
const request = async <T>(promise: Promise<{ data: T }>): Promise<T> => {
  try {
    const res = await promise;
    return res.data;
  } catch (err: any) {
    throw err.response?.data || err;
  }
};

/* ---------------------------------------------
   API METHODS
---------------------------------------------- */
export default {
  /* EVENTS */
  getEvents: async (filters?: Record<string, any>) =>
    request<Event[]>(axiosInstance.get("/events", { params: filters })),

  getEventById: async (id: string) =>
    request<Event>(axiosInstance.get(`/events/${id}`)),

  /* DARK SITES */
  getDarkSites: async (lat: number, lon: number) =>
    request<DarkSite[]>(
      axiosInstance.get("/darksites/nearest", { params: { lat, lon } })
    ),

  /* AUTH */
  login: async (email: string, password: string) =>
    request<AuthResponse>(
      axiosInstance.post("/users/login", { email, password })
    ),

  register: async (email: string, password: string, displayName: string) =>
    request<AuthResponse>(
      axiosInstance.post("/users/register", {
        email,
        password,
        displayName
      })
    ),

  /* DEVICE TOKEN */
  registerDeviceToken: async (
    token: string,
    platform: string,
    authToken: string
  ) =>
    request(
      axiosInstance.post(
        "/notifications/device-token",
        { token, platform },
        { headers: { Authorization: `Bearer ${authToken}` } }
      )
    ),

  /* BADGES */
  getUserBadges: async (userId: string) =>
    request<Badge[]>(axiosInstance.get(`/users/${userId}/badges`)),

  /* LEADERBOARD (new updated format) */
  getLeaderboard: async (limit?: number) =>
    request<LeaderboardEntry[]>(
      axiosInstance.get("/leaderboard", { params: { limit } })
    ),

  /* VISIT REPORT (updated format) */
  reportVisit: async (
    data: {
      eventId?: string;
      darkSiteId?: string;
      lat: number;
      lon: number;
      photoUrl?: string;
    },
    authToken: string
  ) =>
    request<Visit>(
      axiosInstance.post("/visits", data, {
        headers: { Authorization: `Bearer ${authToken}` }
      })
    )
};
