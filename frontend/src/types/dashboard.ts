// Mirrors the backend /api/dashboard/summary response exactly. Dates are ISO strings.
export interface ServiceSummary {
  total_services: number;
  healthy_services: number;
  degraded_services: number;
  down_services: number;
  unknown_services: number;
}

export interface HealthSummary {
  latest_checks_count: number;
  healthy_checks: number;
  degraded_checks: number;
  down_checks: number;
  average_response_time_ms: number | null;
}

export interface ReleaseSummary {
  total_releases: number;
  planned_releases: number;
  in_progress_releases: number;
  testing_releases: number;
  released_releases: number;
  rolled_back_releases: number;
  average_readiness_score: number | null;
  ready_releases: number;
  risky_releases: number;
  blocked_releases: number;
}

export interface IncidentSummary {
  total_incidents: number;
  open_incidents: number;
  investigating_incidents: number;
  mitigated_incidents: number;
  resolved_incidents: number;
  critical_incidents: number;
  high_incidents: number;
  recent_updates_count: number;
}

export interface MetricsSummary {
  total_metric_samples: number;
  average_latency_ms: number | null;
  total_requests: number;
  total_errors: number;
  error_rate_percent: number;
  slowest_endpoint: string | null;
  slowest_endpoint_latency_ms: number | null;
}

export interface ActivityItem {
  type: string;
  title: string;
  subtitle: string;
  timestamp: string;
}

export interface DashboardSummary {
  service_summary: ServiceSummary;
  health_summary: HealthSummary;
  release_summary: ReleaseSummary;
  incident_summary: IncidentSummary;
  metrics_summary: MetricsSummary;
  recent_activity: ActivityItem[];
}
