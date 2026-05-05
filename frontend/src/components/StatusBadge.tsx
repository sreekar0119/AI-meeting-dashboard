import type { PropsWithChildren } from 'react';

import type { ActionItemStatus } from '../api/types';

const styles: Record<ActionItemStatus, string> = {
  open: 'bg-danger-100 text-danger-700',
  in_progress: 'bg-warning-100 text-warning-700',
  complete: 'bg-success-100 text-success-700',
};

export function StatusBadge({
  status,
  children,
}: PropsWithChildren<{ status: ActionItemStatus }>) {
  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${styles[status]}`}>{children}</span>;
}
