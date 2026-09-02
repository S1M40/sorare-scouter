import { mockApi } from "@/services/mock/api";
import { createRestApi } from "./rest";
import { http, USE_MOCK_API } from "./client";
import type { ScoutlabApi } from "./types";

/**
 * Single entry point for all data access.
 *
 * When `VITE_API_BASE_URL` is set (e.g. `http://localhost:8000`),
 * `USE_MOCK_API` is false and all calls go through `createRestApi(http)`
 * which talks to the FastAPI backend. Otherwise the in-memory mock layer
 * is used for offline/demo development.
 */
export const api: ScoutlabApi = USE_MOCK_API ? mockApi : createRestApi(http);

export type { ScoutlabApi, ScoutQuery } from "./types";
