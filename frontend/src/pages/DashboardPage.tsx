import PageHeader from "../components/layout/PageHeader";
import Card, { CardBody } from "../components/ui/Card";
import Badge from "../components/ui/Badge";

export default function DashboardPage() {
  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Service health, release readiness, and incident activity at a glance."
      />
      <Card>
        <CardBody>
          <div className="flex items-center gap-3">
            <Badge tone="signal">Phase F3</Badge>
            <p className="text-sm text-content-muted">
              Summary cards and the activity feed will render here once
              dashboard data is wired.
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
