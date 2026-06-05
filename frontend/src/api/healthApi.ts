import { apiGet, apiPost } from "../lib/apiClient";
import type { HealthCheck } from "../types/health";

export const healthApi = {
  list: (serviceId: string) =>
    apiGet<HealthCheck[]>(`/api/services/${serviceId}/health`),
  runCheck: (serviceId: string) =>
    apiPost<HealthCheck>(`/api/services/${serviceId}/health/check`),
};
