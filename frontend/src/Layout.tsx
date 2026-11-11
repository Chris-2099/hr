import { useState } from "react";
import { Outlet, Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { Header } from "./components/layout/Header";
import { Sidebar } from "./components/layout/Sidebar";

// Frontend-side mirror of the backend's DISABLE_AUTH (app/config.py). Kept
// separate from `devInfo.disable_auth` (which requires a successful backend
// round trip) so the login screen stays off during testing even if the API
// is briefly unreachable - e.g. the backend not started yet. Flip both this
// and the backend flag back to re-enable real login later.
const FRONTEND_AUTH_DISABLED = import.meta.env.VITE_DISABLE_AUTH === "true";

export default function Layout() {
  const { user, loading, devInfo } = useAuth();
  const authDisabled = FRONTEND_AUTH_DISABLED || devInfo?.disable_auth === true;
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  if (loading) return <div className="loading">Loading…</div>;

  if (!user) {
    if (authDisabled) {
      return (
        <div className="login-shell">
          <div className="login-card">
            <h1>Can't reach the backend</h1>
            <p className="subtitle">
              Login is disabled for testing, but the API at{" "}
              <code>{import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}</code> didn't respond.
            </p>
            <p className="demo-hint">
              Start it with: <code>cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000</code>,
              then reload this page.
            </p>
          </div>
        </div>
      );
    }
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-full bg-slate-100">
      <Header onToggleSidebar={() => setSidebarCollapsed((prev) => !prev)} />
      <Sidebar collapsed={sidebarCollapsed} />

      {!sidebarCollapsed ? (
        <button
          type="button"
          aria-label="Close sidebar overlay"
          className="fixed inset-0 z-20 bg-slate-900/20 md:hidden"
          onClick={() => setSidebarCollapsed(true)}
        />
      ) : null}

      <main
        className={`min-h-full pt-14 transition-[padding] duration-300 ease-in-out pl-[68px] ${
          sidebarCollapsed ? "md:pl-[68px]" : "md:pl-64"
        }`}
      >
        <div className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
