"use client";

import React, { useState, useEffect } from "react";
import DashboardLayout from "./DashboardLayout";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/useAuthStore";

interface Pdf {
  id: string;
  file_name: string;
  file_url: string;
  uploaded_at: string;
}

const DashboardPage = () => {
  const { user, fetchUser } = useAuthStore();
  const router = useRouter();
  const [pdfs, setPdfs] = useState<Pdf[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!user) {
      fetchUser().then(() => {
        if (!useAuthStore.getState().user) {
          router.push("/signin");
        } else {
          fetchPdfs();
        }
      });
    } else {
      fetchPdfs();
    }
  }, [user, fetchUser, router]);

  const fetchPdfs = async () => {
    try {
      const response = await fetch(
        "https://maiden-backend.onrender.com/api/auth/pdf/list/",
        {
          method: "GET",
          credentials: "include",
        }
      );
      if (!response.ok) {
        throw new Error("Failed to fetch PDFs");
      }
      const data = await response.json();
      setPdfs(data);
    } catch (err) {
      console.error("Fetch PDFs error:", err);
      setError("Failed to load PDFs");
    }
  };

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "https://maiden-backend.onrender.com/api/auth/pdf/upload/",
        {
          method: "POST",
          credentials: "include",
          body: formData,
        }
      );
      const data = await response.json();
      if (!response.ok) {
        if (response.status === 403) {
          router.push("/pricing");
          return;
        }
        throw new Error(data.message || "Failed to upload PDF");
      }
      setPdfs([data, ...pdfs]);
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleCardClick = (pdfId: string) => {
    router.push(`/dashboard/${pdfId}`);
  };

  if (!user) {
    return null; // Render nothing while checking auth
  }

  return (
    <DashboardLayout>
      <div className="container mx-auto py-8">
        <h1 className="text-3xl font-bold mb-4">Welcome to your Dashboard</h1>
        <div className="mb-6">
          <h2 className="text-xl font-semibold">Welcome, {user.username}!</h2>
          <p>You have {user.credits} credits.</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <p className="text-lg font-medium">{pdfs.length}/5 PDFs uploaded</p>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-blue-600 h-2.5 rounded-full"
              style={{ width: `${(pdfs.length / 5) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Upload Button */}
        <div className="mb-6">
          <label className="btn bg-blue-600 text-white shadow-sm hover:bg-blue-700 cursor-pointer">
            {uploading ? "Uploading..." : "Upload PDF"}
            <input
              type="file"
              accept="application/pdf"
              className="hidden"
              onChange={handleUpload}
              disabled={uploading}
            />
          </label>
          {error && <p className="text-red-500 mt-2">{error}</p>}
        </div>

        {/* PDF Card Grid */}
        {pdfs.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {pdfs.map((pdf) => (
              <div
                key={pdf.id}
                className="bg-white shadow-md rounded-lg p-4 hover:shadow-lg transition cursor-pointer"
                onClick={() => handleCardClick(pdf.id)}
              >
                <h3 className="text-lg font-semibold truncate">
                  {pdf.file_name}
                </h3>
                <p className="text-sm text-gray-500">
                  Uploaded: {new Date(pdf.uploaded_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No PDFs uploaded yet.</p>
        )}
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
