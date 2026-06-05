export type IncidentSeverity = "low" | "medium" | "high" | "critical";
export type IncidentStatus =
  | "open"
  | "investigating"
  | "mitigated"
  | "resolved";

export interface Incident {
  id: string;
  service_id: string;
  release_id: string | null;
  title: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  summary: string | null;
  root_cause: string | null;
  started_at: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface IncidentCreate {
  service_id: string;
  title: string;
  severity: IncidentSeverity;
  status?: IncidentStatus;
  summary?: string | null;
  root_cause?: string | null;
  started_at?: string | null;
  resolved_at?: string | null;
  // Optional, user-confirmed link to the likely release (same service).
  release_id?: string | null;
}

// service_id is immutable from the frontend; all other fields optional.
export type IncidentUpdatePayload = Partial<Omit<IncidentCreate, "service_id">>;

export interface IncidentUpdate {
  id: string;
  incident_id: string;
  message: string;
  author: string | null;
  status: IncidentStatus | null;
  created_at: string;
  updated_at: string;
}

// incident_id comes from the path, not the body. status optional.
export interface IncidentUpdateCreate {
  message: string;
  author?: string | null;
  status?: IncidentStatus | null;
}
