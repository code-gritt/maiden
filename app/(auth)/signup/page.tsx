"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SignUp() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const username = formData.get("username") as string;
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const response = await fetch(
        "https://maiden-backend.onrender.com/api/auth/register/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ username, email, password }),
          signal: controller.signal,
        }
      );
      clearTimeout(timeoutId);

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || "Registration failed");
      }

      console.log("Registration successful:", data);
      router.push("/signin");
      router.refresh();
    } catch (err: any) {
      setError(err.message || "Server may be unresponsive");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full space-y-8">
        <div className="mb-10">
          <h1 className="text-4xl font-bold">Create your account</h1>
        </div>
        {error && <p className="text-red-500 text-center">{error}</p>}
        {loading && (
          <div className="fixed inset-0  bg-opacity-10 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-600"></div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label
                className="mb-1 block text-sm font-medium text-gray-700"
                htmlFor="username"
              >
                Username
              </label>
              <input
                id="username"
                name="username"
                className="form-input w-full py-2"
                type="text"
                placeholder="coreybarker"
                required
              />
            </div>
            <div>
              <label
                className="mb-1 block text-sm font-medium text-gray-700"
                htmlFor="email"
              >
                Email
              </label>
              <input
                id="email"
                name="email"
                className="form-input w-full py-2"
                type="email"
                placeholder="corybarker@email.com"
                required
              />
            </div>
            <div>
              <label
                className="mb-1 block text-sm font-medium text-gray-700"
                htmlFor="password"
              >
                Password
              </label>
              <input
                id="password"
                name="password"
                className="form-input w-full py-2"
                type="password"
                autoComplete="on"
                placeholder="••••••••"
                required
              />
            </div>
          </div>
          <div className="mt-6 space-y-3">
            <button
              type="submit"
              disabled={loading}
              className="btn w-full bg-blue-600 text-white shadow-sm hover:bg-blue-700"
            >
              {loading ? "Registering..." : "Register"}
            </button>
          </div>
        </form>
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            By signing up, you agree to the{" "}
            <a
              className="whitespace-nowrap font-medium text-gray-700 underline hover:no-underline"
              href="#0"
            >
              Terms of Service
            </a>{" "}
            and{" "}
            <a
              className="whitespace-nowrap font-medium text-gray-700 underline hover:no-underline"
              href="#0"
            >
              Privacy Policy
            </a>
            .
          </p>
        </div>
      </div>
    </div>
  );
}
