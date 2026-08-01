/**
 * Web implementation - expo-secure-store has no browser backend (its
 * native module is an empty stub on web, since there is no OS keychain
 * to wrap: `ExpoSecureStore.default.getValueWithKeyAsync is not a
 * function`). Metro picks this file over secureStorage.ts when
 * bundling for web (platform-specific extension), so this is the only
 * place that knows about the difference - callers stay unchanged.
 * localStorage is unencrypted, acceptable only because Web is not yet
 * a supported production target (see docs/DECISIONS.md).
 */

export async function getItemAsync(key: string): Promise<string | null> {
  return window.localStorage.getItem(key);
}

export async function setItemAsync(key: string, value: string): Promise<void> {
  window.localStorage.setItem(key, value);
}

export async function deleteItemAsync(key: string): Promise<void> {
  window.localStorage.removeItem(key);
}
