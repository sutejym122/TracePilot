import { useMemo, useState, type FormEvent, type ReactNode } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import Card, { CardBody, CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import Spinner from "../components/ui/Spinner";
import ErrorState from "../components/ui/ErrorState";
import Modal from "../components/ui/Modal";
import Input from "../components/ui/Input";
import Select from "../components/ui/Select";
import Textarea from "../components/ui/Textarea";
import StatusBadge from "../components/domain/StatusBadge";
import SeverityBadge from "../components/domain/SeverityBadge";
import Timeline from "../components/domain/Timeline";
import {
  useIncident,
  useIncidentUpdates,
  useAddIncidentUpdate,
  useUpdateIncident,
  useDeleteIncident,
} from "../hooks/useIncident";
import { useServices } from "../hooks/useServices";
import { useReleases } from "../hooks/useReleases";
import { formatDateTime } from "../lib/format";
import { ApiError } from "../lib/apiClient";
import type { IncidentStatus } from "../types/incident";

function InfoRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 py-2">
      <span className="text-sm text-content-muted">{label}</span>
      <span className="text-right text-sm text-content">{children}</span>
    </div>
  );
}

const STATUSES: IncidentStatus[] = [
  "open",
  "investigating",
  "mitigated",
  "resolved",
];
// Sentinel for "no status change" in the composer select.
const NO_CHANGE = "";

