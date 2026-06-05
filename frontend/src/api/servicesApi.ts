import { apiDelete, apiGet, apiPatch, apiPost } from "../lib/apiClient";
import type { Service, ServiceCreate, ServiceUpdate } from "../types/service";

export const servicesApi = {
  list: () => apiGet<Service[]>("/api/services"),
  get: (id: string) => apiGet<Service>(`/api/services/${id}`),
  create: (payload: ServiceCreate) =>
    apiPost<Service>("/api/services", payload),
  update: (id: string, payload: ServiceUpdate) =>
    apiPatch<Service>(`/api/services/${id}`, payload),
  remove: (id: string) => apiDelete<void>(`/api/services/${id}`),
};
