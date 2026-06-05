import type { ApiMetric } from "../../types/metric";
import Table, { Td, Th, Tr } from "../ui/Table";
import EmptyState from "../ui/EmptyState";
import { formatDateTime } from "../../lib/format";

interface Props {
  metrics: ApiMetric[];
}

export default function MetricsTable({ metrics }: Props) {
  if (metrics.length === 0) {
    return (
      <EmptyState
        title="No metrics yet"
        description="Simulate a metric or add one manually to populate this service's performance data."
      />
    );
  }

  return (
    <Table
      head={
        <>
          <Th>Method</Th>
          <Th>Endpoint</Th>
          <Th>Code</Th>
          <Th>Latency</Th>
          <Th>Requests</Th>
          <Th>Errors</Th>
          <Th>Captured</Th>
        </>
      }
    >
      {metrics.map((m) => (
        <Tr key={m.id}>
          <Td className="font-mono text-content-muted">{m.method}</Td>
          <Td className="max-w-[16rem] truncate font-mono">{m.endpoint}</Td>
          <Td className="font-mono text-content-muted">{m.status_code}</Td>
          <Td className="font-mono">{m.latency_ms}ms</Td>
          <Td className="font-mono text-content-muted">{m.request_count}</Td>
          <Td
            className={`font-mono ${m.error_count > 0 ? "text-status-down" : "text-content-muted"}`}
          >
            {m.error_count}
          </Td>
          <Td className="whitespace-nowrap text-content-muted">
            {formatDateTime(m.captured_at)}
          </Td>
        </Tr>
      ))}
    </Table>
  );
}
