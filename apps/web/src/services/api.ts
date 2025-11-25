import axios from "axios";
import { Event, DarkSite } from "@singularity/shared";

const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000"
});

// Automatically attach auth token
axiosInstance.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const request = async <T>(promise: Promise<{ data: T }>): Promise<T> => {
  try {
    const res = await promise;
    return res.data;
  } catch (err: any) {
    throw err.response?.data || err;
  }
};

export default {
  getEvents: async (filters?: Record<string, any>) =>
    request<Event[]>(axiosInstance.get("/events", { params: filters })),

  getEventById: async (id: string) =>
    request<Event>(axiosInstance.get(`/events/${id}`)),

  getDarkSites: async (lat: number, lon: number) =>
    request<DarkSite[]>(
      axiosInstance.get("/darksites/nearest", { params: { lat, lon } })
    ),

  // NEW METHODS
  login: async (email: string, password: string) =>
    request<{ token: string }>(
      axiosInstance.post("/users/login", { email, password })
    ),

  register: async (email: string, password: string, displayName: string) =>
    request<{ token: string }>(
      axiosInstance.post("/users/register", {
        email,
        password,
        displayName
      })
    ),

  registerDeviceToken: async (token: string, platform: string, authToken: string) =>
    request(
      axiosInstance.post(
        "/notifications/device-token",
        { token, platform },
        { headers: { Authorization: `Bearer ${authToken}` } }
      )
    )
};
