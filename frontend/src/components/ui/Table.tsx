import type { ReactNode } from "react";

interface TableProps {
  head: ReactNode; // <th> cells
  children: ReactNode; // <tr> rows
  className?: string;
}

// A thin styled table wrapper for the console look. Horizontally scrolls on small screens.
export default function Table({ head, children, className = "" }: TableProps) {
  return (
    <div className="scrollbar-thin -mx-1 overflow-x-auto px-1">
      <table className={`w-full border-collapse text-sm ${className}`}>
        <thead>
          <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-content-faint">
            {head}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

export function Th({
  children,
  className = "",
}: {
  children?: ReactNode;
  className?: string;
}) {
  return <th className={`px-3 py-2 font-medium ${className}`}>{children}</th>;
}

export function Td({
  children,
  className = "",
}: {
  children?: ReactNode;
  className?: string;
}) {
  return (
    <td className={`px-3 py-2.5 align-middle ${className}`}>{children}</td>
  );
}

export function Tr({
  children,
  className = "",
  onClick,
}: {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}) {
  return (
    <tr
      onClick={onClick}
      className={`border-b border-border/60 last:border-0 ${onClick ? "cursor-pointer hover:bg-surface-hover" : ""} ${className}`}
    >
      {children}
    </tr>
  );
}
