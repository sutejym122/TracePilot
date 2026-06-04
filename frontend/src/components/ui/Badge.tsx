import type { ReactNode } from "react";

// Maps the backend's lowercase enum values to the spec's color system.
// One source of truth for every status/severity/readiness color in the app.
type Tone =
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

const toneClasses: Record<Tone, string> = {
  healthy: "text-status-healthy border-status-healthy/30 bg-status-healthy/10",
  degraded:
    "text-status-degraded border-status-degraded/30 bg-status-degraded/10",
  down: "text-status-down border-status-down/30 bg-status-down/10",
  unknown: "text-status-unknown border-status-unknown/30 bg-status-unknown/10",
  ready: "text-status-ready border-status-ready/30 bg-status-ready/10",
  risky: "text-status-risky border-status-risky/30 bg-status-risky/10",
  blocked: "text-status-blocked border-status-blocked/30 bg-status-blocked/10",
  critical:
    "text-status-critical border-status-critical/30 bg-status-critical/10",
  high: "text-status-high border-status-high/30 bg-status-high/10",
  medium: "text-status-medium border-status-medium/30 bg-status-medium/10",
  low: "text-status-low border-status-low/30 bg-status-low/10",
  neutral: "text-content-muted border-border-strong bg-surface-raised",
  signal: "text-signal border-signal/30 bg-signal/10",
};

interface BadgeProps {
  tone?: Tone;
  children: ReactNode;
  className?: string;
}

export default function Badge({
  tone = "neutral",
  children,
  className = "",
}: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium ${toneClasses[tone]} ${className}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-80" />
      {children}
    </span>
  );
}
