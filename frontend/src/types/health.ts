export type HealthCheckStatus = "healthy" | "degraded" | "down";

export interface HealthCheck {
  id: string;
  service_id: string;
  status_code: number | null;
  response_time_ms: number | null;
  status: HealthCheckStatus;
  error_message: string | null;
  checked_at: string;
  created_at: string;
  updated_at: string;
}
