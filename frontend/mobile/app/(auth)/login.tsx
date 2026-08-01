import { useRouter } from "expo-router";
import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";

import { ApiError } from "@/data/remote/httpClient";
import { useAuth } from "@/features/auth/useAuth";

export default function LoginScreen() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    setError(null);
    setIsSubmitting(true);
    try {
      await login(email, password);
      router.replace("/(app)");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setError("Invalid email or password.");
      } else if (error instanceof TypeError) {
        setError("Could not connect to the server. Please check your connection.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text>Athlos</Text>
      <TextInput
        placeholder="Email"
        autoCapitalize="none"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        placeholder="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      {error ? <Text>{error}</Text> : null}
      <Button
        title={isSubmitting ? "..." : "Log in"}
        onPress={handleSubmit}
        disabled={isSubmitting}
      />
      <Button title="Create account" onPress={() => router.push("/(auth)/register")} />
    </View>
  );
}
