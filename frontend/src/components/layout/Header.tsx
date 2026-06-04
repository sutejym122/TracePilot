import { useLocation } from "react-router-dom";
import Button from "../ui/Button";

// Maps the current path to a page title for the header.
function titleFor(pathname: string): string {
  if (pathname === "/") return "Dashboard";
  if (pathname.startsWith("/services")) return "Services";
  if (pathname.startsWith("/releases")) return "Releases";
  if (pathname.startsWith("/incidents")) return "Incidents";
  if (pathname.startsWith("/settings")) return "Settings";
  return "TracePilot";
}

export default function Header() {
  const { pathname } = useLocation();
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-surface/60 px-5 backdrop-blur">
      <h1 className="text-sm font-semibold tracking-tight">
        {titleFor(pathname)}
      </h1>
      <div className="flex items-center gap-3">
        {/* Auth wiring (real user + logout) arrives in Phase F2. */}
        <span className="text-xs text-content-muted">Not signed in</span>
        <Button variant="ghost" size="sm" disabled>
          Logout
        </Button>
      </div>
    </header>
  );
}
