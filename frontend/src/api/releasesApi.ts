import { apiDelete, apiGet, apiPatch, apiPost } from "../lib/apiClient";
import type {
  ChecklistUpdate,
  Release,
  ReleaseChecklist,
  ReleaseCreate,
  ReleaseUpdate,
} from "../types/release";

export const releasesApi = {
  list: () => apiGet<Release[]>("/api/releases"),
  get: (id: string) => apiGet<Release>(`/api/releases/${id}`),
  create: (payload: ReleaseCreate) =>
    apiPost<Release>("/api/releases", payload),
  update: (id: string, payload: ReleaseUpdate) =>
    apiPatch<Release>(`/api/releases/${id}`, payload),
  remove: (id: string) => apiDelete<void>(`/api/releases/${id}`),
  getChecklist: (id: string) =>
    apiGet<ReleaseChecklist>(`/api/releases/${id}/checklist`),
  updateChecklist: (id: string, payload: ChecklistUpdate) =>
    apiPatch<ReleaseChecklist>(`/api/releases/${id}/checklist`, payload),
};
