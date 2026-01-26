export type Role = "client" | "provider";

export type Me = {
  id: string;
  email: string;
  role: Role;
};

export type Slot = {
  start_at: string; // ISO
  end_at: string;   // ISO
};

export type AppointmentStatus = "pending" | "confirmed" | "canceled";

export type Appointment = {
  id: string;
  start_at: string;
  end_at: string;
  description?: string | null;
  status: AppointmentStatus;
  client_id?: string; // provider view (MVP)
};
