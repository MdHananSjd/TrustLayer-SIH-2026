import React, { createContext, useContext, useState, ReactNode } from "react";

interface DemoModeContextType {
  isOfflineMode: boolean;
  toggleOfflineMode: () => void;
}

const DemoModeContext = createContext<DemoModeContextType | undefined>(
  undefined,
);

export const DemoModeProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  // Default to offline mode for ultimate safety during the live demo
  const [isOfflineMode, setIsOfflineMode] = useState<boolean>(true);

  const toggleOfflineMode = () => {
    setIsOfflineMode((prev) => !prev);
  };

  return (
    <DemoModeContext.Provider value={{ isOfflineMode, toggleOfflineMode }}>
      {children}
    </DemoModeContext.Provider>
  );
};

export const useDemoMode = (): DemoModeContextType => {
  const context = useContext(DemoModeContext);
  if (!context) {
    throw new Error("useDemoMode must be used within a DemoModeProvider");
  }
  return context;
};
