"use client";

import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Appointment, Me, Slot } from "@/lib/types";
import { fmtDateTimeLocal, fmtTimeLocal, toIsoWithOffset } from "@/lib/time";

import { AppNavbar } from "@/components/app-navbar";
import { EmptyState } from "@/components/empty-state";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";

function statusBadgeVariant(s: string) {
  if (s === "confirmed") return "default";
  if (s === "pending") return "secondary";
  return "outline";
}

export default function ClientDashboard() {
  const [me, setMe] = useState<Me | null>(null);

  // Book tab
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10)); // YYYY-MM-DD
  const slotMinutes = 30;

  const [slots, setSlots] = useState<Slot[]>([]);
  const [slotsLoading, setSlotsLoading] = useState(false);

  const [selectedSlot, setSelectedSlot] = useState<Slot | null>(null);
  const [desc, setDesc] = useState("Haircut");
  const [createLoading, setCreateLoading] = useState(false);

  // My appointments
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [apptsLoading, setApptsLoading] = useState(false);

  // Cancel/reschedule modals
  const [cancelId, setCancelId] = useState<string | null>(null);
  const [cancelLoading, setCancelLoading] = useState(false);

  const [reschedule, setReschedule] = useState<{ id: string } | null>(null);
  const [rsDate, setRsDate] = useState(date);
  const [rsSlots, setRsSlots] = useState<Slot[]>([]);
  const [rsSlotsLoading, setRsSlotsLoading] = useState(false);
  const [rsPick, setRsPick] = useState<Slot | null>(null);
  const [rsLoading, setRsLoading] = useState(false);

  const token = useMemo(() => getToken(), []);

  useEffect(() => {
    if (!token) {
      window.location.href = "/login";
      return;
    }

    (async () => {
      try {
        const m = await api<Me>("/me");
        if (m.role !== "client") {
          window.location.href = m.role === "provider" ? "/provider" : "/login";
          return;
        }
        setMe(m);
        await loadAppointments();
      } catch {
        // api() ya maneja 401
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function loadSlots(d = date) {
    setSlotsLoading(true);
    setSlots([]);
    try {
      const data = await api<Slot[]>(
        `/availability/slots?date=${encodeURIComponent(d)}&slot_minutes=${slotMinutes}`,
        { method: "GET" }
      );
      setSlots(data);
      if (data.length === 0) toast.message("No slots available for this day");
    } catch (err: any) {
      toast.error(err?.message || "Failed to load slots");
    } finally {
      setSlotsLoading(false);
    }
  }

  async function loadAppointments() {
    setApptsLoading(true);
    try {
      const data = await api<Appointment[]>("/me/appointments", { method: "GET" });
      setAppointments(data);
    } catch (err: any) {
      toast.error(err?.message || "Failed to load appointments");
    } finally {
      setApptsLoading(false);
    }
  }

  async function createAppointment() {
    if (!selectedSlot || createLoading) return;
    setCreateLoading(true);

    try {
      await api("/appointments", {
        method: "POST",
        body: JSON.stringify({
          start_at: selectedSlot.start_at,
          end_at: selectedSlot.end_at,
          description: desc?.trim() || null,
        }),
      });

      toast.success("Appointment created (pending)");
      setSelectedSlot(null);
      await loadAppointments();
    } catch (err: any) {
      if (err?.status === 409) toast.error("This time is no longer available");
      else if (err?.status === 422 && String(err?.message).includes("OUTSIDE_AVAILABILITY"))
        toast.error("Outside working hours");
      else if (err?.status === 422 && String(err?.message).includes("INVALID_TIME_RANGE"))
        toast.error("Invalid time range");
      else toast.error(err?.message || "Failed to create appointment");
    } finally {
      setCreateLoading(false);
    }
  }

  async function cancelAppointment(id: string) {
    if (cancelLoading) return;
    setCancelLoading(true);
    try {
      await api(`/me/appointments/${id}/cancel`, { method: "PATCH" });
      toast.success("Appointment canceled");
      setCancelId(null);
      await loadAppointments();
    } catch (err: any) {
      toast.error(err?.message || "Failed to cancel");
    } finally {
      setCancelLoading(false);
    }
  }

  async function loadRescheduleSlots(d: string) {
    setRsSlotsLoading(true);
    setRsSlots([]);
    setRsPick(null);
    try {
      const data = await api<Slot[]>(
        `/availability/slots?date=${encodeURIComponent(d)}&slot_minutes=${slotMinutes}`,
        { method: "GET" }
      );
      setRsSlots(data);
      if (data.length === 0) toast.message("No slots available for this day");
    } catch (err: any) {
      toast.error(err?.message || "Failed to load slots");
    } finally {
      setRsSlotsLoading(false);
    }
  }

  async function doReschedule() {
    if (!reschedule || !rsPick || rsLoading) return;
    setRsLoading(true);
    try {
      await api(`/me/appointments/${reschedule.id}/reschedule`, {
        method: "PATCH",
        body: JSON.stringify({
          start_at: rsPick.start_at,
          end_at: rsPick.end_at,
        }),
      });
      toast.success("Rescheduled");
      setReschedule(null);
      await loadAppointments();
    } catch (err: any) {
      if (err?.status === 409) toast.error("This time is no longer available");
      else toast.error(err?.message || "Failed to reschedule");
    } finally {
      setRsLoading(false);
    }
  }

  return (
    <div>
      <AppNavbar title="Client" email={me?.email} />

      <main className="mx-auto max-w-5xl px-4 py-6">
        <Tabs defaultValue="book" className="w-full">
          <TabsList>
            <TabsTrigger value="book">Book Appointment</TabsTrigger>
            <TabsTrigger value="mine">My Appointments</TabsTrigger>
          </TabsList>

          <TabsContent value="book" className="mt-6">
            <Card className="p-5 rounded-2xl">
              <div className="flex flex-col md:flex-row md:items-end gap-4 justify-between">
                <div className="grid gap-2">
                  <Label>Date</Label>
                  <Input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                  />
                </div>

                <div className="grid gap-2">
                  <Label>Slot minutes</Label>
                  <Input value={slotMinutes} disabled />
                </div>

                <Button onClick={() => loadSlots(date)} disabled={slotsLoading}>
                  {slotsLoading ? "Loading..." : "Load slots"}
                </Button>
              </div>

              <div className="mt-6">
                {slotsLoading ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {Array.from({ length: 8 }).map((_, i) => (
                      <Skeleton key={i} className="h-14 rounded-xl" />
                    ))}
                  </div>
                ) : slots.length === 0 ? (
                  <EmptyState
                    title="No slots available for this day"
                    description="Try another date."
                  />
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {slots.map((s) => (
                      <Card
                        key={s.start_at}
                        className="p-3 rounded-xl hover:shadow-sm transition cursor-pointer"
                        onClick={() => setSelectedSlot(s)}
                      >
                        <div className="text-lg font-semibold">
                          {fmtTimeLocal(s.start_at)}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {fmtTimeLocal(s.start_at)} - {fmtTimeLocal(s.end_at)}
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </Card>

            <Dialog open={!!selectedSlot} onOpenChange={(o) => !o && setSelectedSlot(null)}>
              <DialogContent className="rounded-2xl">
                <DialogHeader>
                  <DialogTitle>Confirm appointment</DialogTitle>
                </DialogHeader>

                {selectedSlot ? (
                  <div className="grid gap-4">
                    <Card className="p-4 rounded-2xl">
                      <div className="text-sm text-muted-foreground">Time</div>
                      <div className="font-medium">
                        {fmtDateTimeLocal(selectedSlot.start_at)} → {fmtDateTimeLocal(selectedSlot.end_at)}
                      </div>
                    </Card>

                    <div className="grid gap-2">
                      <Label>Description (optional)</Label>
                      <Textarea
                        value={desc}
                        onChange={(e) => setDesc(e.target.value)}
                        placeholder="Haircut"
                      />
                    </div>
                  </div>
                ) : null}

                <DialogFooter className="gap-2">
                  <Button variant="outline" onClick={() => setSelectedSlot(null)}>
                    Cancel
                  </Button>
                  <Button onClick={createAppointment} disabled={createLoading}>
                    {createLoading ? "Requesting..." : "Request appointment"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </TabsContent>

          <TabsContent value="mine" className="mt-6">
            <Card className="p-5 rounded-2xl">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-lg font-semibold">My appointments</div>
                  <div className="text-sm text-muted-foreground">
                    Pending can be canceled or rescheduled.
                  </div>
                </div>
                <Button variant="outline" onClick={loadAppointments} disabled={apptsLoading}>
                  Refresh
                </Button>
              </div>

              <div className="mt-6 grid gap-3">
                {apptsLoading ? (
                  <>
                    <Skeleton className="h-20 rounded-2xl" />
                    <Skeleton className="h-20 rounded-2xl" />
                    <Skeleton className="h-20 rounded-2xl" />
                  </>
                ) : appointments.length === 0 ? (
                  <EmptyState title="No appointments yet" description="Book your first slot." />
                ) : (
                  appointments.map((a) => (
                    <Card key={a.id} className="p-4 rounded-2xl">
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                        <div>
                          <div className="font-medium">
                            {fmtDateTimeLocal(a.start_at)} → {fmtDateTimeLocal(a.end_at)}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {a.description || "—"}
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Badge variant={statusBadgeVariant(a.status)}>{a.status}</Badge>

                          {a.status === "pending" ? (
                            <>
                              <Button variant="outline" onClick={() => setReschedule({ id: a.id })}>
                                Reschedule
                              </Button>
                              <Button variant="destructive" onClick={() => setCancelId(a.id)}>
                                Cancel
                              </Button>
                            </>
                          ) : null}
                        </div>
                      </div>
                    </Card>
                  ))
                )}
              </div>
            </Card>

            {/* Cancel modal */}
            <Dialog open={!!cancelId} onOpenChange={(o) => !o && setCancelId(null)}>
              <DialogContent className="rounded-2xl">
                <DialogHeader>
                  <DialogTitle>Cancel appointment?</DialogTitle>
                </DialogHeader>
                <div className="text-sm text-muted-foreground">
                  This action can’t be undone.
                </div>
                <DialogFooter className="gap-2">
                  <Button variant="outline" onClick={() => setCancelId(null)}>
                    Keep
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() => cancelId && cancelAppointment(cancelId)}
                    disabled={cancelLoading}
                  >
                    {cancelLoading ? "Canceling..." : "Cancel appointment"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Reschedule modal */}
            <Dialog open={!!reschedule} onOpenChange={(o) => !o && setReschedule(null)}>
              <DialogContent className="rounded-2xl">
                <DialogHeader>
                  <DialogTitle>Reschedule</DialogTitle>
                </DialogHeader>

                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <Label>New date</Label>
                    <div className="flex gap-2">
                      <Input
                        type="date"
                        value={rsDate}
                        onChange={(e) => setRsDate(e.target.value)}
                      />
                      <Button
                        variant="outline"
                        onClick={() => loadRescheduleSlots(rsDate)}
                        disabled={rsSlotsLoading}
                      >
                        {rsSlotsLoading ? "Loading..." : "Load slots"}
                      </Button>
                    </div>
                  </div>

                  {rsSlotsLoading ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {Array.from({ length: 8 }).map((_, i) => (
                        <Skeleton key={i} className="h-14 rounded-xl" />
                      ))}
                    </div>
                  ) : rsSlots.length === 0 ? (
                    <EmptyState title="No slots" description="Try another date." />
                  ) : (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {rsSlots.map((s) => {
                        const active = rsPick?.start_at === s.start_at;
                        return (
                          <Card
                            key={s.start_at}
                            className={`p-3 rounded-xl cursor-pointer transition ${
                              active ? "border-primary shadow-sm" : "hover:shadow-sm"
                            }`}
                            onClick={() => setRsPick(s)}
                          >
                            <div className="text-lg font-semibold">
                              {fmtTimeLocal(s.start_at)}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {fmtTimeLocal(s.start_at)} - {fmtTimeLocal(s.end_at)}
                            </div>
                          </Card>
                        );
                      })}
                    </div>
                  )}
                </div>

                <DialogFooter className="gap-2">
                  <Button variant="outline" onClick={() => setReschedule(null)}>
                    Close
                  </Button>
                  <Button onClick={doReschedule} disabled={!rsPick || rsLoading}>
                    {rsLoading ? "Saving..." : "Save new time"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
