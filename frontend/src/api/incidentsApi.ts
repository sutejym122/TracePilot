import { apiDelete, apiGet, apiPatch, apiPost } from "../lib/apiClient";
import type {
  Incident,
  IncidentCreate,
  IncidentUpdate,
  IncidentUpdateCreate,
  IncidentUpdatePayload,
} from "../types/incident";
import type { Release } from "../types/release";

export const incidentsApi = {
  list: () => apiGet<Incident[]>("/api/incidents"),
  get: (id: string) => apiGet<Incident>(`/api/incidents/${id}`),
  create: (payload: IncidentCreate) =>
    apiPost<Incident>("/api/incidents", payload),
  update: (id: string, payload: IncidentUpdatePayload) =>
    apiPatch<Incident>(`/api/incidents/${id}`, payload),
  remove: (id: string) => apiDelete<void>(`/api/incidents/${id}`),
  listUpdates: (id: string) =>
    apiGet<IncidentUpdate[]>(`/api/incidents/${id}/updates`),
  addUpdate: (id: string, payload: IncidentUpdateCreate) =>
    apiPost<IncidentUpdate>(`/api/incidents/${id}/updates`, payload),
  // Candidate releases (newest first) on a service, for the "likely release" link.
  suggestedReleases: (serviceId: string) =>
    apiGet<Release[]>(`/api/incidents/suggested-releases/${serviceId}`),
};
