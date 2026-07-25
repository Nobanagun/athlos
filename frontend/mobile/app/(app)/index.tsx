import { Link, useRouter } from "expo-router";
import { Button, Text, View } from "react-native";

import { useAuth } from "@/features/auth/useAuth";

/**
 * Home screen - confirms the session works end-to-end (GET /users/me)
 * and links to the activities list. Kept as-is rather than replaced by
 * the activities list (D7.1) - it stays the proof that auth works,
 * with training screens one navigation away.
 */
export default function HomeScreen() {
  const { session, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.replace("/(auth)/login");
  };

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", gap: 12 }}>
      <Text>Signed in as {session?.user.email}</Text>
      <Link href="/(app)/activities">View activities</Link>
      <Button title="Log out" onPress={handleLogout} />
    </View>
  );
}
