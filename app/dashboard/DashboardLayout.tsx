"use client";
import Header from "@/components/ui/header";
import React, { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

const DashboardLayout = ({ children }: Props) => {
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="pt-20 px-4 max-w-6xl mx-auto">{children}</main>
    </div>
  );
};

export default DashboardLayout;
