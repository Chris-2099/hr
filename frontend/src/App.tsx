import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import Layout from "./Layout";
import Landing from "./pages/Landing";
import Summary from "./pages/Summary";
import Employees from "./pages/Employees";
import PowerBI from "./pages/PowerBI";
import ComingSoon from "./pages/ComingSoon";

// No login gate here on purpose - zero login functionality during
// testing. Every route renders directly; the backend's DISABLE_AUTH
// auto-authenticates every request.
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<Layout />}>
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
