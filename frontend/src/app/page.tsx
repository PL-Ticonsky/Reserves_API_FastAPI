import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function Landing() {
  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      <div className="flex flex-col gap-10">
        <div className="flex items-start justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm text-muted-foreground">
              <span className="h-2 w-2 rounded-full bg-primary" />
              MVP Booking — Single Provider
            </div>
            <h1 className="mt-4 text-4xl md:text-5xl font-semibold tracking-tight">
              Book your haircut in seconds
            </h1>
            <p className="mt-3 text-base md:text-lg text-muted-foreground max-w-xl">
              Pick a time slot, confirm, done. Simple experience for clients and a clean dashboard for the barber.
            </p>
            <div className="mt-6 flex gap-3">
              <Button asChild>
                <Link href="/login">Login</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/register">Create account</Link>
              </Button>
            </div>
          </div>

          <Card className="hidden md:block w-[360px] p-5 rounded-2xl shadow-sm">
            <div className="text-sm font-medium">How it works</div>
            <ul className="mt-3 text-sm text-muted-foreground space-y-2 list-disc pl-4">
              <li>Choose date → load slots</li>
              <li>Request appointment (pending)</li>
              <li>Barber confirms or cancels</li>
            </ul>
          </Card>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {[
            ["Working hours", "Availability is managed by the barber weekly."],
            ["Fast booking", "Slots are loaded from the backend in real time."],
            ["Clear status", "Pending, confirmed, canceled — always visible."],
          ].map(([t, d]) => (
            <Card key={t} className="p-5 rounded-2xl">
              <div className="font-medium">{t}</div>
              <div className="mt-1 text-sm text-muted-foreground">{d}</div>
            </Card>
          ))}
        </div>

        <Card className="p-6 rounded-2xl">
          <div className="font-medium">Mini FAQ</div>
          <div className="mt-3 grid gap-3 text-sm text-muted-foreground">
            <div>
              <span className="font-medium text-foreground">Do I need an account?</span>{" "}
              Yes, clients create an account to manage bookings.
            </div>
            <div>
              <span className="font-medium text-foreground">Can I reschedule?</span>{" "}
              Pending appointments can be rescheduled from “My Appointments”.
            </div>
          </div>
        </Card>
      </div>
    </main>
  );
}
