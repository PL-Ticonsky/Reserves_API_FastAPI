"use client";

import { useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { api } from "@/lib/api";

import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (loading) return;

    setLoading(true);
    try {
      await api("/auth/register", {
        method: "POST",
        auth: false,
        body: JSON.stringify({ email, password }),
      });

      toast.success("Account created. Please login.");
      window.location.href = "/login";
    } catch (err: any) {
      toast.error(err?.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md px-4 py-12">
      <Card className="p-6 rounded-2xl">
        <div className="text-xl font-semibold">Create account</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Client accounts only (MVP).
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
            {loading ? "Creating..." : "Create"}
          </Button>

          <div className="text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link className="text-foreground underline" href="/login">
              Login
            </Link>
          </div>
        </form>
      </Card>
    </main>
  );
}
