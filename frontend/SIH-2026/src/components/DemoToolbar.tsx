import React from "react";
import { useDemoMode } from "../context/DemoModeContext";
import { Server, ServerOff, ShieldCheck } from "lucide-react";

export const DemoToolbar: React.FC = () => {
  const { isOfflineMode, toggleOfflineMode } = useDemoMode();

  return (
    <div
      className={`w-full px-4 py-2 flex items-center justify-between text-xs font-bold uppercase tracking-wider transition-colors duration-300 ${isOfflineMode ? "bg-yellow-400 text-yellow-900" : "bg-emerald-600 text-white"}`}
    >
      <div className="flex items-center space-x-2">
        <ShieldCheck size={16} />
        <span>AegisAI Governance Platform • SIH 2026</span>
      </div>

      <div className="flex items-center space-x-4">
        <span className="flex items-center space-x-1">
          {isOfflineMode ? <ServerOff size={14} /> : <Server size={14} />}
          <span>
            Status:{" "}
            {isOfflineMode
              ? "Offline Fallback (Cached Data)"
              : "Live API Connected"}
          </span>
        </span>

        <button
          onClick={toggleOfflineMode}
          className={`px-3 py-1 rounded shadow-sm transition-colors ${isOfflineMode ? "bg-yellow-500 hover:bg-yellow-600 text-yellow-900" : "bg-emerald-700 hover:bg-emerald-800 text-white"}`}
        >
          Toggle Demo Mode
        </button>
      </div>
    </div>
  );
};
