import type { TextareaHTMLAttributes } from "react";

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export default function Textarea({
  label,
  error,
  id,
  className = "",
  ...rest
}: TextareaProps) {
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
      <textarea
        id={id}
        className={`w-full rounded-md border border-border-strong bg-surface-raised px-3 py-2 text-sm text-content placeholder:text-content-faint focus:border-signal/50 focus:outline-none focus:ring-2 focus:ring-signal/30 ${className}`}
        {...rest}
      />
      {error && <p className="mt-1 text-xs text-status-down">{error}</p>}
    </div>
  );
}
