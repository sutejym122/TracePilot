import { apiGet, apiPost } from "../lib/apiClient";
import type { ApiMetric, ApiMetricCreate } from "../types/metric";

export const metricsApi = {
  list: (serviceId: string) =>
    apiGet<ApiMetric[]>(`/api/services/${serviceId}/metrics`),
  create: (serviceId: string, payload: ApiMetricCreate) =>
    apiPost<ApiMetric>(`/api/services/${serviceId}/metrics`, payload),
  simulate: (serviceId: string) =>
    apiPost<ApiMetric>(`/api/services/${serviceId}/metrics/simulate`),
};
