// Centralized React Query keys so list/detail/nested collections stay consistent.
export const qk = {
  services: ["services"] as const,
  service: (id: string) => ["services", id] as const,
  serviceHealth: (id: string) => ["services", id, "health"] as const,
  serviceMetrics: (id: string) => ["services", id, "metrics"] as const,
  releases: ["releases"] as const,
  release: (id: string) => ["releases", id] as const,
  releaseChecklist: (id: string) => ["releases", id, "checklist"] as const,
  incidents: ["incidents"] as const,
  incident: (id: string) => ["incidents", id] as const,
  incidentUpdates: (id: string) => ["incidents", id, "updates"] as const,
  dashboard: ["dashboard", "summary"] as const,
};
