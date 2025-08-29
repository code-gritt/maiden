"use client";

import React, { useState, useEffect, FormEvent } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuthStore } from "@/store/useAuthStore";
import dynamic from "next/dynamic";
import DashboardLayout from "../DashboardLayout";

// Dynamically import PDF Viewer (client-side only)
const PDFViewer = dynamic(() => import("../PdfViewer"), { ssr: false });

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
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      fetchUser().then(() => {
        if (!useAuthStore.getState().user) router.push("/signin");
        else fetchPdf();
      });
    } else fetchPdf();
  }, [user, fetchUser, router, id]);

  const fetchPdf = async () => {
    try {
      const res = await fetch(
        `https://maiden-backend.onrender.com/api/auth/pdf/${id}/`,
        { credentials: "include" }
      );
      if (!res.ok) throw new Error("Failed to fetch PDF");
      const data = await res.json();
      setPdf(data);
      setChatMessages(data.chat_messages || []);
    } catch (err) {
      console.error(err);
      setError("Failed to load PDF");
    }
  };

  const handleChatSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(
        `https://maiden-backend.onrender.com/api/auth/pdf/${id}/chat/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ message }),
        }
      );
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 403) router.push("/pricing");
        else throw new Error(data.message || "Chat failed");
      }
      setChatMessages([...chatMessages, data.user_message, data.ai_response]);
      setMessage("");
      fetchUser(); // refresh credits
    } catch (err: any) {
      setError(err.message || "Chat failed");
    } finally {
      setLoading(false);
    }
  };

  if (!user || !pdf) return null;

  return (
    <DashboardLayout>
      <div className="container mx-auto py-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: PDF Viewer */}
        <div className="bg-white shadow-md rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-4">{pdf.file_name}</h2>
          <PDFViewer file={pdf.file_url} />
          {error && <p className="text-red-500 mt-2">{error}</p>}
        </div>

        {/* Right Column: Chat */}
        <div className="bg-white shadow-md rounded-lg p-4 flex flex-col">
          <h2 className="text-xl font-semibold mb-4">Chat with PDF</h2>
          <div className="flex-1 overflow-y-auto max-h-[70vh] mb-4">
            {chatMessages.length ? (
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
              placeholder="Ask a question..."
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
