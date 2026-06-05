import type { ReactNode } from "react";
import PageHeader from "../components/layout/PageHeader";
import Card, { CardBody, CardHeader } from "../components/ui/Card";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { formatDateTime } from "../lib/format";

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1 py-2.5 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
      <span className="text-sm text-content-muted">{label}</span>
      <span className="text-sm text-content sm:text-right">{children}</span>
    </div>
  );
}

export default function SettingsPage() {
  const { user, token, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        title="Settings"
        description="Your account and session details."
      />

      <div className="flex flex-col gap-6">
        {/* Profile */}
        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold tracking-tight">Profile</h3>
          </CardHeader>
          <CardBody className="divide-y divide-border/60">
            <Row label="Name">{user?.name || "—"}</Row>
            <Row label="Email">{user?.email ?? "—"}</Row>
            <Row label="User ID">
              <span className="font-mono text-xs break-all">
                {user?.id ?? "—"}
              </span>
            </Row>
            <Row label="Account created">
              {formatDateTime(user?.created_at ?? null)}
            </Row>
          </CardBody>
        </Card>

        {/* Session */}
        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold tracking-tight">Session</h3>
          </CardHeader>
          <CardBody className="divide-y divide-border/60">
            <Row label="Status">
              {isAuthenticated ? (
                <Badge tone="healthy">Signed in</Badge>
              ) : (
                <Badge tone="down">Signed out</Badge>
              )}
            </Row>
            <Row label="Token">
              <span className="font-mono text-xs text-content-muted">
                {token ? `${token.slice(0, 12)}…${token.slice(-6)}` : "—"}
              </span>
            </Row>
            <Row label="API base URL">
              <span className="font-mono text-xs break-all">{apiBase}</span>
            </Row>
          </CardBody>
        </Card>

        {/* Scope note + logout */}
        <Card>
          <CardBody className="flex flex-col gap-4">
            <div>
              <h3 className="text-sm font-semibold tracking-tight">
                MVP scope
              </h3>
              <p className="mt-1 text-sm text-content-muted">
                This MVP uses user-scoped tenancy. Workspace/team collaboration
                is planned as a future phase.
              </p>
            </div>
            <div>
              <Button variant="secondary" onClick={handleLogout}>
                Log out
              </Button>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
