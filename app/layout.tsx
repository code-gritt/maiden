import { GoogleOAuthProvider } from "@react-oauth/google";
import "./css/style.css";
import { Inter } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata = {
  title: "mAIden – Chat with Your PDFs",
  description:
    "mAIden is your AI-powered assistant. Upload PDFs, chat with your documents using Google Gemini, export and download your conversations.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body
        className={`${inter.variable} bg-gray-50 font-inter tracking-tight text-gray-900 antialiased`}
      >
        <div className="flex min-h-screen flex-col overflow-hidden supports-[overflow:clip]:overflow-clip">
          <GoogleOAuthProvider
            clientId={
              process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ||
              "956326249480-h0aqid5tklb077n2kk8gsbm8arpjod00.apps.googleusercontent.com"
            }
          >
            {children}
          </GoogleOAuthProvider>
        </div>
      </body>
    </html>
  );
}
