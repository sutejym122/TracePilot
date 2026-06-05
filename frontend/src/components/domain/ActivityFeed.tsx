import type { ReactNode } from "react";
import type { ActivityItem } from "../../types/dashboard";
import EmptyState from "../ui/EmptyState";

// Relative time formatter ("3m ago", "2h ago", "5d ago"), with an absolute fallback.
function relativeTime(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return iso;
  const diffSec = Math.round((Date.now() - then) / 1000);
  if (diffSec < 0) return "just now";
  if (diffSec < 60) return `${diffSec}s ago`;
  const min = Math.floor(diffSec / 60);
  if (min < 60) return `${min}m ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const day = Math.floor(hr / 24);
  if (day < 30) return `${day}d ago`;
  return new Date(iso).toLocaleDateString();
}

const icon = (path: string): ReactNode => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    className="h-4 w-4"
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d={path} />
  </svg>
);

// Per-type icon + accent color for the left rail of each row.
const TYPE_META: Record<
  string,
  { icon: ReactNode; color: string; label: string }
> = {
  health_check: {
    icon: icon("M22 12h-4l-3 9L9 3l-3 9H2"),
    color: "text-status-healthy",
    label: "Health check",
  },
  release: {
    icon: icon("M12 2 4 6v6c0 5 3.5 8 8 10 4.5-2 8-5 8-10V6l-8-4Z"),
    color: "text-signal",
    label: "Release",
  },
  incident: {
    icon: icon(
      "M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z",
    ),
    color: "text-status-down",
    label: "Incident",
  },
  incident_update: {
    icon: icon("M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"),
    color: "text-status-degraded",
    label: "Update",
  },
  metric: {
    icon: icon("M3 3v18h18M7 14l3-3 3 3 5-6"),
    color: "text-status-low",
    label: "Metric",
  },
};

interface ActivityFeedProps {
  items: ActivityItem[];
}

export default function ActivityFeed({ items }: ActivityFeedProps) {
  if (items.length === 0) {
    return (
      <EmptyState
        title="No recent activity"
        description="Health checks, releases, incidents, and metrics will appear here as they happen."
      />
    );
  }

  return (
    <ul className="flex flex-col">
      {items.map((item, i) => {
        const meta = TYPE_META[item.type] ?? {
          icon: icon("M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Z"),
          color: "text-content-muted",
          label: item.type,
        };
        return (
          <li
            key={`${item.type}-${item.timestamp}-${i}`}
            className="flex items-start gap-3 border-b border-border/60 py-3 last:border-0"
          >
            <span className={`mt-0.5 shrink-0 ${meta.color}`}>{meta.icon}</span>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-3">
                <p className="truncate text-sm font-medium text-content">
                  {item.title}
                </p>
                <time className="shrink-0 font-mono text-xs text-content-faint">
                  {relativeTime(item.timestamp)}
                </time>
              </div>
              <p className="mt-0.5 truncate text-xs text-content-muted">
                {item.subtitle}
              </p>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
