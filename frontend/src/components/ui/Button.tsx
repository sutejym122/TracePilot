import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
}

const variants: Record<Variant, string> = {
  primary:
    "bg-signal text-canvas font-semibold hover:bg-signal/90 active:bg-signal/80",
  secondary:
    "bg-surface-raised text-content border border-border-strong hover:bg-surface-hover",
  ghost: "text-content-muted hover:text-content hover:bg-surface-hover",
  danger:
    "bg-transparent text-status-down border border-status-down/40 hover:bg-status-down/10",
};

const sizes: Record<Size, string> = {
  sm: "px-2.5 py-1 text-xs",
  md: "px-3.5 py-2 text-sm",
};

export default function Button({
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-md transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-signal/50 disabled:opacity-50 disabled:pointer-events-none ${variants[variant]} ${sizes[size]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
