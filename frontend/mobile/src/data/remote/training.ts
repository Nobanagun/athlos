import type {
  ActivitySummary,
  CyclingActivity,
  GymActivity,
  RunningActivity,
} from "@/domain/training";

import { request } from "./httpClient";

/**
 * Calls to training's HTTP interface (read-only for this increment -
 * see docs/DECISIONS.md, D6.2). Unlike `identity.ts`, the wire shape
 * (snake_case) genuinely differs from the domain shape (camelCase +
 * per-sport field sets), so this module maps DTO -> domain explicitly
 * rather than returning the raw response - it is the translation
 * boundary `ARCHITECTURE.md` describes for `data/`.
 */

interface ActivitySummaryDto {
  id: string;
  sport: string;
  started_at: string;
}

interface RunningActivityDto {
  id: string;
  sport: string;
  distance_meters: number;
  duration_seconds: number;
  started_at: string;
}

interface CyclingActivityDto {
  id: string;
  sport: string;
  distance_meters: number;
  duration_seconds: number;
  started_at: string;
}

interface GymActivityDto {
  id: string;
  sport: string;
  duration_seconds: number;
  started_at: string;
}

function toActivitySummary(dto: ActivitySummaryDto): ActivitySummary {
  return { id: dto.id, sport: dto.sport as ActivitySummary["sport"], startedAt: dto.started_at };
}

function toRunningActivity(dto: RunningActivityDto): RunningActivity {
  return {
    id: dto.id,
    sport: "running",
    distanceMeters: dto.distance_meters,
    durationSeconds: dto.duration_seconds,
    startedAt: dto.started_at,
  };
}

function toCyclingActivity(dto: CyclingActivityDto): CyclingActivity {
  return {
    id: dto.id,
    sport: "cycling",
    distanceMeters: dto.distance_meters,
    durationSeconds: dto.duration_seconds,
    startedAt: dto.started_at,
  };
}

function toGymActivity(dto: GymActivityDto): GymActivity {
  return {
    id: dto.id,
    sport: "gym",
    durationSeconds: dto.duration_seconds,
    startedAt: dto.started_at,
  };
}

export async function listActivities(token: string): Promise<ActivitySummary[]> {
  const dtos = await request<ActivitySummaryDto[]>("/activities", { token });
  return dtos.map(toActivitySummary);
}

export async function getRunningActivity(id: string, token: string): Promise<RunningActivity> {
  const dto = await request<RunningActivityDto>(`/activities/running/${id}`, { token });
  return toRunningActivity(dto);
}

export async function getCyclingActivity(id: string, token: string): Promise<CyclingActivity> {
  const dto = await request<CyclingActivityDto>(`/activities/cycling/${id}`, { token });
  return toCyclingActivity(dto);
}

export async function getGymActivity(id: string, token: string): Promise<GymActivity> {
  const dto = await request<GymActivityDto>(`/activities/gym/${id}`, { token });
  return toGymActivity(dto);
}
