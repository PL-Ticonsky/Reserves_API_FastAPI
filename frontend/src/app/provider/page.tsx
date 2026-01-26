"use client";

import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Appointment, Me } from "@/lib/types";
import { fmtDateTimeLocal } from "@/lib/time";

import { AppNavbar } from "@/components/app-navbar";
import { ProviderSidebar } from "@/components/provider-sidebar";
import { EmptyState } from "@/components/empty-state";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";

type StatusFilter = "pending" | "confirmed" | "canceled";

function statusBadgeVariant(s: string) {
  if (s === "confirmed") return "default";
  if (s === "pending") return "secondary";
  return "outline";
}

type AvailabilityBlock = {
  weekday: number; // 0=Mon ... 6=Sun (puedes adaptar si tu backend define otro mapping)
  start_time: string; // HH:MM
  end_time: string;   // HH:MM
};

const weekdays = [
  { k: 0, label: "Mon" },
  { k: 1, label: "Tue" },
  { k: 2, label: "Wed" },
  { k: 3, label: "Thu" },
  { k: 4, label: "Fri" },
  { k: 5, label: "Sat" },
  { k: 6, label: "Sun" },
];

export default function ProviderDashboard() {
  const [me, setMe] = useState<Me | null>(null);
  const token = useMemo(() => getToken(), []);

  const [view, setView] = useState<"appointments" | "availability">("appointments");

  // appointments
  const [status, setStatus] = useState<StatusFilter>("pending");
  const [from, setFrom] = useState<string>("");
  const [to, setTo] = useState<string>("");

  const [items, setItems] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);

  const [cancel, setCancel] = useState<{ id: string } | null>(null);
  const [cancelReason, setCancelReason] = useState("");
  const [cancelLoading, setCancelLoading] = useState(false);

  const [confirmLoadingId, setConfirmLoadingId] = useState<string | null>(null);

  // availability
  const [blocks, setBlocks] = useState<AvailabilityBlock[]>([
    { weekday: 0, start_time: "09:00", end_time: "18:00" },
    { weekday: 1, start_time: "09:00", end_time: "18:00" },
    { weekday: 2, start_time: "09:00", end_time: "18:00" },
    { weekday: 3, start_time: "09:00", end_time: "18:00" },
    { weekday: 4, start_time: "09:00", end_time: "18:00" },
  ]);
  const [saveAvailLoading, setSaveAvailLoading] = useState(false);

  useEffect(() => {
    if (!token) {
      window.location.href = "/login";
      return;
    }

    (async () => {
      try {
        const m = await api<Me>("/me");
        if (m.role !== "provider") {
          window.location.href = m.role === "client" ? "/client" : "/login";
          return;
        }
        setMe(m);
        await loadAppointments();
      } catch {
        // api() maneja 401
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function loadAppointments() {
    setLoading(true);
    try {
      const qs = new URLSearchParams();
      qs.set("status_", status);
      if (from) qs.set("from", from);
      if (to) qs.set("to", to);

      const data = await api<Appointment[]>(
        `/barber/appointments?${qs.toString()}`,
        { method: "GET" }
      );
      setItems(data);
    } catch (err: any) {
      toast.error(err?.message || "Failed to load appointments");
    } finally {
      setLoading(false);
    }
  }

  async function confirm(id: string) {
    if (confirmLoadingId) return;
    setConfirmLoadingId(id);
    try {
      await api(`/barber/appointments/${id}/confirm`, { method: "PATCH" });
      toast.success("Confirmed");
      await loadAppointments();
    } catch (err: any) {
      toast.error(err?.message || "Failed to confirm");
    } finally {
      setConfirmLoadingId(null);
    }
  }

  async function cancelAppointment() {
    if (!cancel || cancelLoading) return;
    setCancelLoading(true);
    try {
      await api(`/barber/appointments/${cancel.id}/cancel`, {
        method: "PATCH",
        body: JSON.stringify(cancelReason?.trim() ? { reason: cancelReason.trim() } : {}),
      });
      toast.success("Canceled");
      setCancel(null);
      setCancelReason("");
      await loadAppointments();
    } catch (err: any) {
      toast.error(err?.message || "Failed to cancel");
    } finally {
      setCancelLoading(false);
    }
  }

  function addBlock(day: number) {
    setBlocks((prev) => [...prev, { weekday: day, start_time: "09:00", end_time: "18:00" }]);
  }

  function updateBlock(idx: number, patch: Partial<AvailabilityBlock>) {
    setBlocks((prev) => prev.map((b, i) => (i === idx ? { ...b, ...patch } : b)));
  }

  function removeBlock(idx: number) {
    setBlocks((prev) => prev.filter((_, i) => i !== idx));
  }

  async function saveAvailability() {
    if (saveAvailLoading) return;

    // validación mínima UX
    for (const b of blocks) {
      if (!b.start_time || !b.end_time) {
        toast.error("Fill all start/end times");
        return;
      }
      if (b.start_time >= b.end_time) {
        toast.error("Start time must be before end time");
        return;
      }
    }

    setSaveAvailLoading(true);
    try {
      await api("/barber/availability/bulk", {
        method: "POST",
        body: JSON.stringify(blocks),
      });
      toast.success("Availability saved");
    } catch (err: any) {
      toast.error(err?.message || "Failed to save availability");
    } finally {
      setSaveAvailLoading(false);
    }
  }

  return (
    <div>
      <AppNavbar title="Provider" email={me?.email} />

      <main className="mx-auto max-w-5xl px-4 py-6">
        <div className="flex flex-col md:flex-row gap-4">
          <ProviderSidebar active={view} onChange={setView} />

          <div className="flex-1">
            {view === "appointments" ? (
              <Card className="p-5 rounded-2xl">
                <div className="flex flex-col gap-4">
                  <div>
                    <div className="text-lg font-semibold">Appointments</div>
                    <div className="text-sm text-muted-foreground">
                      Filter by status and optional date range.
                    </div>
                  </div>

                  <div className="grid md:grid-cols-4 gap-3 items-end">
                    <div className="grid gap-2">
                      <Label>Status</Label>
                      <Select value={status} onValueChange={(v) => setStatus(v as StatusFilter)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="pending">pending</SelectItem>
                          <SelectItem value="confirmed">confirmed</SelectItem>
                          <SelectItem value="canceled">canceled</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="grid gap-2">
                      <Label>From (optional)</Label>
                      <Input value={from} onChange={(e) => setFrom(e.target.value)} placeholder="YYYY-MM-DD" />
                    </div>

                    <div className="grid gap-2">
                      <Label>To (optional)</Label>
                      <Input value={to} onChange={(e) => setTo(e.target.value)} placeholder="YYYY-MM-DD" />
                    </div>

                    <Button onClick={loadAppointments} disabled={loading}>
                      {loading ? "Loading..." : "Apply"}
                    </Button>
                  </div>

                  <div className="mt-2 grid gap-3">
                    {loading ? (
                      <>
                        <Skeleton className="h-20 rounded-2xl" />
                        <Skeleton className="h-20 rounded-2xl" />
                        <Skeleton className="h-20 rounded-2xl" />
                      </>
                    ) : items.length === 0 ? (
                      <EmptyState title="No appointments yet" />
                    ) : (
                      items.map((a) => (
                        <Card key={a.id} className="p-4 rounded-2xl">
                          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                            <div>
                              <div className="font-medium">
                                {fmtDateTimeLocal(a.start_at)} → {fmtDateTimeLocal(a.end_at)}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                client_id: {a.client_id || "—"} · {a.description || "—"}
                              </div>
                            </div>

                            <div className="flex items-center gap-2">
                              <Badge variant={statusBadgeVariant(a.status)}>{a.status}</Badge>

                              {a.status === "pending" ? (
                                <>
                                  <Button
                                    onClick={() => confirm(a.id)}
                                    disabled={confirmLoadingId === a.id}
                                  >
                                    {confirmLoadingId === a.id ? "Confirming..." : "Confirm"}
                                  </Button>
                                  <Button
                                    variant="destructive"
                                    onClick={() => setCancel({ id: a.id })}
                                  >
                                    Cancel
                                  </Button>
                                </>
                              ) : a.status === "confirmed" ? (
                                <Button
                                  variant="destructive"
                                  onClick={() => setCancel({ id: a.id })}
                                >
                                  Cancel
                                </Button>
                              ) : null}
                            </div>
                          </div>
                        </Card>
                      ))
                    )}
                  </div>
                </div>

                <Dialog open={!!cancel} onOpenChange={(o) => !o && setCancel(null)}>
                  <DialogContent className="rounded-2xl">
                    <DialogHeader>
                      <DialogTitle>Cancel appointment</DialogTitle>
                    </DialogHeader>

                    <div className="grid gap-2">
                      <Label>Reason (optional)</Label>
                      <Textarea
                        value={cancelReason}
                        onChange={(e) => setCancelReason(e.target.value)}
                        placeholder="Client no-show, etc."
                      />
                    </div>

                    <DialogFooter className="gap-2">
                      <Button variant="outline" onClick={() => setCancel(null)}>
                        Close
                      </Button>
                      <Button
                        variant="destructive"
                        onClick={cancelAppointment}
                        disabled={cancelLoading}
                      >
                        {cancelLoading ? "Canceling..." : "Cancel"}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </Card>
            ) : (
              <Card className="p-5 rounded-2xl">
                <div>
                  <div className="text-lg font-semibold">Availability</div>
                  <div className="text-sm text-muted-foreground">
                    Weekly blocks. Save sends a full bulk list.
                  </div>
                </div>

                <div className="mt-6 grid gap-4">
                  {weekdays.map((d) => {
                    const dayBlocks = blocks
                      .map((b, idx) => ({ b, idx }))
                      .filter((x) => x.b.weekday === d.k);

                    return (
                      <Card key={d.k} className="p-4 rounded-2xl">
                        <div className="flex items-center justify-between">
                          <div className="font-medium">{d.label}</div>
                          <Button variant="outline" onClick={() => addBlock(d.k)}>
                            Add block
                          </Button>
                        </div>

                        <div className="mt-3 grid gap-2">
                          {dayBlocks.length === 0 ? (
                            <div className="text-sm text-muted-foreground">
                              No blocks for this day.
                            </div>
                          ) : (
                            dayBlocks.map(({ b, idx }) => (
                              <div key={idx} className="grid grid-cols-12 gap-2 items-end">
                                <div className="col-span-5">
                                  <Label>Start</Label>
                                  <Input
                                    value={b.start_time}
                                    onChange={(e) => updateBlock(idx, { start_time: e.target.value })}
                                    placeholder="09:00"
                                  />
                                </div>
                                <div className="col-span-5">
                                  <Label>End</Label>
                                  <Input
                                    value={b.end_time}
                                    onChange={(e) => updateBlock(idx, { end_time: e.target.value })}
                                    placeholder="18:00"
                                  />
                                </div>
                                <div className="col-span-2">
                                  <Button
                                    variant="destructive"
                                    className="w-full"
                                    onClick={() => removeBlock(idx)}
                                  >
                                    Remove
                                  </Button>
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      </Card>
                    );
                  })}
                </div>

                <div className="mt-6 flex justify-end">
                  <Button onClick={saveAvailability} disabled={saveAvailLoading}>
                    {saveAvailLoading ? "Saving..." : "Save availability"}
                  </Button>
                </div>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
