import { useLocation, useNavigate } from "react-router-dom";
import Button from "../ui/Button";
import { useAuth } from "../../hooks/useAuth";

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
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-surface/60 px-5 backdrop-blur">
      <h1 className="text-sm font-semibold tracking-tight">
        {titleFor(pathname)}
      </h1>
      <div className="flex items-center gap-3">
        <span className="text-xs text-content-muted">
          {user ? user.name || user.email : ""}
        </span>
        <Button variant="ghost" size="sm" onClick={handleLogout}>
          Logout
        </Button>
      </div>
    </header>
  );
}
