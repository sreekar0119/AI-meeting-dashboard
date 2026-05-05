import { Link } from 'react-router-dom';

import type { MeetingListItem } from '../api/types';
import { formatDate } from '../utils/format';
import { StatusBadge } from './StatusBadge';

interface MeetingCardProps {
  meeting: MeetingListItem;
}

export function MeetingCard({ meeting }: MeetingCardProps) {
  return (
    <Link
      to={`/meetings/${meeting.id}`}
      className="group block rounded-[1.75rem] border border-white/70 bg-white/90 p-5 transition hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-lg hover:shadow-brand-100/40"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-500">{formatDate(meeting.date)}</p>
          <h3 className="mt-2 text-lg font-semibold text-ink transition group-hover:text-brand-700">{meeting.title}</h3>
        </div>
        <StatusBadge status={meeting.overdue_action_item_count > 0 ? 'open' : 'complete'}>
          {meeting.has_insights ? 'Insights ready' : 'Needs insights'}
        </StatusBadge>
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-600">
        {meeting.summary_short ?? 'Transcript captured and ready for insight generation.'}
      </p>
      <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-500">
        <span className="rounded-full bg-brand-50 px-3 py-1 font-medium text-brand-700">
          {meeting.participants.length} participants
        </span>
        <span className="rounded-full bg-slate-100 px-3 py-1 font-medium">
          {meeting.action_item_count} tracked tasks
        </span>
      </div>
    </Link>
  );
}
