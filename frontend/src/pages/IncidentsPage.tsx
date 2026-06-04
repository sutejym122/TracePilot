import PageHeader from "../components/layout/PageHeader";
import Card, { CardBody } from "../components/ui/Card";
import Badge from "../components/ui/Badge";

export default function IncidentsPage() {
  return (
    <div>
      <PageHeader title="Incidents" />
      <Card>
        <CardBody>
          <div className="flex items-center gap-3">
            <Badge tone="signal">Coming soon</Badge>
            <p className="text-sm text-content-muted">
              Incidents will be implemented in a later phase.
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
