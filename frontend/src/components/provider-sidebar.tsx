"use client";

import { Button } from "@/components/ui/button";

export function ProviderSidebar({
  active,
  onChange,
}: {
  active: "appointments" | "availability";
  onChange: (v: "appointments" | "availability") => void;
}) {
  return (
    <div className="w-full md:w-56 md:sticky md:top-16 md:self-start">
      <div className="grid gap-2 p-4 border rounded-2xl bg-card">
        <Button
          variant={active === "appointments" ? "default" : "outline"}
          className="justify-start"
          onClick={() => onChange("appointments")}
        >
          Appointments
        </Button>
        <Button
          variant={active === "availability" ? "default" : "outline"}
          className="justify-start"
          onClick={() => onChange("availability")}
        >
          Availability
        </Button>
      </div>
    </div>
  );
}
