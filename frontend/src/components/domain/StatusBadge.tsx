// Maps a backend enum string to the correct Badge tone. One place that knows
// which status word gets which color, reused across the app.
import Badge from "../ui/Badge";

type BadgeTone =
  | "healthy"
  | "degraded"
  | "down"
  | "unknown"
  | "ready"
  | "risky"
  | "blocked"
  | "critical"
  | "high"
  | "medium"
  | "low"
  | "neutral"
  | "signal";

// Every lowercase enum value the backend can emit -> a tone.
const VALUE_TONE: Record<string, BadgeTone> = {
  // service / health
  healthy: "healthy",
  degraded: "degraded",
  down: "down",
  unknown: "unknown",
  // readiness
  ready: "ready",
  risky: "risky",
  blocked: "blocked",
  // incident severity
  critical: "critical",
  high: "high",
  medium: "medium",
  low: "low",
  // release status
  planned: "neutral",
  in_progress: "signal",
  testing: "signal",
  released: "ready",
  rolled_back: "down",
  // incident status
  open: "down",
  investigating: "degraded",
  mitigated: "signal",
  resolved: "ready",
};

interface StatusBadgeProps {
  value: string;
  className?: string;
}

// Renders e.g. "in_progress" -> "in progress" with the right color.
export default function StatusBadge({ value, className }: StatusBadgeProps) {
  const tone = VALUE_TONE[value] ?? "neutral";
  const label = value.replace(/_/g, " ");
  return (
    <Badge tone={tone} className={className}>
      {label}
    </Badge>
  );
}
