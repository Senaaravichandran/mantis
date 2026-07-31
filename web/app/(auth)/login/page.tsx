"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // In dev mode, auth is disabled — just redirect
      // In production, this would call Keycloak or the API's auth endpoint
      if (!email || !password) {
        setError("Please enter email and password");
        return;
      }

      // Simulate login for MVP
      localStorage.setItem("mantis_user", JSON.stringify({ email, name: "Operator" }));
      router.push("/");
    } catch {
      setError("Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDevLogin = () => {
    localStorage.setItem("mantis_user", JSON.stringify({ email: "dev@mantis.io", name: "Dev User" }));
    router.push("/");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-mantis-600 text-white font-bold text-xl">
            M
          </div>
          <CardTitle className="text-2xl">MANTIS</CardTitle>
          <p className="text-sm text-gray-500 mt-1">
            Infrastructure Intelligence Platform
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
            )}
            <div>
              <label className="text-sm font-medium text-gray-700">Email</label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="operator@municipality.gov"
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Password</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                className="mt-1"
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          <div className="mt-6 border-t pt-4">
            <Button variant="ghost" className="w-full text-sm" onClick={handleDevLogin}>
              Skip Login (Dev Mode)
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
