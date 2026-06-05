import type { ReactNode } from "react";
import PageHeader from "../components/layout/PageHeader";
import Card, { CardBody, CardHeader } from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import ErrorState from "../components/ui/ErrorState";
import SummaryCard from "../components/domain/SummaryCard";
import ActivityFeed from "../components/domain/ActivityFeed";
import { useDashboard } from "../hooks/useDashboard";

// A labeled row with a colored status dot and a monospaced count.
function StatRow({
  label,
  value,
  dotClass,
}: {
  label: string;
  value: ReactNode;
  dotClass: string;
}) {
  return (
    <div className="flex items-center justify-between py-1.5">
      <span className="flex items-center gap-2 text-sm text-content-muted">
        <span className={`h-2 w-2 rounded-full ${dotClass}`} />
        {label}
      </span>
      <span className="font-mono text-sm text-content">{value}</span>
    </div>
  );
}

function SectionCard({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-semibold tracking-tight">{title}</h3>
      </CardHeader>
      <CardBody>{children}</CardBody>
    </Card>
  );
}

const fmt = (n: number | null, suffix = "") =>
  n === null || n === undefined ? "—" : `${n}${suffix}`;

export default function DashboardPage() {
  const { data, isLoading, isError, refetch, isFetching } = useDashboard();

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Operational summary across services, releases, and incidents."
      />

      {isLoading ? (
        <Spinner label="Loading dashboard…" />
      ) : isError ? (
        <ErrorState
          title="Couldn't load the dashboard"
          message="We couldn't reach the server. Check that the backend is running, then retry."
          onRetry={() => refetch()}
        />
      ) : data ? (
        <div className="flex flex-col gap-6">
          {/* Top summary grid */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-6">
            <SummaryCard
              label="Services"
              value={data.service_summary.total_services}
              hint={`${data.service_summary.healthy_services} healthy`}
            />
            <SummaryCard
              label="Health Checks"
              value={data.health_summary.latest_checks_count}
              hint={
                data.health_summary.average_response_time_ms === null
                  ? "no response data"
                  : `${data.health_summary.average_response_time_ms}ms avg`
              }
            />
            <SummaryCard
              label="Releases"
              value={data.release_summary.total_releases}
              hint={`${data.release_summary.released_releases} released`}
            />
            <SummaryCard
              label="Incidents"
              value={data.incident_summary.total_incidents}
              hint={`${data.incident_summary.open_incidents} open`}
            />
            <SummaryCard
              label="Metrics"
              value={data.metrics_summary.total_metric_samples}
              hint={`${data.metrics_summary.total_requests} requests`}
            />
            <SummaryCard
              label="Error Rate"
              value={`${data.metrics_summary.error_rate_percent}%`}
              hint={`${data.metrics_summary.total_errors} errors`}
              accent={data.metrics_summary.error_rate_percent > 0}
            />
          </div>

          {/* Breakdown cards */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <SectionCard title="Service status">
              <StatRow
                label="Healthy"
                value={data.service_summary.healthy_services}
                dotClass="bg-status-healthy"
              />
              <StatRow
                label="Degraded"
                value={data.service_summary.degraded_services}
                dotClass="bg-status-degraded"
              />
              <StatRow
                label="Down"
                value={data.service_summary.down_services}
                dotClass="bg-status-down"
              />
              <StatRow
                label="Unknown"
                value={data.service_summary.unknown_services}
                dotClass="bg-status-unknown"
              />
            </SectionCard>

            <SectionCard title="Release readiness">
              <StatRow
                label="Ready"
                value={data.release_summary.ready_releases}
                dotClass="bg-status-ready"
              />
              <StatRow
                label="Risky"
                value={data.release_summary.risky_releases}
                dotClass="bg-status-risky"
              />
              <StatRow
                label="Blocked"
                value={data.release_summary.blocked_releases}
                dotClass="bg-status-blocked"
              />
              <div className="mt-2 border-t border-border/60 pt-2">
                <StatRow
                  label="Avg readiness score"
                  value={fmt(data.release_summary.average_readiness_score)}
                  dotClass="bg-signal"
                />
              </div>
            </SectionCard>

            <SectionCard title="Incidents">
              <StatRow
                label="Open"
                value={data.incident_summary.open_incidents}
                dotClass="bg-status-down"
              />
              <StatRow
                label="Investigating"
                value={data.incident_summary.investigating_incidents}
                dotClass="bg-status-degraded"
              />
              <StatRow
                label="Mitigated"
                value={data.incident_summary.mitigated_incidents}
                dotClass="bg-signal"
              />
              <StatRow
                label="Resolved"
                value={data.incident_summary.resolved_incidents}
                dotClass="bg-status-ready"
              />
              <div className="mt-2 border-t border-border/60 pt-2">
                <StatRow
                  label="Critical"
                  value={data.incident_summary.critical_incidents}
                  dotClass="bg-status-critical"
                />
                <StatRow
                  label="High"
                  value={data.incident_summary.high_incidents}
                  dotClass="bg-status-high"
                />
              </div>
            </SectionCard>
          </div>

          {/* Metrics overview + activity */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <SectionCard title="Metrics overview">
              <StatRow
                label="Average latency"
                value={fmt(data.metrics_summary.average_latency_ms, "ms")}
                dotClass="bg-status-low"
              />
              <StatRow
                label="Total requests"
                value={data.metrics_summary.total_requests}
                dotClass="bg-signal"
              />
              <StatRow
                label="Total errors"
                value={data.metrics_summary.total_errors}
                dotClass="bg-status-down"
              />
              <div className="mt-2 border-t border-border/60 pt-2">
                <div className="py-1.5">
                  <div className="text-sm text-content-muted">
                    Slowest endpoint
                  </div>
                  <div className="mt-1 break-all font-mono text-xs text-content">
                    {data.metrics_summary.slowest_endpoint ?? "—"}
                    {data.metrics_summary.slowest_endpoint_latency_ms !==
                      null && (
                      <span className="text-content-faint">
                        {" "}
                        · {data.metrics_summary.slowest_endpoint_latency_ms}ms
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </SectionCard>

            {/* Activity spans two columns on large screens */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold tracking-tight">
                    Recent activity
                  </h3>
                  {isFetching && (
                    <span className="text-xs text-content-faint">
                      refreshing…
                    </span>
                  )}
                </CardHeader>
                <CardBody>
                  <ActivityFeed items={data.recent_activity} />
                </CardBody>
              </Card>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
