import React from "react";
import { DemoModeProvider } from "./context/DemoModeContext";
import { DemoToolbar } from "./components/DemoToolbar";
import AuditDashboard from "./pages/AuditDashboard";

function App() {
  return (
    <DemoModeProvider>
      <div className="flex flex-col min-h-screen bg-gray-50 font-sans text-gray-900">
        {/* Presentation Fallback Toolbar */}
        <DemoToolbar />

        {/* Main Application Area */}
        <main className="flex-grow w-full">
          <AuditDashboard />
        </main>

        {/* Footer Polish */}
        <footer className="bg-white border-t border-gray-200 py-6 text-center text-sm text-gray-500">
          <p>
            TrustLayer Continuous Responsible AI Assurance • Smart India
            Hackathon 2026
          </p>
        </footer>
      </div>
    </DemoModeProvider>
  );
}

export default App;
