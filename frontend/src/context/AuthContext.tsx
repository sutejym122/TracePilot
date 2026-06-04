// Single source of truth for auth state. Boots by reading the stored token and
// validating it via /users/me; exposes login/register/logout to the app.
import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { authApi } from "../api/authApi";
import { clearToken, getToken, setToken } from "../lib/auth";
import { UNAUTHORIZED_EVENT } from "../lib/apiClient";
import type { LoginPayload, RegisterPayload, User } from "../types/auth";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(getToken());
  const [isLoading, setIsLoading] = useState<boolean>(Boolean(getToken()));

  // On boot: if a token exists, validate it and hydrate the user.
  useEffect(() => {
    const existing = getToken();
    if (!existing) {
      setIsLoading(false);
      return;
    }
    let cancelled = false;
    authApi
      .me()
      .then((u) => {
        if (!cancelled) {
          setUser(u);
          setTokenState(existing);
        }
      })
      .catch(() => {
        // Invalid/expired token (or backend down). Reset to logged-out.
        if (!cancelled) {
          clearToken();
          setUser(null);
          setTokenState(null);
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Global 401 handler: any API call that 401s resets auth state.
  useEffect(() => {
    const onUnauthorized = () => {
      setUser(null);
      setTokenState(null);
    };
    window.addEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const { access_token } = await authApi.login(payload);
    setToken(access_token);
    setTokenState(access_token);
    const u = await authApi.me();
    setUser(u);
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    const res = await authApi.register(payload);
    setToken(res.access_token);
    setTokenState(res.access_token);
    // Register returns the user fields in the same response — no extra /me call.
    setUser({
      id: res.id,
      email: res.email,
      name: res.name,
      created_at: res.created_at,
    });
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    setTokenState(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token && user),
      isLoading,
      login,
      register,
      logout,
    }),
    [user, token, isLoading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
