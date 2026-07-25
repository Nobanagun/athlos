import { Redirect } from "expo-router";

/**
 * Entry route - always points at the authenticated shell; `(app)`'s own
 * layout redirects to `(auth)/login` when there is no session. Keeps
 * the "which group to show" decision in a single place.
 */
export default function Index() {
  return <Redirect href="/(app)" />;
}
