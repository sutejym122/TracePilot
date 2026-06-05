import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../components/layout/PageHeader";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Spinner from "../components/ui/Spinner";
import ErrorState from "../components/ui/ErrorState";
import EmptyState from "../components/ui/EmptyState";
import Modal from "../components/ui/Modal";
import Input from "../components/ui/Input";
import Select from "../components/ui/Select";
import Textarea from "../components/ui/Textarea";
import Table, { Td, Th, Tr } from "../components/ui/Table";
import StatusBadge from "../components/domain/StatusBadge";
import SeverityBadge from "../components/domain/SeverityBadge";
import { useIncidents, useCreateIncident } from "../hooks/useIncidents";
import { useServices } from "../hooks/useServices";
import { useReleases } from "../hooks/useReleases";
import { formatDateTime } from "../lib/format";
import { ApiError } from "../lib/apiClient";
import type { IncidentSeverity, IncidentStatus } from "../types/incident";

function toIsoOrNull(local: string): string | null {
  if (!local) return null;
  const d = new Date(local);
  return Number.isNaN(d.getTime()) ? null : d.toISOString();
}

// Sentinel for "no linked release" in the picker.
const NO_RELEASE = "";

export default function IncidentsPage() {
  const navigate = useNavigate();
  const incidents = useIncidents();
  const services = useServices();
  const releases = useReleases();
  const createIncident = useCreateIncident();

  const serviceName = useMemo(() => {
    const map = new Map<string, string>();
    (services.data ?? []).forEach((s) => map.set(s.id, s.name));
    return map;
  }, [services.data]);

  const [open, setOpen] = useState(false);
  const [serviceId, setServiceId] = useState("");
  const [releaseId, setReleaseId] = useState<string>(NO_RELEASE);
  const [title, setTitle] = useState("");
  const [severity, setSeverity] = useState<IncidentSeverity>("low");
  const [status, setStatus] = useState<IncidentStatus>("open");
  const [summary, setSummary] = useState("");
  const [rootCause, setRootCause] = useState("");
  const [startedAt, setStartedAt] = useState("");
  const [resolvedAt, setResolvedAt] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const hasServices = (services.data?.length ?? 0) > 0;

  // Releases on the currently selected service, newest first.
  const serviceReleases = useMemo(() => {
    if (!serviceId) return [];
    return (releases.data ?? [])
      .filter((r) => r.service_id === serviceId)
      .slice()
      .sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      );
  }, [releases.data, serviceId]);

  // When the selected service changes, default the picker to its most recent
  // release (the "likely release"), or clear if the service has none.
  useEffect(() => {
    setReleaseId(serviceReleases[0]?.id ?? NO_RELEASE);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [serviceId, releases.data]);

  const resetForm = () => {
    setServiceId("");
    setReleaseId(NO_RELEASE);
    setTitle("");
    setSeverity("low");
    setStatus("open");
    setSummary("");
    setRootCause("");
    setStartedAt("");
    setResolvedAt("");
    setFormError(null);
  };

  const openModal = () => {
    setServiceId(services.data?.[0]?.id ?? "");
    setOpen(true);
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!serviceId) return setFormError("Please choose a service.");
    if (!title.trim()) return setFormError("Title is required.");
    try {
      await createIncident.mutateAsync({
        service_id: serviceId,
        title: title.trim(),
        severity,
        status,
        summary: summary.trim() || null,
        root_cause: rootCause.trim() || null,
        started_at: toIsoOrNull(startedAt),
        resolved_at: toIsoOrNull(resolvedAt),
        // Only include a link when one is chosen.
        release_id: releaseId || null,
      });
      setOpen(false);
      resetForm();
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Failed to create incident.",
      );
    }
  };

  return (
    <div>
      <PageHeader
        title="Incidents"
        description="Track and resolve incidents across your services."
        action={<Button onClick={openModal}>New Incident</Button>}
      />

      {incidents.isLoading ? (
        <Spinner label="Loading incidents…" />
      ) : incidents.isError ? (
        <ErrorState onRetry={() => incidents.refetch()} />
      ) : !incidents.data || incidents.data.length === 0 ? (
        <EmptyState
          title="No incidents yet"
          description="When something breaks, open an incident to track investigation and resolution."
          action={<Button onClick={openModal}>New Incident</Button>}
        />
      ) : (
        <Card className="px-1 py-1">
          <Table
            head={
              <>
                <Th>Title</Th>
                <Th>Service</Th>
                <Th>Severity</Th>
                <Th>Status</Th>
                <Th>Started</Th>
                <Th>Resolved</Th>
              </>
            }
          >
            {incidents.data.map((i) => (
              <Tr key={i.id} onClick={() => navigate(`/incidents/${i.id}`)}>
                <Td className="font-medium text-content">{i.title}</Td>
                <Td className="text-content-muted">
                  {serviceName.get(i.service_id) ?? (
                    <span className="font-mono text-xs">
                      {i.service_id.slice(0, 8)}…
                    </span>
                  )}
                </Td>
                <Td>
                  <SeverityBadge severity={i.severity} />
                </Td>
                <Td>
                  <StatusBadge value={i.status} />
                </Td>
                <Td className="whitespace-nowrap text-content-muted">
                  {formatDateTime(i.started_at ?? i.created_at)}
                </Td>
                <Td className="whitespace-nowrap text-content-muted">
                  {i.resolved_at ? formatDateTime(i.resolved_at) : "—"}
                </Td>
              </Tr>
            ))}
          </Table>
        </Card>
      )}

      <Modal
        open={open}
        onClose={() => {
          setOpen(false);
          resetForm();
        }}
        title="New incident"
      >
        {!hasServices ? (
          <div className="flex flex-col gap-4">
            <p className="text-sm text-content-muted">
              You need a service before creating an incident. Create one on the
              Services page first.
            </p>
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setOpen(false)}>
                Close
              </Button>
              <Button onClick={() => navigate("/services")}>
                Go to Services
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="flex flex-col gap-4">
            <Select
              id="service_id"
              label="Service *"
              value={serviceId}
              onChange={(e) => setServiceId(e.target.value)}
            >
              {services.data!.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.environment})
                </option>
              ))}
            </Select>

            {/* Optional, user-confirmed link to the likely release on this service. */}
            <Select
              id="release_id"
              label="Likely release"
              value={releaseId}
              onChange={(e) => setReleaseId(e.target.value)}
            >
              <option value={NO_RELEASE}>No linked release</option>
              {serviceReleases.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.version} ({r.status})
                </option>
              ))}
            </Select>

            <Input
              id="title"
              label="Title *"
              placeholder="Payment latency spike"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <div className="grid grid-cols-2 gap-3">
              <Select
                id="severity"
                label="Severity"
                value={severity}
                onChange={(e) =>
                  setSeverity(e.target.value as IncidentSeverity)
                }
              >
                <option value="low">low</option>
                <option value="medium">medium</option>
                <option value="high">high</option>
                <option value="critical">critical</option>
              </Select>
              <Select
                id="status"
                label="Status"
                value={status}
                onChange={(e) => setStatus(e.target.value as IncidentStatus)}
              >
                <option value="open">open</option>
                <option value="investigating">investigating</option>
                <option value="mitigated">mitigated</option>
                <option value="resolved">resolved</option>
              </Select>
            </div>
            <Textarea
              id="summary"
              label="Summary"
              rows={2}
              placeholder="What's happening?"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
            />
            <Textarea
              id="root_cause"
              label="Root cause"
              rows={2}
              placeholder="If known"
              value={rootCause}
              onChange={(e) => setRootCause(e.target.value)}
            />
            <div className="grid grid-cols-2 gap-3">
              <Input
                id="started_at"
                label="Started at"
                type="datetime-local"
                value={startedAt}
                onChange={(e) => setStartedAt(e.target.value)}
              />
              <Input
                id="resolved_at"
                label="Resolved at"
                type="datetime-local"
                value={resolvedAt}
                onChange={(e) => setResolvedAt(e.target.value)}
              />
            </div>
            {formError && (
              <p className="rounded-md border border-status-down/30 bg-status-down/10 px-3 py-2 text-xs text-status-down">
                {formError}
              </p>
            )}
            <div className="flex justify-end gap-2 pt-1">
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  setOpen(false);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={createIncident.isPending}>
                {createIncident.isPending ? "Creating…" : "Create incident"}
              </Button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
}
