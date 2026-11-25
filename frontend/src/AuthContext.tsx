import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "./api";

export type Me = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  can_view_compensation: boolean;
  department_scope: string[] | null;
};

type AuthContextValue = {
  user: Me | null;
  loading: boolean;
};

const AuthContext = createContext<AuthContextValue | null>(null);

// No login/logout here on purpose - this project has zero login UI during
// testing. The backend's DISABLE_AUTH auto-authenticates every request as
// a dev user, so this just fetches whoever that is for display/RBAC
// purposes; there's no token to acquire or manage.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        setUser(await api.get<Me>("/auth/me"));
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return <AuthContext.Provider value={{ user, loading }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
