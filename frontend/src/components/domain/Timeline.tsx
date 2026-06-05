import type { IncidentUpdate } from "../../types/incident";
import StatusBadge from "./StatusBadge";
import EmptyState from "../ui/EmptyState";
import { formatDateTime } from "../../lib/format";

interface Props {
  updates: IncidentUpdate[];
}

// Chronological incident timeline (oldest first), rendered as a vertical rail.
export default function Timeline({ updates }: Props) {
  if (updates.length === 0) {
    return (
      <EmptyState
        title="No updates yet"
        description="Post the first update to start this incident's timeline."
      />
    );
  }

  // Ensure ascending order regardless of backend ordering guarantees.
  const ordered = [...updates].sort(
    (a, b) =>
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  );

  return (
    <ol className="relative ml-2 border-l border-border">
      {ordered.map((u) => (
        <li key={u.id} className="relative ml-6 pb-6 last:pb-0">
          {/* node on the rail */}
          <span className="absolute -left-[1.84rem] top-1 h-3 w-3 rounded-full border-2 border-canvas bg-signal" />
          <div className="rounded-lg border border-border bg-surface-raised px-4 py-3">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                {u.author ? (
                  <span className="text-sm font-medium text-content">
                    {u.author}
                  </span>
                ) : (
                  <span className="text-sm text-content-muted">System</span>
                )}
                {u.status && <StatusBadge value={u.status} />}
              </div>
              <time className="shrink-0 font-mono text-xs text-content-faint">
                {formatDateTime(u.created_at)}
              </time>
            </div>
            <p className="mt-1.5 whitespace-pre-wrap text-sm text-content">
              {u.message}
            </p>
          </div>
        </li>
      ))}
    </ol>
  );
}
