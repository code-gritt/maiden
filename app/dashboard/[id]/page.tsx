"use client";

import React, { useState, useEffect, FormEvent } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuthStore } from "@/store/useAuthStore";
import DashboardLayout from "../DashboardLayout";

// Backend base URL from environment variable
const BACKEND_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface Pdf {
  id: string;
  file_name: string;
  file_url: string;
  uploaded_at: string;
  chat_messages: ChatMessage[];
}

interface ChatMessage {
  id: string;
  content: string;
  is_user_message: boolean;
  created_at: string;
}

const PdfViewPage = () => {
  const { user, fetchUser } = useAuthStore();
  const router = useRouter();
  const { id } = useParams();
  const [pdf, setPdf] = useState<Pdf | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string>("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);

  useEffect(() => {
    if (!user) {
      fetchUser().then(() => {
        if (!useAuthStore.getState().user) {
          router.push("/signin");
        } else {
          fetchPdf();
        }
      });
    } else {
      fetchPdf();
    }
  }, [user, fetchUser, router, id]);

  const fetchPdf = async () => {
    try {
      const response = await fetch(
        `https://maiden-backend.onrender.com/api/auth/pdf/${id}/`,
        {
          method: "GET",
          credentials: "include",
        }
      );
      if (!response.ok) {
        throw new Error("Failed to fetch PDF");
      }
      const data = await response.json();
      // Prepend backend base URL to file_url
      setPdf({
        ...data,
        file_url: `${BACKEND_BASE_URL}${data.file_url}`,
      });
      setChatMessages(data.chat_messages || []);
    } catch (err) {
      console.error("Fetch PDF error:", err);
      setError("Failed to load PDF");
    }
  };

  const handleChatSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `https://maiden-backend.onrender.com/api/auth/pdf/${id}/chat/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ message }),
        }
      );
      const data = await response.json();
      if (!response.ok) {
        if (response.status === 403) {
          router.push("/pricing");
          return;
        }
        throw new Error(data.message || "Failed to send message");
      }
      setChatMessages([...chatMessages, data.user_message, data.ai_response]);
      setMessage("");
      useAuthStore.getState().fetchUser(); // Update credits
    } catch (err: any) {
      setError(err.message || "Chat failed");
    } finally {
      setLoading(false);
    }
  };

  if (!user || !pdf) {
    return null;
  }

  return (
    <DashboardLayout>
      <div className="container mx-auto py-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: PDF Viewer */}
        <div className="bg-white shadow-md rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-4">{pdf.file_name}</h2>
          <div className="overflow-y-auto max-h-[80vh]">
            <iframe
              src={pdf.file_url}
              className="w-full h-[80vh]"
              title={pdf.file_name}
            />
          </div>
          {error && <p className="text-red-500 mt-2">{error}</p>}
        </div>

        {/* Right Column: Chat Interface */}
        <div className="bg-white shadow-md rounded-lg p-4 flex flex-col">
          <h2 className="text-xl font-semibold mb-4">Chat with PDF</h2>
          <div className="flex-1 overflow-y-auto max-h-[70vh] mb-4">
            {chatMessages.length > 0 ? (
              chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`mb-2 p-2 rounded-lg ${
                    msg.is_user_message
                      ? "bg-blue-100 text-right"
                      : "bg-gray-100 text-left"
                  }`}
                >
                  <p className="text-sm">{msg.content}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(msg.created_at).toLocaleString()}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-gray-500">Start chatting about your PDF!</p>
            )}
          </div>
          <form onSubmit={handleChatSubmit} className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask a question about the PDF..."
              className="form-input flex-1 py-2"
              disabled={loading}
            />
            <button
              type="submit"
              className="btn bg-blue-600 text-white shadow-sm hover:bg-blue-700 disabled:bg-gray-300"
              disabled={loading}
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </form>
          <p className="text-sm text-gray-500 mt-2">
            {user.credits} credits remaining (2 credits per message)
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default PdfViewPage;
