"use client";

import { Document, Page, pdfjs } from "react-pdf";
import { useState } from "react";

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

export default function PdfViewer({ file }: { file: string }) {
  const [numPages, setNumPages] = useState(0);
  const [pageNumber, setPageNumber] = useState(1);

  const onLoadSuccess = ({ numPages }: { numPages: number }) =>
    setNumPages(numPages);

  return (
    <div className="overflow-y-auto max-h-[80vh]">
      <Document
        file={file}
        onLoadSuccess={onLoadSuccess}
        className="flex justify-center"
      >
        <Page pageNumber={pageNumber} />
      </Document>
      <div className="flex justify-between mt-4">
        <button
          onClick={() => setPageNumber((p) => Math.max(p - 1, 1))}
          disabled={pageNumber <= 1}
          className="btn bg-blue-600 text-white disabled:bg-gray-300"
        >
          Previous
        </button>
        <p>
          Pages {pageNumber} of {numPages}
        </p>
        <button
          onClick={() => setPageNumber((p) => Math.min(p + 1, numPages))}
          disabled={pageNumber >= numPages}
          className="btn bg-blue-600 text-white disabled:bg-gray-300"
        >
          Next
        </button>
      </div>
    </div>
  );
}
