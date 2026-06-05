import type { Environment } from "./service";

export type ReleaseStatus =
  | "planned"
  | "in_progress"
  | "testing"
  | "released"
  | "rolled_back";
export type ReadinessStatus = "blocked" | "risky" | "ready";

export interface Release {
  id: string;
  service_id: string;
  version: string;
  environment: Environment;
  status: ReleaseStatus;
  owner: string | null;
  release_notes: string | null;
  released_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReleaseCreate {
  service_id: string;
  version: string;
  environment: Environment;
  status?: ReleaseStatus;
  owner?: string | null;
  release_notes?: string | null;
  released_at?: string | null;
}

// service_id is immutable from the frontend; all other fields optional.
export type ReleaseUpdate = Partial<Omit<ReleaseCreate, "service_id">>;

export interface ReleaseChecklist {
  id: string;
  release_id: string;
  tests_passed: boolean;
  security_review_done: boolean;
  rollback_plan_ready: boolean;
  monitoring_ready: boolean;
  stakeholder_approval: boolean;
  readiness_score: number;
  readiness_status: ReadinessStatus;
  created_at: string;
  updated_at: string;
}

// Only the five booleans are ever sent; backend computes score/status.
export type ChecklistUpdate = Partial<{
  tests_passed: boolean;
  security_review_done: boolean;
  rollback_plan_ready: boolean;
  monitoring_ready: boolean;
  stakeholder_approval: boolean;
}>;
