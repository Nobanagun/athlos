/**
 * Client-side mirror of training's domain types (see
 * docs/ARCHITECTURE.md: "domain/ - Tipos y modelos de dominio del
 * cliente, en espejo con los bounded contexts del backend"). No
 * business logic here - read-only shapes for this increment (see
 * docs/DECISIONS.md, D6.2).
 *
 * A discriminated union by `sport`, mirroring the backend's
 * `ActivitySummary` Protocol (D1.4): the only fields every activity
 * shares are `id`/`sport`/`startedAt` - everything else is specific to
 * `RunningActivity`/`CyclingActivity`/`GymActivity`, which stay
 * otherwise independent, same as their backend counterparts.
 */

export type Sport = "running" | "cycling" | "gym";

export interface ActivitySummary {
  id: string;
  sport: Sport;
  startedAt: string;
}

export interface RunningActivity {
  id: string;
  sport: "running";
  distanceMeters: number;
  durationSeconds: number;
  startedAt: string;
}

export interface CyclingActivity {
  id: string;
  sport: "cycling";
  distanceMeters: number;
  durationSeconds: number;
  startedAt: string;
}

export interface GymActivity {
  id: string;
  sport: "gym";
  durationSeconds: number;
  startedAt: string;
}

export type ActivityDetail = RunningActivity | CyclingActivity | GymActivity;
