export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface ApiMetric {
  id: string;
  service_id: string;
  endpoint: string;
  method: string; // backend returns a plain string
  status_code: number;
  latency_ms: number;
  request_count: number;
  error_count: number;
  captured_at: string;
  created_at: string;
  updated_at: string;
}

export interface ApiMetricCreate {
  endpoint: string;
  method: HttpMethod;
  status_code: number;
  latency_ms: number;
  request_count: number;
  error_count: number;
  captured_at?: string | null;
}
