import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, ApiError, loadStoredAuthToken, setAuthToken } from "./api";

export type Me = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  can_view_compensation: boolean;
  department_scope: string[] | null;
};

export type AuthConfig = {
  auth_mode: "local" | "entra" | "hybrid";
};

type AuthContextValue = {
  user: Me | null;
  authConfig: AuthConfig;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Me | null>(null);
  const [authConfig, setAuthConfig] = useState<AuthConfig>({ auth_mode: "local" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      loadStoredAuthToken();
      try {
        const config = await api.get<AuthConfig>("/auth/config");
        setAuthConfig(config);
      } catch {
        // config endpoint missing/unreachable - fall back to local-only UI
      }
      try {
        const me = await api.get<Me>("/auth/me");
        setUser(me);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function login(email: string, password: string) {
    setError(null);
    try {
      const { access_token } = await api.post<{ access_token: string }>("/auth/login", {
        email,
        password,
      });
      setAuthToken(access_token);
      const me = await api.get<Me>("/auth/me");
      setUser(me);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
      throw err;
    }
  }

  function logout() {
    setAuthToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, authConfig, loading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
