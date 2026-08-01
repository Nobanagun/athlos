import * as SecureStore from "@/shared/secureStorage";
import { createContext, type ReactNode, useCallback, useEffect, useState } from "react";

import { getCurrentUser, login as loginRequest, registerDevice } from "@/data/remote/identity";
import { isNetworkOrApiError, setUnauthorizedHandler } from "@/data/remote/httpClient";
import type { AuthSession } from "@/domain/auth";
import { getOrCreateDeviceId } from "@/shared/deviceId";

const TOKEN_STORAGE_KEY = "athlos.access_token";

interface AuthContextValue {
  session: AuthSession | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(async () => {
    setSession(null);
    await SecureStore.deleteItemAsync(TOKEN_STORAGE_KEY);
  }, []);

  // No refresh tokens on the backend (see docs/DECISIONS.md, Fase 3
  // incremento 4) - any 401 forces an immediate logout, no silent
  // refresh attempt.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      void logout();
    });
    return () => setUnauthorizedHandler(null);
  }, [logout]);

  useEffect(() => {
    (async () => {
      const storedToken = await SecureStore.getItemAsync(TOKEN_STORAGE_KEY);
      if (storedToken) {
        try {
          const user = await getCurrentUser(storedToken);
          setSession({ accessToken: storedToken, user });
        } catch {
          await SecureStore.deleteItemAsync(TOKEN_STORAGE_KEY);
        }
      }
      setIsLoading(false);
    })();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { access_token: accessToken } = await loginRequest(email, password);
    await SecureStore.setItemAsync(TOKEN_STORAGE_KEY, accessToken);

    // Device linking is best-effort: the token is already saved, so a
    // network/HTTP failure here must not block login - it's retried on
    // the next login, since registration is idempotent on the backend
    // (see docs/DECISIONS.md, Fase 3 incremento 5). Anything else (a
    // bug, an unexpected local failure) still propagates - only the two
    // expected operational failure modes are swallowed.
    try {
      const deviceId = await getOrCreateDeviceId();
      await registerDevice(deviceId, accessToken);
    } catch (error) {
      if (!isNetworkOrApiError(error)) {
        throw error;
      }
      console.warn("[auth] device registration failed, will retry on next login", error);
    }

    const user = await getCurrentUser(accessToken);
    setSession({ accessToken, user });
  }, []);

  return (
    <AuthContext.Provider value={{ session, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
