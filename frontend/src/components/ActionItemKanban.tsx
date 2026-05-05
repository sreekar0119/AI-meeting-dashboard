import type { ActionItem, ActionItemStatus, MeetingListItem } from '../api/types';
import { getStatusLabel } from '../utils/format';
import { Card } from './Card';
import { EmptyState } from './EmptyState';
import { PriorityBadge } from './PriorityBadge';
import { StatusBadge } from './StatusBadge';

const columns: { status: ActionItemStatus; title: string }[] = [
  { status: 'open', title: 'Open' },
  { status: 'in_progress', title: 'In Progress' },
  { status: 'complete', title: 'Complete' },
];

interface ActionItemKanbanProps {
  items: ActionItem[];
  meetingsById: Record<string, MeetingListItem>;
  onStatusChange: (itemId: string, status: ActionItemStatus) => Promise<void>;
}

export function ActionItemKanban({
  items,
  meetingsById,
  onStatusChange,
}: ActionItemKanbanProps) {
  if (items.length === 0) {
    return <EmptyState title="No tasks yet" description="Adjust the filters or generate insights for a meeting." />;
  }

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {columns.map((column) => {
        const columnItems = items.filter((item) => item.status === column.status);

        return (
          <Card key={column.status} className="flex min-h-[280px] flex-col gap-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-500">
                  {column.title}
                </p>
                <h3 className="text-lg font-semibold text-ink">{columnItems.length} items</h3>
              </div>
              <StatusBadge status={column.status}>{getStatusLabel(column.status)}</StatusBadge>
            </div>

            <div className="space-y-3">
              {columnItems.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-brand-200 bg-white/60 px-4 py-5 text-sm text-slate-500">
                  Nothing here yet.
                </div>
              ) : (
                columnItems.map((item) => (
                  <div
                    key={item.id}
                    className="rounded-2xl border border-white/70 bg-white/90 p-4 shadow-sm shadow-brand-100/40"
                  >
                    <div className="mb-3 flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-ink">{item.task}</p>
                        <p className="mt-1 text-xs text-slate-500">
                          {meetingsById[item.meeting_id]?.title ?? 'Meeting'} · {item.owner}
                        </p>
                      </div>
                      <PriorityBadge priority={item.priority} />
                    </div>

                    <label className="block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                      Move to
                    </label>
                    <select
                      aria-label={`Update status for ${item.task}`}
                      className="mt-2 w-full rounded-xl border border-brand-100 bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200"
                      value={item.status}
                      onChange={(event) => onStatusChange(item.id, event.target.value as ActionItemStatus)}
                    >
                      {columns.map((statusOption) => (
                        <option key={statusOption.status} value={statusOption.status}>
                          {statusOption.title}
                        </option>
                      ))}
                    </select>
                  </div>
                ))
              )}
            </div>
          </Card>
        );
      })}
    </div>
  );
}
