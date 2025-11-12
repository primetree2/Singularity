"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function NotificationToggle() {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("notifyEnabled");
    if (stored) setEnabled(stored === "true");
  }, []);

  const toggle = () => {
    const newState = !enabled;
    setEnabled(newState);
    localStorage.setItem("notifyEnabled", String(newState));
  };

  return (
    <Button
      variant={enabled ? "default" : "outline"}
      size="sm"
      onClick={toggle}
      className="text-xs"
    >
      {enabled ? "🔔 Notifications On" : "🔕 Enable Notifications"}
    </Button>
  );
}
