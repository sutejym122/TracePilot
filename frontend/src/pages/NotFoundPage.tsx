import { Link } from "react-router-dom";
import Button from "../components/ui/Button";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <p className="font-mono text-5xl font-semibold text-signal">404</p>
      <h1 className="mt-3 text-lg font-semibold">Page not found</h1>
      <p className="mt-1 text-sm text-content-muted">
        That route doesn't exist in TracePilot.
      </p>
      <Link to="/" className="mt-5">
        <Button variant="secondary" size="md">
          Back to dashboard
        </Button>
      </Link>
    </div>
  );
}