export default function IncidentDetailPage() {
  const { incidentId = "" } = useParams();
  const navigate = useNavigate();

  const incident = useIncident(incidentId);
  const updates = useIncidentUpdates(incidentId);
  const services = useServices();
  const releases = useReleases();

  const addUpdate = useAddIncidentUpdate(incidentId);
  const updateIncident = useUpdateIncident(incidentId);
  const deleteIncident = useDeleteIncident(incidentId);

  const [message, setMessage] = useState("");
  const [author, setAuthor] = useState("");
  const [updateStatus, setUpdateStatus] = useState<IncidentStatus | "">(
    NO_CHANGE,
  );
  const [composerError, setComposerError] = useState<string | null>(null);

  const [editStatus, setEditStatus] = useState(false);
  const [statusDraft, setStatusDraft] = useState<IncidentStatus>("open");
  const [confirmDelete, setConfirmDelete] = useState(false);

  const serviceName = useMemo(() => {
    const i = incident.data;
    if (!i) return null;
    return services.data?.find((s) => s.id === i.service_id)?.name ?? null;
  }, [incident.data, services.data]);

  const linkedRelease = useMemo(() => {
    const i = incident.data;
    if (!i || !i.release_id) return null;
    return releases.data?.find((r) => r.id === i.release_id) ?? null;
  }, [incident.data, releases.data]);

  if (incident.isLoading) return <Spinner label="Loading incident…" />;
  if (incident.isError) {
    const notFound =
      incident.error instanceof ApiError && incident.error.status === 404;
    return (
      <div>
        <Link to="/incidents" className="text-sm text-signal hover:underline">
          ← Back to incidents
        </Link>
        <div className="mt-4">
          <ErrorState
            title={notFound ? "Incident not found" : "Couldn't load incident"}
            message={
              notFound
                ? "This incident doesn't exist or doesn't belong to your account."
                : "We couldn't reach the server. Please retry."
            }
            onRetry={notFound ? undefined : () => incident.refetch()}
          />
        </div>
      </div>
    );
  }

  const i = incident.data!;

  const submitUpdate = async (e: FormEvent) => {
    e.preventDefault();
    setComposerError(null);
    if (!message.trim()) return setComposerError("Message is required.");
    try {
      await addUpdate.mutateAsync({
        message: message.trim(),
        author: author.trim() || null,
        // Only send status when the user picked one; omit for "no change".
        ...(updateStatus ? { status: updateStatus } : {}),
      });
      setMessage("");
      setAuthor("");
      setUpdateStatus(NO_CHANGE);
    } catch (err) {
      setComposerError(
        err instanceof ApiError ? err.message : "Failed to post update.",
      );
    }
  };

  const openStatusEdit = () => {
    setStatusDraft(i.status);
    setEditStatus(true);
  };
  const saveStatus = async () => {
    try {
      await updateIncident.mutateAsync({ status: statusDraft });
      setEditStatus(false);
    } catch {
      /* surfaced via mutation state */
    }
  };

  const onDelete = async () => {
    try {
      await deleteIncident.mutateAsync();
      navigate("/incidents", { replace: true });
    } catch {
      setConfirmDelete(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link to="/incidents" className="text-sm text-signal hover:underline">
          ← Back to incidents
        </Link>
        <div className="mt-3 flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-semibold tracking-tight">{i.title}</h2>
            <SeverityBadge severity={i.severity} />
            <StatusBadge value={i.status} />
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={openStatusEdit}>
              Edit status
            </Button>
            <Button variant="danger" onClick={() => setConfirmDelete(true)}>
              Delete
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Info */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <h3 className="text-sm font-semibold tracking-tight">
              Incident info
            </h3>
          </CardHeader>
          <CardBody className="divide-y divide-border/60">
            <InfoRow label="Service">
              {serviceName ?? (
                <span className="font-mono text-xs">
                  {i.service_id.slice(0, 8)}…
                </span>
              )}
            </InfoRow>
            <InfoRow label="Linked release">
              {i.release_id ? (
                linkedRelease ? (
                  <Link
                    to={`/releases/${linkedRelease.id}`}
                    className="inline-flex items-center gap-2 text-signal hover:underline"
                  >
                    <span className="font-mono">{linkedRelease.version}</span>
                    <StatusBadge value={linkedRelease.status} />
                    <span className="font-mono text-xs text-content-muted">
                      {linkedRelease.environment}
                    </span>
                  </Link>
                ) : (
                  // Linked, but the release isn't in the loaded list (e.g. on
                  // another page of data) — still link by id.
                  <Link
                    to={`/releases/${i.release_id}`}
                    className="font-mono text-xs text-signal hover:underline"
                  >
                    {i.release_id.slice(0, 8)}…
                  </Link>
                )
              ) : (
                "—"
              )}
            </InfoRow>
            <InfoRow label="Started">{formatDateTime(i.started_at)}</InfoRow>
            <InfoRow label="Resolved">{formatDateTime(i.resolved_at)}</InfoRow>
            <InfoRow label="Created">{formatDateTime(i.created_at)}</InfoRow>
            <InfoRow label="Updated">{formatDateTime(i.updated_at)}</InfoRow>
            <div className="py-2">
              <div className="text-sm text-content-muted">Summary</div>
              <p className="mt-1 whitespace-pre-wrap text-sm text-content">
                {i.summary || "—"}
              </p>
            </div>
            <div className="py-2">
              <div className="text-sm text-content-muted">Root cause</div>
              <p className="mt-1 whitespace-pre-wrap text-sm text-content">
                {i.root_cause || "—"}
              </p>
            </div>
          </CardBody>
        </Card>

        {/* Timeline + composer */}
        <div className="flex flex-col gap-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold tracking-tight">Timeline</h3>
            </CardHeader>
            <CardBody>
              {updates.isLoading ? (
                <Spinner label="Loading timeline…" />
              ) : updates.isError ? (
                <ErrorState onRetry={() => updates.refetch()} />
              ) : (
                <Timeline updates={updates.data ?? []} />
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold tracking-tight">
                Add update
              </h3>
            </CardHeader>
            <CardBody>
              <form onSubmit={submitUpdate} className="flex flex-col gap-4">
                <Textarea
                  id="message"
                  label="Message *"
                  rows={3}
                  placeholder="What changed? What did you find?"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  required
                />
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    id="author"
                    label="Author"
                    placeholder="your name"
                    value={author}
                    onChange={(e) => setAuthor(e.target.value)}
                  />
                  <Select
                    id="update_status"
                    label="Set status"
                    value={updateStatus}
                    onChange={(e) =>
                      setUpdateStatus(e.target.value as IncidentStatus | "")
                    }
                  >
                    <option value={NO_CHANGE}>No status change</option>
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </Select>
                </div>
                {composerError && (
                  <p className="rounded-md border border-status-down/30 bg-status-down/10 px-3 py-2 text-xs text-status-down">
                    {composerError}
                  </p>
                )}
                <div className="flex justify-end">
                  <Button type="submit" disabled={addUpdate.isPending}>
                    {addUpdate.isPending ? "Posting…" : "Post update"}
                  </Button>
                </div>
              </form>
            </CardBody>
          </Card>
        </div>
      </div>

      {/* Edit status modal */}
      <Modal
        open={editStatus}
        onClose={() => setEditStatus(false)}
        title="Edit incident status"
      >
        <div className="flex flex-col gap-4">
          <Select
            id="status_edit"
            label="Status"
            value={statusDraft}
            onChange={(e) => setStatusDraft(e.target.value as IncidentStatus)}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </Select>
          {updateIncident.isError && (
            <p className="text-xs text-status-down">
              {updateIncident.error instanceof ApiError
                ? updateIncident.error.message
                : "Update failed."}
            </p>
          )}
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setEditStatus(false)}>
              Cancel
            </Button>
            <Button onClick={saveStatus} disabled={updateIncident.isPending}>
              {updateIncident.isPending ? "Saving…" : "Save"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete confirm */}
      <Modal
        open={confirmDelete}
        onClose={() => setConfirmDelete(false)}
        title="Delete incident"
      >
        <p className="text-sm text-content-muted">
          Delete <span className="font-medium text-content">{i.title}</span>?
          This also removes its timeline updates and cannot be undone.
        </p>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirmDelete(false)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={onDelete}
            disabled={deleteIncident.isPending}
          >
            {deleteIncident.isPending ? "Deleting…" : "Delete"}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
