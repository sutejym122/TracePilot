import { useState, type FormEvent } from "react";
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
import Table, { Td, Th, Tr } from "../components/ui/Table";
import StatusBadge from "../components/domain/StatusBadge";
import { useServices, useCreateService } from "../hooks/useServices";
import { formatDateTime } from "../lib/format";
import { ApiError } from "../lib/apiClient";
import type { Environment } from "../types/service";

export default function ServicesPage() {
  const navigate = useNavigate();
  const { data: services, isLoading, isError, refetch } = useServices();
  const createService = useCreateService();

  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [environment, setEnvironment] = useState<Environment>("dev");
  const [owner, setOwner] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [healthUrl, setHealthUrl] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const resetForm = () => {
    setName("");
    setEnvironment("dev");
    setOwner("");
    setRepoUrl("");
    setHealthUrl("");
    setFormError(null);
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!name.trim()) {
      setFormError("Name is required.");
      return;
    }
    try {
      await createService.mutateAsync({
        name: name.trim(),
        environment,
        owner: owner.trim() || null,
        repo_url: repoUrl.trim() || null,
        health_url: healthUrl.trim() || null,
      });
      setOpen(false);
      resetForm();
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Failed to create service.",
      );
    }
  };

  return (
    <div>
      <PageHeader
        title="Services"
        description="Microservices registered to your account."
        action={<Button onClick={() => setOpen(true)}>New Service</Button>}
      />

      {isLoading ? (
        <Spinner label="Loading services…" />
      ) : isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : !services || services.length === 0 ? (
        <EmptyState
          title="No services yet"
          description="Register your first service to start tracking its health, releases, and incidents."
          action={<Button onClick={() => setOpen(true)}>New Service</Button>}
        />
      ) : (
        <Card className="px-1 py-1">
          <Table
            head={
              <>
                <Th>Name</Th>
                <Th>Environment</Th>
                <Th>Status</Th>
                <Th>Owner</Th>
                <Th>Health URL</Th>
                <Th>Updated</Th>
              </>
            }
          >
            {services.map((s) => (
              <Tr key={s.id} onClick={() => navigate(`/services/${s.id}`)}>
                <Td className="font-medium text-content">{s.name}</Td>
                <Td className="font-mono text-content-muted">
                  {s.environment}
                </Td>
                <Td>
                  <StatusBadge value={s.status} />
                </Td>
                <Td className="text-content-muted">{s.owner ?? "—"}</Td>
                <Td className="max-w-[16rem] truncate font-mono text-content-muted">
                  {s.health_url ?? "—"}
                </Td>
                <Td className="whitespace-nowrap text-content-muted">
                  {formatDateTime(s.updated_at)}
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
        title="New service"
      >
        <form onSubmit={onSubmit} className="flex flex-col gap-4">
          <Input
            id="name"
            label="Name *"
            placeholder="payment-service"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
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
          <Input
            id="owner"
            label="Owner"
            placeholder="team or person"
            value={owner}
            onChange={(e) => setOwner(e.target.value)}
          />
          <Input
            id="repo_url"
            label="Repository URL"
            placeholder="https://github.com/org/repo"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
          />
          <Input
            id="health_url"
            label="Health URL"
            placeholder="https://api.example.com/health"
            value={healthUrl}
            onChange={(e) => setHealthUrl(e.target.value)}
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
            <Button type="submit" disabled={createService.isPending}>
              {createService.isPending ? "Creating…" : "Create service"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
