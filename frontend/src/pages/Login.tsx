import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <h1>HR Workforce &amp; Org Health</h1>
        <p className="subtitle">Sign in to view your dashboards.</p>

        {error && <div className="error-banner">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button className="primary" type="submit" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <button className="ghost" type="button" disabled title="Not configured yet — Microsoft Entra ID SSO is planned for a later phase.">
          Sign in with Microsoft (coming soon)
        </button>

        <div className="demo-hint">
          Demo accounts (password <code>Password123!</code>): admin@company.example (Admin),
          melissa.torres@company.example (Executive), stephanie.mchugh@company.example (HR Business Partner),
          charlie.osei@company.example (Recruiter), pat.reyes@company.example (Viewer).
        </div>
      </div>
    </div>
  );
}
