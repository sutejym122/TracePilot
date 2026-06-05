import type { ReactNode } from "react";
import Card, { CardBody } from "../ui/Card";

interface SummaryCardProps {
  label: string;
  value: ReactNode; // usually a number/string; monospaced
  hint?: string; // small caption under the value
  accent?: boolean; // highlight the value in the signal color
  icon?: ReactNode;
}

// A single metric tile for the top dashboard grid.
export default function SummaryCard({
  label,
  value,
  hint,
  accent,
  icon,
}: SummaryCardProps) {
  return (
    <Card>
      <CardBody className="px-4 py-3.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium uppercase tracking-wide text-content-muted">
            {label}
          </span>
          {icon && <span className="text-content-faint">{icon}</span>}
        </div>
        <div
          className={`mt-2 font-mono text-2xl font-semibold ${
            accent ? "text-signal" : "text-content"
          }`}
        >
          {value}
        </div>
        {hint && <div className="mt-1 text-xs text-content-muted">{hint}</div>}
      </CardBody>
    </Card>
  );
}
