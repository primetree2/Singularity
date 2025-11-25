// Listen for push events sent from the server (Web Push)
self.addEventListener("push", (event) => {
  // If the push message has no data, provide a fallback
  const payload = event.data ? event.data.json() : { title: "Singularity", body: "New update" };

  const title = payload.title || "Singularity";
  const options = {
    body: payload.body || "",
    icon: payload.icon || "/icons/icon-192.png",
    badge: payload.badge || "/icons/badge-72.png",
    data: {
      url: payload.url || "/",
      ...payload.data
    }
  };

  // Ensure the notification is shown while the service worker stays alive
  event.waitUntil(self.registration.showNotification(title, options));
});

// Handle clicks on notifications
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const targetUrl = (event.notification.data && event.notification.data.url) || "/";

  // Focus an existing window/tab with the app or open a new one
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url === targetUrl && "focus" in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
