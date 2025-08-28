"use client";

import Link from "next/link";
import Logo from "./logo";
import { useAuthStore } from "@/store/useAuthStore";

export default function Header() {
  const { user, logout } = useAuthStore();

  const initials = user
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
    : "";

  return (
    <header className="fixed top-2 z-30 w-full md:top-6">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="relative flex h-14 items-center justify-between gap-3 rounded-2xl bg-white/90 px-3 shadow-lg">
          {/* Branding */}
          <div className="flex flex-1 items-center">
            <Logo />
          </div>

          {/* Right side */}
          <ul className="flex flex-1 items-center justify-end gap-3">
            {!user ? (
              <>
                <li>
                  <Link
                    href="/signin"
                    className="btn-sm bg-white text-gray-800 shadow-sm hover:bg-gray-50"
                  >
                    Login
                  </Link>
                </li>
                <li>
                  <Link
                    href="/signup"
                    className="btn-sm bg-gray-800 text-gray-200 shadow-sm hover:bg-gray-900"
                  >
                    Register
                  </Link>
                </li>
              </>
            ) : (
              <>
                <li>
                  <Link
                    href="/dashboard"
                    className="btn-sm bg-blue-600 text-white hover:bg-blue-700"
                  >
                    Dashboard
                  </Link>
                </li>
                <li className="text-gray-700 font-medium">
                  Credits: {user.credits}
                </li>
                <li>
                  <div className="w-8 h-8 rounded-full bg-gray-800 text-white flex items-center justify-center font-bold">
                    {initials}
                  </div>
                </li>
                <li>
                  <button
                    onClick={logout}
                    className="btn-sm bg-red-600 text-white hover:bg-red-700"
                  >
                    Logout
                  </button>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </header>
  );
}
