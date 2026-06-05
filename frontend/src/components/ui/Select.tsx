import type { SelectHTMLAttributes, ReactNode } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  children: ReactNode;
}

export default function Select({
  label,
  id,
  className = "",
  children,
  ...rest
}: SelectProps) {
  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={id}
          className="mb-1.5 block text-xs font-medium text-content-muted"
        >
          {label}
        </label>
      )}
      <select
        id={id}
        className={`w-full rounded-md border border-border-strong bg-surface-raised px-3 py-2 text-sm text-content focus:border-signal/50 focus:outline-none focus:ring-2 focus:ring-signal/30 ${className}`}
        {...rest}
      >
        {children}
      </select>
    </div>
  );
}
