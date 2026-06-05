import Badge from "../ui/Badge";
import type { IncidentSeverity } from "../../types/incident";

// Severity -> Badge tone. low blue, medium yellow, high orange, critical red.
const TONE: Record<IncidentSeverity, "low" | "medium" | "high" | "critical"> = {
  low: "low",
  medium: "medium",
  high: "high",
  critical: "critical",
};

export default function SeverityBadge({
  severity,
}: {
  severity: IncidentSeverity;
}) {
  return <Badge tone={TONE[severity]}>{severity}</Badge>;
}
