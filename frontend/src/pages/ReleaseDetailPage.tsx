import { useMemo, useState, type ReactNode } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import Card, { CardBody, CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import Spinner from "../components/ui/Spinner";
import ErrorState from "../components/ui/ErrorState";
import Modal from "../components/ui/Modal";
import Select from "../components/ui/Select";
import StatusBadge from "../components/domain/StatusBadge";
import SeverityBadge from "../components/domain/SeverityBadge";
import ReadinessRing from "../components/domain/ReadinessRing";
import ChecklistEditor from "../components/domain/ChecklistEditor";
import Table, { Td, Th, Tr } from "../components/ui/Table";
import EmptyState from "../components/ui/EmptyState";
import {
  useRelease,
  useReleaseChecklist,
  useUpdateChecklist,
  useUpdateRelease,
  useDeleteRelease,
} from "../hooks/useRelease";
import { useServices } from "../hooks/useServices";
import { useIncidents } from "../hooks/useIncidents";
import { formatDateTime } from "../lib/format";
import { ApiError } from "../lib/apiClient";
import type { ChecklistUpdate, ReleaseStatus } from "../types/release";

function InfoRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 py-2">
      <span className="text-sm text-content-muted">{label}</span>
      <span className="text-right text-sm text-content">{children}</span>
    </div>
  );
}

const STATUSES: ReleaseStatus[] = [
  "planned",
  "in_progress",
  "testing",
  "released",
  "rolled_back",
];

