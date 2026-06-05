import type { HealthCheck } from "../../types/health";
import Table, { Td, Th, Tr } from "../ui/Table";
import StatusBadge from "./StatusBadge";
import EmptyState from "../ui/EmptyState";
import { formatDateTime } from "../../lib/format";

interface Props {
  checks: HealthCheck[];
}

export default function HealthCheckTable({ checks }: Props) {
  if (checks.length === 0) {
    return (
      <EmptyState
        title="No health checks yet"
        description="Run a health check to record the first result for this service."
      />
    );
  }

  return (
    <Table
      head={
        <>
          <Th>Status</Th>
          <Th>Code</Th>
          <Th>Response</Th>
          <Th>Error</Th>
          <Th>Checked</Th>
        </>
      }
    >
      {checks.map((c) => (
        <Tr key={c.id}>
          <Td>
            <StatusBadge value={c.status} />
          </Td>
          <Td className="font-mono text-content-muted">
            {c.status_code ?? "—"}
          </Td>
          <Td className="font-mono">
            {c.response_time_ms === null ? "—" : `${c.response_time_ms}ms`}
          </Td>
          <Td className="max-w-[20rem] truncate text-content-muted">
            {c.error_message ?? "—"}
          </Td>
          <Td className="whitespace-nowrap text-content-muted">
            {formatDateTime(c.checked_at)}
          </Td>
        </Tr>
      ))}
    </Table>
  );
}
