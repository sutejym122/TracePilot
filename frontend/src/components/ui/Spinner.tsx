interface SpinnerProps {
  label?: string;
  className?: string;
}

export default function Spinner({ label, className = "" }: SpinnerProps) {
  return (
    <div
      className={`flex items-center justify-center gap-3 py-12 text-content-muted ${className}`}
    >
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-border-strong border-t-signal" />
      {label && <span className="text-sm">{label}</span>}
    </div>
  );
}
