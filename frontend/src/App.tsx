import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import Layout from "./Layout";
import Login from "./pages/Login";
import Summary from "./pages/Summary";
import TalentAcquisition from "./pages/TalentAcquisition";
import Retention from "./pages/Retention";
import Performance from "./pages/Performance";
import Engagement from "./pages/Engagement";
import Compensation from "./pages/Compensation";
import Employees from "./pages/Employees";
import PowerBIEmbed from "./pages/PowerBIEmbed";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<Layout />}>
            <Route path="/" element={<Summary />} />
            <Route path="/talent-acquisition" element={<TalentAcquisition />} />
            <Route path="/retention" element={<Retention />} />
            <Route path="/performance" element={<Performance />} />
            <Route path="/engagement" element={<Engagement />} />
            <Route path="/compensation" element={<Compensation />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/powerbi" element={<PowerBIEmbed />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
