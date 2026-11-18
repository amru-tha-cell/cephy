import React from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import AnalysisWorkspace from "./pages/AnalysisWorkspace";
import Reports from "./pages/Reports";
import Analytics from "./pages/Analytics";
import Navigation from "./components/Navigation";
import useCase from "./hooks/useCase";

function AppContent() {
  // One shared case state for the entire application.
  const caseController = useCase();

  return (
    <div className="app">
      <Navigation />

      <main className="app-main">
        <Routes>
          <Route
            path="/"
            element={
              <Dashboard caseController={caseController} />
            }
          />

          <Route
            path="/analysis"
            element={
              <AnalysisWorkspace caseController={caseController} />
            }
          />

          <Route
            path="/reports"
            element={
              <Reports caseController={caseController} />
            }
          />

          <Route
            path="/analytics"
            element={
              <Analytics caseController={caseController} />
            }
          />

          <Route
            path="*"
            element={<Navigate to="/" replace />}
          />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;