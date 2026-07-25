import * as Crypto from "expo-crypto";
import * as SecureStore from "expo-secure-store";

/**
 * This installation's device_id - client-generated (see
 * docs/DECISIONS.md, Fase 3 incremento 5): the backend's DeviceId is a
 * UUID it only registers, never generates. Uses `expo-crypto` rather
 * than a global `crypto.randomUUID()` for reliable availability across
 * the Expo runtime, and persists the value once so it survives app
 * restarts (not the native iOS/Android install identifier - that isn't
 * always UUID-shaped, and the backend requires UUID).
 */

const STORAGE_KEY = "athlos.device_id";

export async function getOrCreateDeviceId(): Promise<string> {
  const existing = await SecureStore.getItemAsync(STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const generated = Crypto.randomUUID();
  await SecureStore.setItemAsync(STORAGE_KEY, generated);
  return generated;
}
