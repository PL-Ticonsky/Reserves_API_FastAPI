import "./globals.css";
import { ClientToaster } from "@/components/client-toaster";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background text-foreground">
        {children}
        <ClientToaster />
      </body>
    </html>
  );
}
