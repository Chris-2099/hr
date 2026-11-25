import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { signInWithMicrosoft } from "../msal";

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

  async function onMicrosoftSignIn() {
    if (!ssoEnabled) return;
    await signInWithMicrosoft();
    // TODO once AUTH_MODE is flipped on: exchange the MSAL result for our
    // own backend session via /api/auth/entra/callback, then navigate("/").
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-900">HR Workforce Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">Sign in to continue.</p>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700">Email</label>
            <input
              type="text"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </div>
          {formError && <p className="text-sm text-red-600">{formError}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="mt-4 flex items-center gap-3">
          <div className="h-px flex-1 bg-slate-200" />
          <span className="text-xs text-slate-400">or</span>
          <div className="h-px flex-1 bg-slate-200" />
        </div>

        <button
          type="button"
          onClick={onMicrosoftSignIn}
          disabled={!ssoEnabled}
          title={ssoEnabled ? "Sign in with your Microsoft account" : "SSO isn't enabled yet"}
          className="mt-4 w-full rounded-md border border-slate-300 py-2 text-sm font-medium text-slate-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Sign in with Microsoft {!ssoEnabled && "(coming soon)"}
        </button>
      </div>
    </div>
  );
}
