import { useState, type FormEvent, type ReactNode } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import Card, { CardBody, CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import Spinner from "../components/ui/Spinner";
import ErrorState from "../components/ui/ErrorState";
import Modal from "../components/ui/Modal";
import Input from "../components/ui/Input";
import Select from "../components/ui/Select";
import StatusBadge from "../components/domain/StatusBadge";
import HealthCheckTable from "../components/domain/HealthCheckTable";
import MetricsTable from "../components/domain/MetricsTable";
import {
  useService,
  useServiceHealth,
  useServiceMetrics,
  useRunHealthCheck,
  useSimulateMetric,
  useCreateMetric,
  useDeleteService,
} from "../hooks/useService";
import { formatDateTime } from "../lib/format";
import { ApiError } from "../lib/apiClient";
import type { HttpMethod } from "../types/metric";

function InfoRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 py-2">
      <span className="text-sm text-content-muted">{label}</span>
      <span className="text-right text-sm text-content">{children}</span>
    </div>
  );
}

export default function ServiceDetailPage() {
  const { serviceId = "" } = useParams();
  const navigate = useNavigate();

  const service = useService(serviceId);
  const health = useServiceHealth(serviceId);
  const metrics = useServiceMetrics(serviceId);

  const runCheck = useRunHealthCheck(serviceId);
  const simulate = useSimulateMetric(serviceId);
  const createMetric = useCreateMetric(serviceId);
  const deleteService = useDeleteService(serviceId);

  const [metricOpen, setMetricOpen] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  // Manual metric form state
  const [endpoint, setEndpoint] = useState("");
  const [method, setMethod] = useState<HttpMethod>("GET");
  const [statusCode, setStatusCode] = useState("200");
  const [latency, setLatency] = useState("100");
  const [requests, setRequests] = useState("1");
  const [errors, setErrors] = useState("0");
  const [metricError, setMetricError] = useState<string | null>(null);

  if (service.isLoading) return <Spinner label="Loading service…" />;
  if (service.isError) {
    const notFound =
      service.error instanceof ApiError && service.error.status === 404;
    return (
      <div>
        <Link to="/services" className="text-sm text-signal hover:underline">
          ← Back to services
        </Link>
        <div className="mt-4">
          <ErrorState
            title={notFound ? "Service not found" : "Couldn't load service"}
            message={
              notFound
                ? "This service doesn't exist or doesn't belong to your account."
                : "We couldn't reach the server. Please retry."
            }
            onRetry={notFound ? undefined : () => service.refetch()}
          />
        </div>
      </div>
    );
  }

  const s = service.data!;

  const resetMetricForm = () => {
    setEndpoint("");
    setMethod("GET");
    setStatusCode("200");
    setLatency("100");
    setRequests("1");
    setErrors("0");
    setMetricError(null);
  };

  const submitMetric = async (e: FormEvent) => {
    e.preventDefault();
    setMetricError(null);
    const rc = Number(requests),
      ec = Number(errors),
      lat = Number(latency),
      sc = Number(statusCode);
    if (!endpoint.trim()) return setMetricError("Endpoint is required.");
    if (ec > rc)
      return setMetricError("Error count cannot exceed request count.");
    if (lat < 0 || rc < 0 || ec < 0)
      return setMetricError("Values cannot be negative.");
    try {
      await createMetric.mutateAsync({
        endpoint: endpoint.trim(),
        method,
        status_code: sc,
        latency_ms: lat,
        request_count: rc,
        error_count: ec,
      });
      setMetricOpen(false);
      resetMetricForm();
    } catch (err) {
      setMetricError(
        err instanceof ApiError ? err.message : "Failed to create metric.",
      );
    }
  };

  const onDelete = async () => {
    try {
      await deleteService.mutateAsync();
      navigate("/services", { replace: true });
    } catch {
      setConfirmDelete(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link to="/services" className="text-sm text-signal hover:underline">
          ← Back to services
        </Link>
        <div className="mt-3 flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-semibold tracking-tight">{s.name}</h2>
            <StatusBadge value={s.status} />
            <span className="font-mono text-xs text-content-muted">
              {s.environment}
            </span>
          </div>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              onClick={() => runCheck.mutate()}
              disabled={runCheck.isPending}
            >
              {runCheck.isPending ? "Checking…" : "Run health check"}
            </Button>
            <Button
              variant="secondary"
              onClick={() => simulate.mutate()}
              disabled={simulate.isPending}
            >
              {simulate.isPending ? "Simulating…" : "Simulate metric"}
            </Button>
            <Button variant="danger" onClick={() => setConfirmDelete(true)}>
              Delete
            </Button>
          </div>
        </div>
        {runCheck.isError && (
          <p className="mt-2 text-xs text-status-down">
            Health check failed:{" "}
            {runCheck.error instanceof ApiError
              ? runCheck.error.message
              : "unknown error"}
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Info card */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <h3 className="text-sm font-semibold tracking-tight">
              Service info
            </h3>
          </CardHeader>
          <CardBody className="divide-y divide-border/60">
            <InfoRow label="Owner">{s.owner ?? "—"}</InfoRow>
            <InfoRow label="Repository">
              {s.repo_url ? (
                <a
                  href={s.repo_url}
                  target="_blank"
                  rel="noreferrer"
                  className="font-mono text-xs text-signal hover:underline break-all"
                >
                  {s.repo_url}
                </a>
              ) : (
                "—"
              )}
            </InfoRow>
            <InfoRow label="Health URL">
              <span className="font-mono text-xs break-all">
                {s.health_url ?? "—"}
              </span>
            </InfoRow>
            <InfoRow label="Last deployed">
              {formatDateTime(s.last_deployed_at)}
            </InfoRow>
            <InfoRow label="Created">{formatDateTime(s.created_at)}</InfoRow>
            <InfoRow label="Updated">{formatDateTime(s.updated_at)}</InfoRow>
          </CardBody>
        </Card>

        {/* Health + metrics */}
        <div className="flex flex-col gap-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold tracking-tight">
                Health checks
              </h3>
            </CardHeader>
            <CardBody>
              {health.isLoading ? (
                <Spinner label="Loading…" />
              ) : health.isError ? (
                <ErrorState onRetry={() => health.refetch()} />
              ) : (
                <HealthCheckTable checks={health.data ?? []} />
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader className="flex items-center justify-between">
              <h3 className="text-sm font-semibold tracking-tight">
                API metrics
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setMetricOpen(true)}
              >
                Add metric
              </Button>
            </CardHeader>
            <CardBody>
              {metrics.isLoading ? (
                <Spinner label="Loading…" />
              ) : metrics.isError ? (
                <ErrorState onRetry={() => metrics.refetch()} />
              ) : (
                <MetricsTable metrics={metrics.data ?? []} />
              )}
            </CardBody>
          </Card>
        </div>
      </div>

      {/* Manual metric modal */}
      <Modal
        open={metricOpen}
        onClose={() => {
          setMetricOpen(false);
          resetMetricForm();
        }}
        title="Add metric"
      >
        <form onSubmit={submitMetric} className="flex flex-col gap-4">
          <Input
            id="endpoint"
            label="Endpoint *"
            placeholder="/api/payments/charge"
            value={endpoint}
            onChange={(e) => setEndpoint(e.target.value)}
            required
          />
          <Select
            id="method"
            label="Method"
            value={method}
            onChange={(e) => setMethod(e.target.value as HttpMethod)}
          >
            <option>GET</option>
            <option>POST</option>
            <option>PUT</option>
            <option>PATCH</option>
            <option>DELETE</option>
          </Select>
          <div className="grid grid-cols-2 gap-3">
            <Input
              id="status_code"
              label="Status code"
              type="number"
              value={statusCode}
              onChange={(e) => setStatusCode(e.target.value)}
            />
            <Input
              id="latency_ms"
              label="Latency (ms)"
              type="number"
              min={0}
              value={latency}
              onChange={(e) => setLatency(e.target.value)}
            />
            <Input
              id="request_count"
              label="Requests"
              type="number"
              min={0}
              value={requests}
              onChange={(e) => setRequests(e.target.value)}
            />
            <Input
              id="error_count"
              label="Errors"
              type="number"
              min={0}
              value={errors}
              onChange={(e) => setErrors(e.target.value)}
            />
          </div>
          {metricError && (
            <p className="rounded-md border border-status-down/30 bg-status-down/10 px-3 py-2 text-xs text-status-down">
              {metricError}
            </p>
          )}
          <div className="flex justify-end gap-2 pt-1">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setMetricOpen(false);
                resetMetricForm();
              }}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createMetric.isPending}>
              {createMetric.isPending ? "Adding…" : "Add metric"}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete confirm modal */}
      <Modal
        open={confirmDelete}
        onClose={() => setConfirmDelete(false)}
        title="Delete service"
      >
        <p className="text-sm text-content-muted">
          Delete <span className="font-medium text-content">{s.name}</span>?
          This removes its health checks, metrics, releases, and incidents, and
          cannot be undone.
        </p>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirmDelete(false)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={onDelete}
            disabled={deleteService.isPending}
          >
            {deleteService.isPending ? "Deleting…" : "Delete"}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
