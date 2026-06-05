import type { ReadinessStatus } from "../../types/release";
import StatusBadge from "./StatusBadge";

interface Props {
  score: number; // 0..100
  status: ReadinessStatus;
}

// Maps readiness status to the stroke color (uses the same palette as badges).
const STROKE: Record<ReadinessStatus, string> = {
  blocked: "#f87171",
  risky: "#fbbf24",
  ready: "#34d399",
};

export default function ReadinessRing({ score, status }: Props) {
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(100, score)) / 100;
  const dash = circumference * pct;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative h-36 w-36">
        <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90">
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke="#222834"
            strokeWidth="10"
          />
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke={STROKE[status]}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circumference - dash}`}
            className="transition-all duration-500 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono text-3xl font-semibold text-content">
            {score}
          </span>
          <span className="text-xs text-content-muted">/ 100</span>
        </div>
      </div>
      <StatusBadge value={status} />
    </div>
  );
}
