import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import Layout from "./Layout";
import Login from "./pages/Login";
import Landing from "./pages/Landing";
import Summary from "./pages/Summary";
import Employees from "./pages/Employees";
import PowerBI from "./pages/PowerBI";
import ComingSoon from "./pages/ComingSoon";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex h-screen items-center justify-center text-sm text-slate-500">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            element={
              <RequireAuth>
                <Layout />
              </RequireAuth>
            }
          >
            <Route path="/" element={<Landing />} />
            <Route path="/executive-snapshot" element={<Summary />} />
            <Route path="/talent-acquisition" element={<ComingSoon title="Talent Acquisition" />} />
            <Route path="/retention" element={<ComingSoon title="Retention & Flight Risk" />} />
            <Route path="/performance" element={<ComingSoon title="Performance & Productivity" />} />
            <Route path="/engagement" element={<ComingSoon title="Engagement & Organizational Health" />} />
            <Route path="/compensation" element={<ComingSoon title="Compensation & Total Rewards" />} />
            <Route path="/succession" element={<ComingSoon title="Succession Planning" />} />
            <Route path="/workforce-planning" element={<ComingSoon title="Workforce Planning" />} />
            <Route path="/learning" element={<ComingSoon title="Learning & Capability" />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/power-bi" element={<PowerBI />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
