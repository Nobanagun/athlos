import { Link } from "expo-router";
import { useEffect, useState } from "react";
import { FlatList, Pressable, Text, View } from "react-native";

import { listActivities } from "@/data/remote/training";
import type { ActivitySummary } from "@/domain/training";
import { useAuth } from "@/features/auth/useAuth";

/**
 * List screen - read-only for this increment (D6.2). Local
 * loading/error state, no shared data-fetching hook (D7.2) - same
 * pattern already used in (auth)/login.tsx.
 */
export default function ActivitiesScreen() {
  const { session } = useAuth();
  const [activities, setActivities] = useState<ActivitySummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) {
      return;
    }
    let cancelled = false;
    listActivities(session.accessToken)
      .then((result) => {
        if (!cancelled) {
          setError(null);
          setActivities(result);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError("Could not load activities.");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [session]);

  if (error) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24 }}>
        <Text>{error}</Text>
      </View>
    );
  }

  if (activities === null) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <Text>Loading...</Text>
      </View>
    );
  }

  if (activities.length === 0) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24 }}>
        <Text>No activities yet.</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={activities}
      keyExtractor={(activity) => activity.id}
      contentContainerStyle={{ padding: 16, gap: 8 }}
      renderItem={({ item }) => (
        <Link href={`/(app)/activities/${item.sport}/${item.id}`} asChild>
          <Pressable style={{ padding: 12, borderWidth: 1, borderRadius: 8 }}>
            <Text>{item.sport}</Text>
            <Text>{item.startedAt}</Text>
          </Pressable>
        </Link>
      )}
    />
  );
}
