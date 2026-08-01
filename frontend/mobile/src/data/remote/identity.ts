import type { User } from "@/domain/auth";
import { request } from "./httpClient";

/**
 * Calls to the identity module's HTTP interface. Response shapes match
 * the backend's Pydantic schemas exactly (snake_case) - this module is
 * the translation boundary, no separate mapping layer until a real need
 * for one shows up.
 */

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface DeviceResponse {
  device_id: string;
  registered_at: string;
}

export function registerUser(email: string, password: string): Promise<{ id: string }> {
  return request("/users", { method: "POST", body: { email, password } });
}

export function login(email: string, password: string): Promise<LoginResponse> {
  return request("/login", { method: "POST", body: { email, password } });
}

export function registerDevice(deviceId: string, token: string): Promise<DeviceResponse> {
  return request("/devices", { method: "POST", body: { device_id: deviceId }, token });
}

export function getCurrentUser(token: string): Promise<User> {
  return request("/users/me", { token });
}
