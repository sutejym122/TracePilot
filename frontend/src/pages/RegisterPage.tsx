import { Link } from "react-router-dom";
import Card, { CardBody } from "../components/ui/Card";
import Button from "../components/ui/Button";

export default function RegisterPage() {
  return (
    <div className="flex h-full items-center justify-center px-4">
      <Card className="w-full max-w-sm">
        <CardBody className="px-6 py-7">
          <div className="mb-6 flex items-center gap-2.5">
            <svg viewBox="0 0 32 32" className="h-7 w-7">
              <rect width="32" height="32" rx="7" fill="#11141b" />
              <path
                d="M5 20 L12 20 L15 11 L18 25 L21 16 L27 16"
                fill="none"
                stroke="#2dd4bf"
                strokeWidth="2.4"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span className="text-lg font-semibold tracking-tight">
              TracePilot
            </span>
          </div>
          <h1 className="text-sm font-semibold">Create account</h1>
          <p className="mt-1 text-sm text-content-muted">
            Registration is implemented in Phase F2.
          </p>
          <Button variant="primary" size="md" className="mt-5 w-full" disabled>
            Create account
          </Button>
          <p className="mt-4 text-center text-xs text-content-muted">
            Already have an account?{" "}
            <Link to="/login" className="text-signal hover:underline">
              Sign in
            </Link>
          </p>
        </CardBody>
      </Card>
    </div>
  );
}
