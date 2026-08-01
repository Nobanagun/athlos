import { act, renderHook, waitFor } from "@testing-library/react-native";
import type { ReactNode } from "react";
import * as SecureStore from "@/shared/secureStorage";

import { ApiError } from "@/data/remote/httpClient";
import * as identity from "@/data/remote/identity";

import { AuthProvider } from "./AuthContext";
import { useAuth } from "./useAuth";

jest.mock("@/shared/secureStorage", () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

jest.mock("@/data/remote/identity", () => ({
  login: jest.fn(),
  registerUser: jest.fn(),
  registerDevice: jest.fn(),
  getCurrentUser: jest.fn(),
}));

jest.mock("@/shared/deviceId", () => ({
  getOrCreateDeviceId: jest.fn().mockResolvedValue("device-123"),
}));

const mockedSecureStore = SecureStore as jest.Mocked<typeof SecureStore>;
const mockedIdentity = identity as jest.Mocked<typeof identity>;

function wrapper({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}

async function renderReadyAuth() {
  const rendered = await renderHook(() => useAuth(), { wrapper });
  await waitFor(() => expect(rendered.result.current.isLoading).toBe(false));
  return rendered;
}

beforeEach(() => {
  jest.clearAllMocks();
  // No persisted session on startup, in every test unless overridden.
  mockedSecureStore.getItemAsync.mockResolvedValue(null);
  mockedIdentity.getCurrentUser.mockResolvedValue({ id: "u1", email: "alice@example.com" });
});

describe("login tolerates a failing device registration", () => {
  test("login succeeds and a session is started even when registerDevice fails (HTTP error)", async () => {
    mockedIdentity.login.mockResolvedValue({ access_token: "token-abc", token_type: "bearer" });
    mockedIdentity.registerDevice.mockRejectedValue(new ApiError(500, "boom"));

    const { result } = await renderReadyAuth();

    await act(async () => {
      await result.current.login("alice@example.com", "s3cret!!");
    });

    expect(result.current.session).toEqual({
      accessToken: "token-abc",
      user: { id: "u1", email: "alice@example.com" },
    });
  });

  test("login succeeds even when registerDevice fails (network error)", async () => {
    mockedIdentity.login.mockResolvedValue({ access_token: "token-abc", token_type: "bearer" });
    mockedIdentity.registerDevice.mockRejectedValue(new TypeError("Network request failed"));

    const { result } = await renderReadyAuth();

    await act(async () => {
      await result.current.login("alice@example.com", "s3cret!!");
    });

    expect(result.current.session?.user.email).toBe("alice@example.com");
  });

  test("the access token is persisted even when registerDevice fails", async () => {
    mockedIdentity.login.mockResolvedValue({ access_token: "token-abc", token_type: "bearer" });
    mockedIdentity.registerDevice.mockRejectedValue(new ApiError(409, "conflict"));

    const { result } = await renderReadyAuth();

    await act(async () => {
      await result.current.login("alice@example.com", "s3cret!!");
    });

    expect(mockedSecureStore.setItemAsync).toHaveBeenCalledWith(
      "athlos.access_token",
      "token-abc",
    );
  });

  test("the device registration error is not propagated to the caller", async () => {
    mockedIdentity.login.mockResolvedValue({ access_token: "token-abc", token_type: "bearer" });
    mockedIdentity.registerDevice.mockRejectedValue(new ApiError(500, "boom"));

    const { result } = await renderReadyAuth();

    await expect(
      act(async () => {
        await result.current.login("alice@example.com", "s3cret!!");
      }),
    ).resolves.not.toThrow();
  });
});

describe("login still fails loudly for anything outside device registration", () => {
  test("propagates errors from login itself (wrong credentials) and starts no session", async () => {
    mockedIdentity.login.mockRejectedValue(new ApiError(401, "Invalid email or password."));

    const { result } = await renderReadyAuth();

    await expect(
      act(async () => {
        await result.current.login("alice@example.com", "wrong-password");
      }),
    ).rejects.toThrow("Invalid email or password.");

    expect(result.current.session).toBeNull();
    expect(mockedIdentity.registerDevice).not.toHaveBeenCalled();
  });

  test("propagates unexpected (non network/HTTP) errors raised during device linking", async () => {
    mockedIdentity.login.mockResolvedValue({ access_token: "token-abc", token_type: "bearer" });
    const { getOrCreateDeviceId } = jest.requireMock("@/shared/deviceId");
    getOrCreateDeviceId.mockRejectedValueOnce(new Error("SecureStore unavailable"));

    const { result } = await renderReadyAuth();

    await expect(
      act(async () => {
        await result.current.login("alice@example.com", "s3cret!!");
      }),
    ).rejects.toThrow("SecureStore unavailable");
  });
});
