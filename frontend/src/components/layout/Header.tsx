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

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-surface/60 px-4 backdrop-blur sm:px-5">
      <div className="flex items-center gap-2">
        {/* Hamburger — only on mobile */}
        <button
          onClick={onMenuClick}
          className="-ml-1 rounded-md p-2 text-content-muted transition-colors hover:bg-surface-hover hover:text-content md:hidden"
          aria-label="Open menu"
        >
          <svg
            viewBox="0 0 24 24"
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          >
            <path d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 className="text-sm font-semibold tracking-tight">
          {titleFor(pathname)}
        </h1>
      </div>
      <div className="flex items-center gap-3">
        <span className="hidden text-xs text-content-muted sm:inline">
          {user ? user.name || user.email : ""}
        </span>
        <Button variant="ghost" size="sm" onClick={handleLogout}>
          Logout
        </Button>
      </div>
    </header>
  );
}
