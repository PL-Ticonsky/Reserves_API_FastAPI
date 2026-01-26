"use client";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { clearToken } from "@/lib/auth";

export function AppNavbar({
  title = "Booking",
  email,
}: {
  title?: string;
  email?: string;
}) {
  return (
    <div className="sticky top-0 z-20 bg-background/80 backdrop-blur border-b">
      <div className="mx-auto max-w-5xl px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-primary/10 border" />
          <div className="font-semibold">{title}</div>
        </div>
        <div className="flex items-center gap-3">
          {email ? <div className="text-sm text-muted-foreground">{email}</div> : null}
          <Separator orientation="vertical" className="h-6" />
          <Button
            variant="outline"
            onClick={() => {
              clearToken();
              window.location.href = "/login";
            }}
          >
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
}
