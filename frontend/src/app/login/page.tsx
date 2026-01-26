"use client";

import { useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { setToken } from "@/lib/auth";
import { Me } from "@/lib/types";

import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (loading) return;

    setLoading(true);
    try {
      const res = await api<{ access_token: string; token_type: string }>(
        "/auth/login",
        {
          method: "POST",
          auth: false,
          body: JSON.stringify({ email, password }),
        }
      );

      setToken(res.access_token);

      const me = await api<Me>("/me", { method: "GET" });

      toast.success("Logged in");
      window.location.href = me.role === "provider" ? "/provider" : "/client";
    } catch (err: any) {
      const code = err?.code || err?.raw?.detail;
      if (err?.status === 401 && String(code).includes("INVALID_CREDENTIALS")) {
        toast.error("Invalid email or password");
      } else {
        toast.error(err?.message || "Login failed");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md px-4 py-12">
      <Card className="p-6 rounded-2xl">
        <div className="text-xl font-semibold">Login</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Access your dashboard.
        </div>

        <form className="mt-6 grid gap-4" onSubmit={onSubmit}>
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" value={password} onChange={(e) => setPassword(e.target.value)} type="password" required />
          </div>

          <Button type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </Button>

          <div className="text-sm text-muted-foreground">
            No account?{" "}
            <Link className="text-foreground underline" href="/register">
              Create one
            </Link>
          </div>
        </form>
      </Card>
    </main>
  );
}
