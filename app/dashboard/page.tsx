"use client";

import React from "react";
import DashboardLayout from "./DashboardLayout";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/useAuthStore";

const DashboardPage = () => {
  const { user, fetchUser } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      fetchUser().then(() => {
        if (!useAuthStore.getState().user) {
          router.push("/signin");
        }
      });
    }
  }, [user, fetchUser, router]);

  if (!user) {
    return null; // Render nothing while checking auth
  }
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-4">Welcome to your Dashboard</h1>
      <div className="min-h-screen flex items-center justify-center">
        <div className="max-w-md w-full space-y-8">
          <h1 className="text-4xl font-bold">Welcome, {user.username}!</h1>
          <p>You have {user.credits} credits.</p>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
