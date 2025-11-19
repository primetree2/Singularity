import axios from "axios";
import { Event, DarkSite } from "@singularity/shared";


const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000"
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
    )
};
