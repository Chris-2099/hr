import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, setToken, setDevUserEmail, type MeResponse, type DevInfoResponse } from "./api";

interface AuthState {
  user: MeResponse | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  // DEV ONLY - see backend DISABLE_AUTH (app/config.py). When set, the
  // login screen is skipped and this lists who you can impersonate instead.
  devInfo: DevInfoResponse | null;
  switchDevUser: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<MeResponse | null>(null);
  const [devInfo, setDevInfoState] = useState<DevInfoResponse | null>(null);
  const [loading, setLoading] = useState(true);

  async function refreshMe() {
    try {
      const me = await api.get<MeResponse>("/api/auth/me");
      setUser(me);
    } catch {
      setUser(null);
      setToken(null);
    }
  }

  useEffect(() => {
    (async () => {
      try {
        const info = await api.get<DevInfoResponse>("/api/auth/dev-info");
        setDevInfoState(info);
      } catch {
        setDevInfoState(null);
      }
      await refreshMe();
      setLoading(false);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(email: string, password: string) {
    const res = await api.post<{ access_token: string }>("/api/auth/login", { email, password });
    setToken(res.access_token);
    await refreshMe();
  }

  function logout() {
    setToken(null);
    setDevUserEmail(null);
    setUser(null);
  }

  async function switchDevUser(email: string) {
    setDevUserEmail(email);
    await refreshMe();
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, devInfo, switchDevUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
