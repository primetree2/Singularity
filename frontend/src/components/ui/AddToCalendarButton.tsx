"use client";

import { Button } from "@/components/ui/button";

type AddToCalendarButtonProps = {
  title: string;
  start: string; // ISO string
  end: string;
  description?: string;
};

export default function AddToCalendarButton({
  title,
  start,
  end,
  description = "Satellite viewing event",
}: AddToCalendarButtonProps) {
  const handleDownload = () => {
    const content = `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:${title}
DTSTART:${formatICSDate(start)}
DTEND:${formatICSDate(end)}
DESCRIPTION:${description}
END:VEVENT
END:VCALENDAR`;
    const blob = new Blob([content], { type: "text/calendar;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${title.replace(/\s+/g, "_")}.ics`;
    link.click();
  };

  return (
    <Button variant="outline" size="sm" onClick={handleDownload} className="text-xs">
      📅 Add to Calendar
    </Button>
  );
}

function formatICSDate(dateStr: string) {
  const date = new Date(dateStr);
  return date
    .toISOString()
    .replace(/[-:]/g, "")
    .split(".")[0] + "Z";
}
