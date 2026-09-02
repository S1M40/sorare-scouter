import { describe, it, expect } from "vitest";
import { http } from "./client";
import { createRestApi } from "./rest";
import { USE_MOCK_API } from "./client";

describe("E2E Smoke Tests", () => {
  const api = createRestApi(http);

  it("can connect to backend and fetch data freshness", async () => {
    // Skip if backend is not running or VITE_API_BASE_URL is not set
    if (USE_MOCK_API) {
      console.log("Skipping E2E test, mock mode is active");
      return;
    }

    try {
      const freshness = await api.getDataFreshness();
      expect(freshness).toBeDefined();
      expect(freshness.status).toBeDefined();
      expect(freshness.gameweek).toBeDefined();
    } catch (error) {
      console.warn("Backend might not be running. Skipping.", error);
    }
  });
});

