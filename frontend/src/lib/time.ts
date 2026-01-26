import { formatInTimeZone } from "date-fns-tz";

const TZ = process.env.NEXT_PUBLIC_PROVIDER_TZ || "America/Bogota";

export function fmtDateTimeLocal(iso: string) {
  return formatInTimeZone(new Date(iso), TZ, "yyyy-MM-dd HH:mm");
}

export function fmtTimeLocal(iso: string) {
  return formatInTimeZone(new Date(iso), TZ, "HH:mm");
}

// Construye ISO con offset correcto usando Date local del navegador.
// (En Colombia normalmente -05:00, pero esto respeta el entorno del usuario.)
export function toIsoWithOffset(d: Date) {
  const pad = (n: number) => String(n).padStart(2, "0");
  const yyyy = d.getFullYear();
  const mm = pad(d.getMonth() + 1);
  const dd = pad(d.getDate());
  const hh = pad(d.getHours());
  const mi = pad(d.getMinutes());
  const ss = pad(d.getSeconds());

  const offsetMin = -d.getTimezoneOffset(); // minutos hacia UTC
  const sign = offsetMin >= 0 ? "+" : "-";
  const abs = Math.abs(offsetMin);
  const offH = pad(Math.floor(abs / 60));
  const offM = pad(abs % 60);

  return `${yyyy}-${mm}-${dd}T${hh}:${mi}:${ss}${sign}${offH}:${offM}`;
}
