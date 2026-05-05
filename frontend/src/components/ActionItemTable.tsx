import type { ActionItem, ActionItemStatus, MeetingListItem } from '../api/types';
import { getStatusLabel } from '../utils/format';
import { EmptyState } from './EmptyState';
import { PriorityBadge } from './PriorityBadge';
import { StatusBadge } from './StatusBadge';

interface ActionItemTableProps {
  items: ActionItem[];
  meetingsById: Record<string, MeetingListItem>;
  onStatusChange?: (itemId: string, status: ActionItemStatus) => Promise<void>;
  showMeeting?: boolean;
}

export function ActionItemTable({
  items,
  meetingsById,
  onStatusChange,
  showMeeting = true,
}: ActionItemTableProps) {
  if (items.length === 0) {
    return <EmptyState title="No action items found" description="Create a meeting or change the active filters." />;
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-white/70 bg-white/90 shadow-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-100 text-left">
          <thead className="bg-slate-50/80 text-xs uppercase tracking-[0.22em] text-slate-500">
            <tr>
              <th className="px-5 py-4 font-semibold">Task</th>
              {showMeeting ? <th className="px-5 py-4 font-semibold">Meeting</th> : null}
              <th className="px-5 py-4 font-semibold">Owner</th>
              <th className="px-5 py-4 font-semibold">Priority</th>
              <th className="px-5 py-4 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100/80">
            {items.map((item) => (
              <tr key={item.id} className="align-top">
                <td className="px-5 py-4">
                  <div>
                    <p className="font-semibold text-ink">{item.task}</p>
                    <p className="mt-1 text-xs text-slate-500">
                      {item.source === 'insight' ? 'Generated from meeting insights' : 'Manually tracked'}
                    </p>
                  </div>
                </td>
                {showMeeting ? (
                  <td className="px-5 py-4 text-sm text-slate-600">
                    {meetingsById[item.meeting_id]?.title ?? 'Unknown meeting'}
                  </td>
                ) : null}
                <td className="px-5 py-4 text-sm font-medium text-ink">{item.owner}</td>
                <td className="px-5 py-4">
                  <PriorityBadge priority={item.priority} />
                </td>
                <td className="px-5 py-4">
                  {onStatusChange ? (
                    <select
                      aria-label={`Update status for ${item.task}`}
                      className="w-full min-w-[148px] rounded-xl border border-brand-100 bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200"
                      value={item.status}
                      onChange={(event) =>
                        void onStatusChange(item.id, event.target.value as ActionItemStatus)
                      }
                    >
                      <option value="open">Open</option>
                      <option value="in_progress">In Progress</option>
                      <option value="complete">Complete</option>
                    </select>
                  ) : (
                    <StatusBadge status={item.status}>{getStatusLabel(item.status)}</StatusBadge>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
