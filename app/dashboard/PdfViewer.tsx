"use client";

import { useState } from "react";
import dynamic from "next/dynamic";

// Only load client-side
const Document = dynamic(
  () => import("react-pdf/dist/esm/entry.webpack").then((mod) => mod.Document),
  { ssr: false }
);
const Page = dynamic(
  () => import("react-pdf/dist/esm/entry.webpack").then((mod) => mod.Page),
  { ssr: false }
);

import { pdfjs } from "react-pdf";
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

export default function PdfViewer({ fileUrl }: { fileUrl: string }) {
  const [numPages, setNumPages] = useState<number>(0);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  return (
    <Document file={fileUrl} onLoadSuccess={onDocumentLoadSuccess}>
      {Array.from({ length: numPages }, (_, index) => (
        <Page key={index} pageNumber={index + 1} />
      ))}
    </Document>
  );
}
