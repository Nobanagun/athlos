import {
  getCyclingActivity,
  getGymActivity,
  getRunningActivity,
  listActivities,
} from "./training";

const originalFetch = globalThis.fetch;
const originalApiUrl = process.env.EXPO_PUBLIC_API_URL;

beforeEach(() => {
  process.env.EXPO_PUBLIC_API_URL = "https://api.test";
  globalThis.fetch = jest.fn();
});

afterEach(() => {
  process.env.EXPO_PUBLIC_API_URL = originalApiUrl;
  globalThis.fetch = originalFetch;
  jest.resetAllMocks();
});

function mockResponse(body: unknown): Response {
  return { ok: true, status: 200, statusText: "", json: async () => body } as Response;
}

test("listActivities maps the summary DTO (snake_case) to the domain shape (camelCase)", async () => {
  (globalThis.fetch as jest.Mock).mockResolvedValue(
    mockResponse([{ id: "1", sport: "running", started_at: "2026-07-24T08:00:00Z" }]),
  );

  const result = await listActivities("token-abc");

  expect(result).toEqual([{ id: "1", sport: "running", startedAt: "2026-07-24T08:00:00Z" }]);
});

test("listActivities sends the Authorization header with the given token", async () => {
  (globalThis.fetch as jest.Mock).mockResolvedValue(mockResponse([]));

  await listActivities("token-abc");

  const [, init] = (globalThis.fetch as jest.Mock).mock.calls[0];
  expect(init.headers.Authorization).toBe("Bearer token-abc");
});

test("getRunningActivity maps distance_meters/duration_seconds to camelCase", async () => {
  (globalThis.fetch as jest.Mock).mockResolvedValue(
    mockResponse({
      id: "1",
      sport: "running",
      distance_meters: 10_000,
      duration_seconds: 3600,
      started_at: "2026-07-24T08:00:00Z",
    }),
  );

  const result = await getRunningActivity("1", "token-abc");

  expect(result).toEqual({
    id: "1",
    sport: "running",
    distanceMeters: 10_000,
    durationSeconds: 3600,
    startedAt: "2026-07-24T08:00:00Z",
  });
});

test("getCyclingActivity maps to the domain shape", async () => {
  (globalThis.fetch as jest.Mock).mockResolvedValue(
    mockResponse({
      id: "2",
      sport: "cycling",
      distance_meters: 40_000,
      duration_seconds: 5400,
      started_at: "2026-07-24T08:00:00Z",
    }),
  );

  const result = await getCyclingActivity("2", "token-abc");

  expect(result.sport).toBe("cycling");
  expect(result.distanceMeters).toBe(40_000);
});

test("getGymActivity maps to the domain shape without a distance field", async () => {
  (globalThis.fetch as jest.Mock).mockResolvedValue(
    mockResponse({
      id: "3",
      sport: "gym",
      duration_seconds: 2700,
      started_at: "2026-07-24T08:00:00Z",
    }),
  );

  const result = await getGymActivity("3", "token-abc");

  expect(result).toEqual({
    id: "3",
    sport: "gym",
    durationSeconds: 2700,
    startedAt: "2026-07-24T08:00:00Z",
  });
  expect("distanceMeters" in result).toBe(false);
});
