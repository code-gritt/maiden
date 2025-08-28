"use client";
import { create } from "zustand";

interface User {
  id: number;
  name: string;
  email: string;
  credits: number;
}

interface AuthState {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  fetchProfile: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,

  login: async (email, password) => {
    try {
      const res = await fetch(
        "https://maiden-backend.onrender.com/api/auth/login/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        }
      );

      if (!res.ok) return false;

      const data = await res.json();
      set({ token: data.token });
      await get().fetchProfile();
      return true;
    } catch (err) {
      console.error("Login failed", err);
      return false;
    }
  },

  fetchProfile: async () => {
    const { token } = get();
    if (!token) return;

    try {
      const res = await fetch(
        "https://maiden-backend.onrender.com/api/auth/profile/",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (res.ok) {
        const data = await res.json();
        set({ user: data });
      }
    } catch (err) {
      console.error("Failed to fetch profile", err);
    }
  },

  logout: () => set({ user: null, token: null }),
}));