export default function ReleaseDetailPage() {
  const { releaseId = "" } = useParams();
  const navigate = useNavigate();

  const release = useRelease(releaseId);
  const checklist = useReleaseChecklist(releaseId);
  const services = useServices();
  const incidents = useIncidents();

  const updateChecklist = useUpdateChecklist(releaseId);
  const updateRelease = useUpdateRelease(releaseId);
  const deleteRelease = useDeleteRelease(releaseId);

  const [confirmDelete, setConfirmDelete] = useState(false);
  const [editStatus, setEditStatus] = useState(false);
  const [statusDraft, setStatusDraft] = useState<ReleaseStatus>("planned");

  const serviceName = useMemo(() => {
    const r = release.data;
    if (!r) return null;
    return services.data?.find((s) => s.id === r.service_id)?.name ?? null;
  }, [release.data, services.data]);

  // Incidents explicitly linked to this release.
  const relatedIncidents = useMemo(() => {
    return (incidents.data ?? []).filter((i) => i.release_id === releaseId);
  }, [incidents.data, releaseId]);

  if (release.isLoading) return <Spinner label="Loading release…" />;
  if (release.isError) {
    const notFound =
      release.error instanceof ApiError && release.error.status === 404;
    return (
      <div>
        <Link to="/releases" className="text-sm text-signal hover:underline">
          ← Back to releases
        </Link>
        <div className="mt-4">
          <ErrorState
            title={notFound ? "Release not found" : "Couldn't load release"}
            message={
              notFound
                ? "This release doesn't exist or doesn't belong to your account."
                : "We couldn't reach the server. Please retry."
            }
            onRetry={notFound ? undefined : () => release.refetch()}
          />
        </div>
      </div>
    );
  }

  const r = release.data!;

  const onToggle = (field: keyof ChecklistUpdate, value: boolean) => {
    updateChecklist.mutate({ [field]: value });
  };

  const openStatusEdit = () => {
    setStatusDraft(r.status);
    setEditStatus(true);
  };

  const saveStatus = async () => {
    try {
      await updateRelease.mutateAsync({ status: statusDraft });
      setEditStatus(false);
    } catch {
      // error surfaced via mutation state; modal stays open
    }
  };

  const onDelete = async () => {
    try {
      await deleteRelease.mutateAsync();
      navigate("/releases", { replace: true });
    } catch {
      setConfirmDelete(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link to="/releases" className="text-sm text-signal hover:underline">
          ← Back to releases
        </Link>
        <div className="mt-3 flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <h2 className="font-mono text-xl font-semibold tracking-tight">
              {r.version}
            </h2>
            <StatusBadge value={r.status} />
            <span className="font-mono text-xs text-content-muted">
              {r.environment}
            </span>
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
              Release info
            </h3>
          </CardHeader>
          <CardBody className="divide-y divide-border/60">
            <InfoRow label="Service">
              {serviceName ?? (
                <span className="font-mono text-xs">
                  {r.service_id.slice(0, 8)}…
                </span>
              )}
            </InfoRow>
            <InfoRow label="Owner">{r.owner ?? "—"}</InfoRow>
            <InfoRow label="Released at">
              {formatDateTime(r.released_at)}
            </InfoRow>
            <InfoRow label="Created">{formatDateTime(r.created_at)}</InfoRow>
            <InfoRow label="Updated">{formatDateTime(r.updated_at)}</InfoRow>
            <div className="py-2">
              <div className="text-sm text-content-muted">Release notes</div>
              <p className="mt-1 whitespace-pre-wrap text-sm text-content">
                {r.release_notes || "—"}
              </p>
            </div>
          </CardBody>
        </Card>

        {/* Readiness + checklist */}
        <div className="flex flex-col gap-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold tracking-tight">
                Readiness
              </h3>
            </CardHeader>
            <CardBody>
              {checklist.isLoading ? (
                <Spinner label="Loading checklist…" />
              ) : checklist.isError ? (
                <ErrorState onRetry={() => checklist.refetch()} />
              ) : checklist.data ? (
                <div className="flex flex-col items-center gap-8 sm:flex-row sm:items-center sm:gap-10">
                  <ReadinessRing
                    score={checklist.data.readiness_score}
                    status={checklist.data.readiness_status}
                  />
                  <div className="w-full flex-1">
                    <ChecklistEditor
                      checklist={checklist.data}
                      onToggle={onToggle}
                      disabled={updateChecklist.isPending}
                    />
                  </div>
                </div>
              ) : null}
              {updateChecklist.isError && (
                <p className="mt-3 text-xs text-status-down">
                  Failed to update checklist:{" "}
                  {updateChecklist.error instanceof ApiError
                    ? updateChecklist.error.message
                    : "unknown error"}
                </p>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold tracking-tight">
                Related incidents
              </h3>
            </CardHeader>
            <CardBody>
              {incidents.isLoading ? (
                <Spinner label="Loading incidents…" />
              ) : relatedIncidents.length === 0 ? (
                <EmptyState
                  title="No linked incidents"
                  description="Incidents linked to this release will appear here."
                />
              ) : (
                <Table
                  head={
                    <>
                      <Th>Title</Th>
                      <Th>Severity</Th>
                      <Th>Status</Th>
                    </>
                  }
                >
                  {relatedIncidents.map((inc) => (
                    <Tr
                      key={inc.id}
                      onClick={() => navigate(`/incidents/${inc.id}`)}
                    >
                      <Td className="font-medium text-content">{inc.title}</Td>
                      <Td>
                        <SeverityBadge severity={inc.severity} />
                      </Td>
                      <Td>
                        <StatusBadge value={inc.status} />
                      </Td>
                    </Tr>
                  ))}
                </Table>
              )}
            </CardBody>
          </Card>
        </div>
      </div>

      {/* Edit status modal */}
      <Modal
        open={editStatus}
        onClose={() => setEditStatus(false)}
        title="Edit release status"
      >
        <div className="flex flex-col gap-4">
          <Select
            id="status_edit"
            label="Status"
            value={statusDraft}
            onChange={(e) => setStatusDraft(e.target.value as ReleaseStatus)}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </Select>
          {updateRelease.isError && (
            <p className="text-xs text-status-down">
              {updateRelease.error instanceof ApiError
                ? updateRelease.error.message
                : "Update failed."}
            </p>
          )}
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setEditStatus(false)}>
              Cancel
            </Button>
            <Button onClick={saveStatus} disabled={updateRelease.isPending}>
              {updateRelease.isPending ? "Saving…" : "Save"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete confirm */}
      <Modal
        open={confirmDelete}
        onClose={() => setConfirmDelete(false)}
        title="Delete release"
      >
        <p className="text-sm text-content-muted">
          Delete release{" "}
          <span className="font-mono font-medium text-content">
            {r.version}
          </span>
          ? This also removes its checklist and cannot be undone.
        </p>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirmDelete(false)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={onDelete}
            disabled={deleteRelease.isPending}
          >
            {deleteRelease.isPending ? "Deleting…" : "Delete"}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
