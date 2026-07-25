import { ApiError, request, setUnauthorizedHandler } from "./httpClient";

const originalFetch = globalThis.fetch;
const originalApiUrl = process.env.EXPO_PUBLIC_API_URL;

beforeEach(() => {
  process.env.EXPO_PUBLIC_API_URL = "https://api.test";
  globalThis.fetch = jest.fn();
});

afterEach(() => {
  process.env.EXPO_PUBLIC_API_URL = originalApiUrl;
  globalThis.fetch = originalFetch;
  setUnauthorizedHandler(null);
  jest.resetAllMocks();
});

function mockResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: "",
    json: async () => body,
  } as Response;
}

test("request sends the base URL and JSON body", async () => {
  (globalThis.fetch as jest.Mock).mockResolvedValue(mockResponse(200, { id: "1" }));

  const result = await request<{ id: string }>("/users", {
    method: "POST",
    body: { email: "a@b.com" },
  });

  expect(result).toEqual({ id: "1" });
  expect(globalThis.fetch).toHaveBeenCalledWith(
    "https://api.test/users",
    expect.objectContaining({
      method: "POST",
      body: JSON.stringify({ email: "a@b.com" }),
    }),
  );
});

test("request attaches the Authorization header when a token is given", async () => {
  (globalThis.fetch as jest.Mock).mockResolvedValue(mockResponse(200, { email: "a@b.com" }));

  await request("/users/me", { token: "abc123" });

  const [, init] = (globalThis.fetch as jest.Mock).mock.calls[0];
  expect(init.headers.Authorization).toBe("Bearer abc123");
});

test("request throws ApiError with the backend's detail message on failure", async () => {
  (globalThis.fetch as jest.Mock).mockResolvedValue(
    mockResponse(409, { detail: "Email already registered" }),
  );

  await expect(request("/users", { method: "POST", body: {} })).rejects.toMatchObject({
    status: 409,
    message: "Email already registered",
  });
});

test("request returns undefined for a 204 response", async () => {
  (globalThis.fetch as jest.Mock).mockResolvedValue(mockResponse(204, null));

  const result = await request("/devices/some-id", { method: "DELETE" });

  expect(result).toBeUndefined();
});

test("request calls the registered unauthorized handler on 401", async () => {
  const handler = jest.fn();
  setUnauthorizedHandler(handler);
  (globalThis.fetch as jest.Mock).mockResolvedValue(
    mockResponse(401, { detail: "Invalid or expired authentication token." }),
  );

  await expect(request("/users/me", { token: "expired" })).rejects.toBeInstanceOf(ApiError);
  expect(handler).toHaveBeenCalledTimes(1);
});
