import * as SecureStore from "expo-secure-store";

/**
 * Native (iOS/Android) implementation - thin pass-through to
 * expo-secure-store. Metro resolves secureStorage.web.ts instead of
 * this file when bundling for web (platform-specific file extension),
 * so callers (deviceId.ts, AuthContext.tsx) import "./secureStorage"
 * without knowing which one they get.
 */

export async function getItemAsync(key: string): Promise<string | null> {
  return SecureStore.getItemAsync(key);
}

export async function setItemAsync(key: string, value: string): Promise<void> {
  await SecureStore.setItemAsync(key, value);
}

export async function deleteItemAsync(key: string): Promise<void> {
  await SecureStore.deleteItemAsync(key);
}
