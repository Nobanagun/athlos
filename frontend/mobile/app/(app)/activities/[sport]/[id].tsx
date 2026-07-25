import { useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import { Text, View } from "react-native";

import { getCyclingActivity, getGymActivity, getRunningActivity } from "@/data/remote/training";
import type { ActivityDetail, Sport } from "@/domain/training";
import { useAuth } from "@/features/auth/useAuth";

function isSport(value: string): value is Sport {
  return value === "running" || value === "cycling" || value === "gym";
}

function fetchDetail(sport: Sport, id: string, token: string): Promise<ActivityDetail> {
  switch (sport) {
    case "running":
      return getRunningActivity(id, token);
    case "cycling":
      return getCyclingActivity(id, token);
    case "gym":
      return getGymActivity(id, token);
  }
}

export default function ActivityDetailScreen() {
  const { sport, id } = useLocalSearchParams<{ sport: string; id: string }>();
  const { session } = useAuth();
  const [activity, setActivity] = useState<ActivityDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session || !isSport(sport)) {
      return;
    }
    let cancelled = false;
    fetchDetail(sport, id, session.accessToken)
      .then((result) => {
        if (!cancelled) {
          setError(null);
          setActivity(result);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError("Could not load this activity.");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [session, sport, id]);

  if (!isSport(sport)) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24 }}>
        <Text>Unknown activity type.</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24 }}>
        <Text>{error}</Text>
      </View>
    );
  }

  if (activity === null) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, padding: 24, gap: 8 }}>
      <Text>{activity.sport}</Text>
      <Text>{activity.startedAt}</Text>
      {activity.sport !== "gym" && <Text>{activity.distanceMeters} m</Text>}
      <Text>{activity.durationSeconds} s</Text>
    </View>
  );
}
