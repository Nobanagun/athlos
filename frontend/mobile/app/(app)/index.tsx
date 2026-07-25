import { useRouter } from "expo-router";
import { Button, Text, View } from "react-native";

import { useAuth } from "@/features/auth/useAuth";

/**
 * Placeholder home screen - confirms the session works end-to-end
 * (GET /users/me). Real training/activity screens are Fase 4 proper,
 * not this bootstrap increment.
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
      <Button title="Log out" onPress={handleLogout} />
    </View>
  );
}
