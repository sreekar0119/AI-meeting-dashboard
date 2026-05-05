import type { Priority } from '../api/types';

const styles: Record<Priority, string> = {
  high: 'bg-danger-100 text-danger-700',
  medium: 'bg-warning-100 text-warning-700',
  low: 'bg-brand-100 text-brand-700',
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  return <span className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${styles[priority]}`}>{priority}</span>;
}
