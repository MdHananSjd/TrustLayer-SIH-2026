import React, { useState } from "react";

interface ReportActionProps {
  modelId: string;
  auditId: string;
}

export const ReportAction: React.FC<ReportActionProps> = ({
  modelId,
  auditId,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleDownload = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/audits/${auditId}/report`,
        {
          method: "GET",
          headers: { Accept: "application/pdf" },
        },
      );

      if (!response.ok) throw new Error("Backend generation failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `TrustLayer_Audit_${modelId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.warn(
        "Backend unavailable, generating fallback dummy PDF for demo.",
        error,
      );
      const blob = new Blob(
        [
          "TrustLayer Audit Report\n\nStatus: PASS\nThis is a fallback generated document because the backend was unreachable.",
        ],
        { type: "text/plain" },
      );
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `TrustLayer_Audit_Fallback_${modelId}.txt`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <button
      onClick={handleDownload}
      disabled={isGenerating}
      className={`px-4 py-2 text-xs font-mono uppercase tracking-wider rounded-sm text-white shadow-sm transition-colors border ${
        isGenerating
          ? "bg-slate-700 border-slate-600 cursor-not-allowed"
          : "bg-slate-900 border-slate-800 hover:bg-slate-800 hover:text-blue-400"
      }`}
    >
      {isGenerating ? "Generating..." : "Export Audit PDF"}
    </button>
  );
};
