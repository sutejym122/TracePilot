import { apiGet } from "../lib/apiClient";
import type { DashboardSummary } from "../types/dashboard";

export const dashboardApi = {
  summary: () => apiGet<DashboardSummary>("/api/dashboard/summary"),
};
