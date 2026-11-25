import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { signInWithMicrosoft } from "../msal";

// DEV-ONLY shortcut: logs straight in as the seeded demo admin account
// (admin/password) so testing doesn't require typing credentials every
// time. This is a real login call, not an auth bypass - it works whether
// the backend's DISABLE_AUTH is on or off. Remove this button (and
// DEMO_LOGIN_ENABLED) before any real deployment.
const DEMO_LOGIN_ENABLED = true;
const DEMO_EMAIL = "admin";
const DEMO_PASSWORD = "password";

export default function Login() {
  const { login, authConfig } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const ssoEnabled = authConfig.auth_mode === "entra" || authConfig.auth_mode === "hybrid";

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      await login(email, password);
      navigate("/");
    } catch {
      setFormError("Invalid email or password.");
    } finally {
      setSubmitting(false);
    }
  }

  async function onDemoLogin() {
    setSubmitting(true);
    setFormError(null);
    try {
      await login(DEMO_EMAIL, DEMO_PASSWORD);
      navigate("/");
    } catch {
      setFormError("Demo login failed - is the backend seeded and reachable?");
    } finally {
      setSubmitting(false);
    }
  }

  async function onMicrosoftSignIn() {
    if (!ssoEnabled) return;
    await signInWithMicrosoft();
    // TODO once AUTH_MODE is flipped on: exchange the MSAL result for our
    // own backend session via /api/auth/entra/callback, then navigate("/").
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
      <div
        className="pointer-events-none fixed inset-0 opacity-40"
        style={{
          background:
            "radial-gradient(600px circle at 20% 20%, rgba(79,70,229,0.25), transparent 60%), radial-gradient(600px circle at 80% 80%, rgba(14,165,233,0.2), transparent 60%)",
        }}
      />

      <div className="relative w-full max-w-sm rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl backdrop-blur">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-base font-bold text-white">
          H
        </div>
        <h1 className="mt-4 text-xl font-semibold tracking-tight text-white">HR Workforce Dashboard</h1>
        <p className="mt-1 text-sm text-slate-400">Sign in to continue.</p>

        {DEMO_LOGIN_ENABLED && (
          <>
            <button
              type="button"
              onClick={onDemoLogin}
              disabled={submitting}
              className="mt-6 w-full rounded-lg bg-emerald-600 py-2.5 text-sm font-medium text-white shadow-lg shadow-emerald-900/30 transition-colors hover:bg-emerald-500 disabled:opacity-60"
            >
              {submitting ? "Signing in..." : "Continue (demo login)"}
            </button>
            <div className="mt-5 flex items-center gap-3">
              <div className="h-px flex-1 bg-slate-800" />
              <span className="text-xs text-slate-500">or sign in manually</span>
              <div className="h-px flex-1 bg-slate-800" />
            </div>
          </>
        )}

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300">Email</label>
            <input
              type="text"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800/60 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800/60 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          {formError && <p className="text-sm text-red-400">{formError}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-medium text-white shadow-lg shadow-indigo-900/30 transition-colors hover:bg-indigo-500 disabled:opacity-60"
          >
            {submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="mt-5 flex items-center gap-3">
          <div className="h-px flex-1 bg-slate-800" />
          <span className="text-xs text-slate-500">or</span>
          <div className="h-px flex-1 bg-slate-800" />
        </div>

        <button
          type="button"
          onClick={onMicrosoftSignIn}
          disabled={!ssoEnabled}
          title={ssoEnabled ? "Sign in with your Microsoft account" : "SSO isn't enabled yet"}
          className="mt-4 w-full rounded-lg border border-slate-700 py-2.5 text-sm font-medium text-slate-400 transition-colors disabled:cursor-not-allowed disabled:opacity-50"
        >
          Sign in with Microsoft {!ssoEnabled && "(coming soon)"}
        </button>
      </div>
    </div>
  );
}
