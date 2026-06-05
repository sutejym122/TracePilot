import { useMemo, useState, type FormEvent } from "react";
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
import { useReleases, useCreateRelease } from "../hooks/useReleases";
import { useServices } from "../hooks/useServices";
import { formatDateTime } from "../lib/format";
import { ApiError } from "../lib/apiClient";
import type { Environment } from "../types/service";
import type { ReleaseStatus } from "../types/release";

// datetime-local value -> ISO string (or null when empty).
function toIsoOrNull(local: string): string | null {
  if (!local) return null;
  const d = new Date(local);
  return Number.isNaN(d.getTime()) ? null : d.toISOString();
}

export default function ReleasesPage() {
  const navigate = useNavigate();
  const releases = useReleases();
  const services = useServices();
  const createRelease = useCreateRelease();

  const serviceName = useMemo(() => {
    const map = new Map<string, string>();
    (services.data ?? []).forEach((s) => map.set(s.id, s.name));
    return map;
  }, [services.data]);

  const [open, setOpen] = useState(false);
  const [serviceId, setServiceId] = useState("");
  const [version, setVersion] = useState("");
  const [environment, setEnvironment] = useState<Environment>("dev");
  const [status, setStatus] = useState<ReleaseStatus>("planned");
  const [owner, setOwner] = useState("");
  const [notes, setNotes] = useState("");
  const [releasedAt, setReleasedAt] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const hasServices = (services.data?.length ?? 0) > 0;

  const resetForm = () => {
    setServiceId("");
    setVersion("");
    setEnvironment("dev");
    setStatus("planned");
    setOwner("");
    setNotes("");
    setReleasedAt("");
    setFormError(null);
  };

  const openModal = () => {
    // Default the picker to the first service for convenience.
    setServiceId(services.data?.[0]?.id ?? "");
    setOpen(true);
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!serviceId) return setFormError("Please choose a service.");
    if (!version.trim()) return setFormError("Version is required.");
    try {
      await createRelease.mutateAsync({
        service_id: serviceId,
        version: version.trim(),
        environment,
        status,
        owner: owner.trim() || null,
        release_notes: notes.trim() || null,
        released_at: toIsoOrNull(releasedAt),
      });
      setOpen(false);
      resetForm();
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Failed to create release.",
      );
    }
  };

  return (
    <div>
      <PageHeader
        title="Releases"
        description="Track release readiness across your services."
        action={<Button onClick={openModal}>New Release</Button>}
      />

      {releases.isLoading ? (
        <Spinner label="Loading releases…" />
      ) : releases.isError ? (
        <ErrorState onRetry={() => releases.refetch()} />
      ) : !releases.data || releases.data.length === 0 ? (
        <EmptyState
          title="No releases yet"
          description="Create a release to start tracking its readiness checklist."
          action={<Button onClick={openModal}>New Release</Button>}
        />
      ) : (
        <Card className="px-1 py-1">
          <Table
            head={
              <>
                <Th>Version</Th>
                <Th>Service</Th>
                <Th>Environment</Th>
                <Th>Status</Th>
                <Th>Owner</Th>
                <Th>Released</Th>
              </>
            }
          >
            {releases.data.map((r) => (
              <Tr key={r.id} onClick={() => navigate(`/releases/${r.id}`)}>
                <Td className="font-mono font-medium text-content">
                  {r.version}
                </Td>
                <Td className="text-content-muted">
                  {serviceName.get(r.service_id) ?? (
                    <span className="font-mono text-xs">
                      {r.service_id.slice(0, 8)}…
                    </span>
                  )}
                </Td>
                <Td className="font-mono text-content-muted">
                  {r.environment}
                </Td>
                <Td>
                  <StatusBadge value={r.status} />
                </Td>
                <Td className="text-content-muted">{r.owner ?? "—"}</Td>
                <Td className="whitespace-nowrap text-content-muted">
                  {formatDateTime(r.released_at ?? r.created_at)}
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
        title="New release"
      >
        {!hasServices ? (
          <div className="flex flex-col gap-4">
            <p className="text-sm text-content-muted">
              You need a service before creating a release. Create one on the
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
            <Input
              id="version"
              label="Version *"
              placeholder="1.0.0"
              required
              value={version}
              onChange={(e) => setVersion(e.target.value)}
            />
            <div className="grid grid-cols-2 gap-3">
              <Select
                id="environment"
                label="Environment"
                value={environment}
                onChange={(e) => setEnvironment(e.target.value as Environment)}
              >
                <option value="dev">dev</option>
                <option value="uat">uat</option>
                <option value="prod">prod</option>
              </Select>
              <Select
                id="status"
                label="Status"
                value={status}
                onChange={(e) => setStatus(e.target.value as ReleaseStatus)}
              >
                <option value="planned">planned</option>
                <option value="in_progress">in_progress</option>
                <option value="testing">testing</option>
                <option value="released">released</option>
                <option value="rolled_back">rolled_back</option>
              </Select>
            </div>
            <Input
              id="owner"
              label="Owner"
              placeholder="team or person"
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
            />
            <Textarea
              id="release_notes"
              label="Release notes"
              rows={3}
              placeholder="What's in this release?"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
            <Input
              id="released_at"
              label="Released at"
              type="datetime-local"
              value={releasedAt}
              onChange={(e) => setReleasedAt(e.target.value)}
            />
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
              <Button type="submit" disabled={createRelease.isPending}>
                {createRelease.isPending ? "Creating…" : "Create release"}
              </Button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
}
