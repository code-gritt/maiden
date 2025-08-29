"use client";

import { create } from "zustand";

interface User {
  username: string;
  email: string;
  credits: number;
}

interface AuthState {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  login: async (email: string, password: string) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const response = await fetch(
        "https://maiden-backend.onrender.com/api/auth/login/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ email, password }),
          signal: controller.signal,
        }
      );
      clearTimeout(timeoutId);

      if (!response.ok) {
        const data = await response.json();
        console.error("Login failed:", data.message);
        return false;
      }

      console.log("Login successful");
      await useAuthStore.getState().fetchUser();
      return true;
    } catch (error) {
      console.error("Login error:", error);
      return false;
    }
  },
  logout: async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const response = await fetch(
        "https://maiden-backend.onrender.com/api/auth/logout/",
        {
          method: "POST",
          credentials: "include",
          signal: controller.signal,
        }
      );
      clearTimeout(timeoutId);
      if (response.ok) {
        console.log("Logout successful");
        set({ user: null });
      } else {
        console.error("Logout failed:", response.statusText);
      }
    } catch (error) {
      console.error("Logout error:", error);
    }
  },
  fetchUser: async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const response = await fetch(
        "https://maiden-backend.onrender.com/api/auth/profile/",
        {
          method: "GET",
          credentials: "include",
          signal: controller.signal,
        }
      );
      clearTimeout(timeoutId);

      if (!response.ok) {
        console.error("Fetch user failed:", response.statusText);
        set({ user: null });
        return;
      }

      const user = await response.json();
      console.log("User fetched:", user);
      set({ user });
    } catch (error) {
      console.error("Fetch user error:", error);
      set({ user: null });
    }
  },
}));
