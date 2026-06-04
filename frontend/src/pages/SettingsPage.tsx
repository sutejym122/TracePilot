import PageHeader from "../components/layout/PageHeader";
import Card, { CardBody } from "../components/ui/Card";

export default function SettingsPage() {
  return (
    <div>
      <PageHeader
        title="Settings"
        description="Profile and account preferences."
      />
      <Card>
        <CardBody>
          <p className="text-sm text-content-muted">
            Profile details and logout will live here.
          </p>
        </CardBody>
      </Card>
    </div>
  );
}
