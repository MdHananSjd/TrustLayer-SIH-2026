import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx"; // Use .tsx if you are using TypeScript
import "./index.css"; // This imports your Tailwind CSS!

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
