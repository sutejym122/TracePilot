// Centralized React Query keys so list/detail/nested collections stay consistent.
export const qk = {
  services: ["services"] as const,
  service: (id: string) => ["services", id] as const,
  serviceHealth: (id: string) => ["services", id, "health"] as const,
  serviceMetrics: (id: string) => ["services", id, "metrics"] as const,
  dashboard: ["dashboard", "summary"] as const,
};
