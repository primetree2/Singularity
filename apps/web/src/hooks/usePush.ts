import { useState, useEffect } from "react";
import axios from "axios";

export default function usePush() {
  const [isSupported, setIsSupported] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null);

  useEffect(() => {
    const supported =
      typeof window !== "undefined" &&
      "serviceWorker" in navigator &&
      "PushManager" in window;

    setIsSupported(supported);

    if (!supported) return;

    const registerSW = async () => {
      try {
        const reg = await navigator.serviceWorker.register("/sw.js");
        setRegistration(reg);

        const sub = await reg.pushManager.getSubscription();
        setIsSubscribed(!!sub);
      } catch {
        setIsSupported(false);
      }
    };

    registerSW();
  }, []);

  const subscribe = async () => {
    if (!registration) return;

    try {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") return;

      // TODO: Requires VAPID keys for production
      const sub = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: undefined
      });

      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/notifications/device-token`,
        { subscription: sub },
        {
          headers: {
            Authorization: `Bearer token`
          }
        }
      );

      setIsSubscribed(true);
    } catch {
      setIsSubscribed(false);
    }
  };

  const unsubscribe = async () => {
    if (!registration) return;

    try {
      const sub = await registration.pushManager.getSubscription();
      if (sub) await sub.unsubscribe();
      setIsSubscribed(false);
    } catch {
      setIsSubscribed(true);
    }
  };

  return {
    isSupported,
    isSubscribed,
    subscribe,
    unsubscribe
  };
}
