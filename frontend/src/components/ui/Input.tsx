import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export default function Input({ label, error, id, className = "", ...rest }: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label htmlFor={id} className="mb-1.5 block text-xs font-medium text-content-muted">
          {label}
        </label>
      )}
      <input
        id={id}
        className={`w-full rounded-md border border-border-strong bg-surface-raised px-3 py-2 text-sm text-content placeholder:text-content-faint focus:border-signal/50 focus:outline-none focus:ring-2 focus:ring-signal/30 ${className}`}
        {...rest}
      />
      {error && <p className="mt-1 text-xs text-status-down">{error}</p>}
    </div>
  );
}
