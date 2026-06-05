import type { ReleaseChecklist, ChecklistUpdate } from "../../types/release";

// The five readiness items, in display order, with human labels.
const ITEMS: { key: keyof ChecklistUpdate; label: string; hint: string }[] = [
  {
    key: "tests_passed",
    label: "Tests passed",
    hint: "Automated test suite is green",
  },
  {
    key: "security_review_done",
    label: "Security review done",
    hint: "Security sign-off complete",
  },
  {
    key: "rollback_plan_ready",
    label: "Rollback plan ready",
    hint: "A tested rollback path exists",
  },
  {
    key: "monitoring_ready",
    label: "Monitoring ready",
    hint: "Dashboards and alerts are in place",
  },
  {
    key: "stakeholder_approval",
    label: "Stakeholder approval",
    hint: "Owners have approved the release",
  },
];

interface Props {
  checklist: ReleaseChecklist;
  onToggle: (field: keyof ChecklistUpdate, value: boolean) => void;
  disabled?: boolean;
}

export default function ChecklistEditor({
  checklist,
  onToggle,
  disabled,
}: Props) {
  return (
    <ul className="flex flex-col">
      {ITEMS.map((item) => {
        const checked = checklist[
          item.key as keyof ReleaseChecklist
        ] as boolean;
        return (
          <li
            key={item.key}
            className="flex items-center justify-between gap-4 border-b border-border/60 py-3 last:border-0"
          >
            <div className="min-w-0">
              <p className="text-sm font-medium text-content">{item.label}</p>
              <p className="text-xs text-content-muted">{item.hint}</p>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={checked}
              disabled={disabled}
              onClick={() => onToggle(item.key, !checked)}
              className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-signal/50 disabled:opacity-50 ${
                checked
                  ? "bg-signal"
                  : "bg-surface-hover border border-border-strong"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-canvas transition-transform ${
                  checked ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </li>
        );
      })}
    </ul>
  );
}
