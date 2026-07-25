/**
 * Typed access to build-time environment variables.
 *
 * Uses Expo's native `EXPO_PUBLIC_*` support (SDK 49+) - no extra
 * dependency (e.g. `react-native-dotenv`), same minimalism criterion
 * already applied on the backend (see docs/DECISIONS.md).
 *
 * `getApiUrl()` reads lazily, on first real use - not at import time.
 * Same reasoning as `backend/src/athlos/config/settings.py`'s
 * `get_database_url()`: importing this module must never require
 * `EXPO_PUBLIC_API_URL` to be set, so tests can import anything that
 * transitively imports it without configuring the env var first.
 */

export function getApiUrl(): string {
  const value = process.env.EXPO_PUBLIC_API_URL;
  if (!value) {
    throw new Error("EXPO_PUBLIC_API_URL is not set - see frontend/mobile/.env.example.");
  }
  return value;
}
